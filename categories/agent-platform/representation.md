# Agent Platform Representation Model

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

| 对象 | 含义 | Trust |
|---|---|---|
| AgentCard | 能力/schema/版本/权限 | config |
| ToolSchema | 参数/返回/副作用 | config |
| ExecutionTrace | 步骤/调用/结果/耗时 | high |
| TenantConfig | 权限/配额/允许模型 | config |
| DeployManifest | 版本/依赖/配置 | config |
| HealthStatus | 可用性/延迟/错误率 | high |
