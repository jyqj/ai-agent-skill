# Trace Sampling

> **Evidence Status** — synthesized. 生产 Agent 的成本、隐私、调试、评估需求。

## 1. 采样策略

| 事件 | 采样 |
|---|---|
| 高风险写动作 | 全量 |
| policy block / security event | 全量 |
| 用户纠错 | 全量，注意隐私 |
| 工具失败 | 全量 |
| 低风险成功问答 | 采样 |
| 大型 tool output | 引用 + 摘要，原始输出按保留策略 |
| secret / personal data | 脱敏或不落盘 |

## 2. 采样不是删除证据

对于关键验证链，不能只保留文本摘要。应保留：

```text
raw ref
hash
redacted structured fields
effect id
verification status
```
