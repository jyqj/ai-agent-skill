# Representation-First Design

> **Evidence Status** — synthesized. 从多品类在输入采样、结构化和回读验证上的共同约束中归纳。

## 核心命题

Agent 直接处理的不是现实本身，而是现实进入系统后的表示。

这意味着：
- 看不到的对象，Agent 不能处理；
- 没保留的原始证据，Agent 不能回查；
- 没建模的新鲜度、置信度、来源可信度，Agent 无法可靠区分“现实如此”与“表示如此”。

## 设计要求

### 1. 原始引用优先
- 保留 `raw_ref`，而不是只保留摘要。
- 大文件保留页码、行号、时间区间、偏移量。

### 2. 转换链可见
- 记录 OCR / ASR / HTML 抽取 / rerank / summarize / chunk。
- 标记哪些步骤有损。

### 3. 语义分层
- Raw Observation ≠ Summary ≠ Claim ≠ Inference ≠ Memory Projection。
- 不同语义层的信息不能混着驱动高风险动作。

### 4. 新鲜度与置信度是系统字段
- World state 相关观察必须带 `observed_at`。
- OCR / ASR / vision / parser 结果应带 `confidence`。
- 快速变化对象要有 TTL 和 refresh policy。

### 5. 表示必须能接入效果验证
- 表示层不是只为“输入理解”服务，也要支撑 read-after-write、claim verification、incident replay。

## 一个最小设计检查

```text
[ ] 是否保留 raw refs？
[ ] 是否记录 transform chain？
[ ] 是否区分原始观察、摘要、推断、记忆、断言？
[ ] 是否记录 freshness / confidence / authority？
[ ] 关键结论是否可回查原始材料？
```

## 关联文档

- `../../concepts/representation-and-effects.md`
- `../../architecture/planes/representation/overview.md`
- `../../architecture/planes/world-state/overview.md`
- `../../architecture/planes/effects/overview.md`
- `../../architecture/planes/security/overview.md`
