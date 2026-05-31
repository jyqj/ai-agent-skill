# Gateway Control Plane

> **Evidence Status** — grounded. OpenClaw thin gateway protocol 实现。

## 模式定义

Gateway 作为纯控制平面协调 Agent、Channel、Plugin，自身不运行 Agent loop。采用 thin protocol（data-first, acyclic）和 additive-only 演化策略。

## 核心特征

| 特征 | 说明 |
|------|------|
| 控制平面 | Gateway 只做调度和协调，Agent 在独立进程运行 |
| Thin Protocol | RPC method registry + schema validation (AJV) |
| Additive-Only | 新方法/事件/字段只能添加，不能删除或修改语义 |
| Data-First | protocol 层无循环依赖，纯数据定义 |

## 与 Harness Container 的关系

| 维度 | Gateway Control Plane | Harness Container |
|------|---------------------|-------------------|
| 关注点 | 通信协议 + 调度 | 执行环境 + 隔离 |
| Agent 位置 | 独立进程 | 容器内 |
| 协议 | RPC/WebSocket | 进程间通信 |
| 扩展 | 新 RPC method | 新 Agent 类型 |

## 实现参考

| 项目 | Protocol | RPC 数 |
|------|----------|--------|
| OpenClaw | JSON-RPC + WebSocket | 100+ |
| Hermes | HTTP REST | ~20 |

## 适用条件

- 需要多渠道/多设备协调
- Agent 需要独立于 Gateway 生命周期
- 需要向后兼容的长期演化
