# 资源清单

> 持续更新。发现新赛事/靶场就往这里加一条 —— 这也是 commit。

---

## 一、赛事（按类型）

### 纯 AI / Agent 安全

| 赛事 | 说明 | 备注 |
|---|---|---|
| **CrowdStrike + AWS `AI Unlocked: Agents of Chaos`** | 三幕制（Sanctum $10K / Gatekeeper $20K / Basilisk $70K），红队攻击 AI Agent | **按 token 消耗扣分**，精确打击 > 暴力穷举 |
| **KubeArmor AI Security CTF** | 18 题，三个赛道：Prompt Injection Lab / Agent Workflow Hijack / Hidden API & Guardrail Bypass | 浏览器内完成，零环境门槛，新手第一场首选 |
| **AI Cyber Challenge (AIxCC)** | DARPA 主办，AI 自动挖掘与修补漏洞 | 门槛高，关注即可 |

### 传统 CTF 中的 AI 分类

| 赛事 | 说明 |
|---|---|
| **Snyk CTF** | 设有独立 AI 类别（2026 年 5 题：Backstage Pass / Vibecoding / Notely / Admin Only Forum / AI WAF），全是 prompt injection 变体 |
| **BSidesSF CTF** | `verialabs/ctf-agent` 在此打出 52/52 |
| **DEF CON CTF** | 近年出现 AI/LLM 相关题目与 AI 赛道 |

**找比赛的通用入口**：CTFtime.org（看 AI/ML 标签）、各类安全会议的 CTF 公告。

---

## 二、在线练习靶场

| 名称 | 类型 | 适合 |
|---|---|---|
| **Lakera Gandalf** | 7 关提示注入，浏览器内 | Week 2 入门，必做 |
| **Lakera Taxonomy** | 攻击分类图谱 | 建立体系 |
| **Prompt Injection playgrounds** | 各类开源靶场 | 补充练习 |
| **HackTheBox AI 相关房间** | 综合 | Week 7+ |

---

## 三、必读框架与标准

- **OWASP Top 10 for LLM Applications** — 入门第一份文档，只求眼熟
- **OWASP Agentic AI Top 10**（关注更新）— Agent 特有的威胁分类
- **MITRE ATLAS** — 对抗性机器学习威胁知识库，AI 版的 ATT&CK
- **NIST AI RMF** — 偏治理，写防御方案时引用

---

## 四、参考项目

| 项目 | 看点 |
|---|---|
| `verialabs/ctf-agent` | 多模型竞速 + Docker 沙箱 + CTFd 轮询；BSidesSF 2026 52/52。**阶段三的主要参照** |
| `CTF-BTFly` | 国产方案，Wails + Go + Docker 沙箱，接 OpenAI 兼容模型 |
| `Eruditus` | 单模型 CTF 脚本化，比 ctf-agent 简单，适合读源码入门 |

**建议**：先读 Eruditus（简单），再读 ctf-agent（完整）。不要一上来就 clone ctf-agent 配环境。

---

## 五、必读 writeup（学习攻击思路）

- Snyk CTF 2026 AI 类别 writeup（adragos.ro）— 五道题全是真实集成模式的抽象，
  特别是 `Backstage Pass`：应用层的「便利函数」+ 模型可控输出 = 自动化泄露

---

## 六、工具

```
日常    Burp Suite / 浏览器 F12        抓包、改请求体
注入    toolkits/inject_fuzzer.py      本仓库自带
编码    cyberchef                      Base64 / ROT13 / Hex 快速变换
Pwn     pwntools, gdb (+pwndbg), ROPgadget
Rev     radare2 / Ghidra, strings, ltrace
Crypto  SageMath, z3, RsaCtfTool
Misc    binwalk, exiftool, zsteg, volatility3
```

---

## 七、一条学习顺序建议

```
1. OWASP LLM Top 10 过一遍（不求记住）
2. Lakera Gandalf 打完 7 关
3. 本仓库 lab01-lab06 打完 + 自己再造 2 个
4. 读 Snyk CTF AI writeup，复现思路
5. 报名第一场真比赛（KubeArmor 类）
6. 打完 2 场之后，才开始写 solver
```
