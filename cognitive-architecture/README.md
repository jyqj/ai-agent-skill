# Cognitive Architecture

> **Evidence Status** — mixed. 部分来自经典 AI 认知科学（ACT-R、Soar、Global Workspace Theory），部分是向 LLM Agent 工程实践的映射推导，尚未全面实证。

## 定位

知识树中的层级关系：

```text
concepts/                → Agent 是什么，认识论基础
paradigms/               → 推理/记忆/工具/协作/控制范式
cognitive-architecture/  → [本层] 认知架构：工作记忆动力学、目标层级、推理模式、心智理论
categories/              → 品类架构（Coding / Research / Browser ...）
architecture/            → 运行时 plane 的工程实现
```

`paradigms/` 告诉你"用 ReAct 还是 Plan-Execute"，但不解释为什么推理需要区分演绎和类比、目标冲突时谁优先、何时该反思何时该行动。这些问题属于认知架构层。

认知架构层回答的核心问题是 **"Agent 的认知应该如何组织"**，而不是"运行时模块怎么实现"。它连接经典 AI 认知科学和现代 LLM Agent 工程实现：

- 从认知科学中提取对 Agent 设计有指导意义的模型和约束
- 将这些模型映射到 `architecture/planes/` 中的运行时模块
- 为范式选择和模块设计提供更底层的理论依据

## 子文件导航

| 问题 | 文件 |
|---|---|
| 上下文窗口不是简单缓冲——工作记忆应如何管理？ | `working-memory-dynamics.md` |
| 目标冲突时谁优先？终极目标和即时目标如何协调？ | `goal-hierarchy.md` |
| Agent 在做什么类型的推理？不只是"什么时候调工具" | `reasoning-modes.md` |
| 与人和 Agent 协作时，如何建模对方的信念和意图？ | `theory-of-mind.md` |
| Skill Memory 和 Knowledge Memory 为什么要区分？ | `procedural-vs-declarative.md` |
| Agent 的注意力如何在大量信息中分配权重？ | `attention-and-salience.md` |
| Agent 如何从新手到专家？技能发展路径如何映射？ | `skill-acquisition.md` |
| Agent 何时该反思、何时该行动？ | `metacognitive-control.md` |

## 阅读建议

- 如果你关心上下文管理策略，先读 `working-memory-dynamics.md`。
- 如果你在设计多步骤任务的目标分解，先读 `goal-hierarchy.md`。
- 如果你在选择 prompt 策略，先读 `reasoning-modes.md`，然后回到 `paradigms/reasoning-paradigms.md` 对照。
- 如果你在做多 Agent 编排或用户交互设计，先读 `theory-of-mind.md`。
- 如果你在设计 Memory 或 Learning 子系统，先读 `procedural-vs-declarative.md`。
- 如果你在优化上下文组装或处理信息过载问题，先读 `attention-and-salience.md`。
- 如果你在设计技能固化、学习演进或 Prompt 动态调整策略，先读 `skill-acquisition.md`。
- 如果你在处理 Agent 卡住、漫游、无限自省等问题，先读 `metacognitive-control.md`。

## 与其他层的关系

| 方向 | 说明 |
|---|---|
| 向下依赖 concepts/ | 本层假设读者已理解 Agent 定义、认识论基础和术语表 |
| 向上支撑 paradigms/ | 为范式选择提供认知层面的解释和约束 |
| 向上支撑 architecture/ | 为运行时模块设计提供认知模型映射 |
| 平级参考 categories/ | 不同品类 Agent 侧重不同的认知能力组合 |
