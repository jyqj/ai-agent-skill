# MVA Planner

> **Evidence Status** — synthesized. 从 `../design-space/methodology/minimum-viable-agent.md` 压缩而来，用于避免一开始套完整 25 plane 架构。

## 30 秒判断

MVA 问的不是“最终要多强”，而是：**第一个能交付价值的版本需要做到哪一步？**

| MVA | 能力 | 最小闭环 | 不要提前做 |
|---|---|---|---|
| MVA-0 | 只回答/解释 | Prompt + 输出边界 | 工具、记忆、复杂状态 |
| MVA-1 | 生成草稿/计划 | Output contract + success criteria | 自动执行 |
| MVA-2 | 单步/短链工具辅助 | Tool schema + normalized observation | 长期记忆、复杂编排 |
| MVA-3 | 执行并验证 | postcondition + readback/test | 多租户运维平台 |
| MVA-4 | 长任务可恢复 | TaskState + checkpoint + world-state refresh | 自学习自动激活 |
| MVA-5 | 可观测可回归 | trace + eval + config fingerprint | 完全自治 |
| MVA-6 | 持续运行系统 | dataflow + heartbeat + rollback + ops | 无人工治理的开放自治 |

## 风险与深度判断

风险越高、效果越不可逆、世界状态越容易变化，需要的执行深度越高。

| 问题 | 低 | 中 | 高 |
|---|---|---|---|
| 是否写外部世界 | 只读 | 可撤销写 | 不可逆写 / 生产写 |
| 是否可验证 | 用户可看 | readback / test | 需要外部 ack / 传感器 |
| 状态跨度 | 单轮 | 多步 | 跨会话 / 长任务 |
| 失败成本 | 可忽略 | 需修复 | 金钱 / 安全 / 生产事故 |
| 自主权 | 建议 | 人审批执行 | Agent 自动执行 |

推荐深度：

| 组合 | 推荐 | 单次调用基准 | Agent 成本放大 |
|---|---|---|---|
| 只读 + 单轮 + 低失败成本 | D1-D2 | 1x | 1-2x |
| 多步分析 + 需要证据 | D3-D4 | 1x | 3-5x |
| 写文件/API + 可回读 | D4-D5 | 1x | 5-8x |
| 生产变更 / 不可逆动作 | D5-D6 + approval | 1x | 5-10x |
| 持续监控和自动处置 | D6 + Operations | 1x | 10x+ |

Agent 调用通常是单次 LLM 调用成本的 3-10 倍——包括多轮推理、工具调用、重试、验证回读。推理模型（o1/o3 等）的单次成本本身已是标准模型的 5-20 倍，叠加 Agent 循环后需要格外注意。

深度不是越高越好。如果只是探索或原型，保持 D3/D4，加上 `blocked / pending / unverifiable_by_agent` 状态，比假装 D6 更诚实。

## 最小产出

```yaml
mva_level: MVA-3
required_depth: D4
risk_factors: ["writes external API", "needs read-after-write"]
minimum_modules:
  - representation
  - tools
  - execution
  - effects
  - control
upgrade_trigger:
  - "task spans multiple sessions"
  - "needs production rollout"
```

## 升级触发器

| 看到这个信号 | 升级到 |
|---|---|
| 用户反复复制执行你的建议 | MVA-2 |
| 工具执行后需要确认现实变化 | MVA-3 |
| 任务会中断、恢复或跨天 | MVA-4 |
| 变更后可能静默回归 | MVA-5 |
| 系统需要持续监控和自动响应 | MVA-6 |

## 下一步

1. `module-picker.md`
2. `eval-planner.md`
3. `../design-space/methodology/minimum-viable-agent.md`
