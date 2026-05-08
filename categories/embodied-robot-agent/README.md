# Embodied Robot Agent Architecture

> **Evidence Status** — synthesized. SayCan、Inner Monologue、RT-2、VLA 综述、Open X-Embodiment、ROS2。

> **文档深度**：骨架级——提供设计维度清单和关键问题，不提供完整蓝图。详细设计需结合 `architecture/planes/` 和 `paradigms/` 自行组装。

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

物理动作不可逆，验证必须依赖传感器回读而非推断。部分任务（如人机交互中的用户满意度）超越标准 postcondition：

- 物理效果验证：传感器状态 + 力/位置/视觉多通道回读
- 安全验证：硬件边界（force/speed/e-stop）独立于 LLM 判断
- 扩展验证：`../../concepts/beyond-verification.md` — 超越 postcondition 的验证语义
- 主观性评估：`../../evaluation/subjective-eval.md` — 适用于人机交互场景的评估框架
