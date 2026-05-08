# Recovery × Cost 交叉设计

> **Evidence Status** — synthesized. 从 Recovery plane 和 Cost plane 的独立设计中抽取的约束关系。

## 核心冲突

Recovery 操作消耗 token 和时间。当 Cost budget 接近耗尽时，Recovery 的重试可能加速预算枯竭。反过来，如果为了省成本而跳过 Recovery，可能导致更大的后续损失（部分完成的写操作、不一致的状态）。

## 约束规则

| 规则 | 内容 | 优先级 |
|---|---|---|
| R1 | Recovery 操作的 token 消耗从 Cost budget 中扣除，不另设独立池 | Cost 优先 |
| R2 | 当 Cost budget 剩余 <20% 时，Recovery 降级为"仅补偿，不重试" | Cost 优先 |
| R3 | 对写操作的 Recovery（补偿/回滚），即使预算不足也必须执行 | Recovery 优先 |
| R4 | Recovery 每次重试前检查 Cost budget，不足时自动 escalate 为人工处理 | 联合 |
| R5 | 连续 Recovery 操作的成本按指数增长估算（retry 1 = 1x, retry 2 = 2x, retry 3 = 4x），超过阈值时停止 | Cost 优先 |

## 决策流程

```text
Recovery 需要重试？
  ├─ 是写操作的补偿？ → 无条件执行（R3）
  ├─ Cost budget > 20%？ → 正常重试，扣减预算（R1）
  ├─ Cost budget 10-20%？ → 仅补偿，不重试新方案（R2）
  └─ Cost budget < 10%？ → escalate 为人工处理（R4）
```

## 参考

- Recovery Plane: `../planes/recovery/overview.md`
- Cost Plane: `../planes/cost/overview.md`
