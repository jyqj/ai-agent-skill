# Orchestration Engine
>
> **所属域**：6. Coordination — 多 Agent 协作与通信
>
> **Evidence Status** — synthesized. 通用运行时模块来自多个参考项目的统一抽象。

**Principle Refs**: BR-01, IS-03 — 多 Agent 协作需要预算在子代理间显式传播；各模型对世界的表征可能彼此偏离

单 Agent 能力有限，复杂任务需要多 Agent 协作完成。Orchestration Engine 是多 Agent 系统的调度中枢，决定谁做什么、如何合并、冲突如何仲裁。

## 定义

Orchestration Engine 管理多 Agent/Worker 协作：子代理派生、Worker 任务分配、多窗口执行、结果合并。

## 模块接口

**输入**：Kernel 的 spawn/delegate 请求
**输出**：Worker 结果（通过 Output Contract 标准化）
**配置**：branch budget、merge strategy、conflict policy

## 何时需要编排

| 场景 | 编排方式 |
|---|---|
| 独立子任务可并行 | Worker 并行 + 合并 |
| 需要独立上下文 | Subagent（隔离上下文） |
| 上下文将满 | 新窗口（multi-window） |
| 跨部门流程 | Worker 流水线 |

## Output Contract

每个 Worker 的输出必须遵守约定格式，否则合并会出问题：

```yaml
worker_output:
  worker_id: string
  task_ref: string
  status: complete | partial | failed
  artifacts: []
  conflicts: []
  decisions_made: []
```

## Merge Strategy

| 策略 | 适用 |
|---|---|
| Append | 各 Worker 输出独立，直接拼接 |
| Priority | 有明确优先级时，高优先覆盖 |
| Conflict Resolution | Worker 输出有冲突，需要解决 |
| Human Review | 冲突严重，交给人类 |

## 设计模式

| 模式 | 详见 |
|---|---|
| Subagent | `../../../design-space/patterns/subagent.md` |
| Worker Orchestration | `../../../design-space/patterns/worker-orchestration.md` |
| Multi-Window | `../../../design-space/patterns/multi-window.md` |

## 参考实现

- **Claude Code**：Fork vs Spawn 子代理模式，见 `projects/coding-agents/claude-code/orchestration-layer.md`
- **Augment**：Worker Agent 编排 + Checkpoint，见 `projects/coding-agents/augment/patterns.md`
- **Codex**：Orchestrator 调度，见 `projects/coding-agents/codex/orchestrator.md`
- **OpenCode**：编排层实现，见 `projects/coding-agents/opencode/orchestration.md`

## 协议补强

多 Agent 编排至少需要四个对象：

```text
AgentMessage        # Agent 间消息协议
OutputContract      # 子任务交付契约
SharedWorldModel    # 多 Agent 共享外部状态引用
ArbitrationDecision # 冲突仲裁结果
```

新增入口：

- `communication.md`：Agent 间通信协议。
- `shared-world-model.md`：共享世界模型和冲突记录。
- `topology.md`：star / pipeline / hierarchy / mesh / blackboard 拓扑。
- `async-patterns.md`：异步协作、租约、heartbeat、取消传播。
- `governance.md`：多 Agent 治理——责任归因、冲突仲裁、级联失败、治理拓扑。
- `trust-and-attribution.md`：Agent 间信任模型、输出可信度传播、身份联邦。
