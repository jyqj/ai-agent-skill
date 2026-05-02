# Ops / SRE Agent Design Decisions

> **Evidence Status** — synthesized. 基于品类架构模板和 Ops/SRE 场景的通用设计。

## 核心决策

| 决策 | 默认 | 升级触发 |
|---|---|---|
| 自治 | 诊断自主，缓解需确认 | 低风险高置信可自动 |
| 架构 | Supervisor + 子 Agent (metrics/logs/topology/runbook) | — |
| 数据 | 查询现有可观测性平台 | 跨平台需统一抽象 |
| 记忆 | 历史 incident + runbook + 拓扑 | 组织知识库集成 |

## 关键陷阱

- **Alert Storm 过载：** 先聚合去重再分析。
- **过度自治：** 高风险缓解必须人工确认。
- **过度自信：** 部分信号时标注置信度。
