# Multimodal Grounding

> **Evidence Status** — synthesized. screenshot / DOM / OCR / audio / video 等多模态 Agent 的共同表示需求。

## 定义

Multimodal Grounding 讨论的不是“模型能看图吗”，而是：

```text
多个模态的观察，如何被绑定到同一个世界对象、同一个动作目标和同一个验证闭环上。
```

## Observation Bundle

```yaml
observation_bundle:
  bundle_id: string
  observed_at: datetime
  subject_ref: string|null
  modalities:
    - modality: screenshot
      raw_ref: string
    - modality: dom
      raw_ref: string
    - modality: ocr
      raw_ref: string
    - modality: audio
      raw_ref: string
  alignment:
    viewport: {}
    element_candidates: []
    sync_token: string|null
  trust_notes: []
```

## 为什么单模态不够

| 单模态 | 典型盲点 |
|---|---|
| Screenshot | 缺结构、难知可编辑状态 |
| DOM | 看不见真实呈现、遮挡层、视觉焦点 |
| OCR | 识别错误、坐标偏移 |
| Audio transcript | 丢失时间同步和上下文 |
| Video summary | 容易把过程压成有损摘要 |

## 设计规则

- raw ref 分模态保存，不要只保留融合后的摘要。
- 每个模态都记录 transform chain 和 confidence。
- 关键动作前，显式确认当前 observation bundle 仍然 fresh。
- 当多个模态冲突时，不自动挑一个“看起来更合理”的；应重采样或降级结论。

## 与其他模块的关系

| 模块 | 关系 |
|---|---|
| Effects | 决定 GUI / physical actions 如何验证 |
| Security | 决定 visual prompt injection、phishing、secret exposure 如何识别 |
| Interaction | 决定向用户展示哪些视觉证据 |
| Cost | 截图频率、OCR 频率、多模态缓存都会影响成本 |

## 相关文档

- `overview.md`
- `../../../../design-space/patterns/dual-channel-gui-verification.md`
- `../../../../design-space/frontier/multimodal-and-computer-use.md`
