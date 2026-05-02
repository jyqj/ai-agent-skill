# Architecture Decision Records

> **Evidence Status** — synthesized. Agent 架构中的范式、权限、工具、记忆、验证和成本策略存在强 tradeoff；ADR 用于记录“为什么这样设计”，避免设计决策只留在口头或 prompt 中。

## 什么时候写 ADR

当决策会改变 Agent 的行为边界、风险、成本或可验证性时，应写 ADR：

- 选择 ReAct、Plan-and-Execute、ORDA-VU 或多 Agent 拓扑；
- 引入新工具、MCP server、外部写动作或高风险权限；
- 改变记忆写入、上下文压缩、prompt contract 或 policy；
- 改变 effect verification、rollback、approval、eval gate；
- 上线到生产、多租户、持续运行或允许自治行动。

## ADR 格式

使用 `adr-template.md`。每条 ADR 至少包含：上下文、决策、备选方案、后果、验证方式和失效触发器。

## ADR 不是什么

ADR 不是发布说明，不表达 skill 自身的版本状态。它只记录架构选择和选择背后的证据。

## 示例

- `adr-effect-ledger-first-class.md` — 将 Effect Ledger 作为一等运行时对象。
