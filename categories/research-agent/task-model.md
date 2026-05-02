# Research Agent Task Model

> **Evidence Status** — speculative. research workflow、citation-backed systems、`evaluation/research-agent-evals.md`、相关 frontier 文档。

## 任务类型

| 类型 | 用户输入示例 | 默认深度 | 默认自治 | 成功定义 |
|---|---|---|---|---|
| Fact Check | “这个说法可靠吗？” | D3-D4 | L3-L4 | 核心 claim 有 evidence，冲突/不足被明示 |
| Comparative Brief | “比较这几家公司的产品和策略” | D4 | L3-L4 | 维度齐全、来源可回查、时间窗清楚 |
| Literature / Source Review | “梳理这个方向的主要观点” | D4-D5 | L3 | 主题分组、关键来源、争议点与空白清楚 |
| Due Diligence | “给我一个风险导向的背景调研” | D4-D5 | L3 | 高风险 claim 多源支持或明确 unresolved |
| Ongoing Briefing | “持续跟踪这个主题” | D3-D4 | L3-L4 | 新旧来源分离、过期信息不静默复用 |

## TaskEnvelope

```yaml
task_envelope:
  task_type: fact_check | comparative_brief | literature_review | due_diligence | ongoing_briefing
  research_question: string
  scope:
    time_window: string|null
    geography: string|null
    entity_scope: []
  success_criteria:
    - key claims have citation chain
    - major conflicts preserved
  constraints:
    - no fabricated citations
    - label uncertainty explicitly
  budget:
    max_queries: integer|null
    max_sources: integer|null
    max_report_sections: integer|null
  output_contract:
    sections: []
    citation_style: inline | footnote | appendix
```

## 任务分解原则

### 1. 先定义问题树，再定义搜索词树

不要直接把用户原句扔给搜索器。Research Agent 应先补出：

- 关键定义；
- 子问题；
- 时间窗；
- 哪些是事实判断，哪些是价值判断；
- 哪些结论需要 first-party 或高 authority 来源；

### 2. 优先覆盖关键维度，而不是堆来源数量

Research 质量更多取决于：

```text
是否漏掉关键角度 / 关键异议 / 关键时间变化
```

而不只是收集了多少篇材料。

### 3. 报告可部分完成

当关键结论还不能验证时，允许交付：

- 已支持部分；
- 冲突部分；
- 空白部分；
- 建议下一步搜索；

而不是硬凑一个完整结论。

## 成功维度

| 维度 | 问题 | 证据 |
|---|---|---|
| Coverage | 关键问题树是否被覆盖 | query plan、source map |
| Citation Integrity | claim 是否有 citation chain | claim → evidence → raw ref |
| Conflict Honesty | 冲突是否保留 | conflict record、output wording |
| Freshness | 时间敏感信息是否刷新或标注 | source freshness、refresh trace |
| Authority | 关键 claim 是否有足够 authority | source type、cross-source support |
| Synthesis Quality | 报告是否结构化、非拼贴 | section coherence + evidence mapping |

## 失败分类

| 失败 | 表现 | 恢复策略 |
|---|---|---|
| Orphan Claim | 结论没有证据链 | 禁止进入 final section |
| Citation Drift | 引用存在，但不支撑该句 | 重绑 claim / evidence |
| Freshness Blindness | 过期资料继续使用 | refresh query / relabel stale |
| Single-Source Collapse | 用一篇材料代表全局 | 扩展 source coverage |
| Conflict Flattening | 冲突被写平 | restore conflict record |
| Search Thrash | 查询很多但无新信息 | stop or reframe question tree |
| Over-summary | raw material 过早被压缩 | replay raw refs |

## 最终交付契约

```text
1. 结论：按主题分组，而不是按来源堆砌
2. 引用：关键 claim 内联或邻近引用
3. 冲突与不足：不隐藏
4. 时间与范围：明确写出
5. 后续建议：说明下一步怎么补证据
```
