# Shadow Mode Regression

> **Evidence Status** — synthesized. 源自 Operations、Eval Runner、Trace Replay 等系统的生产需求，尚处于草稿阶段。

## 核心思路

升级 Agent 运行时（Runtime）时，最大的风险是它"悄悄变差"：做出了不同的决策，漏掉了关键证据，或者低估了风险。Shadow Mode 解决的就是这个问题：让新运行时在真实输入上做一次 dry-run，不产生任何外部效果，只记录它"将会做什么"，然后与当前运行时的实际行为做对比。

## 流程

```text
real runtime handles task
shadow runtime receives same observations and state copy
shadow runtime can decide but cannot act
compare decision / tool_call / risk / cost / final_answer
block rollout if divergence exceeds threshold
```

影子运行时（Shadow Runtime）拿到与正式运行时完全相同的观测和状态副本，独立做出决策，但没有执行权限。两侧的输出在五个维度上进行比较，任何一个维度的偏离超过阈值，就阻止新版本上线。

## 比较维度

- **Decision divergence** — 是否选择了不同的工具或操作对象。这是最直观的分歧信号。
- **Risk divergence** — 新运行时是否低估了风险。例如旧版本标记为"需要人工审批"的操作，新版本直接自动执行。
- **Cost divergence** — 成本是否显著增加，包括 token 用量和工具调用次数。
- **Evidence divergence** — 新运行时是否遗漏了关键证据，导致结论的支撑变弱。
- **Effect divergence** — 如果真正执行，两侧是否会产生不同的外部效果（文件修改、API 调用、消息发送等）。
