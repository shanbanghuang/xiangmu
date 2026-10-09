# agent-ctf-lab

> **AI Agent 安全攻防实验场 + CTF 自动解题工具箱**
>
> 从零起步，两条腿：先打 **LLM / Agent 安全攻防赛道**，再把它沉淀成 **自动解题 Agent**。

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## 为什么这么设计：两条路线其实是同一件事

很多人把「AI 攻防」和「AI 解题」当成两个方向。实际上它们是同一套能力的两面：

| | 你在做的事 | 核心动作 |
|---|---|---|
| **攻防赛道** | 让目标 Agent 违背它自己的系统提示 | 构造输入 → 观察模型/工具链行为 → 绕过约束 |
| **自动解题** | 让自己的 Agent 完成一道人类设计的难题 | 构造提示 → 观察模型/工具链行为 → 达成目标 |

**两边都在练同一件事：如何稳定地操纵一个带工具、带记忆、带权限的 LLM 系统。**
区别只在于 flag 在谁手里。所以先攻防（成本低、反馈快、题目公开），后解题（工程量大、需要攻防积累的直觉来写 solver 的提示词）。

> 参考战绩：`verialabs/ctf-agent` 在 BSidesSF 2026 以多模型竞速 + Docker 沙箱打出 52/52 全解、拿第一。
> 这个仓库初期不追求复现它，而是把它拆开、按你能消化的速度重建一遍。

---

## 仓库结构

```
agent-ctf-lab/
├── docs/                        # 知识资产（最值钱的部分）
│   ├── 00-roadmap.md            # 12 周从零到参赛路线
│   ├── 01-attack-surface.md     # Agent 攻击面图谱 + 现场速查卡
│   ├── 02-playbook.md           # 比赛当天操作手册
│   └── 03-writeup-template.md   # writeup 模板
│
├── labs/                        # 自建靶场：先被自己人打，再去打别人
│   ├── _harness/                # 共用骨架（可插拔 LLM 后端）
│   ├── lab01-direct-injection/  # 直接提示注入 / 系统提示泄露
│   ├── lab02-indirect-injection/# 间接注入（RAG 投毒 / 文件投毒）
│   └── ...                      # lab03 工具越权 / lab04 记忆污染 / lab05 工作流劫持 / lab06 MCP 投毒
│
├── toolkits/                    # 比赛即战力小工具
│   ├── inject_fuzzer.py         # 注入 payload 批量测试器
│   └── payloads/                # 注入语料库（多语言 / 编码 / 分隔符绕过）
│
├── solver/                      # 阶段三：自动解题 Agent（CTFd 轮询 + 沙箱 + 多模型竞速）
│
└── writeups/                    # 外部赛事 writeup（按 年份-赛事 归档）
```

每个 lab 的目录都是同一个形状，方便你批量造题：

```
lab0X-xxx/
├── app.py        # 脆弱的 Agent 应用（FastAPI，自带 /chat 与工具）
├── flag.txt      # flag（本地靶场里明文放着，别害羞）
├── solve.py      # 参考解法，跑通即得分
└── WRITEUP.md    # 一题一记：思路 → 失败尝试 → 成功链
```

---

## 三阶段路线（详见 `docs/00-roadmap.md`）

```
阶段一  攻防基础      Week 1-4    本地靶场 + 攻击面图谱 + payload 库
阶段二  实战参赛      Week 5-10   打公开 AI CTF，沉淀 writeup
阶段三  自动解题      Week 11+    接入 CTFd，把阶段一二的经验编译成 solver 提示词
```

**新手最容易犯的错**：一上来就 clone `ctf-agent` 然后配环境配一礼拜，最后一行题没做。
这个仓库的顺序是反过来的 —— 前四周你**只需要一个 Python 环境**，不需要 API Key、不需要 Docker、不需要花钱。

---

## 5 分钟跑起来

```bash
git clone https://github.com/<you>/agent-ctf-lab.git
cd agent-ctf-lab

# 方式 A：uv（推荐，快）
uv venv && uv pip install -r requirements.txt

# 方式 B：pip
python -m venv .venv && source .venv/bin/activate
pip install -e .

# 起第一个靶场（零成本，用内置的 MockLLM，不需要任何 API Key）
make lab01
# → http://127.0.0.1:8001/docs

# 另一个终端里，用参考解法把它打穿
python labs/lab01-direct-injection/solve.py
```

**MockLLM 是什么？**
一个用规则模拟"脆弱模型"的假后端。它让你在没有 API Key、不花钱的情况下也能练习注入手法 ——
因为**绝大多数注入题的考点不在模型有多聪明，而在应用层的拼接、过滤和权限设计**。
练熟之后把 `LLM_BACKEND=openai` 一改，就能切到真模型上验证。

---

## 赛事日历（持续更新在 `docs/resources.md`）

| 赛事 | 类型 | 备注 |
|---|---|---|
| CrowdStrike + AWS `Agents of Chaos` | Agent 红队 | 三幕制，$100K，按 token 效率扣分 |
| KubeArmor AI Security CTF | 纯 AI 安全 | 18 题，浏览器内完成，零环境 |
| Snyk CTF（AI 类别） | 混合 CTF | AI WAF 绕过、Agent 工具越权、vibe-coded 应用 |
| DEF CON / BSidesSF 等传统 CTF 的 AI 题 | 混合 CTF | 越来越常见的独立 AI 分类 |

---

## 免责声明

本仓库所有靶场均为**本地运行的人造脆弱应用**，用于学习和授权测试。
请勿对未授权的系统、模型或服务使用本仓库中的任何 payload 或工具。

## License

MIT
