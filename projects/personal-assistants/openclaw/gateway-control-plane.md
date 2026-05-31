# OpenClaw Gateway Control Plane

> **Evidence Status** — grounded. OpenClaw src/gateway/ 源码分析。

## 设计原则

- Gateway 是控制平面，不运行 Agent loop
- Agent 在独立进程中运行
- Protocol 是 data-first, acyclic（无循环依赖）
- Additive-only evolution（只添加，不删除/修改语义）

## Protocol Layer

`src/gateway/protocol/index.ts`：37,159 行，100+ RPC methods

关键类型：ChatEvent, TalkEvent, AgentEvent, ExecApprovalRequestParams, CronAddParams

## Server 架构

- Boot phase → Event loop readiness → Config reload
- Session management (multi-agent routing)
- Channel lifecycle (start/stop)
- Control UI (Web frontend)
- Rate limiting

## 通信

- WebSocket：实时事件
- HTTP/REST：配置和 RPC
- MCP：Model Context Protocol
