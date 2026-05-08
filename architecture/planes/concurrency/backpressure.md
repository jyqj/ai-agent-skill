# Backpressure

> **所属域**：6. Coordination — 并发、超时与取消
>
> **Evidence Status** — grounded. Datadog 2026 LLM Observability Report 显示生产环境中 1/3 的 LLM 调用错误源于 rate limit；Netflix Gradient2/Vegas 自适应并发控制已在微服务中大规模验证；Envoy proxy 的负载卸除策略被广泛采用。

**Principle Refs**: BR-01 — 预算约束按线程独立核算；背压是预算执行的运行时机制

## 1. 问题陈述

Agent 系统面临三层速率瓶颈：模型 API 的 rate limit、工具执行的吞吐上限、共享状态（记忆、数据库）的写入争用。任何一层过载都会引发级联失败——重试放大负载、token 预算耗尽、部分结果丢失。

**核心数据**：Datadog 2026 报告指出，生产环境中约 1/3 的 LLM 调用错误是 rate limit（429 Too Many Requests），而非模型本身的推理错误。这意味着并发控制和背压是 Agent 可靠性的首要问题，优先级高于 prompt 优化。

## 2. 背压机制层

背压不是单一机制，而是多层协同：

```text
入口控制 → 队列管理 → 并发限制 → 下游保护 → 反馈循环
```

| 层 | 机制 | 目标 |
|---|---|---|
| **入口控制** | 准入控制、优先级队列 | 过载时拒绝低优先级请求 |
| **队列管理** | 队列深度限制、队列时间 SLO | 防止请求在队列中老化 |
| **并发限制** | Token Bucket、自适应并发 | 控制同时在途请求数 |
| **下游保护** | 熔断器、隔板（Bulkhead） | 隔离故障依赖 |
| **反馈循环** | 延迟信号、错误率信号 | 动态调整并发上限 |

## 3. Token Bucket 限流

Token Bucket 是最基础的速率控制——每秒补充固定数量的 token，每次请求消耗 token，bucket 为空时拒绝或排队。

```yaml
token_bucket:
  capacity: 100           # bucket 最大容量
  refill_rate: 10/s       # 每秒补充速率
  initial_tokens: 100     # 初始 token 数
  overflow_policy: queue | reject | degrade
```

**Agent 场景适配**：
- 模型 API 调用：按 API provider 的 RPM/TPM 限制设置。
- 工具调用：按工具类别设置不同速率（文件读取 vs. 网络请求 vs. 数据库写入）。
- 子 Agent 分派：Orchestrator 级别控制同时活跃的子 Agent 数量。

## 4. 自适应并发控制

固定并发上限在负载波动时表现不佳——过高导致过载，过低浪费吞吐。自适应算法根据实时信号动态调整。

### 4.1 Netflix Gradient2

Gradient2 通过测量请求延迟的梯度（变化率）来推断服务端负载：

```text
gradient = RTT_noload / RTT_actual
new_limit = current_limit × gradient + queue_size
```

- 延迟上升 → gradient < 1 → 降低并发上限。
- 延迟稳定 → gradient ≈ 1 → 保持当前上限。
- 延迟下降 → gradient > 1 → 缓慢提升上限。

### 4.2 Vegas

Vegas 算法基于 TCP Vegas 的思想，通过队列延迟估算拥塞程度：

```text
queue_size_estimate = current_limit × (1 - RTT_noload / RTT_actual)
if queue_size_estimate < alpha: increase limit
if queue_size_estimate > beta:  decrease limit
```

### 4.3 Agent 系统的信号选择

传统微服务用 HTTP 延迟作为信号，Agent 系统需要更丰富的信号：

| 信号 | 来源 | 含义 |
|---|---|---|
| LLM API 延迟 | 模型调用 RTT | 模型端负载 |
| 429 错误率 | API 响应码 | 达到 rate limit |
| 工具执行延迟 | 工具调用 RTT | 工具端瓶颈 |
| 队列等待时间 | 任务队列 | 入口过载 |
| Token 消耗速率 | budget tracker | 预算耗尽风险 |

## 5. 队列时间 SLO

请求在队列中等待的时间也需要约束——排队 30 秒的请求即使最终执行成功，用户体验也已经不可接受。

```yaml
queue_slo:
  max_wait_time: 10s            # 超过即卸除
  age_based_priority: true      # 越老优先级越低（防止队头阻塞）
  stale_threshold: 30s          # 超过直接丢弃
  shedding_policy: oldest_first # 卸除最老的请求
```

**自适应卸除（Adaptive Shedding）**：当队列深度超过阈值时，按优先级从低到高逐步卸除。高优先级请求（用户直接交互）始终保留；低优先级请求（后台预取、投机执行）优先丢弃。

## 6. 对冲请求（Hedged Requests）

对冲请求是应对尾延迟的策略——同时发送两个相同请求，取先返回的结果。

### 6.1 适用条件

| 条件 | 要求 |
|---|---|
| 幂等性 | 请求必须是幂等的（GET、纯推理、只读工具调用） |
| 非过载 | 仅在系统负载低于阈值时启用 |
| 预算充足 | 对冲请求消耗双倍 token 预算 |

### 6.2 禁用场景

- 系统过载时（429 错误率 > 5%）：对冲会加剧过载。
- 非幂等操作（写入、删除、外部 API 调用）：不可对冲。
- 预算紧张时：对冲的 token 成本不可接受。

```yaml
hedged_request:
  enabled: true
  delay_before_hedge: p95_latency    # 超过 P95 延迟才发对冲
  max_hedges: 1                       # 最多一次对冲
  disable_conditions:
    - error_rate > 0.05
    - budget_remaining < 20%
    - operation_type == write
```

## 7. 隔板隔离（Bulkhead Isolation）

隔板模式将不同的依赖或流量类别隔离到独立的资源池，防止一个依赖的故障拖垮整个系统。

### 7.1 按依赖隔离

```text
┌──────────────────────────────────────────────┐
│                  Agent 运行时                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ LLM Pool │  │ Tool Pool│  │ Memory   │   │
│  │ max=10   │  │ max=20   │  │ Pool     │   │
│  │          │  │          │  │ max=5    │   │
│  └──────────┘  └──────────┘  └──────────┘   │
│   独立限流      独立限流      独立限流         │
└──────────────────────────────────────────────┘
```

### 7.2 按流量类别隔离

| 流量类别 | 资源配额 | 卸除优先级 |
|---|---|---|
| 用户实时交互 | 60% | 最后卸除 |
| 后台任务（eval、预取） | 25% | 优先卸除 |
| 内部 health check | 15% | 中等 |

## 8. Akka Bounded Mailbox 策略

Akka Actor 的 mailbox 是天然的背压控制点。当 mailbox 满时，三种策略：

| 策略 | 行为 | 适用场景 |
|---|---|---|
| **Drop** | 丢弃新消息 | 非关键通知、metrics 上报 |
| **Block** | 阻塞发送者直到 mailbox 有空间 | 需要背压传播的流水线 |
| **Crash** | Actor 崩溃，由 Supervisor 重启 | 快速失败优先的场景 |

Agent 系统中，Drop 策略适合投机执行结果的收集；Block 策略适合多 Agent 协作的消息传递；Crash 策略适合"宁可重启也不丢数据"的持久化场景。

## 9. Agent 特有的背压场景

| 场景 | 瓶颈 | 背压策略 |
|---|---|---|
| 模型 API rate limit | Provider RPM/TPM 限制 | Token bucket + 自适应退避 + provider 轮转 |
| 工具执行吞吐 | 工具端 CPU/IO/网络 | Semaphore + 按工具类型隔板 |
| 记忆写入争用 | 向量数据库写入延迟 | 写入队列 + 批量合并 + 异步刷盘 |
| 多 Agent 消息风暴 | Orchestrator 消息处理能力 | Bounded mailbox + 优先级队列 |
| Streaming 输出 | 客户端消费速率 | 流控（背压传播到 LLM 调用） |

## 10. 评审清单

```text
[ ] 模型 API 调用是否有速率限制，而非依赖 429 重试？
[ ] 并发上限是固定值还是自适应调整？
[ ] 队列是否有深度限制和等待时间 SLO？
[ ] 不同依赖是否隔离到独立资源池？
[ ] 对冲请求是否仅用于幂等操作且过载时自动禁用？
[ ] 背压信号是否反馈到入口控制层？
[ ] token 预算耗尽是否触发请求卸除？
```

## 交叉引用

| 关联文件 | 关系 |
|---|---|
| [Concurrency Plane overview](./overview.md) | 父文件，并发模型选择 |
| [Cancellation Tokens](./cancellation-tokens.md) | 背压触发取消的协同 |
| [Event Ordering](./event-ordering.md) | 背压下的消息顺序保证 |
| [Cost Plane overview](../cost/overview.md) | 背压是成本控制的运行时执行层 |
| [Token Budgeting](../cost/token-budgeting.md) | 预算耗尽触发背压 |
| [Circuit Breaker pattern](../../../design-space/patterns/depth-budgeting.md) | 熔断器是背压的下游保护层 |
| [Infinite Retry anti-pattern](../../../design-space/anti-patterns/README.md) | 缺乏背压导致的典型反模式 |
