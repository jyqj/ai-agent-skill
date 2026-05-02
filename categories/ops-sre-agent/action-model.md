# Ops / SRE Agent Action Model

> **Evidence Status** — synthesized. 基于品类架构模板和 Ops/SRE 场景的通用设计。

## 动作分类

| 动作 | 风险 | Precondition | Verification |
|---|---|---|---|
| 查询指标/日志/trace | safe | 时间范围合理 | 数据返回 |
| 告警 ack/silence | check | 告警存在 | 状态已更新 |
| 重启 Pod/Service | approval | 无活跃流量 | health check |
| 回滚部署 | approval | 旧版本可用 | SLI 恢复 |
| 扩容 | check | 资源充足 | 新副本 Ready |
| 修改 feature flag | approval | flag 存在 | 回读+效果监控 |

## 安全原则

- 所有写操作有自动回滚条件（SLI 未改善 → 5min 回滚）。
- 高风险动作需 on-call approve。
- 每个缓解后监控 SLI ≥ 5 分钟。
