# Caching Strategy

> **Evidence Status** — synthesized. 表示构建、RAG、工具读取、world state 刷新的常见成本约束。

## 1. 可缓存对象

| 对象 | 可缓存性 | TTL 原则 |
|---|---|---|
| OCR/ASR result | 高 | raw hash 不变即可复用 |
| Embedding | 高 | parser/model change 时失效 |
| Static docs | 高 | content hash 变更失效 |
| API read result | 中 | 按业务 freshness ttl |
| World State | 中/低 | 写前必须按 stale_policy 刷新 |
| Tool write result | 低 | 不缓存为事实，写 effect record |
| Verification result | 中 | 依赖 evidence 和 config fingerprint |

## 2. 缓存记录

```yaml
cache_record:
  key: string
  source_refs: []
  created_from: parser_or_tool
  content_hash: string
  ttl: duration
  invalidation_triggers: []
  trust_lane: string
```

## 3. 缓存风险

- Stale Cache：外部状态变化但缓存仍被用来写。
- Trust Confusion：不可信网页内容缓存后被当可信数据。
- Hidden Drift：parser 改了但旧缓存没有失效。
