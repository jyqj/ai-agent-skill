# 构建 Research Agent：最短路径

> **Evidence Status** — synthesized. 基于 `categories/research-agent/`、citation / conflict / freshness 评估文档压缩而来；这是操作清单，不是生产实现。

## 定位

Research Agent 的交付物不是“看起来完整的报告”，而是：

```text
可回查 claim + evidence + citation + conflict + freshness 边界
```

完整品类设计见 `../categories/research-agent/README.md`。

## 1. 先定问题边界

```yaml
agent_type: research-agent
primary_deliverable: "cited research brief"
question: "..."
scope:
  time_window: null
  geography: null
  entities: []
source_policy:
  preferred_sources: []
  excluded_sources: []
  freshness_required: true
success_criteria:
  - key claims have citations
  - conflicting evidence is preserved
  - uncertainty is explicit
  - stale sources are refreshed or labeled
```

先读：`../toolkit/choose-agent-type.md`、`../categories/research-agent/task-model.md`。

## 2. 选择最小运行时

| 模块 | Research Agent 最小要求 |
|---|---|
| Representation | SourceRecord、ClaimRecord、EvidenceSnippet、CitationRecord、ConflictRecord |
| Context | 当前问题树、候选 claim、来源摘要、raw refs |
| Tools | search / fetch / extract / cite / freshness check |
| Control | source allow/deny、引用完整性、发布前 review |
| Effects | 报告 claims 可回查，不编造 citation |
| Recovery | source unavailable、conflict、low confidence、freshness expired |
| Observability | query trace、source refs、claim-evidence map |

## 3. Runtime loop

```text
intake question
  → decompose into subquestions
  → search / fetch sources
  → extract claims + evidence snippets
  → preserve conflicts
  → synthesize with citations
  → verify citation chain and freshness
  → final: answer + uncertainty + gaps
```

核心边界：摘要不是证据；引用存在不等于 claim 被支持；旧来源不等于当前事实。

## 4. Claim discipline

```text
[ ] 每个关键 claim 是否绑定 evidence refs？
[ ] evidence 是否能回到 raw source？
[ ] 冲突来源是否被保留，而不是被平均掉？
[ ] freshness 是否符合用户问题？
[ ] 推断是否与事实分开标注？
[ ] 低置信结论是否有 uncertainty format？
```

先读：`../design-space/patterns/citation-chain.md`、`../design-space/patterns/conflict-preserving-synthesis.md`。

## 5. Eval

Research Agent eval 至少检查：

```text
[ ] citation 指向真实来源
[ ] claim 与 evidence 语义一致
[ ] source freshness 被检查或标注
[ ] conflict 没有被隐藏
[ ] 最终答案不超过证据强度
[ ] 无法验证时明确 blocked / uncertain
```

先读：`../evaluation/research-agent-evals.md`、`../evaluation/representation-evals.md`。

## 6. 参考项目对照

| 设计问题 | 先对照 |
|---|---|
| citation loop | `../projects/research-agents/openai-deep-research/citation-loop.md` |
| research product shape | `../projects/research-agents/openai-deep-research/README.md` |
| source comparison | `../projects/research-agents/perplexity-analysis.md` |
| 通用 runtime contract | `../synthesis/local-agent-runtime-practices.md` |

## Stop Gate

```text
[ ] 关键 claim 有 citation chain
[ ] raw source 可回查
[ ] freshness / uncertainty / conflict 已标注
[ ] 没有把模型推断包装成来源事实
[ ] 未覆盖范围和后续建议已说明
```
