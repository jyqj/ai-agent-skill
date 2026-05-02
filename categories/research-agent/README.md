# Research Agent Architecture

> **Evidence Status** — synthesized. `projects/research-agents/openai-deep-research/`、citation-backed report systems、通用 research workflow、`evaluation/research-agent-evals.md` 与相关 architecture planes。

## Core Job

Research Agent 的工作不是“搜几个链接”，而是：

```text
把问题变成可验证的问题树
→ 检索和读取多源材料
→ 提取 claim / evidence / conflict
→ 形成带 citation 的结论
→ 明确保留不确定性和 freshness 边界
```

## 用户模型

| 用户 | 心智模型 | 信任建立方式 | 默认交互 |
|---|---|---|---|
| 知识工作者 | 研究助理 | 结论可回查、引用准确、知道哪里不确定 | 默认输出摘要 + 可展开证据 |
| 管理者/分析师 | briefing 生成器 | 重点结论清楚、风险与来源透明 | 默认少打扰，关键歧义时澄清 |
| 咨询/研究团队 | 调研 co-pilot | question tree、citation chain、可复用结构 | 允许分阶段交付 |
| 合规/策略团队 | 证据收集器 | freshness、authority、conflict 明确 | 强调证据与结论分离 |

## 任务模型

详见 `task-model.md`。核心任务包括：

| 任务 | 默认深度 | 完成定义 |
|---|---|---|
| Fact Check | D3-D4 | 关键 claim 有证据绑定，冲突被说明 |
| Literature / Source Review | D4-D5 | 多源综述 + 主题分组 + citation chain |
| Market / Competitive Scan | D4 | 事实、时间窗口、来源可信度被标注 |
| Due Diligence Brief | D4-D5 | 高风险结论有多源支持或明确 unresolved |
| Ongoing Briefing | D3-D4 | 新旧来源区分、过期信息不被静默复用 |

## 表示模型

详见 `representation.md`。Research Agent 的关键对象不是“文档片段”而是：

```text
SourceRecord、EvidenceSnippet、ClaimRecord、ConflictRecord、CitationRecord、SynthesisState
```

设计原则：

- raw ref 永不丢；
- 任何 summary 都标记为 lossy；
- final claim 没有 citation chain 就不能升格为 supported conclusion；
- freshness、authority、conflict 必须和 claim 一起走，而不是最后补注脚。

## 行动模型

详见 `action-model.md`。

| 动作 | 作用 | 默认风险 |
|---|---|---|
| Search | 扩展候选来源 | safe |
| Fetch / Read | 获取 raw material | safe |
| Extract | 形成 evidence / claim 候选 | check |
| Verify / Refresh | 解决冲突、补 freshness | check |
| Synthesize | 形成报告 | check |
| Publish / Send | 对外扩散结果 | approval in high-risk contexts |

## 闭环模型

详见 `closed-loop.md`。

```text
Observe question
  → Represent sources / claims / conflicts
  → Decide next query / read / verification step
  → Act through search / fetch / extract / refresh / synthesize
  → Verify citations / conflict handling / freshness
  → Update report state or deliver partial result
```

Stop gate：

```text
[ ] 核心结论均可回到 citation chain
[ ] 关键冲突未被静默抹平
[ ] freshness 风险已说明
[ ] source authority 和 limitations 已表达
[ ] 未验证部分被明确标注
```

## 品类特有设计决策

详见 `design-decisions.md`。

| 决策 | 默认建议 |
|---|---|
| 检索策略 | breadth-first 建图，再 depth-first 补关键 claim |
| 上下文策略 | 以 claim / evidence 为中心装配，不直接把整堆网页塞进上下文 |
| 表示策略 | source / claim / citation 分对象，不让 summary 覆盖 raw ref |
| 冲突策略 | preserve-first，resolve-second |
| 成本策略 | 对 search fanout、read depth、refresh 次数设置预算 |
| 交互策略 | 默认少打扰，但对任务范围、时间窗、关键定义歧义做最小澄清 |

## 模块配置配方

| 模块 | Research Agent 特化配置 | 通用参考 |
|---|---|---|
| Representation | SourceRecord、ClaimRecord、CitationRecord、ConflictRecord | `../../architecture/planes/representation/overview.md` |
| Context | claim / evidence centered context pack + progressive disclosure | `../../architecture/planes/context/overview.md` |
| Tools | search、fetch、read_pdf、extract、citation binding | `../../architecture/planes/tools/overview.md` |
| Control | citation gate、freshness gate、conflict preservation | `../../architecture/planes/control/overview.md` |
| Observability | evidence trace、search fanout、cost per section、source coverage | `../../architecture/planes/observability/overview.md` |
| Cost | query budget、read budget、refresh budget、report depth choice | `../../architecture/planes/cost/overview.md` |
| Interaction | clarification、progress、partial deliver、confidence disclosure | `../../architecture/planes/interaction/overview.md` |

## 参考实现映射

详见 `implementation-map.md`。

| 参考实现 | 重点学习 |
|---|---|
| OpenAI Deep Research | report-first artifact、citation-rich delivery、长时 research orchestration |
| Hermes Agent | 冻结快照、延迟压缩、raw ref 分离 |
| Generic Agent | self-evolution、tool / memory / loop scaffolding |

## 阅读路径

```text
README.md
  → task-model.md
  → representation.md
  → action-model.md
  → closed-loop.md
  → design-decisions.md
  → eval-cases.md
  → implementation-map.md
```

- 主观性任务的验证扩展：`../../concepts/beyond-verification.md`
