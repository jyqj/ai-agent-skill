# Embodied Robot Agent Implementation Map

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

| 参考 | 学习点 |
|---|---|
| SayCan | affordance scoring |
| Inner Monologue | 多模态反馈 |
| RT-2 | VLA 端到端 |
| ROS2+MoveIt | 底层控制 |
| Isaac Lab | GPU 仿真 |

## 架构

```text
LLM/VLM (高层规划) ↕ Scene Description
Skill Library (中层) ↕ Action Primitives
Motion Planner (低层) ↕ Joint Commands
Hardware Abstraction
```

MVA: 0(语音→回复) → 2(固定 skill) → 3(多步+验证) → 4(动态重规划+人类协作) → 5(长期自主+新技能)
