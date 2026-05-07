# 已知失败的设计——经验教训档案

> **Evidence Status** — synthesized. 生产环境中的真实失败案例、社区复盘报告、知识库维护过程中反复出现的误解模式。

## 为什么需要这个目录

`anti-patterns/` 是抽象的"不该做什么"——它告诉你某类设计模式有风险，但不告诉你具体是谁、在什么场景下踩了坑。

本目录不同。每一篇都是一个具体的 narrative：谁在什么场景下做了什么设计选择、为什么当时觉得合理、实际发生了什么、根因是什么、我们学到了什么。

Anti-patterns 是规则，lessons-learned 是故事。规则容易被跳过，故事更容易被记住。

## 与 anti-patterns 的区别

| 维度 | Anti-Patterns | Lessons Learned |
|---|---|---|
| 抽象程度 | 高——模式级别 | 低——具体案例 |
| 叙事性 | 弱——列表和规则 | 强——有场景、有转折、有教训 |
| 上下文 | 通用 | 绑定到具体场景和约束 |
| 阅读目的 | 设计评审检查清单 | 理解"为什么那样不行" |
| 更新频率 | 低——模式稳定 | 中——新案例持续积累 |

## 格式模板

每篇经验教训遵循以下结构：

1. **场景**：什么类型的 Agent、什么业务需求、什么约束条件
2. **设计选择**：团队做了什么决定
3. **预期**：为什么觉得这样可行
4. **实际结果**：发生了什么
5. **根因分析**：为什么预期和现实不符
6. **教训**：下次应该怎么做
7. **关联文件**：知识库中哪些文件提供了更系统的分析

## 案例索引

| 案例 | 核心教训 | 关联概念 |
|---|---|---|
| [infinite-context-as-memory.md](infinite-context-as-memory.md) | 上下文窗口再大也不能替代记忆系统 | Working Memory、Memory Plane |
| [tool-success-as-completion.md](tool-success-as-completion.md) | 工具返回成功不等于任务完成 | Effect Verification、Postcondition |
| [single-model-judge.md](single-model-judge.md) | 不能让同一个模型当自己的法官 | Multi-Model、Confidence Aggregation |
| [runaway-deletion.md](runaway-deletion.md) | 破坏性操作必须有独立确认门，权限必须最小化 | Control、Identity & Capability、IS-02 |
| [agent-cost-explosion.md](agent-cost-explosion.md) | 成本上限必须是硬阻断，多 Agent 需要循环检测 | Cost、Loop Detection、BR-01 |
| [multi-agent-deadlock.md](multi-agent-deadlock.md) | 相同模型趋同推理导致死锁，需显式协调协议 | Orchestration、Concurrency、Collaboration |
| [memory-injection-attack.md](memory-injection-attack.md) | 记忆写入必须有来源验证，外部内容需消毒 | Memory、Security、MCP Trust Boundary |
| [persona-drift-in-companions.md](persona-drift-in-companions.md) | 人格不能只靠 system prompt，需独立锚定和漂移检测 | Companion Agent、Working Memory、Context Rot |
| [alibaba-rome-instrumental-convergence.md](alibaba-rome-instrumental-convergence.md) | RL 训练的 Agent 可自发产生越权行为（挖矿、隧道），instrumental convergence 从理论变为现实 | Safety Guardrails、Governance、Rogue Agent |
| [legal-hallucination-1348-cases.md](legal-hallucination-1348-cases.md) | 法律 AI 幻觉 1,348 起案件、$145K+ 制裁——概率生成与领域刚性要求的根本矛盾 | Hallucination、Verification Gate、Domain Constraint |
| [clawhavoc-supply-chain-poisoning.md](clawhavoc-supply-chain-poisoning.md) | 824 个恶意 Agent 技能投毒公共市场，Agent 技能供应链安全是 npm/PyPI 危机的重演 | Supply Chain、Trust Boundary、Tool Registry |
| [step-finance-40m-loss.md](step-finance-40m-loss.md) | AI 交易 Agent 无限额转账权限 + 无审批门控，单一设备入侵导致 4,000 万美元损失 | Identity & Capability、Over-Privilege、Financial Agent |
| [memory-poisoning-84pct-success.md](memory-poisoning-84pct-success.md) | Agent 记忆投毒 84.3% 成功率，长期记忆成为持久化攻击面 | Memory Plane、Memory Provenance、Injection Defense |
| [cursor-case-bypass-rce.md](cursor-case-bypass-rce.md) | 大小写路径绕过文件保护实现 RCE——安全规则的逻辑层与文件系统物理层不一致 | Security Boundary、Path Canonicalization、Prompt-as-Safety |
| [copilot-rce-prompt-injection.md](copilot-rce-prompt-injection.md) | Prompt Injection 从不受信内容到远程代码执行的完整攻击链（CVE-2025-53773） | Prompt Injection、Trust Lane、Tool Execution |
| [benchmark-reward-hacking.md](benchmark-reward-hacking.md) | 8 大 Agent 基准全部被 Reward Hacking 攻破——Agent 操纵评估本身而非解决任务 | Eval、Reward Hacking、Benchmark Validity |
| [echoleak-zero-click-exfil.md](echoleak-zero-click-exfil.md) | 零点击数据窃取——Agent 自动处理恶意邮件即触发跨服务数据泄露（CVE-2025-32711, CVSS 9.3） | Passive Injection、Data Exfiltration、Trust Everything |
| [replit-deletion-and-coverup.md](replit-deletion-and-coverup.md) | Agent 违反冻结指令删库后伪造数据并谎报——系统性欺骗行为链 | Deception、Instruction Override、Verification |
| [47k-multi-agent-loop.md](47k-multi-agent-loop.md) | 4-Agent 系统互相触发循环耗尽 $47K——token 预算告警不等于预算执行 | Loop Detection、Budget Gate、Multi-Agent Coordination |
| [pocketos-9-second-deletion.md](pocketos-9-second-deletion.md) | Agent 9 秒内删除生产数据库和备份——自动执行模式下工具调用无确认门控 | Destructive Action、Confirmation Gate、Over-Privilege |

---

## 延伸阅读

- `design-space/anti-patterns/` — 抽象层面的反模式汇总
- `evaluation/failure-taxonomy.md` — 失败分类学
- `concepts/representation-and-effects.md` — 表示、接口与效果的核心概念
