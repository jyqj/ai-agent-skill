# Interface Gateway & Perception Adapters
>
> **所属域**：1. Sensing & Representation — 现实如何进入系统
>
> **Evidence Status** — grounded. Hermes 的 multi-platform gateway、Generic Agent 的 frontend adapter、Naga 的多模态入口、workflow / webhook 类系统的统一 envelope 需求；this repository 对入口层与感知层的统一抽象。

**Principle Refs**: IS-01, EM-03 — 接口决定 Agent 感知边界，环境约束可用动作。

## 定义

入口层回答两个问题：

1. **请求从哪里来？**（Chat / CLI / IDE / API / Webhook / Voice / Browser / Sensor）
2. **原始输入如何进入系统？**（文本、截图、音频、DOM、数据库事件、日志、文件）

因此建议把这一层拆成两个子层：

```text
Interface Gateway   ← 产品入口统一：Chat / CLI / IDE / API / Webhook
Perception Adapter  ← 现实采样：OCR / ASR / DOM / Screenshot / Sensor / Log / DB
```

Gateway 负责统一会话和身份；Perception 负责保留原始输入、解析链和质量信息。

## Task Envelope

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

## Perception Event

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

## 设计原则

- 入口层必须保留 **raw refs**，而不是只保留转写或摘要。
- 解析链必须可追溯：ASR / OCR / HTML 提取 / 切块 / 摘要都要可见。
- Gateway 不直接执行高风险动作。
- 同一 Runtime 可以接多个 Gateway；同一 Gateway 可以接多个 Perception Adapter。
- 多模态输入进入后必须尽快转入 Representation 层做规范化和 trust tier 标记。

## 常见失败

| 失败 | 表现 | 修复 |
|---|---|---|
| Raw Input Loss | 只保留摘要，没有原始引用 | raw_ref retention |
| Identity Collapse | webhook / schedule / user 行为混淆 | identity + auth context |
| Modality Blindness | DOM / screenshot / ASR 质量差异不见了 | modality + parser metadata |
| Duplicate Trigger | 同一事件多次执行 | event dedupe + idempotency key |

## 设计模式

| 模式 | 详见 |
|---|---|
| Platform Adapter | `platform-adapter.md` |
| Untrusted Context Boundary | `../../../design-space/patterns/untrusted-context-boundary.md` |

## 参考实现

- **Hermes Agent**：Multi-platform Gateway（CLI / Discord / Telegram / Web），见 `projects/general-agents/hermes-agent/gateway.md`
- **Generic Agent**：Frontend Adapter 模式，见 `projects/general-agents/generic-agent/frontend-adapter.md`
- **NagaAgent**：Chat / Voice / Avatar / MCP 多入口，见 `projects/companion-agents/naga-agent/README.md`
