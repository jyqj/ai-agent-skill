# Embodied Robot Agent Design Decisions

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

| 决策 | 默认 |
|---|---|
| 规划 | LLM task decomposition + 经典 motion planning |
| 感知 | 多模态 → 结构化 scene → LLM |
| 安全 | 硬件(力限/急停) + 软件 → LLM 不可覆盖 |
| Sim-to-Real | 仿真 + domain randomization + 真实微调 |
| 恢复 | 单步重试 → 多步重规划 → 安全违反→人工 |
