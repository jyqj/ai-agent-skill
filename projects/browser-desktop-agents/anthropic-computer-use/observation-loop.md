# Observation Loop

> **Evidence Status** — synthesized. 基于 computer-use 系统公开描述与本知识库的表示/效果抽象，非源码级分析。

## 观察

computer-use 系统天然遵循这样的回路：

```text
see current screen
→ infer target element and safe action
→ act
→ re-observe
→ decide whether the intended effect actually happened
```

## 可复用学习点

| 学习点 | 对本知识库的落点 |
|---|---|
| screenshot 不是附属物，是主要 raw ref | `architecture/planes/representation/multimodal-grounding.md` |
| DOM / screenshot 双通道验证 | `design-space/patterns/dual-channel-gui-verification.md` |
| 高风险 GUI 动作要有 approval 和 origin gate | `architecture/planes/security/red-team-cases.md` |
| browser/desktop agent 应把动作验证单列 | `architecture/planes/effects/gui-verification.md` |
