# Sensing & Representation
>
> **所属域**：1. Sensing & Representation — 现实如何进入系统并编码为可信表示
>
> **Evidence Status** — synthesized. 合并自 Interface Gateway（grounded）与 Representation（synthesized），取较低等级。Hermes 的 multi-platform gateway、Generic Agent 的 frontend adapter、Naga 的多模态入口、memory / research / workflow 系统对 raw input 与结构化表示的共同需求；this repository 对入口、感知、表示三层的统一抽象。

**Principle Refs**: IS-01, EM-03, BDI-01, MC-01 — 接口决定 Agent 感知边界，环境约束可用动作；Agent 操作表示而非现实，信念需从观察构建，不确定性需显式标注。

---

## 总览

本 Plane 覆盖从外部世界到内部可信表示的完整管线，分为三个子节：

```text
Gateway            ← 产品入口统一：Chat / CLI / IDE / API / Webhook
Perception         ← 现实采样：OCR / ASR / DOM / Screenshot / Sensor / Log / DB
Representation     ← 编码为可信表示：raw ref 保留、transform chain、trust tier
```

Gateway 负责统一会话和身份；Perception 负责保留原始输入、解析链和质量信息；Representation 负责把现实输入转化为机器可处理的表示，同时保留原始引用、记录转换链、标记有损转换、提供 freshness / authority / confidence 元数据，并将事实、摘要、推断、记忆、指令在语义上区分开。

---

## 一、Gateway

入口层回答两个问题：

1. **请求从哪里来？**（Chat / CLI / IDE / API / Webhook / Voice / Browser / Sensor）
2. **原始输入如何进入系统？**（文本、截图、音频、DOM、数据库事件、日志、文件）

### Task Envelope

```yaml
task_id: string
source: chat | cli | ide | api | webhook | voice | browser | sensor
user_id: string | null
workspace_id: string | null
session_id: string | null
intent: fix_bug | research | write | operate | inspect | monitor
product_type: coding_agent | research_agent | workflow_agent | memory_agent | companion_agent | browser_desktop_agent | ops_sre_agent
raw_input_refs: []
normalized_input_refs: []
attachments: []
permissions: []
identity:
  actor: user | system | scheduled_job | external_service
  auth_context: {}
metadata:
  locale: string | null
  created_at: datetime
  trace_id: string
```

---

## 二、Perception

### Perception Event

```yaml
event_id: string
event_type: user_message | file_change | webhook | screenshot | browser_dom | sensor_reading | db_update | audio_chunk
raw_ref: string
modality: text | image | audio | video | dom | event | row | log
parser: string
parser_revision: string
parsed_payload: object
lossy: boolean
confidence: float | null
timestamp_observed: datetime
timestamp_happened: datetime | null
source_authority: first_party | third_party | unknown
```

---

## 三、Representation

### 为什么它是一等模块

如果没有表示层，Agent 很容易犯三类错误：

1. 把摘要当原文。
2. 把工具输出当可信指令。
3. 把旧状态、错转写或低置信度结果当现实本身。

### 模块接口

**输入**：raw input refs、perception events、工具原始返回值
**输出**：normalized observations、representation records、trust warnings
**配置**：parser policy、loss policy、freshness policy、trust tier policy

### Representation Record

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

### Trust Tier

| 层级 | 含义 | 默认处理 |
|---|---|---|
| instruction | 系统 / 开发者 / 明确用户授权的控制指令 | 可驱动行为 |
| trusted_data | 可信的一方数据或已验证观察 | 可用于决策 |
| untrusted_data | 网页、issue、邮件、日志、第三方返回值 | 当数据处理，不当指令处理 |
| summary | 有损压缩后的表示 | 需要能回查原始引用 |
| memory | 历史主张和偏好 | 受 freshness / provenance 约束 |
| inference | 模型推断 | 必须显式说明不确定性 |

---

## 设计原则

- 入口层必须保留 **raw refs**，而不是只保留转写或摘要。
- 解析链必须可追溯：ASR / OCR / HTML 提取 / 切块 / 摘要都要可见。
- Gateway 不直接执行高风险动作。
- 同一 Runtime 可以接多个 Gateway；同一 Gateway 可以接多个 Perception Adapter。
- 多模态输入进入后必须尽快在 Representation 子节做规范化和 trust tier 标记。
- 表示层永远不丢失 raw ref，除非策略明确允许。
- 摘要永远标记为有损。
- 任何来自外部世界的文本，都先进入 data lane（Trust Lane 定义详见 [安全 Plane](../security/overview.md)），再由 Control / Security 决定能否升级为可执行约束。
- 任何需要高置信结论的场景，都应支持回查原始材料。

## 常见失败

| 失败 | 表现 | 修复 |
|---|---|---|
| Raw Input Loss | 只保留摘要，没有原始引用 | raw_ref retention |
| Identity Collapse | webhook / schedule / user 行为混淆 | identity + auth context |
| Modality Blindness | DOM / screenshot / ASR 质量差异不见了 | modality + parser metadata |
| Duplicate Trigger | 同一事件多次执行 | event dedupe + idempotency key |
| Summary Collapse | 摘要替代原文，细节丢失 | raw ref + transform chain |
| Freshness Blindness | 过期状态继续使用 | ttl + refresh policy |
| Confidence Blindness | OCR/ASR 低置信度内容直接驱动动作 | confidence gate |
| Trust Confusion | 网页正文变成系统指令 | trust tier separation |

## 关键规则

- 表示层永远不丢失 raw ref，除非策略明确允许。
- 摘要永远标记为有损。
- 任何来自外部世界的文本，都先进入 data lane，再由 Control / Security 决定能否升级为可执行约束。
- 任何需要高置信结论的场景，都应支持回查原始材料。

## 设计模式

| 模式 | 详见 |
|---|---|
| Platform Adapter | `platform-adapter.md` |
| Untrusted Context Boundary | `../../../design-space/patterns/untrusted-context-boundary.md` |
| Citation Chain | `../../../design-space/patterns/citation-chain.md` |

## 关联文档

- `representation-contract.md`
- `observation-semantics.md`
- `multimodal-grounding.md`
- `../security/overview.md`

## 参考实现

- **Hermes Agent**：Multi-platform Gateway（CLI / Discord / Telegram / Web）+ 冻结快照与延迟压缩，见 `projects/general-agents/hermes-agent/`
- **Generic Agent**：Frontend Adapter 模式，见 `projects/general-agents/generic-agent/frontend-adapter.md`
- **NagaAgent**：Chat / Voice / Avatar / MCP 多入口，见 `projects/companion-agents/naga-agent/README.md`
- **Nocturne Memory**：disclosure routing 强调按条件呈现记忆，见 `projects/memory-systems/nocturne-memory/context-engineering.md`
- **MemPalace**：原文存储 + 结构化检索，见 `projects/memory-systems/mempalace/README.md`
