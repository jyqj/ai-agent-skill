# Foundations -- 哲学与认知基础

> **Evidence Status** — theoretical

本目录回答的问题是**"为什么 Agent 架构必须是这样"**，而不是"怎么搭"。

`concepts/` 层建立了 Agent 的本体论（什么是 Agent、什么是表示、什么是效果）；`architecture/` 层给出了工程模块和数据模型。但两层之间缺少一个中间地带：为什么 Harness 必然存在？为什么 ORDA-VU 比 ReAct 多出 Represent 和 Verify？为什么 Agent 的"目标"需要被工程化注入而不能依赖模型自发产生？

这些问题的答案不在工程经验里，而在认知科学、哲学和决策理论中。本目录把六个关键理论锚点整理成面向 Agent 架构师的实用指南，让知识库的"哲学参考"定位有据可依。

## 导航

| 文件 | 核心问题 |
|---|---|
| `bounded-rationality.md` | 为什么 Agent 不能单独完成闭环？为什么 Harness 必然存在？ |
| `intentional-stance.md` | "Agent 有目标"是什么意思？目标从哪里来？ |
| `bdi-and-active-inference.md` | ORDA-VU 的认识论根基是什么？它比 ReAct 多了什么、为什么？ |
| `metacognition.md` | Agent 如何知道自己不知道什么？如何动态调整策略？ |
| `value-and-alignment.md` | 安全和对齐有什么区别？价值冲突怎么处理？ |
| `embodiment-and-situation.md` | Agent 的"身体"是什么？为什么工具不是附件而是认知能力的延伸？ |

## 阅读建议

- 如果你在设计一个新 Agent，从 `bounded-rationality.md` 开始，理解为什么"让模型自己搞定"永远不够。
- 如果你在调试 Agent 的目标漂移或拟人化问题，看 `intentional-stance.md`。
- 如果你想理解 ORDA-VU 为什么这样设计，看 `bdi-and-active-inference.md`。
- 如果你在做 paradigm-routing 或置信度校准，看 `metacognition.md`。
- 如果你在做 Companion 或 Creative Agent，`value-and-alignment.md` 比效果验证更重要。
- 如果你在做多模态或具身 Agent，`embodiment-and-situation.md` 提供理论基础。

## 与知识库其他部分的关系

```text
foundations/（为什么必须这样）
  ↓ 理论支撑
concepts/（Agent 是什么、表示与效果、认识论）
  ↓ 概念基础
architecture/（怎么搭、模块怎么分）
  ↓ 工程实现
paradigms/（用什么范式、怎么选）
```
