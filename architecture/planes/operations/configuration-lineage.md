# Configuration Lineage

> **Evidence Status** — synthesized. 生产系统需要追踪模型、prompt、tool schema、policy、eval suite、parser 的组合。

## 1. 定义

Configuration Lineage 记录一次 Agent 行为由哪些配置产生，是运行时审计和回归所需的行为指纹。

## 2. ConfigFingerprint

```yaml
config_fingerprint:
  fingerprint_id: cfg_...
  model_ref: string
  prompt_ref: string
  tool_schema_refs: []
  policy_refs: []
  parser_refs: []
  eval_suite_refs: []
  runtime_flags: object
  created_by: system | operator
```

## 3. 使用场景

| 场景 | 用途 |
|---|---|
| trace replay | 知道当时模型和 prompt 是什么 |
| regression | 比较配置变化前后的输出差异 |
| incident | 定位是 policy、tool schema 还是模型行为变化 |
| canary | 把新配置限制在小范围 |
| rollback | 回到上一个已通过评估的配置组合 |
