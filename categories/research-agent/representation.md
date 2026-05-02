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

## 关联模式

- `../../design-space/patterns/citation-chain.md`
- `../../design-space/patterns/conflict-preserving-synthesis.md`
- `../../architecture/planes/representation/multimodal-grounding.md`
