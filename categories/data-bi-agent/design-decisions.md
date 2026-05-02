# Data / BI Agent Design Decisions

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

| 决策 | 默认 | 升级触发 |
|---|---|---|
| Semantic Layer | 必须有 | 无 → 准确率下降 |
| Schema 检索 | RAG + dynamic | 百万表 → 集群化 |
| 权限 | 只读；继承用户权限 | PII → 自动脱敏 |
| 缓存 | TTL=数据刷新周期 | 实时 → 禁缓存 |
| 可解释性 | SQL+口径+时效 | 合规 → +数据血缘 |
