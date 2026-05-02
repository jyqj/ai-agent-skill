# Decision Frameworks

> **Evidence Status** — synthesized. 核心概念归纳与跨模块一致性整理。

> **完整版**见 `../paradigms/methodology/decision-frameworks.md`。本文保留核心决策矩阵供快速查阅。

## 1. 何时选择自治等级

| 选择 | 使用条件 | 不要使用在 |
|---|---|---|
| L0 手动 | 高风险、无验证、用户只要建议 | 需要快速批量执行 |
| L1 建议后执行 | 动作清晰但需要用户确认 | 每秒级自动化 |
| L2 分步确认 | 长任务、多个高风险节点 | 低风险重复任务 |
| L3 受限自治 | 有工具、有策略、有 checkpoint | 不可逆且无审批场景 |
| L4 高自治 | 有 world state、effect verification、rollback | 用户尚未建立信任 |
| L5 持续自治 | 有监控、eval、incident response、人工接管 | 缺持续观测和资源上限 |

## 2. 何时选择执行深度

| 深度 | 适合 | 必备能力 |
|---|---|---|
| D0 Answer | 解释、问答 | claim caution |
| D1 Plan | 给步骤 | success criteria |
| D2 Assisted Action | 帮用户准备动作 | tool schema |
| D3 Tool Execution | 单步或短链执行 | execution result |
| D4 Verified Execution | 需要验证结果 | tests/readback |
| D5 Stateful Workflow | 长任务、多阶段、可恢复 | checkpoint/world state/effect ledger |
| D6 Continuous Operation | 持续流、监控、自治 | dataflow/incident/cost gate |

## 3. 何时用 Subagent、Worker、Multi-window

| 机制 | 用在 | 不用在 |
|---|---|---|
| Subagent | 子任务需要不同上下文或角色 | 只是普通函数调用 |
| Worker | 可并行、输出可合并、低交互 | 需要强共享状态的任务 |
| Multi-window | 上下文隔离或长研究 | 需要实时一致状态 |
| Multi-agent protocol | 3 个以上角色长期协作 | 简单顺序流程 |

## 4. 何时用 Compaction、Offloading、New Window

| 机制 | 用在 | 风险 |
|---|---|---|
| Compaction | 历史可摘要，细节可回查 | 摘要变事实 |
| Offloading | 工具输出过大但需保留 | 引用丢失 |
| New Window | 任务阶段切换、上下文污染 | 状态断裂 |
| Raw Ref Replay | 关键证据被压缩 | 成本上升 |

## 5. 何时信任记忆 vs 刷新 World State

```text
如果要写外部对象：刷新 World State。
如果只是偏好或历史习惯：查 Memory。
如果 Memory 与 Observation 冲突：优先新鲜可信 Observation，并暴露冲突。
如果 Observation 低置信度：回查 raw ref 或请求用户确认。
```

## 6. 何时中断用户

| 触发器 | 推荐交互 |
|---|---|
| 不可逆动作 | approval_request |
| 关键歧义 | clarification |
| 低置信度但高影响 | confirm_uncertainty |
| 长任务 milestone | progress_report |
| 用户纠错机会 | teaching_prompt |
| 超出预算 | budget_choice |
| 安全风险 | refusal_or_escalation |

## 7. 何时升级模型或降级策略

| 情况 | 策略 |
|---|---|
| 低风险、重复、结构化 | 小模型 + cache |
| 复杂规划、跨源冲突 | 升级到强推理模型 |
| 关键验证 | 使用独立 verifier 或不同模型 |
| 成本接近上限 | 降级为分阶段交付或请求用户选择 |
| 工具失败多次 | 停止盲重试，获取新观察或人工介入 |
