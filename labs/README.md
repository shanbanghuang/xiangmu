# 靶场使用与造题指南

## 跑起来

```bash
pip install -r requirements.txt     # 或 uv pip install -r requirements.txt
make lab01                          # http://127.0.0.1:8001/docs
python labs/lab01-direct-injection/solve.py
```

默认用内置 `MockBackend`，**不需要 API Key、不花钱**。

想换成真模型验证手法的普适性：

```bash
cp .env.example .env
# 编辑 .env：LLM_BACKEND=openai，填入 OPENAI_API_KEY / BASE_URL / MODEL
```

---

## 目录约定

每个 lab 都一样，方便批量造题：

```
lab0X-<名字>/
├── app.py        # 脆弱应用（FastAPI，PORT = 800X）
├── flag.txt      # flag 明文
├── solve.py      # 参考解法，跑通即得分（exit 0 = 通关）
├── WRITEUP.md    # 思路 / 失败尝试 / 正确修法
└── data/         # 需要的话放被投毒的文档
```

命名用 `lab0X-<短横线名>`，端口 `800X`，这样 `make lab0X` 一律对得上。

---

## 已有关卡

| # | 名称 | 考点 | 攻击面层 |
|---|---|---|---|
| 01 | direct-injection | 系统提示泄露、黑名单绕过 | L0 / L7 |
| 02 | indirect-injection | RAG 投毒、数据与指令不分离 | L6 |

## 待造（Week 3-4 的产出）

| # | 名称 | 考点 | 攻击面层 |
|---|---|---|---|
| 03 | tool-abuse | 工具越权、参数注入、链式调用 | L5 |
| 04 | memory-poison | 跨会话记忆污染、渐进式越狱 | L4 |
| 05 | workflow-hijack | 链式工具调用外带、审批门伪造 | L5 / L1 |
| 06 | mcp-supply | MCP 工具描述投毒、插件供应链 | L2 |

---

## 造一个新 lab 的最快方式

1. `cp -r labs/lab01-direct-injection labs/lab03-tool-abuse`
2. 改 `app.py` 里的 `SYSTEM_PROMPT` / `TOOLS` / 端口号
3. 把漏洞点写进 `SYSTEM_PROMPT` 或工具实现里
4. 改 `solve.py` 的 payload，**跑通为止**
5. 写 `WRITEUP.md`（照 `docs/03-writeup-template.md`）

**造题比做题更涨功力。** 你必须先想清楚「正确实现长什么样」，
才能故意把它写错 —— 这个过程会逼你把攻击面图谱真正吃透。

---

## 共用骨架

`labs/_harness/` 里两个文件，所有 lab 都 import 它们：

- `llm.py` — `get_backend()` 返回 mock 或 openai 后端；`decode_variants()` 模拟模型能读懂编码
- `agent.py` — `Agent(system, tools, retriever, memory)` + `AgentTrace` 执行轨迹

`AgentTrace` 是有意设计的：**每道题都要留下「模型看到了什么、调用了什么、参数是什么」**。
蓝队视角的题目（溯源、复盘）全靠它。
