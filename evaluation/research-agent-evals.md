# Research Agent Evaluations

> **Evidence Status** — synthesized. citation-backed research workflow、freshness / conflict / coverage 需求与本仓库 fixture / runner 抽象。

## 评估目标

Research Agent 的主要风险不是“文风不好”，而是：

- claim 没有真实支撑；
- citation 存在但错配；
- 最新性要求被忽略；
- 冲突被静默抹平；
- 找不到时不肯承认；

## 核心指标

| 指标 | 解释 |
|---|---|
| Citation Integrity | 引用是否真的支撑相邻 claim |
| Claim Support Rate | 高价值 claim 中，被 evidence 支撑的比例 |
| Conflict Preservation Rate | 关键冲突是否被保留 |
| Freshness Compliance | 时间敏感题目是否 refresh 或降级 |
| Source Diversity | 是否避免单一来源坍缩 |
| Authority Matching | 关键 claim 是否依赖足够强来源 |
| Honest Partial Delivery | 证据不足时是否诚实 |

## case 设计模板

```yaml
case_id: research_claim_citation_001
product_type: research_agent
required_depth: D4
input_event:
  task: "给出带引用的结论"
allowed_tools:
  - web_search
  - open_url
  - read_pdf
success_criteria:
  - key claim has citation chain
  - final answer marks uncertainty explicitly
metrics:
  - citation_integrity
  - conflict_honesty
  - freshness_compliance
```

## 推荐 case 簇

| case 簇 | 重点 |
|---|---|
| citation | claim/evidence/raw ref 绑定 |
| conflict | preserve-first 而不是 smooth-first |
| freshness | latest/current 任务必须 refresh |
| sparse evidence | honest partial deliver |
| authority mismatch | 低 authority 来源不能支撑高风险断言 |
| multi-section report | coverage + structure |

## 与其他评估文档的关系

- `eval-framework.md`：总框架
- `cost-evals.md`：研究深度与成本曲线
- `fixtures/`：最小化可执行样例
