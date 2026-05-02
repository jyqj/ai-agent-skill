# Design Principles

> **Evidence Status** — synthesized. 多个生产级 Agent 项目中反复出现的设计约束归纳。

Agent 架构的核心设计原则索引。这些原则从多个生产级 Agent 项目中归纳而来，用于设计评审和术语对齐。

1. **Context is a Scarce Resource** — 上下文是预算，按需加载、主动压缩、及时卸载。
2. **Agent Operates on Representations, Not Reality** — 模型处理的是表示，不是现实本身。
3. **Verify Before Claiming Done** — 完成前必须验证产出，执行深度的核心差异在于验证层。
4. **Tool Success Is Not World Success** — 调用成功不代表外部世界已达目标状态。
5. **Trust is Graduated, Not Binary** — 权限按风险、可逆性和信息可信度分级。
6. **Keep Instruction Lanes Separate from Data Lanes** — 系统约束、用户意图、外部内容必须分 lane。
7. **Fail Gracefully, Recover Explicitly** — 有明确的恢复策略，不死循环重试或静默忽略。
8. **State Must Survive Interruption** — 长任务状态必须能从中断点恢复。
9. **Harness Defines the Ceiling, Model Defines the Floor** — Harness 工程决定能力上限。
10. **Fingerprint Everything That Changes Behavior** — 影响行为的变化必须可追踪、可回归。
11. **Paradigms Are Choices, Not Defaults** — 根据任务特征选择范式，不默认某种循环。
12. **Start Minimal, Add Complexity from Evidence** — 从最小闭环开始，用真实失败驱动升级。

> 完整版本含正反例、相关链接和深入讨论，见 [design-space/principles/core-design-principles.md](../design-space/principles/core-design-principles.md)
