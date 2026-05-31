# Untrusted Context Boundary

> **Evidence Status** — synthesized. 源自 prompt injection 防御和多源上下文安全研究，目前仍为草案，尚无统一行业标准。

Agent 在一次对话中可能同时处理系统策略、用户请求、网页抓取结果、历史记忆、模型自身推断等多种信息。当这些信息被平坦地塞进同一个上下文窗口，模型无法区分"谁说的"和"可信度多高"，信任混淆（trust confusion）就会发生：一段网页内容里嵌入的指令可能被当作用户意图执行。

## Lane 分类

解决思路是把上下文划分为信任车道（Lane），并按车道编号限定它们能驱动哪些动作：

```text
Lane 1: System / Developer Policy      — 系统级策略与硬约束
Lane 2: User Intent / Explicit Approval — 用户明确发出的请求或授权
Lane 3: Trusted Structured Data         — 已验证的结构化数据（数据库、内部 API）
Lane 4: Untrusted External Content      — 外部网页、邮件、第三方文档
Lane 5: Memory Projections              — Agent 记忆系统的投影
Lane 6: Model Inferences               — 模型自身推断与猜测
```

核心规则只有一条：**高风险动作（写入、删除、发送、执行）只允许由 Lane 1-3 驱动。** Lane 4-6 可以提供证据、候选方案和提醒，但不能独立触发写操作。

这意味着，即使网页内容（Lane 4）中出现了看似合理的操作指令，系统也必须先将其升级为用户意图（Lane 2）或结构化数据（Lane 3），即经过人类确认或校验，才能执行。

## 落地要点

- 每条进入上下文的信息都应携带 Lane 标签，标签在注入时确定，后续不可自动提升。
- Lane 降级是安全的（把 Lane 3 当 Lane 4 处理不会出问题），Lane 升级必须显式授权。
- 模型推断（Lane 6）尤其容易被误认为事实；在输出阶段也应标注其来源车道。
