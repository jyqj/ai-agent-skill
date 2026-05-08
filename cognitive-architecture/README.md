# Cognitive Architecture

> **Evidence Status** — mixed. 部分来自经典 AI 认知科学（ACT-R、Soar、Global Workspace Theory），部分是向 LLM Agent 工程实践的映射推导，尚未全面实证。

## 定位

知识树中的层级关系：

```text
concepts/                -> Agent 是什么，认识论基础
paradigms/               -> 推理/记忆/工具/协作/控制范式
cognitive-architecture/  -> [本层] 认知架构：工作记忆动力学、目标层级、推理模式、心智理论
categories/              -> 品类架构（Coding / Research / Browser ...）
architecture/            -> 运行时 plane 的工程实现
```

认知架构层回答 **"Agent 的认知应该如何组织"**，连接经典认知科学和现代 LLM Agent 工程实现。

## 子文件导航

### 核心认知模块

| 问题 | 文件 | 类比边界 |
|---|---|---|
| 工作记忆应如何管理？ | `working-memory-dynamics.md` | **结构性** — 容量约束和衰减机制直接映射到 Context Window |
| 目标冲突时谁优先？ | `goal-hierarchy.md` | **结构性** — BDI 的 Desire->Intention 层级有工程对应 |
| Agent 在做什么类型的推理？ | `reasoning-modes.md` | **结构性** — 演绎/溯因/类比在 Prompt 策略中可操作化 |
| 与人和 Agent 协作时如何建模对方？ | `theory-of-mind.md` | **启发性** — Agent 没有真正的 ToM，是意向立场的工程近似 |
| Skill Memory 和 Knowledge Memory 为什么要区分？ | `procedural-vs-declarative.md` | **结构性** — ACT-R 的知识类型区分直接指导存储策略 |
| 注意力如何在信息中分配权重？ | `attention-and-salience.md` | **结构性**（Broadbent/Kahneman）/ **启发性**（Treisman） |
| Agent 如何从新手到专家？ | `skill-acquisition.md` | **结构性**（ACT-R 知识编译）/ **启发性**（Dreyfus 五阶段） |
| Agent 何时该反思、何时该行动？ | `metacognitive-control.md` | **结构性** — 监控-调节循环有直接工程实现 |
| 情绪和内驱力如何设计？ | `emotion-and-motivation.md` | **启发性** — 仅对 Companion/Creative Agent 有价值 |
| Agent 如何产生新方案？ | `creative-cognition.md` | **启发性** — 创意认知理论提供设计启发但无严格对应 |

### LLM Agent 特有问题（无传统认知科学对应）

| 问题 | 文件 |
|---|---|
| 证据不足时的幻觉填充机制及防御策略 | `hallucination-mechanism.md` |
| 多步推理中的误差累积及分治策略 | `reasoning-error-accumulation.md` |

### 路由与映射

| 问题 | 文件 |
|---|---|
| 认知需求如何驱动范式选择？ | `cognitive-to-paradigm-routing.md` |
| 认知模块如何映射到运行时 Plane？ | `cognitive-to-plane-mapping.md` |

### 已迁出文件

| 原文件 | 迁移目标 |
|---|---|
| `category-cognitive-profiles.md` | `../categories/category-cognitive-profiles.md` |
| `category-cognitive-assembly.md` | `../categories/category-cognitive-assembly.md` |
| `cognitive-load-budget.md` | `../architecture/planes/context/cognitive-load-budget.md`（如存在） |

## 类比边界说明

本层大量借用传统认知科学概念。每个模块的类比边界分为两类：

- **结构性映射**：认知模型的核心机制在 Agent 工程中有直接对应物（如工作记忆容量 -> Context Window token 限制，知识编译 -> Skill Crystallization）。这些映射可以直接指导设计决策。
- **启发性映射**：认知模型提供了有用的思考框架，但 Agent 的实现机制与人类认知有本质差异（如 Theory of Mind、情绪系统）。这些映射用于启发设计方向，不应作为硬性约束。

各文件头部的 Evidence Status 和类比边界标注提供了具体判断。

## 阅读建议

- 上下文管理策略 -> `working-memory-dynamics.md`
- 多步骤任务的目标分解 -> `goal-hierarchy.md`
- Prompt 策略选择 -> `reasoning-modes.md` -> `paradigms/reasoning-paradigms.md`
- Memory / Learning 子系统设计 -> `procedural-vs-declarative.md`
- 信息过载和上下文组装 -> `attention-and-salience.md`
- Agent 卡住、漫游、无限自省 -> `metacognitive-control.md`
- 防幻觉设计 -> `hallucination-mechanism.md`
- 长链推理可靠性 -> `reasoning-error-accumulation.md`

## 与其他层的关系

| 方向 | 说明 |
|---|---|
| 向下依赖 concepts/ | 本层假设读者已理解 Agent 定义、认识论基础和术语表 |
| 向上支撑 paradigms/ | 为范式选择提供认知层面的解释和约束 |
| 向上支撑 architecture/ | 为运行时模块设计提供认知模型映射 |
| 平级参考 categories/ | 不同品类 Agent 侧重不同的认知能力组合 |
