# Multi-window Orchestration

> **Evidence Status** — grounded. 从 Claude Code 的 subagent、Augment 的 Worker 系统等多个编码 Agent 的实践中提炼，尚无统一规范。

当一个 Agent 在单个上下文窗口（Context Window）中处理长任务时，三个问题几乎必然出现：上下文膨胀导致推理质量下降、早期信息被逐渐遗忘、不相关的子任务互相污染彼此的工作记忆。Multi-window Orchestration 的核心思路是：既然单窗口撑不住，就别硬撑。

## 做法

把一个复杂任务拆成多个独立的上下文窗口（通常称为 Worker），每个窗口只负责一个子任务。一个监督窗口（Supervisor）通过结构化状态和检查点（Checkpoint）协调它们：

```text
Supervisor Window
  +-- Worker A: research
  +-- Worker B: implementation
  +-- Worker C: verification
```

这种拆分带来的直接好处是：每个 Worker 的上下文小而专注，推理质量更稳定；Worker 之间互不干扰，一个失败不会连带污染其他子任务。

## 设计要点

**独立性**：每个 Worker 拥有独立的上下文和工具权限。Worker 之间不应该通过隐式共享上下文来传递信息。共享状态应走显式通道，比如文件系统、数据库或 Checkpoint 文件。

**结构化输出**：Worker 的返回必须是结构化的（JSON、固定格式文本等），而不是自由文本。Supervisor 需要能可靠地解析 Worker 的结果来做下一步决策。

**不盲信**：Supervisor 不应该无条件信任 Worker 的输出。在关键路径上，Supervisor 应当做基本的一致性校验，或者把校验本身也分配给另一个 Worker。

这个模式与 [Worker Orchestration](./worker-orchestration.md) 和 [Subagent](./subagent.md) 高度相关，它们分别从生命周期管理和上下文隔离的角度切入同一个问题。
