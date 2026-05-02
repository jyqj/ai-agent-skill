# State & Checkpoint Engine
>
> **所属域**：2. Cognition & Continuity — 任务状态与 checkpoint
>
> **Evidence Status** — grounded. Claude Code、Augment、Codex、Generic Agent 对 state tracking、checkpoint、resume 的实现；this repository 对任务状态与外部世界状态的分层抽象。

**Principle Refs**: BDI-03, BR-02 — 意图持续但可修订，任务状态随时间可退化。

## 定义

State Engine 管理**任务当前状态**，Checkpoint Engine 管理**中断恢复**。长任务 Agent 最常见的失败就是丢失进度或恢复到错误上下文。

要特别区分：
- **Task State**：Agent 当前任务走到哪一步；
- **World State**：外部对象当前是什么状态。

State 层主要负责前者，并记录与后者相关的引用和待验证 effect。

## 为什么需要状态层

| 常见失败 | 原因 |
|---|---|
| 上下文满后忘记进度 | 没有外部化的 task state |
| 工具失败后无法恢复 | 没有 checkpoint |
| 多 Worker 不知彼此状态 | 没有共享任务状态 |
| 用户中断后无法继续 | 没有恢复机制 |
| 以旧外部状态继续执行 | world state 没刷新 |

## 模块接口

**输入**：Kernel 的状态更新、checkpoint 请求、effect status、approval status
**输出**：当前任务状态、checkpoint 数据、恢复指令
**配置**：checkpoint 频率、持久化方式、恢复策略

## 状态类型

| 状态 | 作用 | 示例 |
|---|---|---|
| Task State | 任务整体 | 目标、计划、阶段、完成度 |
| Step State | 当前步骤 | 工具调用、输入、输出、错误 |
| Artifact State | 产物 | diff、报告、文件路径 |
| Environment State | 执行环境 | git status、依赖、工作目录 |
| Approval State | 审批 | pending / approved / rejected |
| Pending Effects | 待验证动作 | ticket 已更新待回读、邮件待 outbox 确认 |

## Checkpoint 内容

```yaml
checkpoint_id: string
task_id: string
current_depth: D4
plan_snapshot: {}
completed_steps: []
open_steps: []
artifacts: []
workspace_diff: string | null
world_refs: []
pending_effects: []
resume_instruction: string
```

## 恢复流程

```text
Load checkpoint
  → Hydrate task state
  → Validate environment
  → Refresh stale world refs
  → Rebuild minimal context
  → Continue from next safe step
```

## 设计模式

| 模式 | 详见 |
|---|---|
| Checkpoint Hydration | `../../../design-space/patterns/checkpoint-hydration.md` |
| Feature List Progress | `../../../design-space/patterns/feature-list-progress.md` |
| Scratchpad Progress File | `../../../design-space/patterns/scratchpad-progress-file.md` |
| Decision Log | `../../../design-space/patterns/decision-log.md` |

## 参考实现

- **Claude Code**：Git-based state tracking，见 `projects/coding-agents/claude-code/state-ui-layer.md`
- **Augment**：Checkpoint 系统，见 `projects/coding-agents/augment/patterns.md`
- **Codex**：任务与 memory pipeline 的状态化处理，见 `projects/coding-agents/codex/memory-pipeline.snippet`
