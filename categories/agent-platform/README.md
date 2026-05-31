# Agent Platform Architecture

> **Evidence Status** — synthesized. LangGraph Platform、CrewAI、OpenAI Agents SDK、Temporal、MCP/A2A/ACP 协议生态。

> **文档深度**：骨架级，提供设计维度清单和关键问题，不提供完整蓝图。详细设计需结合 `architecture/planes/` 和 `paradigms/` 自行组装。

## Core Job

提供 Agent 从原型到生产的基础设施层：

```text
注册/发现 → 配置工具和权限 → 编排执行 → 监控运行 → 评估质量 → 安全治理
```

## 核心能力

| 能力域 | 关键组件 |
|---|---|
| Agent Registry | 发现、版本、Agent Card (A2A) |
| Tool Registry | 注册、schema、权限 (MCP) |
| Execution Runtime | 生命周期、checkpoint、超时 |
| Protocol Support | MCP(tools) + A2A(agents) + ACP(messaging) |
| Security | 认证、权限、租户隔离、审计 |
| Observability | trace、成本、延迟 (OpenTelemetry) |
| Evaluation | 离线 eval、A/B、shadow mode |
| Operations | 部署、canary、回滚、配置 |

## 品类设计决策

| 决策 | 默认 |
|---|---|
| 多租户 | 强隔离（数据+计算+网络） |
| 插件安全 | 沙箱+schema 验证+最小权限 |
| 版本 | model+prompt+tools+config = 完整指纹 |
| 协议 | MCP 优先(工具)；A2A 逐步(Agent 间) |
| 成本 | 按租户配额+模型路由+缓存 |

## 参考

| 参考 | 学习点 |
|---|---|
| LangGraph Platform | 状态图、checkpoint |
| OpenAI Agents SDK | hosted runtime、guardrails |
| Temporal | durable execution |
| MCP/A2A | 协议标准 |
| Trellis | Multi-platform Agent Harness, 14 平台 configurator |
| OpenClaw | Personal AI Gateway + plugin platform hybrid |

## 协议栈

```text
AG-UI (Agent-User)
A2A / ACP (Agent-Agent)
MCP / WebMCP (Agent-Tool)
HTTP / SSE / WebSocket
```

- 主观性任务的验证扩展：`../../concepts/beyond-verification.md`
