# Agent Platform Design Decisions

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

| 决策 | 默认 | 升级触发 |
|---|---|---|
| 隔离 | 数据+计算+网络 | 合规 → 物理隔离 |
| 执行 | 容器化+超时+预算 | 长任务 → durable |
| 协议 | MCP 优先; A2A 逐步 | 跨组织 → ANP |
| 版本 | 完整指纹 | 变更追踪+回归 |
| 安全 | 沙箱+最小权限 | 市场 → 审核流程 |
| 成本 | 配额+路由+缓存 | 按用量计费 |
