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

## 最新评估数据（2026 更新）

> 来源：Deep Research Agents 综述 (arXiv 2506.18096)、DRACO Benchmark (Perplexity)、GAIA Benchmark

### GAIA 基准

GAIA 是专家级多轮推理的核心基准。当前最佳表现：

| 系统 | GAIA 分数 | 备注 |
|---|---|---|
| Claude Sonnet 4.5 | 74.6% | 当前公开最高 |
| 人类基线 | ~77% | 仍有差距 |

其他关键基准：HotpotQA（2 跳推理，113k samples）、2WikiMultihopQA（2+ 跳推理，192k samples）、DeepResearch Bench（报告保真度 + 引用准确度）、DRACO（Perplexity 跨域深度研究基准）。

### 引用验证作为核心评估维度

传统 eval 偏重答案正确性，2026 年的共识是引用验证应提升为一等评估维度：

| 评估层级 | 检查内容 |
|---|---|
| 引用存在性 | 关键 claim 是否绑定到至少一个 source |
| 引用支撑性 | source 内容是否真的支撑对应 claim（而非仅主题相关） |
| 引用归因正确性 | 引用是否附加到正确的 claim 上（防止"正确引用，错误主张"） |
| 引用新鲜度 | 时间敏感 claim 的 source 是否足够新 |

Perplexity 平均 21.87 条引用/响应（所有主要平台最高），但数量不等于质量。"正确引用附加到不被支持的主张上"的细微错误仍是行业共性问题。

### 冲突检测评估方法

Research Agent 在面对矛盾来源时的行为是关键质量指标：

| Case | 期望行为 | 失败模式 |
|---|---|---|
| 两个高权威来源结论相反 | 保留冲突，标注差异来源 | 静默选择一方，丢弃另一方 |
| 同一来源内部前后矛盾 | 标注内部不一致 | 仅引用支持结论的部分 |
| 旧来源 vs 新来源 | 标注时间差异，偏向新来源但保留旧来源上下文 | 完全忽略旧来源 |

FutureHouse Falcon 的做法值得参考：分析跨数百篇论文的矛盾证据，标识额外实验可以解决冲突之处，将冲突转化为研究方向而非简单压平。
