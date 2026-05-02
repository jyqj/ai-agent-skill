# Model Routing

> **Evidence Status** — synthesized. 多模型 Agent 系统的常见生产需求。

## 1. 路由目标

模型路由要在质量、成本、延迟和可靠性之间选择，而不是固定一个模型跑所有步骤。

## 2. 路由表

| 任务 | 默认模型 | 升级触发 | 降级触发 |
|---|---|---|---|
| 简单分类/格式化 | small | 多次 schema 失败 | 无 |
| 工具参数生成 | medium | 高风险、复杂对象识别 | 重复任务有模板 |
| 长规划 | large | 跨源冲突、多步骤 | 计划模板已知 |
| 验证/批判 | medium/large | 高风险 claim 或 write effect | 低风险格式检查 |
| 摘要/压缩 | small/medium | 摘要涉及关键证据 | 非关键历史 |
| 用户解释 | medium | 高敏感交互 | 简单进度报告 |

## 3. 升级信号

```text
low_confidence
conflicting_evidence
high_risk_effect
repeated_tool_failure
schema_failure
user_correction
critical_claim
```

## 4. 路由输出

```yaml
model_route:
  step: verify_claim
  selected_class: large
  reason: conflicting_evidence + critical_claim
  expected_cost: number
  fallback: ask_user_or_partial
```
