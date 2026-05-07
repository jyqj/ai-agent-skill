# Cancellation Tokens

> **所属域**：6. Coordination — 并发、超时与取消
>
> **Evidence Status** — synthesized. Temporal context.Done()、LangGraph Interrupt、Akka Supervision Stop、Swift CancellationToken proposal 等机制有各自生产实现，但 AI Agent 领域尚无统一的 CancellationToken 抽象。

**Principle Refs**: BDI-03 — 意图跨故障持续存在且可修正；取消不是"杀死"，而是"协商停止"

## 1. 问题陈述

Agent 系统的取消比传统微服务更复杂：一次取消可能中断 LLM 推理、工具执行、外部写入、子 Agent 协作等多种异构操作。没有统一的取消抽象，系统会出现三种典型故障：

- **Lost Cancellation**：用户已取消，但后台工具继续写外部系统。
- **Orphan Worker**：父任务取消后子 Worker 无感知，继续消耗 token 预算。
- **Zombie Effect**：取消信号到达时外部写入已部分完成，既没有完成也没有回滚。

## 2. 协作式取消模型

Agent 系统的取消必须是协作式（Cooperative）的——不能强制 kill 正在与外部世界交互的操作。

```text
CancellationToken 生命周期：

  Created(reason)
    → Propagated(parent → children)
      → Checked(每个执行点轮询 token.isCancelled)
        → Handled(根据当前状态选择策略)
          → Acknowledged(向上报告取消完成)
```

### 2.1 每层检查，每层决策

| 执行层 | 检查时机 | 取消行为 |
|---|---|---|
| Orchestrator | 收到取消信号 | 标记 token，停止分派新任务 |
| Worker | 每步开始前 | 若 token 已取消，跳过剩余步骤 |
| Tool Call（无副作用） | 调用前 | 立即放弃 |
| Tool Call（有副作用） | 调用中 | 完成当前原子操作后停止 |
| Tool Call（已产生 effect） | 调用后 | 进入补偿逻辑 |
| LLM 推理 | streaming 每 chunk | 停止接收，丢弃不完整输出 |

### 2.2 父取消 → 子级联

取消信号的传播方向是单向的：从父到子，从 Orchestrator 到 Worker 到 Tool。

```yaml
cancellation_token:
  token_id: string
  parent_token_id: string | null
  reason: user_cancel | policy_block | budget_exhausted | timeout | parent_failed
  created_at: timestamp
  propagation: parent_to_child     # 默认
  children: [token_id]
  status: active | cancelled | acknowledged
```

**级联规则**：
- 父 token 取消时，所有子 token 自动标记为 cancelled。
- 子 token 不能取消父 token（单向传播）。
- 子 token 可以独立取消（如单个工具超时），不影响兄弟 token。

## 3. 现有系统的取消机制

不同运行时框架对取消的支持差异显著：

| 框架 | 取消机制 | 传播方式 | 补偿支持 | 持久化 |
|---|---|---|---|---|
| **Temporal** | `context.Done()` + gRPC deadline | 自动级联到 Activity | Saga 补偿 | Workflow history 持久化 |
| **LangGraph** | `interrupt()` + 状态持久化 | 手动检查 | 从 checkpoint 恢复 | Checkpointer 持久化 |
| **Akka** | Supervisor `Stop` 消息 | Actor 层级自动传播 | 自定义 `postStop` 钩子 | 需配合 Persistence |
| **CrewAI** | 无原生支持 | 无 | 无 | 无 |
| **AutoGen** | 基本 `terminate` 消息 | 手动传播 | 无 | 无 |

### 3.1 Temporal：gRPC Deadline 传播

Temporal 通过 gRPC context 传播 deadline，每个 Activity 检查 `ctx.Done()` channel：

```text
Workflow(deadline=120s)
  → Activity_A(timeout=30s)  // 自动继承剩余 deadline
  → Activity_B(timeout=30s)  // 剩余 = 120 - Activity_A耗时
  → ...
```

**优势**：deadline 预算自动递减，子 Activity 不可能超过父 Workflow 的总时间。

### 3.2 LangGraph：Interrupt + Persist + Pause

LangGraph 的 `interrupt()` 不是取消，而是暂停——将当前状态持久化到 Checkpointer，等待外部信号决定是继续还是终止。

```text
Node_A → interrupt() → [状态持久化]
                         ↓
                    外部决策：resume | cancel
                         ↓
               resume: 从 checkpoint 恢复
               cancel: 丢弃或补偿
```

**限制**：需要开发者在每个可中断点手动插入 `interrupt()`，遗漏即不可取消。

### 3.3 Akka：Supervisor Stop

Akka 的取消基于 Actor 层级——Stop 消息沿监督树向下传播：

```text
Supervisor.stop(child)
  → child.preRestart() / postStop()
    → child 的所有子 Actor 递归 stop
```

**优势**：层级传播是自动的。**限制**：`postStop` 中的补偿逻辑不保证执行（进程崩溃时丢失）。

## 4. 结构化取消：带原因的取消

不同取消原因需要不同的处理策略。"取消"不是一个布尔值，而是一个带语义的信号。

| 取消原因 | 处理策略 | 部分结果 |
|---|---|---|
| `user_cancel` | 停止新动作，补偿已执行 effect，交付已完成部分 | 保留并标记 `partial: true` |
| `policy_block` | 停止危险分支，保留安全分支继续执行 | 安全部分正常交付 |
| `budget_exhausted` | 停止高成本步骤，触发 budget_choice 交互 | 交付已完成部分 + 预算报告 |
| `timeout` | 停止超时分支，尝试降级或缩小范围 | 降级结果或部分结果 |
| `parent_failed` | 子任务无条件停止，执行补偿 | 丢弃（父任务已失败） |
| `stale_world_state` | 暂停写动作，先 refresh 再决定 | 暂存，等 refresh 后决定 |

## 5. 优雅关停协议

生产环境中 Agent 服务的关停不是"收到 SIGTERM 立即退出"，而是一个多阶段协议。

```text
阶段 1: 信号捕获
  ├─ SIGTERM / SIGINT → 设置 shutting_down = true
  └─ 停止接受新任务

阶段 2: 排空（Drain）
  ├─ 等待正在执行的任务完成或到达安全点
  ├─ 每个任务检查 cancellation token
  └─ 有副作用的操作完成当前原子步骤

阶段 3: 超时强制
  ├─ drain_timeout（默认 30s）到期
  ├─ 仍未完成的任务强制取消
  └─ 未完成的 effect 记录到 compensation log

阶段 4: 就绪探针
  ├─ readiness probe 返回 not-ready
  └─ 负载均衡器停止路由新流量

阶段 5: 资源释放
  ├─ 关闭数据库连接、清理临时文件
  └─ 最终 flush trace 和 metrics
```

### 5.1 K8s PodDisruptionBudget 对齐

当 Agent 部署在 Kubernetes 上时，取消协议需要与 PodDisruptionBudget（PDB）对齐：

| K8s 概念 | Agent 映射 |
|---|---|
| `terminationGracePeriodSeconds` | drain_timeout，通常设为最长工具调用超时的 2 倍 |
| `preStop` hook | 触发 cancellation token 传播 |
| PodDisruptionBudget `minAvailable` | 确保滚动更新时至少 N 个 Agent 副本可用 |
| Readiness probe | Agent 是否能接受新任务 |
| Liveness probe | Agent 进程是否存活（非死锁） |

## 6. 当前差距与设计方向

AI Agent 领域目前没有统一的 CancellationToken 标准。以下是差距和可能的演进方向：

| 差距 | 当前状态 | 演进方向 |
|---|---|---|
| 跨框架统一接口 | 每个框架自定义取消语义 | 类似 OpenTelemetry Context 的跨框架传播协议 |
| 取消原因语义 | 多数框架只有布尔取消 | 结构化取消原因 + 按原因路由处理 |
| 跨 session 取消 | LangGraph 可持久化，Temporal 可持久化，其余丢失 | 取消状态持久化为一等对象 |
| 补偿自动化 | 需手动编写补偿逻辑 | 从 effect ledger 自动推导补偿步骤 |
| 取消可观测性 | 取消事件通常不在 trace 中 | 取消作为 span event，包含原因和影响范围 |

## 7. 评审清单

```text
[ ] 每个可取消操作是否检查 cancellation token？
[ ] 取消是否区分原因，不同原因是否有不同处理？
[ ] 父取消是否级联到所有子任务？
[ ] 有副作用的操作在取消时是否完成当前原子步骤？
[ ] 已产生的 effect 在取消时是否有补偿路径？
[ ] 服务关停是否有 drain 阶段而非立即退出？
[ ] 取消事件是否记录到 trace 中？
```

## 交叉引用

| 关联文件 | 关系 |
|---|---|
| [Concurrency Plane overview](./overview.md) | 父文件，定义取消语义框架 |
| [Recovery Plane overview](../recovery/overview.md) | 取消后的补偿和恢复逻辑 |
| [Compensation Patterns](../recovery/compensation-patterns.md) | 取消触发的 Saga 补偿 |
| [Async Patterns](../orchestration/async-patterns.md) | Cancellation Propagation 模式 |
| [Checkpoint Hydration](../../../design-space/patterns/checkpoint-hydration.md) | 取消后从 checkpoint 恢复 |
| [Long Horizon Runtime](../../../design-space/frontier/long-horizon-runtime.md) | 跨 session 取消的前沿问题 |
