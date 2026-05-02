# Agent Platform Action Model

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

| 动作 | 风险 | Verification |
|---|---|---|
| Agent CRUD | check | schema+回读 |
| Tool CRUD | check | 连接+schema |
| Agent 执行 | check | 超时/预算 |
| 部署 | approval | health+canary |
| 权限变更 | approval | 审计 |
