# 情绪与动机——Agent 的内驱力设计

> **Evidence Status** — theoretical | **类比边界** — 启发性映射，非结构性对应

## 适用范围

任务交付型 Agent（Coding, Workflow）**不需要情绪系统**——外部 TaskEnvelope 提供了充足的驱动力。本文仅对以下品类有实际价值：Companion Agent（情感响应）、Creative Agent（内在动机）、长期自治系统（主动探索）。

## 过程奖励 vs 结果奖励

对所有品类 Agent 都有实际指导意义的核心概念：

```text
结果奖励：任务成功 +1，失败 0          — 信号稀疏，信用分配困难
过程奖励：每一步是否朝目标前进 — 信号密集，学习效率高

关键数据：3B AgentPRM 达 88.1% 准确率，超越 GPT-4o 的 76.1%（arXiv 2502.10325）
```

设计启发：对多步骤 Agent，逐轮评分优于仅在终点评分。过程奖励可用于 Agent 自监控和路径修正。

## Companion Agent 安全边界

情感响应不等于无条件镜像。Agent 不应复制用户的负面情绪，而应调整交互风格：

- 用户愤怒 -> Agent 更温和、更结构化，而非也表现愤怒
- 用户悲伤 -> Agent 提供支持性响应，而非模拟悲伤
- 情感记忆应与事实记忆分离存储，生命周期更短，需定期衰减

## Creative Agent 的内驱力缺口

当前 LLM Agent 本质是响应式的，缺乏内在动机（不会自发探索）、持续学习（不积累风格偏好）、意图性（无"想要创造"的驱动力）。要实现主动式行为，需显式设计内在动机机制。

## 交叉引用

- `goal-hierarchy.md` — 目标优先级调制
- `metacognitive-control.md` — 何时行动何时反思
- `../architecture/planes/memory/overview.md` — 记忆 plane
- `../architecture/evolution/value-drift.md` — 价值漂移
