# Personal Memory Agent Implementation Map

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

| 组件 | 推荐 |
|---|---|
| Ground Truth | S3/PostgreSQL |
| 结构化 | PostgreSQL/Redis |
| 向量 | pgvector/Pinecone |
| 提取 | LLM |
| 检索 | 混合+重排 |

MVA: 0(会话窗口) → 2(跨会话 profile) → 3(事件+矛盾+时效) → 4(三层+隐私+遗忘) → 5(多模态+可编辑+导出)
