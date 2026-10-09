# solver — 自动解题 Agent（阶段三，Week 11+）

> ⚠️ **先别急着写这里的代码。**
> 打过至少两场真比赛再来。solver 的全部实力来自提示词质量，
> 而好的提示词来自「你知道模型会在哪里卡住」——这只能靠做题积累。

---

## 目标架构

```
                    ┌──────────────┐
                    │   CTFd API   │  每 5s 轮询新题
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │ Coordinator  │  读轨迹 → 定优先级 → 派题 → 交 flag
                    └──────┬───────┘
           ┌───────────────┼───────────────┐
      ┌────▼───┐      ┌────▼───┐      ┌────▼───┐
      │Solver A│      │Solver B│      │Solver C│   多模型竞速，先出 flag 者胜
      │(模型1) │      │(模型2) │      │(模型3) │
      └────┬───┘      └────┬───┘      └────┬───┘
           └───────────────┼───────────────┘
                    ┌──────▼───────┐
                    │ Docker 沙箱   │  pwntools / gdb / radare2 / sage / strings
                    └──────────────┘
```

这个架构不是我原创的 —— `verialabs/ctf-agent` 用它拿下了 BSidesSF 2026 的 52/52。
**但直接 clone 它你学不到什么**，因为关键不在架构，在于：

1. 每个 solver 的**系统提示**怎么写（来自你做的几十道题）
2. 沙箱里**预装哪些工具**（来自你知道每类题需要什么）
3. Coordinator **怎么判断该放弃**（来自你被卡死过的经验）

这三样都只能从阶段一、二里长出来。

---

## 里程碑

- [ ] **M1** `ctfd.py`：拉题目列表、下载附件、提交 flag、查分数
- [ ] **M2** `sandbox/`：Docker 镜像（python + pwntools + gdb + radare2 + binwalk + strings）
- [ ] **M3** 单模型 solver，只做 Misc + Crypto，先跑通闭环
- [ ] **M4** 加 Web（requests + 浏览器自动化）
- [ ] **M5** 加 Pwn/Rev（沙箱里跑 gdb + pwntools 迭代）
- [ ] **M6** 多模型竞速 + 轨迹共享（一个 solver 的发现广播给其他 solver）
- [ ] **M7** 成本闸门：`--max-challenges`、token 上限、超时熔断

---

## 三条硬规则

### 1. 先确认比赛允许

不少 CTF 明确禁止 AI 辅助或禁止自动化。**违规会让整个队伍被取消成绩。**
开赛前一定读规则；不确定就发邮件问主办方。

### 2. 成本闸门必须做在前面

多模型并发 = 多份钱在烧。一场中型比赛跑满并发，几千块是很正常的。
第一版就要有：

```
--max-challenges N        最多同时攻 N 道题
--max-parallel M          最多 M 个 solver 并发
--token-budget X          总 token 预算，超了就停
--per-challenge-timeout   单题超时熔断
```

### 3. 沙箱不是万能的

Docker 隔离了大部分执行环境，但**不要把真实密钥、个人文件、生产网络暴露给题目**。
跑 solver 用一次性虚拟机或专用 VPS。

---

## 与阶段一/二的关系

这个目录里最值钱的东西不在代码，而在**从 writeup 里编译出来的提示词**：

```
writeups/2026-xx-snyk/ai-waf.md  →  solver/prompts/web.md   「遇到 WAF 先试 X，别试 Y」
writeups/2026-xx-xxx/misc.md     →  solver/prompts/misc.md  「附件先跑 strings/binwalk」
labs/lab05/WRITEUP.md            →  solver/prompts/agent.md 「工具描述里常藏注入」
```

**这是「先攻防后解题」这个顺序真正的 payoff：**
你打的每道题，最后都会变成 solver 的一条提示词。
