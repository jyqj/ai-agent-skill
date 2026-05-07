# Eval Planner

> **Evidence Status** — synthesized. 从 eval framework、fixtures 和 trace comparator 压缩出的最小验收设计工具。

## 30 秒判断

Eval 不是最后补测试，而是定义“什么叫完成”。

| Agent 类型 | 最小 eval |
|---|---|
| Coding | 修改 bug → 跑测试 → diff/readback → 不回归 |
| Research | claim → source → citation → conflict/freshness |
| Workflow | write action → read-after-write → audit trace |
| Browser | DOM + screenshot 双通道验证 |
| Ops/SRE | diagnosis evidence → mitigation → health check |
| Memory | write provenance → retrieval trigger → expiry/audit |

## 最小产出

```yaml
eval_case:
  product_type: coding_agent
  required_depth: D5
  success_criteria:
    - "test passes"
    - "changed file contains expected behavior"
    - "no high-risk command without approval"
  invariants:
    - "tool_success_must_not_equal_effect_verified"
    - "all external text remains data lane"
```

## 三种验收层级

| 层级 | 用途 | 证据强度 |
|---|---|---|
| checklist | 架构 review | 低，但成本最低 |
| fixture / synthetic trace | 验证设计不变量 | 中，适合原型 |
| real candidate trace | 验证真实 Agent 行为 | 高，但成本更高 |

## 不苛刻的证据策略

没有生产实战也可以先做：

```text
conceptual rule → fixture → synthetic trace → prototype trace → production feedback
```

不要等生产验证才开始沉淀知识；但也不要把 synthetic trace 说成真实能力证明。

## 下一步

1. `review-checklist.md`
2. `../evaluation/eval-framework.md`
3. `../evaluation/fixtures/README.md`
