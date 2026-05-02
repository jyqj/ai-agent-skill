# Ops / SRE Agent Representation

> **Evidence Status** — synthesized. 基于品类架构模板和 Ops/SRE 场景的通用设计。

## 核心表示对象

| 表示对象 | 含义 | Freshness | Trust |
|---|---|---|---|
| Alert | 告警：来源、严重级、状态 | 实时 | medium（可能误报） |
| MetricTimeSeries | SLI、延迟、错误率 | 秒/分级 | high |
| LogEntry | 结构化/非结构化日志 | 实时 | medium |
| TraceSpan | 分布式 trace | 请求级 | high |
| DeployEvent | 版本、时间、变更 | 事件驱动 | high |
| ServiceTopology | 依赖图、SLA | 低频 | high |
| SLI/SLO/ErrorBudget | 服务级别指标 | 滚动窗口 | high |

## 信号关联

```text
单一信号 → 噪音；多信号关联 → 信号
维度: 时间（5min 内部署/变更）、拓扑（同链路）、模式（历史相似）
```
