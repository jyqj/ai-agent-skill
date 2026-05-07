# Event Ordering

> **所属域**：6. Coordination — 并发、超时与取消
>
> **Evidence Status** — grounded. CodeCRDT（arXiv 2510.18893）Y.Array 因果排序审计日志 ~50ms 中位延迟已有原型验证；Temporal Event History 和 deterministic workflow 有大规模生产验证；sakurasky 确定性重放 7 原语有系统性方案设计。

**Principle Refs**: IS-03 — 并发状态可能彼此偏离导致竞态；事件排序是竞态防护的基础设施

## 1. 问题陈述

Agent 系统中，每一步操作——LLM 推理、工具调用、记忆写入、外部 effect——都会产生事件。当多个 Agent 并发运行时，这些事件的顺序直接决定了系统状态是否一致、行为是否可重放、审计是否可信。

三种排序需求：
- **因果序（Causal Order）**：如果事件 A 导致了事件 B，A 必须排在 B 之前。
- **全序（Total Order）**：所有事件有唯一的全局顺序，冲突解析有确定结果。
- **可重放序（Replay Order）**：给定相同的事件序列和初始状态，重放必须产生相同的最终状态。

## 2. 事件溯源（Event Sourcing）

事件溯源的核心思想：不存储当前状态，存储产生当前状态的所有事件。状态是事件序列的投影。

```text
Event Log:
  [e1: task_created]
  [e2: tool_called(grep, args)]
  [e3: tool_result(grep, output)]
  [e4: llm_decision(edit file X)]
  [e5: tool_called(edit, args)]
  [e6: effect_verified(file X changed)]

Current State = fold(initial_state, [e1, e2, e3, e4, e5, e6])
```

### 2.1 Agent 系统中的优势

| 优势 | 说明 |
|---|---|
| **完美回忆** | 每个决策的输入和输出都有记录，可追溯"为什么做了这个决定" |
| **可审计** | 事件日志是不可变的审计轨迹 |
| **可重放** | 从任意检查点重放事件序列，复现问题 |
| **可分支** | 从某个事件点分叉，尝试不同决策路径（eval 场景） |
| **可压缩** | 定期创建状态快照，截断旧事件 |

### 2.2 事件 Schema

```yaml
agent_event:
  event_id: string                # 全局唯一
  sequence_number: integer        # 单 Agent 内单调递增
  causal_clock: vector_clock      # 多 Agent 因果关系
  timestamp: iso8601              # 物理时间（仅参考，不作为排序依据）
  agent_id: string
  event_type: enum                # task_created | llm_call | tool_call | tool_result | effect | decision | checkpoint | error | cancel
  payload: object
  parent_event_id: string | null  # 因果链上游
  idempotency_key: string         # 去重
```

## 3. 确定性重放

确定性重放（Deterministic Replay）要求给定相同的输入事件序列，系统必须产生完全相同的输出。这是 Agent 调试、回归测试和治理审计的基础。

### 3.1 七原语框架

基于 sakurasky 确定性重放方案，Agent 系统需要七个原语：

| 原语 | 功能 | 说明 |
|---|---|---|
| **Structured Trace** | 结构化记录每个决策点的输入输出 | 不只是日志，是可解析的事件流 |
| **Stable Metadata** | 固定随机种子、模型版本、工具版本 | 消除非确定性来源 |
| **Replay Engine** | 读取事件流，按序驱动 Agent 执行 | 替代真实时间流逝 |
| **Deterministic Stubs** | 替换外部依赖为确定性桩 | LLM 返回录制的响应、工具返回录制的结果 |
| **Agent Harness** | 封装 Agent 运行时，控制输入输出边界 | 隔离被测 Agent 和外部世界 |
| **Governance Integration** | 重放结果与策略规则比对 | 验证"如果重放，是否仍然合规" |
| **Regression Testing** | 将重放结果与基线比对 | 检测行为漂移 |

### 3.2 Temporal 的确定性模型

Temporal 将代码分为两类：

```text
确定性代码（Workflow）：
  - 决策逻辑、分支、循环、状态转移
  - 重放时从 Event History 读取结果，不重新执行
  - 禁止：随机数、当前时间、网络调用、文件 IO

非确定性代码（Activity）：
  - 工具调用、API 请求、文件操作
  - 首次执行时记录结果到 Event History
  - 重放时直接读取记录的结果
```

**关键约束**：Workflow 代码中任何非确定性操作（如 `Math.random()`、`Date.now()`）都会导致重放失败（Non-Determinism Error）。

### 3.3 Continue-As-New：事件历史压缩

长时间运行的 Agent 会积累大量事件历史，影响重放性能和存储成本。Temporal 的 Continue-As-New 机制解决这个问题：

```text
Workflow 运行中：
  Event History: [e1, e2, ..., e10000]  ← 历史过长

Continue-As-New：
  1. 创建当前状态的快照
  2. 启动新的 Workflow Execution，传入快照
  3. 旧 Execution 的 Event History 归档
  4. 新 Execution 从 [e1: snapshot_loaded] 开始

效果：
  - 活跃 Event History 保持短小
  - 历史数据可查询但不参与重放
  - 类似数据库的 WAL checkpoint
```

**Agent 系统建议**：当事件数超过阈值（如 1000 事件或 100MB）时触发 Continue-As-New，或在每个主要子任务完成后触发。

## 4. CodeCRDT：多 Agent 因果排序

CodeCRDT（arXiv 2510.18893）将 CRDT 应用于代码协作编辑，其中 Y.Array 的因果排序机制可直接应用于 Agent 审计日志。

### 4.1 Y.Array 因果排序

```text
Agent_A 的操作：  [op1] → [op2] → [op3]
Agent_B 的操作：  [op4] → [op5]
因果关系：        op2 依赖 op4 的结果

Y.Array 排序结果：
  [op1, op4, op2, op5, op3]
  ↑     ↑    ↑
  A先   B的op4  A依赖op4后继续
  独立   先于op2
```

### 4.2 性能数据

| 指标 | 数值 | 场景 |
|---|---|---|
| 中位延迟 | **~50ms** | 单次操作的因果排序和合并 |
| 吞吐 | 线性扩展至 20-30 Agent | 超过后合并冲突率显著上升 |
| 存储开销 | 每操作 ~200 bytes 元数据 | 包含向量时钟和因果依赖 |

### 4.3 Agent 审计日志应用

将 Y.Array 因果排序用于多 Agent 共享审计日志：

- 每个 Agent 本地追加事件，附带向量时钟。
- 合并时按因果序排列，而非物理时间序。
- 冲突事件（无因果关系的并发事件）按确定性规则排序（如 Agent ID 字典序）。
- **优势**：无需中心化排序服务，每个 Agent 可离线操作后合并。

## 5. CRDT 用于多 Agent 共享状态

CRDT（Conflict-free Replicated Data Types）在多 Agent 共享状态场景中的应用和限制：

### 5.1 TODO-Claim 协议

多 Agent 协作时的任务认领模式：

```text
共享状态（CRDT Map）：
  task_001: { status: "open",    claimed_by: null }
  task_002: { status: "claimed", claimed_by: "agent_A", claimed_at: t1 }
  task_003: { status: "done",    claimed_by: "agent_B", completed_at: t2 }

认领冲突解决：
  Agent_A 和 Agent_B 同时认领 task_004
  → CRDT Last-Writer-Wins：按 (timestamp, agent_id) 排序
  → 输家检测到认领失败，选择下一个 open 任务
```

### 5.2 扩展性限制

| Agent 数量 | 表现 | 原因 |
|---|---|---|
| 1-10 | 良好 | 冲突率低，向量时钟小 |
| 10-20 | 可接受 | 冲突偶发，合并延迟可控 |
| 20-30 | 边界 | 向量时钟膨胀，合并频率高 |
| >30 | 不推荐 | 向量时钟大小 O(n)，合并风暴 |

**超过 30 Agent 的方案**：引入分层结构——Agent 分组，组内 CRDT，组间通过 Orchestrator 协调。

## 6. 排序模型选择矩阵

| 场景 | 推荐排序模型 | 理由 |
|---|---|---|
| 单 Agent 审计日志 | 单调递增序列号 | 简单、高效、无冲突 |
| 多 Agent 共享日志 | 向量时钟 + 因果排序 | 保留因果关系，无需中心化 |
| 确定性重放 | Event Sourcing + Deterministic Stubs | 完全可重放 |
| 多 Agent 协作状态 | CRDT（< 30 Agent）或分层协调 | 无锁合并，最终一致 |
| 合规审计 | 全序（中心化排序服务） | 监管要求唯一全局序 |
| 长时 Agent 任务 | Event Sourcing + Continue-As-New | 历史压缩，重放可控 |

## 7. 评审清单

```text
[ ] 事件是否有全局唯一 ID 和因果链引用？
[ ] 多 Agent 场景是否使用向量时钟而非仅物理时间？
[ ] 确定性重放是否替换了所有非确定性依赖？
[ ] 事件历史是否有压缩/归档策略？
[ ] CRDT 共享状态的 Agent 数量是否在扩展性限制内？
[ ] 审计日志的排序是否满足合规要求？
```

## 交叉引用

| 关联文件 | 关系 |
|---|---|
| [Concurrency Plane overview](./overview.md) | 父文件，消息顺序和事件溯源基础 |
| [Backpressure](./backpressure.md) | 背压下的消息顺序保证 |
| [Cancellation Tokens](./cancellation-tokens.md) | 取消事件在事件流中的排序 |
| [State Plane overview](../state/overview.md) | 状态是事件序列的投影 |
| [Shared World Model](../orchestration/shared-world-model.md) | 多 Agent 共享状态的一致性 |
| [Observability trace-format](../observability/trace-format.md) | 事件排序与 trace span 的对齐 |
| [Effect Ledger pattern](../../../design-space/patterns/effect-ledger.md) | Effect 事件的排序和去重 |
