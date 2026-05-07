# Citation Chain

> **Evidence Status** — synthesized. 源自 research/reporting 系统、citation-backed synthesis 和可追溯交付的共同需求，多个项目中反复出现。

很多 Research Agent 把"来源很多"误当成"引用充分"。真正的问题不是来源数量，而是：最终结论中的每个断言（Claim），是否都能回溯到具体的证据片段（Evidence Snippet）和原始引用（Raw Reference）？

没有引用链（Citation Chain）时，常见的失败模式包括：报告末尾只有参考列表但没有断言级绑定；摘要段落看似可信但无法定位依据；引用指向整个页面却不知道支撑的是哪句话；交叉验证后原始冲突被洗平，无法回查。

## 核心结构

引用链把最终报告中的每个断言显式绑定到一条可重放的链路：

```text
ClaimRecord → EvidenceSnippet → SourceRecord / raw ref → transform chain → final citation token
```

最小数据对象如下：

```yaml
claim_id: string
claim_text: string
claim_status: supported | conflicted | weakly_supported | stale | unresolved
supports:
  - evidence_id: string
    raw_ref: string
    span: string
    freshness: datetime|null
    authority: first_party | third_party | unknown
citations:
  - citation_id: string
    render_text: string
```

`claim_status` 是关键字段——它不只是"有没有引用"，而是表达引用的支撑强度。`conflicted` 和 `weakly_supported` 状态迫使 Agent 诚实面对证据不足的情况，而不是用流畅的文字掩盖。

## 适用场景

- **Research Agent**：断言需要可追溯来源
- **合规/审计报告**：需要事后回查依据
- **企业知识问答**：避免把 RAG 摘要当事实
- **Browser/Desktop 调研**：截图和 DOM 需要绑定到具体断言

## 反模式

只有结尾 bibliography，没有断言级 evidence 绑定。这是最常见的伪引用——看起来有来源，实际上无法验证任何具体结论。

## 配套模式

- `conflict-preserving-synthesis.md`
- `../../categories/research-agent/representation.md`
- `../../evaluation/research-agent-evals.md`
