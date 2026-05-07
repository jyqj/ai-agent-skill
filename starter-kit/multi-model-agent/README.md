# Multi-Model Agent Starter Kit

> **Evidence Status** — synthesized. 概念骨架，不可直接运行。

## 定位

本骨架展示多模型 Agent 架构的核心对象和模式：

- **ModelRouter** — 按任务复杂度选择模型（Adaptive Reasoning Router 模式）
- **Planner / Executor 分离** — 推理模型做规划，轻量模型做执行
- **Budget 约束** — 成本超限时自动降级到更便宜的模型

这些是**概念映射**，不是可运行的框架。想构建多模型 Agent，请走 `guides/` 的端到端指南。

## 文件结构

| 文件 | 内容 |
|------|------|
| `models.py` | 数据模型：ModelProfile、ModelRole、RoutingDecision、TaskComplexity |
| `router.py` | ModelRouter — 复杂度评估 + 模型选择 + Budget 降级 |
| `planner_executor.py` | Planner-Executor 分离骨架 + plan-then-execute 循环 |
| `main.py` | 示例入口，演示 Router 和 Planner-Executor 的使用 |

## 知识库映射

| 本骨架概念 | 知识库文件 | 关系 |
|-----------|-----------|------|
| ModelRouter / RoutingDecision | `paradigms/reasoning-model-integration.md` § RouteLLM 与模型路由实践 | 路由策略和成本数据 |
| Planner / Executor 分离 | `paradigms/reasoning-model-integration.md` § 模式 2 | Planner-Executor with Budget Awareness |
| ModelRole 四角色 | `paradigms/reasoning-model-integration.md` § 多模型 Agent 中推理模型的角色 | Planner / Executor / Critic / Router |
| TaskComplexity 三级 | `paradigms/reasoning-model-integration.md` § 设计决策树 | 简单 / 中等 / 复杂任务的路由 |
| Budget 约束与降级 | `paradigms/reasoning-model-integration.md` § 成本/质量/延迟权衡 | Budget-Aware Agent Scaling |
| 多模型架构总纲 | `architecture/multi-model/` | 角色分配、层级化推理架构 |

## 与其他 starter-kit 的关系

- `verified-tool-agent/` — 本骨架的 Executor 在生产中会复用 EffectRecord、ToolRegistry 等验证机制
- `react-llm-agent/` — Planner 生成的步骤可通过 ReAct 循环执行
- `stateful-agent/` — 多步 plan-then-execute 循环需要 Checkpoint 持久化支持
