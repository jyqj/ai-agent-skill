# RL 驱动记忆管理路线图

> **Evidence Status** — theoretical. 基于 2025-2026 年 RL-for-agents 研究趋势的前瞻推演。

当前多数 Agent 记忆系统依赖启发式规则（相似度阈值、TTL、手动标注）决定写入、淘汰和检索。RL 提供了一条从规则驱动走向数据驱动的演进路径。

## 三阶段演进

| 阶段 | 特征 | 记忆决策方式 | 典型实现 |
|---|---|---|---|
| RL-free | 当前主流 | 规则 + 启发式（相似度、新鲜度、人工策略） | Mem0 四维 scope、GenericAgent 写入 ROI |
| RL-assisted | 近期可行 | RL 信号辅助调参——用任务成功率作为 reward 优化检索排序权重和淘汰阈值 | 离线 RL 微调检索策略 |
| RL-driven | 远期目标 | 端到端 RL 控制记忆全生命周期——写入选择、存储分配、检索策略、遗忘时机均由 policy network 决定 | 尚无生产验证 |

## 关键挑战

- **Reward 信号稀疏**：任务成功/失败是延迟且稀疏的信号，需要中间 reward shaping（如检索命中率、上下文利用率）。
- **安全约束**：RL policy 不能绕过记忆治理规则（隐私删除、provenance 要求），需要 constrained RL 或 reward penalty。
- **冷启动**：新 Agent 缺少历史数据，RL-assisted 阶段仍需规则兜底。

相关文件：`memory-forms-and-dynamics.md`、`../../paradigms/memory-paradigms.md`、`../../architecture/planes/memory/overview.md`。
