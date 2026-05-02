# Agent Platform Evaluation Cases

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

| 维度 | 指标 |
|---|---|
| 可用性 | > 99.9% |
| 执行成功率 | > 99.5% |
| 延迟 | 启动<2s, 工具 overhead<100ms |
| 隔离 | 跨租户泄露=0 |

## Cases

### 多租户隔离
```yaml
租户 A Agent 访问租户 B → 拒绝+审计+A 不受影响
```

### 恶意插件
```yaml
第三方工具读环境变量 → 沙箱阻止+记录+标记
```
