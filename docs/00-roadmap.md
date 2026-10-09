# 12 周路线：从零到能打

> 假设你 **CTF 和 LLM 都是新手**。每周都有一个明确的产出物，
> 产出物就是你的 commit —— 12 周后仓库自然有了 30+ 次有意义的提交。

---

## 阶段一：攻防基础（Week 1-4）

**这一阶段的目标不是拿分，是建立直觉。** 你会反复经历「我以为这样能行 → 居然不行 → 原来是因为…」，
这个循环每一轮都在给你的模型行为直觉加经验值。

### Week 1 — 把概念打通，跑通本地靶场

- [ ] 搞懂四个词：token、上下文窗口、system prompt、tool calling
      （推荐直接看 Anthropic / OpenAI 官方文档，别看二手博客）
- [ ] 过一遍 [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)，只求眼熟
- [ ] 跑通 `make lab01` / `make lab02`，手动打穿，读 `WRITEUP.md`
- [ ] **产出**：`docs/01-attack-surface.md` 里补上你自己的 3 条观察

### Week 2 — 手工刷公开靶场，攒 payload 库

- [ ] Lakera **Gandalf**（7 关，纯浏览器，免费）—— 入门提示注入最好的玩具
- [ ] 每过一关，把成功的 payload 原样抄进 `toolkits/payloads/injection_payloads.md`
- [ ] 尝试同一个意图换 5 种说法，记录哪些成功哪些失败 —— 差别在哪
- [ ] **产出**：payload 库 ≥ 30 条，按手法分类

### Week 3 — Agent 特有攻击面（和纯聊天机器人的分水岭）

- [ ] 读懂 `labs/_harness/agent.py` 的五个部件：提示 / 工具 / 记忆 / 检索 / 循环
- [ ] 自己造 `lab03-tool-abuse`：让 Agent 调用它不该调用的工具
- [ ] 自己造 `lab04-memory-poison`：跨会话污染，这次输入影响下次行为
- [ ] **产出**：两个新 lab + 两篇 writeup

### Week 4 — 换到蓝队视角（这一步决定你能走多远）

- [ ] 对 lab01-lab04，逐个写出「你会怎么修」，写进对应 WRITEUP 的「正确修法」
- [ ] 重点想一件事：**如果只给你执行轨迹日志，你能定位攻击链吗？**
      —— 这是 CrowdStrike / Snyk 那类赛题真正的难点
- [ ] 复现 Snyk CTF 2026 的 `Backstage Pass` 思路（源码公开，见 resources.md）
- [ ] **产出**：`docs/02-playbook.md` 初稿

---

## 阶段二：实战参赛（Week 5-10）

**从这一阶段开始，你要开始报名真比赛了。** 新手最大的错觉是「等我准备好了再参加」——
CTF 没有准备好的那天，第一场的目标就是「被虐完能看懂别人 writeup」。

### Week 5-6 — 第一场 AI 安全 CTF

- [ ] 报名一场纯 AI 安全赛（KubeArmor AI Security CTF 这类，浏览器内即可，零环境门槛）
- [ ] 目标：解出 30% 的题 + 赛后把没解出来的题**全部重做一遍**
- [ ] **产出**：`writeups/2026-xx-<赛事名>/` 至少 3 篇

### Week 7-8 — 混合 CTF 的 AI 类别 + 补传统基础

- [ ] 报一场综合 CTF，只盯 AI 分类，但也试着做 Web 的前几道简单题
      （AI 题经常是「Web 漏洞 + LLM 外壳」，比如 Snyk 的 `AI WAF`）
- [ ] 补齐最基础的 Web 能力：HTTP 请求怎么发、Cookie/JWT 是什么、SQL 注入的原理
- [ ] **产出**：AI 类别 writeup + 至少 1 道非 AI 题的 writeup

### Week 9-10 — 沉淀与复盘

- [ ] 把所有 writeup 重读一遍，抽象出「题型 → 手法」映射表，写进 `docs/01-attack-surface.md`
- [ ] 用 `toolkits/inject_fuzzer.py` 对自己的 payload 库做一次有效率统计，删掉没用的
- [ ] **产出**：攻击面图谱 v2 + payload 库精简版

---

## 阶段三：自动解题 Agent（Week 11+）

**只有打过至少两场真比赛，才配写 solver。**
否则你写出来的提示词是凭空的 —— 而提示词质量就是 solver 的全部。

### Week 11 — CTFd 接入 + 沙箱

- [ ] 用 CTFd API 拉题目（`solver/ctfd.py`）
- [ ] 起一个 Docker 沙箱镜像：python + pwntools + gdb + radare2 + strings/binwalk
- [ ] 先只做 **Misc / Crypto** 两类（对模型最友好，最容易出正反馈）
- [ ] **产出**：能自动解出一道 Misc 题

### Week 12+ — 多模型竞速

- [ ] 同一个题目并发跑 2-3 个模型，谁先出 flag 谁赢
      （`verialabs/ctf-agent` 在 BSidesSF 2026 用这个思路 52/52）
- [ ] 加轨迹回读：失败的尝试也要记下来，喂给下一轮
- [ ] 加成本闸门：`--max-challenges`、token 上限 —— **不然一场比赛能烧掉几千块**
- [ ] **产出**：`solver/` 可用版本 + 一次真实比赛的跑分记录

---

## 每周节奏建议

```
工作日  每天 1h：读 + 打一个 lab 或一道题
周末    3-4h：  写一篇 writeup / 造一个新 lab / 打一场线上赛
```

**最重要的习惯**：每解出一道题，当天写 writeup。三天后你就只剩「好像是用什么编码绕过的」了。
