# Long-Horizon Runtime

> **Evidence Status** — theoretical. 基于 durable execution runtime、Voyager / Reflexion 等长期任务研究，以及实际 Agent checkpoint 需求。属于 frontier 方向。

## 为什么长时任务特殊

当任务持续时间从几分钟拉长到更长时，系统的主要矛盾会变化：

```text
不是“能不能生成一个答案”
而是“能不能持续保持目标、证据、权限、预算与恢复能力”
```

## 典型失效

- 目标漂移：越做越偏离用户原始 job。
- context rot：关键约束在长链条中丢失。
- state split-brain：任务状态与外部世界状态不同步。
- hidden worker explosion：子任务越来越多，预算失控。
- handoff amnesia：中断恢复后不知道为什么做到这里。

## 长时 runtime 的必备对象

```yaml
task_checkpoint:
  checkpoint_id: string
  task_goal: string
  completed_subgoals: []
  open_questions: []
  relevant_raw_refs: []
  world_state_refs: []
  pending_effects: []
  budget_remaining: {}
  next_safe_resume_step: string
```

## 关键机制

| 机制 | 作用 |
|---|---|
| Checkpoint Hydration | 恢复时把最小必要状态重新装配回来 |
| Milestone Gate | 每完成一个阶段就验证目标、成本和风险 |
| Bounded Worker Tree | 限制子代理 fanout |
| Refresh Before Commit | 长时间后做写动作前刷新世界状态 |
| Skill Reuse | 把稳定成功路径固化，而不是复制长 trace |

## 对品类的影响

- Research Agent：长报告需要 question tree、citation chain 和 refresh gate。
- Workflow Agent：跨系统事务更需要 checkpoint 与 compensation。
- Ops/SRE：incident 响应天然是长时任务，必须有 rollback 和 human escalation。
- Coding Agent：大迁移和多阶段修复必须分里程碑。

## 仍未收敛的问题

- runtime 应该让模型自己决定何时 checkpoint，还是由系统强制。
- 长时任务的记忆写入应该即时发生还是里程碑后再固化。
- “学会一个 skill”与“复制一条长 trace”之间的界线如何自动判断。
