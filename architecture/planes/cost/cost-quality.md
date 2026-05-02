# Cost-Quality Tradeoff

> **Evidence Status** — synthesized. Agent 任务中成本、质量、速度和风险的权衡模型。

## 1. Pareto 视角

同一个任务可以有多条策略：

| 策略 | 成本 | 质量 | 适合 |
|---|---:|---:|---|
| Fast answer | 低 | 中 | 低风险、用户要方向 |
| Evidence-backed | 中 | 高 | 调研、报告、客户沟通 |
| Verified effect | 高 | 高 | 写外部系统、代码变更 |
| Red-team checked | 更高 | 很高 | 安全、合规、高风险发布 |

## 2. 质量目标

```yaml
quality_target:
  level: minimal | standard | high | critical
  required_evidence: none | source | test | readback | independent_verifier
  acceptable_uncertainty: high | medium | low | near_zero
  interaction_policy: none | ask_when_blocked | ask_at_gates | human_in_loop
```

## 3. 用户可选项

当成本接近预算时，不应偷偷降级。应提供：

```text
继续高质量完成
降低验证深度
只交付部分结果
暂停等待用户补充信息
停止并总结目前证据
```
