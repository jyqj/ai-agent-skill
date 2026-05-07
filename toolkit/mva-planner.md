# MVA Planner

> **Evidence Status** — synthesized. 从 `../paradigms/methodology/minimum-viable-agent.md` 压缩而来，用于避免一开始套完整 25 plane 架构。

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

## 最小产出

```yaml
mva_level: MVA-3
why: "needs write actions and read-after-write verification"
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

| 看到这个失败 | 升级到 |
|---|---|
| 用户反复复制执行你的建议 | MVA-2 |
| 工具执行后需要确认现实变化 | MVA-3 |
| 任务会中断、恢复或跨天 | MVA-4 |
| 变更后可能静默回归 | MVA-5 |
| 系统需要持续监控和自动响应 | MVA-6 |

## 下一步

1. `module-picker.md`
2. `risk-depth-calculator.md`
3. `../paradigms/methodology/minimum-viable-agent.md`
