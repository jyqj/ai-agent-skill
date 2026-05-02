# Security Agent Design Decisions

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

| 决策 | 默认 | 升级触发 |
|---|---|---|
| 自身安全 | 净化+隔离+最小权限+审计 | 被利用 → 隔离审查 |
| 误报 | FP>FN; 持续优化 | >50% → 规则调优 |
| 机密 | 自动 redact | 泄露 → 轮换+审计 |
| 响应速度 | 分诊<5min | 自动 → 秒级 |
