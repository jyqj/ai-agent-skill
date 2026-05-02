# Research Agent Evaluation Cases

> **Evidence Status** — synthesized. `evaluation/research-agent-evals.md`、`evaluation/eval-framework.md`、`evaluation/fixtures/` 与 citation / freshness / conflict 的品类需求。

## 评估目标

Research Agent 的 eval 不应只看“答案读起来像不像”，而要看：

```text
结论是否有来源？
引用是否真的支撑对应 claim？
冲突是否被保留？
最新性要求是否被满足？
不确定性是否诚实表达？
```

## 核心指标

| 指标 | 含义 |
|---|---|
| Citation Integrity | claim 与 evidence / raw ref 是否一一对应 |
| Conflict Honesty | 关键冲突是否被保留并正确描述 |
| Freshness Compliance | 时间敏感 claim 是否 refresh 或显式降级 |
| Coverage | 问题树关键分支是否被覆盖 |
| Authority Weighting | 高影响 claim 是否依赖更强来源 |
| Synthesis Quality | 结构、去重、非拼贴、层次清晰 |
| Failure Honesty | 找不到时是否诚实，而非幻觉填补 |
| Cost Efficiency | search/read/refresh 的边际收益 |

## Eval Case 类型

| Case | 目标 | 必备断言 |
|---|---|---|
| Claim with citation | 每个关键 claim 都有 citation chain | final trace has citation event |
| Conflicting sources | 保留冲突，不强行合并 | conflict record present |
| Time-sensitive brief | 检查 freshness gate | refresh event or stale label |
| Multi-section report | 看 coverage 与 section coherence | section-level source distribution |
| Sparse evidence | 看是否 honest partial deliver | unresolved explicitly marked |
| Source authority mismatch | 防止低 authority 支撑高价值 claim | authority notes present |

## 现有 fixture 对应

- `../../evaluation/fixtures/research_claim_citation_001.yaml`
- `../../evaluation/fixtures/research_conflict_resolution_001.yaml`
- `../../evaluation/fixtures/research_freshness_refresh_001.yaml`

## Shadow Mode

Research Agent 非常适合 shadow mode：

```text
真实研究问题
→ Agent 先输出 report draft + citations，但不直接给最终用户
→ 人类 reviewer 标注 citation drift / missed source / unresolved conflict
→ 转回 fixture 和 regression suite
```
