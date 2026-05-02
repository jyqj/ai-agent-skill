# Embodied Robot Agent Representation Model

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

| 对象 | 含义 | Trust |
|---|---|---|
| SceneGraph | 物体/位置/关系 | medium |
| RobotState | 位姿/关节/电量 | high |
| TaskPlan | LLM 高层步骤 | low（需验证） |
| SafetyConstraint | 力限/速度/禁区 | 最高（不可覆盖） |
| HumanPose | 人类位置 | medium |

LLM 不直接处理原始传感器；SafetyConstraint 是硬边界。
