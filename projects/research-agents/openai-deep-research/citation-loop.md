# Citation Loop

> **Evidence Status** — synthesized. 基于 citation-backed report systems 的公开描述与本仓库的统一抽象，非源码级分析。

## 观察

研究型系统的核心是结构化的引用链，而非检索量：

```text
section draft
  ← claim set
  ← evidence snippets
  ← source records
```

如果 citation 只在最后渲染，系统很容易出现 citation drift。

## 可复用学习点

| 学习点 | 对本知识库的落点 |
|---|---|
| report 是一等 artifact | `categories/research-agent/README.md` |
| claim/evidence/citation 要一起设计 | `design-space/patterns/citation-chain.md` |
| 长任务要能部分交付 | `categories/research-agent/closed-loop.md` |
| freshness 和 authority 不能脱离 claim | `categories/research-agent/representation.md` |
