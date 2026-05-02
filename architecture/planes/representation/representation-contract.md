# Representation Contract

> **Evidence Status** — synthesized. tool observations、RAG、memory provenance、OCR/ASR 等常见输入处理链的通用需求。

- Intended use: 作为新 Agent 项目设计输入/观察 schema 的参考模板。

## 目标

Representation Contract 规定：

1. 系统保存哪些原始引用；
2. 哪些转换会发生；
3. 转换的损失如何记录；
4. 表示如何被下游 Context / Memory / Verification 使用。

## 最小契约

```yaml
representation_record:
  representation_id: string
  entity_ref: string | null
  kind: raw_observation | normalized_observation | summary | claim | inference
  modality: text | image | audio | dom | row | event | log
  raw_refs:
    - uri: string
      byte_range: string | null
      page: int | null
      timestamp: datetime | null
  parser:
    name: string
    parser_revision: string
  transform_chain:
    - step: string
      lossy: boolean
      input_refs: []
      output_ref: string | null
      notes: string | null
  quality:
    confidence: float | null
    truncation: boolean
    missing_fields: []
    parse_errors: []
  freshness:
    observed_at: datetime
    expires_at: datetime | null
  trust:
    source_authority: first_party | third_party | unknown
    trust_tier: instruction | trusted_data | untrusted_data | summary | memory | inference
  provenance:
    produced_by: tool_id | parser_id | human
    source_ids: []
  replayable: boolean
```

## 设计建议

### raw refs
- 能留 URI 就不要只留内容片段。
- 大文件保留偏移量、页码、行号。
- 音频/视频保留时间区间。

### transform chain
- 每一步都记录输入和输出。
- 摘要、压缩、rerank 默认视为有损。
- parser 修订变化应被视为可能改变结果的事件。

### quality
- 低置信表示不应直接进入高风险动作。
- 缺字段和 parse_error 要显式暴露给控制层。

### freshness
- world state 相关表示必须有 observed_at。
- 对可能快速变化的系统状态，必须有 ttl。

## 何时必须升级为严格契约

以下场景建议强制启用完整 Representation Contract：

- 浏览器 / 桌面自动化
- 语音控制
- OCR / 文档解析
- 企业工作流写操作
- 安全 / 运维 / 金融 / 医疗等高风险场景
