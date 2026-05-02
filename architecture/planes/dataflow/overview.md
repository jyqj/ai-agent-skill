# Dataflow Plane
>
> **所属域**：6. Coordination — 批量、流式与管道
>
> **Evidence Status** — synthesized. 批量任务、流式处理、持续事件响应、Agent pipeline 的生产需求。

**Principle Refs**: IS-01, BR-02 — 数据是对世界的表征而非世界本身；数据新鲜度随时间结构性衰减

## 1. 定义

Dataflow Plane 负责批量、流式、管道式 Agent 处理：当输入不是单个任务而是一组对象或持续事件流时，Agent 需要管道、窗口、回压和错误传播。

## 2. 处理模式

| 模式 | 适合 | 关键机制 |
|---|---|---|
| Batch | 多文件、多记录、批量审核 | chunking、dedup、checkpoint |
| Stream | 日志、告警、实时事件 | window、watermark、backpressure |
| Pipeline | Agent A 输出给 Agent B | output contract、error propagation |
| Map-Reduce | 大规模可并行任务 | worker fanout、merge verifier |
| Continuous Monitor | 长期观察和触发行动 | subscription、incident gate |

## 3. FlowRun

```yaml
flow_run:
  flow_id: flow_...
  mode: batch | stream | pipeline | monitor
  input_refs: []
  stages:
    - name: represent
      input_schema: object
      output_schema: object
      error_policy: retry | skip | quarantine | stop
  backpressure:
    max_queue_size: integer
    overflow_policy: drop_low_priority | pause_input | ask_human
  metrics:
    throughput: number
    latency_ms: number
    error_rate: number
```

## 4. 错误传播

```text
upstream representation error
  → quarantine item
  → do not pass as fact
  → preserve raw ref
  → report aggregate uncertainty
```

```text
downstream effect failure
  → stop dependent stages
  → mark pending effects
  → compensate if necessary
  → keep successful independent items
```
