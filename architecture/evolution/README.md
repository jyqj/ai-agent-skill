# 演化期

> **Evidence Status** — theoretical
> Agent 不是部署后就不变的系统。生产 Agent 需要处理模型版本升级、用户偏好漂移、工具语义变化、价值观漂移等长期问题。本目录补充这一维度。

## 背景

`../learning/` 模块覆盖了 Agent 如何从经验中学习（skill crystallization、knowledge distillation、feedback loops）。但学习主要关注"变好" -- 从成功中提炼、从失败中改进。

演化期关注的是更广泛的长期变化，包括：

- **被动变化**：模型升级、工具 API 变更、依赖库更新
- **渐变漂移**：用户偏好慢慢改变、memory 累积偏差、行为模式偏移
- **生态变化**：新 Agent 加入协作网络、协议版本升级、信任关系变化
- **终结**：Agent/Skill/Memory 不再有价值，需要有序退役

```text
Learning:   做得更好（向上）
Evolution:  适应变化（向前）
Retirement: 有序结束（向下）
```

## 本目录回答的问题

| 问题 | 文件 |
|---|---|
| 模型升级时 Harness 怎么同步调整？ | `co-evolution.md` |
| 如何检测 Agent 行为偏离初始设计？ | `value-drift.md` |
| 多 Agent 生态中协议如何演化？ | `ecosystem-protocols.md` |
| 什么时候该停用一个 Agent/Skill？ | `retirement.md` |

## 与其他模块的关系

- `../learning/` -- 学习是演化的一部分，但演化还包括非学习性的变化
- `../learning/skill-governance.md` -- Skill 的 deprecated/retired 状态是退役的前置概念
- `../planes/operations/` -- ConfigFingerprint 追踪版本组合，是协同演化的基础设施
- `../../evaluation/` -- 每次演化都应触发评估回归
- `../../concepts/foundations/` -- 价值对齐是价值漂移检测的前置概念

## 演化 vs 学习 vs 运维

| 维度 | Learning | Evolution | Operations |
|---|---|---|---|
| 时间尺度 | 单次任务到数天 | 数周到数月 | 实时到数天 |
| 触发 | 任务成功/失败 | 外部变化 / 内部漂移 | 告警 / 部署 / 配置变更 |
| 目标 | 变得更好 | 适应变化 | 保持稳定 |
| 输出 | Skill / Convention / Policy 更新 | 版本矩阵 / 漂移报告 / 退役计划 | 配置 / 部署 / 事故响应 |

## 延伸阅读

- `co-evolution.md`
- `value-drift.md`
- `ecosystem-protocols.md`
- `retirement.md`
- `../learning/overview.md`
- `../planes/operations/overview.md`
