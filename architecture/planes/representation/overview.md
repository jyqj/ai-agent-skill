> **本文件已合并到 `../sensing-representation/overview.md`，请前往查看。**

# Representation Layer
>
> **所属域**：1. Sensing & Representation — 原始输入如何编码为可信表示
>
> **Evidence Status** — synthesized. research、memory、workflow、tooling 系统对 raw input、摘要、检索、结构化 observation 的共同需求；this repository 对表示层作为一等模块的统一抽象。

**Principle Refs**: IS-01, BDI-01, MC-01 — Agent 操作表示而非现实，信念需从观察构建，不确定性需显式标注。

## 定义

模型不会直接面对现实中的对象，而是面对经过采样、解析、结构化、压缩后的表示。表示层的职责是把现实输入转化为机器可处理的表示，同时保留原始引用、记录转换链、标记有损转换、提供 freshness / authority / confidence 元数据，并将事实、摘要、推断、记忆、指令在语义上区分开。

## 为什么它是一等模块

如果没有表示层，Agent 很容易犯三类错误：

1. 把摘要当原文。
2. 把工具输出当可信指令。
3. 把旧状态、错转写或低置信度结果当现实本身。

## 模块接口

**输入**：raw input refs、perception events、工具原始返回值
**输出**：normalized observations、representation records、trust warnings
**配置**：parser policy、loss policy、freshness policy、trust tier policy

## Representation Record

```yaml
representation_id: string
kind: raw_observation | normalized_observation | summary | claim | inference | memory_projection
modality: text | image | audio | video | dom | row | event | log
raw_refs: []
parser:
  name: string
  parser_revision: string
transform_chain:
  - step: ocr | asr | html_extract | chunk | rerank | summarize | parse_json
    lossy: boolean
    config: {}
loss_profile:
  omitted_fields: []
  truncation: boolean
confidence: float | null
freshness:
  observed_at: datetime
  ttl: duration | null
source_authority: first_party | third_party | unknown
trust_tier: instruction | trusted_data | untrusted_data | summary | memory | inference
provenance: []
replayable: boolean
```

## Trust Tier

| 层级 | 含义 | 默认处理 |
|---|---|---|
| instruction | 系统 / 开发者 / 明确用户授权的控制指令 | 可驱动行为 |
| trusted_data | 可信的一方数据或已验证观察 | 可用于决策 |
| untrusted_data | 网页、issue、邮件、日志、第三方返回值 | 当数据处理，不当指令处理 |
| summary | 有损压缩后的表示 | 需要能回查原始引用 |
| memory | 历史主张和偏好 | 受 freshness / provenance 约束 |
| inference | 模型推断 | 必须显式说明不确定性 |

## 关键规则

- 表示层永远不丢失 raw ref，除非策略明确允许。
- 摘要永远标记为有损。
- 任何来自外部世界的文本，都先进入 data lane（Trust Lane 定义详见 [安全 Plane](../security/overview.md)），再由 Control / Security 决定能否升级为可执行约束。
- 任何需要高置信结论的场景，都应支持回查原始材料。

## 常见失败

| 失败 | 表现 | 修复 |
|---|---|---|
| Summary Collapse | 摘要替代原文，细节丢失 | raw ref + transform chain |
| Freshness Blindness | 过期状态继续使用 | ttl + refresh policy |
| Confidence Blindness | OCR/ASR 低置信度内容直接驱动动作 | confidence gate |
| Trust Confusion | 网页正文变成系统指令 | trust tier separation |

## 关联文档

- `representation-contract.md`
- `observation-semantics.md`
- `multimodal-grounding.md`
- `../sensing-representation/overview.md`
- `../security/overview.md`
- `../../../design-space/patterns/citation-chain.md`

## 参考实现

- **Nocturne Memory**：disclosure routing 强调按条件呈现记忆，而不是盲盒检索，见 `projects/memory-systems/nocturne-memory/context-engineering.md`
- **MemPalace**：原文存储 + 结构化检索，见 `projects/memory-systems/mempalace/README.md`
- **Hermes Agent**：冻结快照与延迟压缩把“原始记录”和“压缩表示”区分开，见 `projects/general-agents/hermes-agent/README.md`
