# Multimodal Agents and Computer Use

> **Evidence Status** — theoretical. 基于 vision / screenshot / DOM / OCR / computer-use agent 的最新实践和 benchmark。属于 frontier 方向。

## 为什么它正在成为核心能力

越来越多 Agent 不再只处理文本，而是处理：

```text
screenshot + DOM + OCR + accessibility tree + coordinate action + network state
```

这迫使表示层、效果层和安全层一起升级。

## 关键变化

### 1. 表示层从单通道变为 observation bundle

一个网页或桌面界面，往往需要同时保留：

- screenshot raw ref
- DOM / accessibility tree
- OCR 或视觉抽取
- viewport / scroll state
- 最近动作和目标元素身份

### 2. 动作空间更脆弱

文本世界里调用一个函数通常是离散的；GUI 世界里 click / type / scroll 更容易因为：

- 坐标漂移；
- 渲染延迟；
- 遮挡层；
- 焦点丢失；
- 页面局部刷新；
- 反自动化或安全确认；

而失败。

### 3. 验证需要双通道

详见 `../patterns/dual-channel-gui-verification.md`。GUI 场景默认不应只看单一通道。

## 设计问题

| 问题 | 需要的对象 |
|---|---|
| 当前看到的到底是什么 | multimodal observation bundle |
| 我要点的是不是那个元素 | element identity + viewport alignment |
| 点完是否真的成功 | DOM + screenshot + optional network / URL verification |
| 高风险动作是否需要拦截 | risk classifier + user approval + origin check |

## 对本知识库的影响

- `representation/` 需要专门讨论 multimodal grounding。
- `effects/` 需要 GUI verification 策略。
- `security/` 需要 browser phishing、visual prompt injection、screenshot secret exposure 案例。
- Browser/Desktop Agent 应升级为完整品类样板。
