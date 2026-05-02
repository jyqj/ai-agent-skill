# Ops / SRE Agent Implementation Map

> **Evidence Status** — synthesized. 基于品类架构模板和 Ops/SRE 场景的通用设计。

## 参考实现

| 参考 | 学习点 |
|---|---|
| New Relic SRE Agent | 遥测诊断、拓扑感知 |
| Azure SRE Agent | 自动根因、runbook 集成 |
| Observe AI SRE | 数据湖、知识图谱 |
| incident.io | 自主调查、90%+ 准确率 |

## 推荐架构

```text
Supervisor Agent
  ├── Metrics Agent (Prometheus/Datadog)
  ├── Logs Agent (ELK/Loki)
  ├── Topology Agent (service map)
  └── Runbook Agent (检索+执行)
```

## MVA 阶梯

| 级别 | 能力 |
|---|---|
| MVA-0 | 告警摘要+自然语言查询 |
| MVA-2 | 分诊+关联聚合 |
| MVA-3 | 根因假设+证据链 |
| MVA-4 | Runbook 半自动+验证 |
| MVA-5 | 自动缓解+回滚+复盘 |
