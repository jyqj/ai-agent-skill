# Compensation Patterns

> **所属域**：7. Lifecycle & Economics — 错误恢复与补偿
>
> **Evidence Status** — grounded. Temporal Saga 补偿有大规模生产验证；Dagster asset-level retry 和 Dapr compensation workflow 有生产实现；LangGraph Checkpointer 和 Replit Snapshot Engine 有原型或生产级状态持久化验证。

**Principle Refs**: BDI-03 — 意图跨故障持续存在且可修正；MC-02 — 自监控检测失败并触发恢复

## 1. 问题陈述

Agent 执行的多步操作经常涉及外部副作用（写文件、调 API、发消息、修改数据库）。当中间步骤失败时，已经完成的步骤不会自动消失。如果不主动补偿（Compensate），系统会停留在不一致状态：一半的文件被修改、一半的 API 调用已发出、用户看到部分完成的结果。

补偿模式的核心思想：为每个有副作用的步骤预先定义"撤销操作"，失败时按反序执行这些撤销操作，将系统恢复到可接受状态。

## 2. Saga 补偿模式

Saga 是分布式事务的替代方案，用一系列本地事务 + 对应的补偿事务取代跨服务的两阶段提交（2PC）。

### 2.1 核心机制

```text
正向执行：
  Step_1(创建分支) → Step_2(修改文件 A) → Step_3(修改文件 B) → Step_4(提交)

Step_3 失败时的补偿：
  Compensate_2(恢复文件 A) → Compensate_1(删除分支)

规则：补偿按正向执行的反序执行。
```

### 2.2 Saga Schema

```yaml
saga:
  saga_id: string
  workflow_id: string
  steps:
    - step_name: string
      action: object                  # 正向操作
      compensation: object            # 补偿操作
      status: pending | completed | failed | compensated
      idempotency_key: string         # 幂等键
      completed_at: timestamp | null
      compensation_result: object | null
  compensation_order: reverse         # 反向补偿
  compensation_status: not_started | in_progress | completed | partial | failed
```

### 2.3 补偿的语义不是"回滚"

补偿（Compensation）和回滚（Rollback）是不同的概念：

| 维度 | 回滚（Rollback） | 补偿（Compensation） |
|---|---|---|
| 语义 | 撤销操作，恢复到原始状态 | 执行反向操作，到达可接受状态 |
| 原始状态 | 完全恢复 | 不一定完全恢复（如已发邮件无法撤回） |
| 时间敏感 | 通常在事务内立即回滚 | 可以延迟执行 |
| 可见性 | 对外部不可见（事务隔离） | 对外部可见（先做了再撤） |

**Agent 场景示例**：Agent 向用户发送了一条消息后发现信息有误。无法"回滚"这条消息（用户已经看到），只能补偿（发送更正消息）。

## 3. 幂等性保证

补偿操作可能执行多次（网络重试、进程重启后重新执行），必须保证幂等：执行一次和执行多次的效果相同。

### 3.1 幂等键设计

```yaml
idempotency_key: "{workflow_id}:{step_name}:{attempt}"
```

| 组成部分 | 作用 |
|---|---|
| `workflow_id` | 标识本次工作流实例 |
| `step_name` | 标识具体步骤 |
| `attempt` | 区分重试次数（补偿的 attempt 独立编号） |

### 3.2 幂等性实现策略

| 策略 | 适用场景 | 实现 |
|---|---|---|
| **数据库唯一键** | 写入操作 | INSERT ... ON CONFLICT DO NOTHING |
| **状态检查** | 外部 API 调用 | 先查询当前状态，已达目标则跳过 |
| **操作日志** | 复杂多步操作 | 记录已执行操作，跳过已完成步骤 |
| **版本号** | 乐观并发控制 | 带版本号更新，版本不匹配则跳过 |

## 4. 检查点粒度

不同框架提供不同粒度的检查点，决定了补偿的精度和恢复的起点。

| 粒度 | 框架 | 说明 | 优势 | 劣势 |
|---|---|---|---|---|
| **节点级** | LangGraph | 每个 Graph 节点执行后自动保存 | 粒度细，恢复精确 | 存储开销大 |
| **Activity 级** | Temporal | 每个 Activity 完成后记录到 Event History | 与确定性重放配合 | 长 Activity 内无中间检查点 |
| **显式提交** | Dagster | 开发者手动标记检查点 | 开发者控制精度 | 遗漏检查点导致重做 |
| **事务级** | 数据库事务 | 事务提交即检查点 | 强一致性 | 跨服务事务不适用 |
| **快照级** | Replit Snapshot Engine | 文件系统级别的完整快照 | 无需感知应用逻辑 | 快照体积大 |

### 4.1 LangGraph Checkpointer

LangGraph 在每个节点执行后，通过 Checkpointer 保存完整的 Graph State。

```text
Node_A 执行
  → Checkpointer.save(state_after_A)
Node_B 执行
  → Checkpointer.save(state_after_B)
Node_C 失败
  → 恢复：Checkpointer.load(state_after_B) → 从 Node_C 重试

支持的 Checkpointer 后端：
  - MemorySaver（内存，测试用）
  - SqliteSaver（单机持久化）
  - PostgresSaver（生产持久化）
```

### 4.2 Temporal Activity 级检查点

Temporal 的检查点粒度是 Activity：每个 Activity 完成后，结果记录到 Event History。Workflow 重放时跳过已完成的 Activity。

```text
Workflow 执行：
  Activity_A → [记录结果] → Activity_B → [记录结果] → Activity_C

进程崩溃后重放：
  Activity_A → [读取记录，跳过] → Activity_B → [读取记录，跳过] → Activity_C → [重新执行]
```

**Activity Heartbeat**：长时间运行的 Activity 可以定期发送 heartbeat 携带进度信息，崩溃后从最后的 heartbeat 恢复，而非从 Activity 起点重做。

### 4.3 Replit Snapshot Engine

Replit 的 Snapshot Engine 采用 copy-on-write 实现常数时间的文件系统快照：

| 特性 | 数值 |
|---|---|
| 快照创建时间 | O(1)，常数时间（copy-on-write） |
| 快照恢复时间 | O(1)，常数时间（指针切换） |
| 存储开销 | 仅存储变化的块（增量） |
| 并发安全 | 快照不影响正在运行的操作 |

**Agent 应用场景**：在执行高风险操作（如大规模文件修改）前创建快照，失败时一键恢复。相比应用层的补偿逻辑，文件系统级快照更简单、更可靠，但只适用于本地文件状态。

## 5. 状态持久化后端选择

不同的持久化后端适用于不同的 Agent 场景：

| 后端 | 延迟 | 持久性 | 适用场景 | 限制 |
|---|---|---|---|---|
| **MemorySaver** | <1ms | 进程内 | 开发测试 | 进程退出即丢失 |
| **SQLite** | 1-5ms | 单机磁盘 | 单机 Agent、CLI 工具 | 不支持多副本共享 |
| **PostgreSQL** | 5-20ms | 持久化 + 复制 | 生产多副本 Agent 服务 | 运维复杂度 |
| **Redis** | 1-3ms | 内存 + AOF | 高频读写、跨副本共享 | 内存受限，大状态不适用 |
| **S3 / Object Storage** | 50-200ms | 高持久性 | 大体积快照、归档 | 延迟高，不适合实时 |

### 5.1 选择启发式

```text
开发测试 → MemorySaver
单机 CLI Agent → SQLite
单机 + 需要快照 → SQLite + S3（快照归档）
多副本服务 → PostgreSQL（主状态）+ Redis（熔断器状态）
大体积快照归档 → S3
```

## 6. 补偿的边界情况

### 6.1 补偿本身失败

```text
Step_1 完成 → Step_2 完成 → Step_3 失败
  → Compensate_2 失败
    → 记录补偿失败，标记为 partial_compensation
    → 升级给人工：说明哪些步骤已补偿、哪些未补偿
```

### 6.2 补偿窗口过期

某些外部系统有操作窗口，例如 API 创建的资源 30 分钟后不可删除。补偿必须在窗口内执行。

```yaml
compensation_window:
  step_name: "create_cloud_resource"
  window_seconds: 1800                # 30 分钟内可删除
  fallback_if_expired: escalate       # 窗口过期后升级给人工
```

### 6.3 并发补偿冲突

多个 Agent 同时对同一资源执行补偿操作时，需要协调。

| 冲突场景 | 解决方案 |
|---|---|
| 两个 Agent 同时回滚同一文件 | 分布式锁 + 先到先得 |
| 补偿操作和正向操作并发 | 正向操作检查 saga 状态，saga 进入补偿则拒绝新操作 |
| 补偿顺序依赖 | 严格按 saga 反序执行，不并行补偿 |

## 7. 评审清单

```text
[ ] 每个有副作用的步骤是否定义了补偿操作？
[ ] 补偿操作是否幂等？
[ ] 补偿是否按正向执行的反序执行？
[ ] 检查点粒度是否匹配恢复精度需求？
[ ] 补偿失败时是否有升级路径？
[ ] 是否考虑了补偿窗口过期？
[ ] 持久化后端是否匹配场景需求？
[ ] 补偿事件是否记录到审计日志？
```

## 交叉引用

| 关联文件 | 关系 |
|---|---|
| [Recovery Plane overview](./overview.md) | 父文件，FailureRecord 和 compensation_refs |
| [Recovery Decision Tree](./recovery-decision-tree.md) | 何时触发补偿的决策逻辑 |
| [Cancellation Tokens](../concurrency/cancellation-tokens.md) | 取消触发的补偿流程 |
| [Event Ordering](../concurrency/event-ordering.md) | 补偿事件在事件流中的排序 |
| [Effects Plane overview](../effects/overview.md) | Effect 记录和 readback 验证 |
| [Checkpoint Hydration](../../../design-space/patterns/checkpoint-hydration.md) | 检查点保存和恢复机制 |
| [Effect Ledger pattern](../../../design-space/patterns/effect-ledger.md) | Effect 记录驱动补偿推导 |
| [State Plane overview](../state/overview.md) | 状态持久化后端选择 |
