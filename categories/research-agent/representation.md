# Research Agent Representation Model

> **Evidence Status** — synthesized. 表示层通用抽象、research/report 系统的 citation 需求、`projects/research-agents/openai-deep-research/`。

## 关键表示对象

| 对象 | 含义 | Freshness | Trust |
|---|---|---|---|
| SourceRecord | 一个原始来源及其 metadata | 视来源而定 | first-party / third-party / unknown |
| EvidenceSnippet | 来源中的具体支撑片段 | 跟随 source | derived but replayable |
| ClaimRecord | 研究中形成的可验证主张 | 需要显式状态 | derived |
| CitationRecord | 用于最终交付的引用绑定 | 跟随 claim / source | derived |
| ConflictRecord | 互相冲突的 claim 组 | 动态 | derived |
| SynthesisState | 报告当前聚合状态 | 动态 | internal state |

## SourceRecord

```yaml
source_id: string
kind: webpage | paper | pdf | filing | transcript | dataset | note
raw_ref: string
source_title: string|null
authority: first_party | third_party | unknown
published_at: datetime|null
retrieved_at: datetime
freshness_ttl: duration|null
transform_chain: []
lossy: boolean
```

## ClaimRecord

```yaml
claim_id: string
claim_text: string
subject: string|null
claim_type: fact | estimate | interpretation | forecast
status: supported | weakly_supported | conflicted | stale | unresolved
supports: []
conflicts_with: []
last_checked_at: datetime|null
```

## 关键规则

### 1. No Orphan Claim

任何进入 final synthesis 的 claim，必须至少绑定到一个 `EvidenceSnippet`，并能回到 `SourceRecord.raw_ref`。

### 2. Summary is Lossy by Default

总结、抽取、重写都默认是 lossy representation。若需要高置信判断，必须支持 raw ref replay。

### 3. Freshness 跟着 claim 走

Research Agent 不能只给 source 打时间戳，而让结论看起来 timeless。对于时间敏感主题，claim 状态应体现：

- freshly supported
- stale but historically accurate
- unresolved due to freshness risk

### 4. Conflict 不是错误，是对象

冲突的来源、时间窗、定义域不同，都应成为 `ConflictRecord`，而不是临时备注。

## ContextPack 组装策略

Research Agent 不应把整堆网页/论文全文塞进模型上下文。更合理的分层是：

```text
1. 当前子问题和输出目标
2. 已有 claim / conflict map
3. 与当前子问题强相关的 evidence snippets
4. 需要回放的 raw refs
5. 压缩历史和预算状态
```

## Trust Lane

| 来源 | 默认 lane |
|---|---|
| 用户研究问题 | user instruction |
| 系统研究 policy | system instruction |
| 网页/论文/PDF 内容 | untrusted_data 或 third-party data |
| 已验证 first-party 数据 | trusted_data |
| 模型总结和推断 | inference |
| 历史研究记忆 | memory |

## 多源冲突处理（2026 更新）

> 来源：Deep Research Agents 综述 (arXiv 2506.18096)、FutureHouse Falcon、Persona-Grounded Safety Evaluation

### Angel-Devil 对抗辩论模式

Profile-Then-Plan 范式中引入 Angel-Devil 对抗辩论机制：两个对立角色分别为和反对某一主张进行论证，通过结构化对抗缓解冷启动幻觉并解决证据冲突。深度评审系统进一步扩展为阶段性流程：分析主张/证据 → 辩论方法论合理性 → 综合论证。

### 冲突保留 vs 压平的权衡

**当前状态**：冲突解决是欠发展领域。多数系统倾向于"压平"冲突（让 LLM 选择一个结论），而非保留冲突作为一等对象。

推荐策略：

| 场景 | 处理方式 |
|---|---|
| 来源权威性明确不对等 | 标注权威差异，偏向高权威来源 |
| 时间窗不同导致冲突 | 保留两者，标注时间上下文 |
| 方法论差异导致冲突 | 保留为 ConflictRecord，说明方法论差异 |
| 无法判定 | 显式保留冲突，不强行合并 |

FutureHouse Falcon 可分析跨数百篇论文的矛盾证据，并标识额外实验可以解决冲突之处。这代表了从"压平冲突"到"利用冲突驱动下一步研究"的范式转变。

### 引用验证仍是开放挑战

引用完整性的细微错误持续存在：正确引用被附加到不被支持的主张上、来源被正确检索但归因到错误 claim。当前缺乏端到端的形式化引用验证协议，多数系统仍依赖 LLM 推理而非结构化校验。Perplexity 相比 Google 幻觉率低 10%（平均 21.87 条引用/响应），但引用质量而非数量才是核心挑战。

## 关联模式

- `../../design-space/patterns/citation-chain.md`
- `../../design-space/patterns/conflict-preserving-synthesis.md`
- `../../architecture/planes/representation/multimodal-grounding.md`
