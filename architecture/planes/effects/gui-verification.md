# GUI Verification Strategies

> **Evidence Status** — synthesized. browser / desktop / computer-use 场景中“动作发出后还要重新观察”的共同需求。

## 问题

GUI 世界里最危险的假设是：

```text
action emitted = task completed
```

点击、输入、滚动、拖拽之后，系统需要重新判断：

- 目标元素是不是正确对象；
- 页面是不是进入目标状态；
- 高风险按钮是不是被误触；
- DOM 与视觉结果是否一致；

## 验证层次

| 层次 | 方法 | 适用 |
|---|---|---|
| Structural | DOM / accessibility / URL / network | 表单、导航、状态更新 |
| Visual | screenshot diff / OCR / viewport landmarks | 渲染确认、toast、disabled state |
| Semantic | LLM/vision interpretation of current state | 复杂 UI、布局变化 |
| Human | 显式确认 | 高风险或低可验证动作 |

## 默认策略

```text
普通动作：至少一结构通道 + 一视觉通道
高风险动作：动作前确认 + 动作后双通道验证 + 必要时 human confirm
```

## EffectRecord 扩展字段

```yaml
gui_verification:
  target_identity: string|null
  pre_action_view_token: string|null
  post_action_view_token: string|null
  structural_evidence: []
  visual_evidence: []
  semantic_assessment: string|null
```

## 典型失败

| 失败 | 表现 | 修复 |
|---|---|---|
| False Click Success | click 返回成功，但界面没变 | re-observe + timeout-aware verify |
| Wrong Element Same Text | 点到同名按钮或遮挡层 | target identity check |
| Stale Screenshot | 验证基于旧图 | fresh view token |
| Hidden Submit | 回车或按钮导致意外提交 | approval + post-action origin/URL check |

## 关联文档

- `overview.md`
- `../../../../design-space/patterns/dual-channel-gui-verification.md`
- `../../../../evaluation/fixtures/browser_gui_grounding_001.yaml`
