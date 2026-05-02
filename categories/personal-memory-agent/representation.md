# Personal Memory Agent Representation Model

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

| 对象 | 含义 | Trust |
|---|---|---|
| MemoryRecord | 类型+内容+来源+时间+置信度 | medium |
| GroundTruth | 原始对话 | high（不可变） |
| UserProfile | 聚合画像 | medium |
| ProvenanceLink | 记忆→原始对话 | high |
| ConflictRecord | 新旧矛盾 | high |

## 记忆类型

| 类型 | 示例 | 时效 | 更新 |
|---|---|---|---|
| 事实 | "我住上海" | TTL | supersede |
| 偏好 | "喜欢咖啡" | 衰减不消失 | 频率加权 |
| 事件 | "上周去巴黎" | 永久(降权) | append |
| 目标 | "今年学日语" | 目标周期 | 进展追踪 |
