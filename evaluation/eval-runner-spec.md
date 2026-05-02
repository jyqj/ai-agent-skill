# Eval Runner Spec

> **Evidence Status** — synthesized. Eval Framework、fixtures、failure injection、config fingerprint 等既有评估文档的统一运行需求。

Eval Runner 是评估框架的执行引擎：它把 case、fixture、mock 和 scoring 串联成可重复运行的回归流水线。

## 目录建议

```text
evaluation/
  README.md
  eval-framework.md
  eval-runner-spec.md
  eval-runner/
  fixtures/
    README.md
    *.yaml
  suites/
    smoke/
    regression/
    canary/
```

## Runner 需要完成什么

1. 加载 case 与 fixture
2. 装配 mock tools / sandbox / world state
3. 注入 failure mode
4. 执行 agent run 或读取真实 trace
5. 收集 trace、artifacts、effect ledger、config fingerprint
6. 自动与人工混合评分
7. 输出配置差异 compare 报告

## 输入契约

### Eval Case

```yaml
case_id: string
product_type: string
required_depth: string
input_event: {}
representation_expectations: []
world_state: []
allowed_tools: []
success_criteria: []
failure_injection: []
metrics: []
```

### Config Fingerprint

```yaml
config_fingerprint:
  fingerprint_id: string
  model_ref: string
  system_prompt_ref: string
  tool_schema_refs: []
  control_policy_refs: []
  eval_suite_refs: []
```

## 执行流程

```text
Load case
  → Materialize fixtures
  → Start instrumented run
  → Capture representation / prompt / decision / tool / effect / checkpoint events
  → Score automatic assertions
  → Queue human review for ambiguous dimensions
  → Store compare-ready result bundle
```

## 自动评分维度

- task_success
- representation_quality
- freshness_trust_compliance
- effect_verified_rate
- claim_verification_rate
- interaction_quality
- policy_compliance
- recovery_success
- cost / latency

## 需要人工评分的维度

- 报告是否清楚披露不确定性
- 升级 / 打断时机是否合适
- 在多解情况下是否做了合理取舍
- 对残余风险的解释是否充分

## 最小输出

```yaml
eval_run:
  run_id: string
  suite: regression
  case_id: string
  config_fingerprint: {}
  passed: true
  metrics:
    task_success: 1.0
    effect_verified_rate: 1.0
    policy_compliance: 1.0
    avg_cost: 1.34
  regressions: []
  artifacts:
    trace_id: string
    effect_records: []
```
