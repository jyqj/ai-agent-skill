# Embodied Robot Agent Architecture

> **Evidence Status** — synthesized. SayCan、Inner Monologue、RT-2、VLA 综述、Open X-Embodiment、ROS2。

## Core Job

在物理世界中通过感知、规划、动作完成实际任务：

```text
感知环境 → 理解指令 → 规划动作序列 → 物理执行 → 感知效果 → 调整
```

核心挑战："代码 bug 可以 revert，物理动作不能。" 安全绝对优先。

## 用户模型

| 用户 | 心智模型 | 信任 |
|---|---|---|
| 操作员 | 智能工具 | 安全可预测可中断 |
| 工程师 | 可编程机器人 | 可调试可复现 |
| 终端用户 | 服务机器人 | 安全有用 |

## 品类设计决策

| 决策 | 默认 |
|---|---|
| 安全 | 硬件边界（force/speed/e-stop）不可被 LLM 覆盖 |
| 规划 | LLM 做高层 task decomposition，经典控制做低层 |
| 感知 | 多模态融合；LLM 不直接处理原始传感器 |
| 验证 | 物理效果通过传感器回读，不靠推断 |
| Sim-to-Real | 仿真训练+真实微调；显式处理 domain gap |

## 参考

| 参考 | 学习点 |
|---|---|
| SayCan | LLM + affordance scoring |
| Inner Monologue | 多模态反馈闭环 |
| RT-2 | VLA 端到端 |
| ROS2+MoveIt | 底层控制框架 |

## 验证与评估扩展

本品类的核心任务涉及主观性判断，标准 postcondition 验证不完全适用：

- 验证哲学：`../../concepts/beyond-verification.md` — 从 postcondition 到 resonance / longitudinal / intersubjective 的验证语义扩展
- 主观性评估：`../../evaluation/subjective-eval.md` — 用户满意度、一致性、对齐度、关系健康度等维度的评估框架
