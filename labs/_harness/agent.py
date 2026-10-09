"""
极简 Agent 骨架。所有 lab 共用它，让你只关心「这一关的漏洞在哪」。

一个 Agent = 系统提示 + 工具集 + 记忆 + 检索器 + 执行循环。
这五个东西，每一个都是攻击面（详见 docs/01-attack-surface.md）。
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field

from llm import LLMReply, ToolCall, get_backend

# 命中即视为「已经拿到 flag」。覆盖 flag{...} / ctf{...} / agentctf{...} / FLAG=xxx
SOLVED_RE = re.compile(r"(?:flag|ctf)\{|FLAG\s*=", re.I)


@dataclass
class Step:
    role: str          # user / tool / assistant
    content: str
    tool: str | None = None
    args: dict | None = None
    ts: float = field(default_factory=time.time)

    def __str__(self) -> str:
        if self.tool:
            return f"[{self.role}] TOOL {self.tool}({json.dumps(self.args or {}, ensure_ascii=False)}) -> {self.content[:120]}"
        return f"[{self.role}] {self.content[:200]}"


@dataclass
class AgentTrace:
    steps: list[Step] = field(default_factory=list)
    flag_leaked: bool = False

    def dump(self) -> str:
        return "\n".join(str(s) for s in self.steps)


class Agent:
    def __init__(
        self,
        system_prompt: str,
        tools: dict[str, callable] | None = None,
        retriever: callable | None = None,
        memory: list[str] | None = None,
        max_turns: int = 4,
    ):
        self.system = system_prompt
        self.tools = tools or {}
        self.retriever = retriever          # (query) -> str，RAG 的入口
        self.memory = memory or []          # 跨会话记忆 —— lab04 的靶子
        self.max_turns = max_turns
        self.backend = get_backend()

    # ------------------------------------------------------------------
    def _build_messages(self, user_input: str) -> list[dict]:
        msgs: list[dict] = []
        # 记忆先注入（这就是「记忆作为注入面」的成因）
        if self.memory:
            msgs.append({"role": "user", "content": "已知信息：\n" + "\n".join(self.memory)})
        # 检索内容再注入（间接注入的入口）
        if self.retriever:
            ctx = self.retriever(user_input)
            if ctx:
                msgs.append({"role": "user", "content": f"参考文档：\n{ctx}"})
        msgs.append({"role": "user", "content": user_input})
        return msgs

    def _exec_tool(self, call: ToolCall) -> str:
        fn = self.tools.get(call.name)
        if fn is None:
            return f"错误：没有工具 {call.name}"
        try:
            return str(fn(**(call.arguments or {})))
        except Exception as e:  # 故意宽泛：真实系统的工具报错也是信息泄露点
            return f"工具异常：{type(e).__name__}: {e}"

    # ------------------------------------------------------------------
    def handle(self, user_input: str) -> AgentTrace:
        trace = AgentTrace()
        trace.steps.append(Step("user", user_input))
        messages = self._build_messages(user_input)
        seen: set[str] = set()   # 防止同一调用被反复触发（真实 Agent 也有这个毛病）

        for _ in range(self.max_turns):
            reply: LLMReply = self.backend.complete(
                self.system, messages, tools=list(self.tools) or None
            )
            trace.steps.append(Step("assistant", reply.content))

            if not reply.tool_calls:
                break

            for call in reply.tool_calls:
                key = call.name + json.dumps(call.arguments, sort_keys=True)
                if key in seen:
                    trace.flag_leaked = bool(SOLVED_RE.search(trace.steps[-1].content))
                    return trace
                seen.add(key)

                result = self._exec_tool(call)
                trace.steps.append(Step("tool", result, tool=call.name, args=call.arguments))
                messages.append({"role": "user", "content": f"工具 {call.name} 返回：{result}"})

            # 工具结果里已经出现 flag，说明打穿了
            if any(SOLVED_RE.search(s.content) for s in trace.steps if s.role == "tool"):
                trace.flag_leaked = True
                break

        if SOLVED_RE.search(trace.steps[-1].content):
            trace.flag_leaked = True
        return trace
