# Concurrency Plane
>
> **所属域**：6. Coordination — 并发、超时与取消
>
> **Evidence Status** — synthesized. 工具并发、worker orchestration、长任务取消、streaming Agent 的生产需求。

**Principle Refs**: BR-01, IS-03 — 预算约束按线程独立核算；并发状态可能彼此偏离导致竞态

当多个工具调用、多个 Worker 或多个 Agent 同时运行时，并发控制（Concurrency）决定系统是否稳定——缺少它，重试风暴、竞态写入和丢失取消都会变成生产事故。

## 1. 定义

Concurrency Plane 负责并发上限、事件排序、超时、取消、中断、重试和资源竞争。

它不是 Orchestration：Orchestration 决定谁做什么；Concurrency 决定同时做多少、何时取消、失败如何传播。

## 2. 核心对象

```yaml
concurrency_policy:
  max_parallel_tool_calls: integer
  max_parallel_workers: integer
  timeout_by_tool: object
  cancellation_propagation: parent_to_child | bidirectional | manual
  retry_policy:
    max_attempts: integer
    requires_new_evidence: true
  ordering:
    event_order: logical_clock | timestamp | causal_chain
```

## 3. 取消语义

| 取消来源 | 处理 |
|---|---|
| 用户取消 | 停止新动作，补偿已执行 effect，交付当前状态 |
| Policy block | 停止危险分支，保留安全分支 |
| Budget exhausted | 停止高成本步骤，触发 budget_choice |
| Parent task failed | 子任务收到 cancellation token |
| Stale world state | 暂停写动作，先 refresh |

## 4. 并发反模式

- Unbounded Workers：worker 数量无上限。
- Retry Storm：失败后多个分支同时重试同一工具。
- Lost Cancellation：用户取消后后台任务继续写外部系统。
- Race-to-Write：多个 Agent 写同一对象无锁或仲裁。
- Timestamp-only Ordering：只按时间排序，不考虑因果关系。
