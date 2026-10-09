"""
可插拔 LLM 后端。

设计意图：让你在没有 API Key、不花一分钱的情况下把靶场跑通。
绝大多数「Agent 安全题」的考点其实不在模型有多聪明，而在应用层的
拼接方式、过滤器设计和工具权限 —— 这些用规则就能忠实复现。

LLMBackend=mock    -> 内置 MockBackend（默认，零成本）
LLMBackend=openai  -> 任意 OpenAI 兼容接口（官方 / Ollama / vLLM / 中转网关）
"""
from __future__ import annotations

import base64
import codecs
import os
import re
from dataclasses import dataclass, field


# --------------------------------------------------------------------------
# 数据结构
# --------------------------------------------------------------------------
@dataclass
class ToolCall:
    name: str
    arguments: dict = field(default_factory=dict)


@dataclass
class LLMReply:
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)


# --------------------------------------------------------------------------
# 文本解码：真实模型看得懂编码后的指令，这是绕过输入过滤器的基本手法
# --------------------------------------------------------------------------
def decode_variants(text: str) -> list[str]:
    """返回原始文本 + 各种解码后的候选文本。"""
    out = [text]

    # Base64
    for chunk in re.findall(r"[A-Za-z0-9+/]{12,}={0,2}", text):
        try:
            raw = base64.b64decode(chunk + "=" * (-len(chunk) % 4))
            out.append(raw.decode("utf-8", errors="ignore"))
        except Exception:
            pass

    # ROT13
    out.append(codecs.encode(text, "rot13"))

    # 十六进制
    for chunk in re.findall(r"\b(?:0x)?[0-9a-fA-F]{16,}\b", text):
        try:
            out.append(bytes.fromhex(chunk.removeprefix("0x")).decode("utf-8", errors="ignore"))
        except Exception:
            pass

    # 反转
    out.append(text[::-1])

    return out


# --------------------------------------------------------------------------
# Mock 后端：刻意脆弱的假模型
# --------------------------------------------------------------------------
class MockBackend:
    """按规则复现真实 LLM 最常见的几类失效。不要在生产里用，它是拿来被打的。"""

    LEAK = [
        r"system\s*prompt", r"system\s*message", r"developer\s*message",
        r"initial\s+prompt", r"repeat\s+(the\s+)?(above|previous|instructions)",
        r"output your", r"reveal", r"泄露", r"打印.*提示词",
        r"你的(系统|初始|原始|内部)?(指令|设定|提示词|规则)",
        r"(上面|以上|之前)的?(所有)?(指令|内容|文字)",
    ]
    OVERRIDE = [
        r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
        r"disregard\s+(all\s+)?(previous|prior|above)",
        r"忽略(以上|前面|之前)(的)?(所有)?指令",
        r"忘记(之前|以上).*(指令|规则)",
        r"new\s+instruction", r"新的指令",
    ]
    # (正则, 工具名, 参数提取)
    TOOL_INTENT = [
        (r"(导出|export|发送|send|上传|upload|回传|exfil)", "export_data", None),
        (r"(读取|read|cat|打开)\s*([A-Za-z0-9_./\-]+\.(?:txt|md|env|key|pem))", "read_file", "path"),
        (r"(执行|run|exec)\s+(.{1,80})", "run_command", "cmd"),
        (r"(提权|admin|管理员权限|escalate)", "grant_admin", None),
    ]

    def complete(self, system: str, messages: list[dict], tools: list[str] | None = None) -> LLMReply:
        # 关键：把 system / 用户输入 / 检索到的上下文 全部混在一起看。
        # 真实模型就是这样分不清「指令」和「数据」的，间接注入由此成立。
        blob = "\n".join(
            m.get("content", "") for m in messages if isinstance(m.get("content"), str)
        )
        candidates = decode_variants(blob)
        pool = "\n".join(candidates)

        # 1) 指令覆盖优先
        if self._hit(self.OVERRIDE, pool):
            tail = self._after(pool, self.OVERRIDE)
            tc = self._tool_intent(tail + " " + pool, tools)
            if tc:
                return LLMReply(content=f"好的，按新指令执行：`{tc.name}`", tool_calls=[tc])
            return LLMReply(content="已切换到新指令模式。请问接下来需要我做什么？")

        # 2) 系统提示泄露
        if self._hit(self.LEAK, pool):
            return LLMReply(
                content="（模拟：模型照做了，把系统提示原样吐了出来）\n\n" + system
            )

        # 3) 工具滥用
        tc = self._tool_intent(pool, tools)
        if tc:
            return LLMReply(content=f"正在调用 `{tc.name}`…", tool_calls=[tc])

        # 4) 正常回答
        last = messages[-1].get("content", "") if messages else ""
        return LLMReply(content=f"（模拟回复）收到你的问题：{last[:60]}。我是一个助手，无法提供额外帮助。")

    # -- helpers -----------------------------------------------------------
    @staticmethod
    def _hit(patterns: list[str], text: str) -> bool:
        return any(re.search(p, text, re.I) for p in patterns)

    @staticmethod
    def _after(text: str, patterns: list[str]) -> str:
        for p in patterns:
            m = re.search(p, text, re.I)
            if m:
                return text[m.end(): m.end() + 200]
        return ""

    def _tool_intent(self, text: str, tools: list[str] | None) -> ToolCall | None:
        for pattern, name, argkey in self.TOOL_INTENT:
            if tools is not None and name not in tools:
                continue
            m = re.search(pattern, text, re.I)
            if not m:
                continue
            args: dict = {}
            if argkey and m.lastindex and m.lastindex >= 2:
                args[argkey] = m.group(2).strip()
            elif argkey == "path":
                args["path"] = "flag.txt"
            elif argkey == "cmd":
                args["cmd"] = m.group(2).strip()[:80]
            return ToolCall(name=name, arguments=args)
        return None


# --------------------------------------------------------------------------
# 真实后端：OpenAI 兼容
# --------------------------------------------------------------------------
class OpenAICompatBackend:
    def __init__(self) -> None:
        import httpx

        self.key = os.getenv("OPENAI_API_KEY", "")
        self.base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._client = httpx.Client(timeout=60)

    def complete(self, system: str, messages: list[dict], tools: list[str] | None = None) -> LLMReply:
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, *messages],
        }
        r = self._client.post(
            f"{self.base}/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {self.key}"},
        )
        r.raise_for_status()
        msg = r.json()["choices"][0]["message"]
        return LLMReply(content=msg.get("content") or "")


# --------------------------------------------------------------------------
def get_backend():
    """按环境变量返回后端。默认 mock，永远可用。"""
    if os.getenv("LLM_BACKEND", "mock").lower() == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("LLM_BACKEND=openai 但没设置 OPENAI_API_KEY")
        return OpenAICompatBackend()
    return MockBackend()
