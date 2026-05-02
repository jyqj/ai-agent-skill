# Async Collaboration Patterns

> **Evidence Status** — synthesized. 长任务、worker、streaming、事件驱动 Agent 的常见协作需求。

## 1. 异步模式

| 模式 | 用途 |
|---|---|
| Fire-and-Collect | 并行 worker 执行，统一收集结果 |
| Event Subscription | Agent 订阅事件流，按触发器行动 |
| Lease-based Work | worker 领取任务租约，超时释放 |
| Heartbeat | 长任务定期报告进度和阻塞 |
| Cancellation Propagation | 上游取消向下游传播 |
| Partial Result Streaming | 允许先交付可验证部分 |

## 2. 必备语义

```text
correlation_id
idempotency_key
cancellation_token
lease_expiry
heartbeat_interval
partial_result_schema
```

## 3. 失败处理

| 失败 | 处理 |
|---|---|
| worker timeout | 取消或重新分派 |
| duplicate event | idempotency 去重 |
| partial failure | 合并成功部分，失败部分进入 recovery |
| stale result | 检查 world state freshness |
| coordinator failure | 从 checkpoint 恢复 |
