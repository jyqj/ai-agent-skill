# Enterprise Workflow Agent Implementation Map

> **Evidence Status** — synthesized. 基于品类架构模板和通用 workflow agent 设计。

## 参考实现

| 参考 | 核心学习点 |
|---|---|
| ServiceNow Flow Designer | 可视化流程、审批链、SLA |
| Temporal / Inngest | durable execution、补偿、checkpoint |
| MCP + A2A | 工具标准化 + 跨 Agent 协作 |
| n8n / Zapier | 多系统集成、webhook、错误处理 |

## 模块到实现映射

| 模块 | 推荐 | 说明 |
|---|---|---|
| 流程引擎 | Temporal / Inngest | 复杂长流程 |
| API 集成 | MCP server per system | 标准化接入 |
| 凭证 | HashiCorp Vault / AWS SM | 轮换+审计 |
| 审计 | PostgreSQL append-only | 不可篡改 |
| 权限 | OPA | policy-as-code |

## MVA 阶梯

| 级别 | 能力 |
|---|---|
| MVA-0 | 流程查询助手（只读） |
| MVA-2 | 单系统写 + effect verification |
| MVA-3 | 审批链 + SLA 时钟 |
| MVA-4 | 跨系统 + SAGA 补偿 + checkpoint |
| MVA-5 | durable execution + 完整审计 + 监控 |
