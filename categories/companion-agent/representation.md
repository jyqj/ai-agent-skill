# Companion Agent Representation Model

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

## 核心对象

| 对象 | 含义 | Freshness | Trust |
|---|---|---|---|
| PersonaDefinition | 特质/风格/知识/禁区 | 不可变(核心) | config |
| UserProfile | 姓名/偏好/日期/关系 | 每次更新 | medium |
| EpisodicMemory | 关键对话+情感标记 | append+压缩 | high |
| EmotionalState | 情感估计 | 每轮推断 | low |

## 记忆架构

```text
STM: 当前对话窗口（滑动窗口）
MTM: 事件摘要+原始引用（向量检索）
LTM: 偏好/事实/关系（结构化 KV）
```

原始对话作为 ground truth 保留，摘要标记为 lossy。
