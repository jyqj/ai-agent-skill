# Agent Product Model

> **Evidence Status** — synthesized. 核心概念归纳与跨模块一致性整理。

> **完整版**见 `../paradigms/methodology/agent-product-model.md`。本文保留核心概念供快速查阅。

## 核心公式

```text
Agent Product = User Job + World Representation + Agent Runtime + Interfaces + Verification + Operations + Evaluation
```

| 组成 | 核心问题 | 常见失败 |
|---|---|---|
| User Job | 用户雇它完成什么工作？ | 只做聊天，不完成任务 |
| World Representation | 现实输入如何被表示？是否新鲜、可信、可回查？ | OCR/摘要/检索片段被当作现实 |
| Agent Runtime | 它如何持续观察、思考、行动？ | 单轮问答伪装成 Agent |
| Interfaces | 它能读取和操作哪些外部系统？ | 只会分析，不会行动 |
| Verification | 它如何证明外部效果真的发生？ | 工具 success = 任务 success |
| Operations | 升级后如何不退步？如何回滚？ | 上线后时好时坏 |
| Evaluation | 如何知道它真的有效？ | 只看 demo，不看真实任务完成率 |

## Agent 产品画布

| 字段 | 要回答的问题 |
|---|---|
| Target User | 谁用？ |
| User Job | 完成什么工作？ |
| Entry Point | 从哪里触发？Chat / CLI / IDE / API / Event / Sensor |
| Observable Inputs | 系统能观察到哪些原始输入？ |
| Representation Contract | 原始输入如何解析、摘要、压缩、结构化？ |
| Deliverable | 最终交付物是什么？ |
| World Objects | Agent 操作的是哪些外部对象？ |
| Intended Effects | 希望外部世界发生什么改变？ |
| Autonomy Level | 自主性等级 |
| Execution Depth | 执行到哪一层？ |
| Required Tools | 必备工具 |
| World State Strategy | 如何读取、缓存、刷新外部状态？ |
| Memory Need | 是否需要跨会话记忆？ |
| Approval Points | 哪些动作必须确认？ |
| Verification | 怎么证明完成？ |
| Failure Recovery | 失败后怎么恢复？ |
| Operations | 配置追踪、回归、告警、回滚如何设计？ |
| Metrics | 用什么指标评估？ |

## 设计原则

1. 先定义交付物，再定义 Agent。
2. 先定义外部对象和效果，再定义工具。
3. 先定义表示契约，再把输入喂给模型。
4. 先定义验证和回滚，再放开高风险动作。
5. 先设计评估和上线回归，再扩大自主范围。
