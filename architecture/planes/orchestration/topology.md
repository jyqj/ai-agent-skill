# Agent Topologies

> **Evidence Status** — synthesized. worker orchestration、subagent、multi-window 等模式。

## 1. 拓扑类型

| 拓扑 | 结构 | 适合 | 风险 |
|---|---|---|---|
| Star | Coordinator 分发给 workers | 并行研究、代码子任务 | coordinator 瓶颈 |
| Pipeline | A 输出给 B | 数据处理、审核链 | 上游错误传播 |
| Hierarchical | 多层 manager/worker | 大项目拆解 | 层级过深丢信息 |
| Mesh | Agent 互相通信 | 开放式协作 | 冲突和成本失控 |
| Blackboard | 共享状态板 | 多专家写入共同世界模型 | 一致性和权限复杂 |

## 2. 选择框架

```text
任务可并行 + 输出可合并 → Star
任务天然顺序依赖 → Pipeline
任务规模大且可分层 → Hierarchical
需要多专家争论 → Mesh，但必须有 arbitration
需要共享事实池 → Blackboard，但必须有 conflict record
```

## 3. 合并策略

| 输出 | 合并方式 |
|---|---|
| 独立文件修改 | diff merge + tests |
| 研究 claim | evidence merge + conflict resolution |
| API actions | effect ledger merge + readback |
| 计划 | coordinator select / synthesize |
| 风险 | 取最高风险，不平均 |
