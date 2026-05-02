# Rollout and Regression

> **Evidence Status** — synthesized. 基于多个项目的运维实践归纳。

## 建议流程

```text
Change proposal
  → local / fixture eval
  → regression suite
  → canary rollout
  → monitor task success + effect verification + approval rate
  → full rollout or rollback
```

## Canary 重点指标

- task_success
- effect_verified_rate
- permission_violation_rate
- stale_state_incidents
- user_interruptions_per_task
- cost_per_task


## Shadow Mode

新配置可以在真实输入上 dry-run，不产生外部效果，只记录将会做出的 decision / tool_call / cost / risk，并与当前运行时比较。
