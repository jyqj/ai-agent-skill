# Research Agent Design Decisions

> **Evidence Status** — speculative. research/report systems、citation workflows、frontier 文档与成本/交互/安全 plane。

## 检索策略

| 决策 | 默认 | 升级触发器 |
|---|---|---|
| Breadth vs Depth | 先 breadth 建 source map，再对高价值 claim depth verify | 冲突多、结论风险高 |
| Query Fanout | 小批量并行，避免无限 retrieval | coverage 不足或 authority 不够 |
| Refresh | 对时间敏感 claim 做 targeted refresh | latest/current/recent 任务 |

## 上下文策略

Research Agent 的上下文中心不是“文档”，而是：

```text
question → claim → evidence → citation → unresolved gaps
```

默认：

- 用 snippets 和 source metadata 组上下文；
- 保留 raw refs，不直接塞全文；
- 对章节级 synthesis 采用 progressive disclosure；

## 成本策略

| 资源 | 默认约束 |
|---|---|
| Search | 限制 fanout 和重复 query |
| Fetch / Read | 先 metadata / relevant sections，再全文 |
| Synthesis | 先 section draft，再总报告整合 |
| Refresh | 只对高影响、时间敏感 claim 触发 |

## 交互策略

| 情况 | 默认交互 |
|---|---|
| 任务范围模糊 | 只问最阻塞的一问 |
| 证据不够但已有部分结果 | partial completion |
| 结论冲突 | 明示冲突，不装作已经解决 |
| 成本接近预算 | 提供“继续检索 / 现在交付”的选择 |

## 控制策略

Research Agent 的关键控制点不是审批按钮，而是：

- fabricated citation gate
- freshness gate
- conflict preservation gate
- publish / send gate

## 运维策略

进入持续使用后，应至少记录：

```text
[ ] query fanout
[ ] source diversity
[ ] section-level citation density
[ ] unresolved conflict count
[ ] cost per completed brief
[ ] refresh hit rate
```

## 升级触发器

| 观察 | 升级 |
|---|---|
| 经常出现 citation drift | 引入 stricter citation chain tooling |
| 结论常被 freshness 打脸 | 强化 refresh policy |
| 报告容易拼贴 | 引入 section-level synthesis state |
| 长任务断裂 | checkpoint + partial deliver |
| 研究主题反复出现 | 引入 scoped memory / source preference memory |
