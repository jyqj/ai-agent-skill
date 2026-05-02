# Ops / SRE Agent Eval Cases

> **Evidence Status** — synthesized. 基于品类架构模板和 Ops/SRE 场景的通用设计。

## 评估维度

| 维度 | 指标 | 参考值 |
|---|---|---|
| 分诊准确率 | 正确分类/总告警 | > 90% |
| MTTR 改善 | Agent vs 人工 | > 50% |
| 告警噪音降低 | 聚合后/原始 | > 60% |

## Cases

### Case 1: 部署后延迟飙升
```yaml
expected: 关联部署事件 → 识别新版本为根因 → 建议回滚 → 验证恢复
```

### Case 2: 级联故障
```yaml
expected: 通过拓扑识别 DB 为根因 → 不被下游告警分散
```

### Case 3: 误报告警
```yaml
expected: 识别为误报 → 建议调整阈值 → 不触发缓解
```
