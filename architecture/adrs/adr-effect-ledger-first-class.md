# ADR: Treat Effect Ledger as a First-Class Runtime Object

> **Evidence Status** — synthesized. 多个 Agent 场景中都出现“工具返回成功但用户任务没有完成”的失败模式，包括代码修改未通过测试、浏览器点击未改变后端状态、CRM API 成功但字段未更新、部署命令成功但服务健康失败。

## Context

Agent 要产生外部效果时，不能只记录 ToolCall 和 ExecutionResult。ToolCall 说明“尝试做了什么”，ExecutionResult 说明“执行宿主返回了什么”，但用户关心的是“现实是否达到目标状态”。

## Decision

所有写动作、发送动作、删除动作、部署动作、购买/转账动作都必须生成 EffectRecord。EffectRecord 至少记录 intended_effect、preconditions、postconditions、verification_method、verification_status 和 rollback_or_compensation。

## Alternatives Considered

| 方案 | 为什么没有选择 |
|---|---|
| 只看工具返回值 | 不能证明外部世界改变 |
| 只在最终回答中说明“我已完成” | 不可回放、不可审计、不可评估 |
| 每个工具自己处理验证 | 缺少统一 trace 和 stop gate |

## Consequences

| 正向后果 | 负向后果 / 成本 |
|---|---|
| 完成定义清晰 | 每个写工具都要补 postcondition |
| 可回放和可评估 | 部分动作需要额外 readback 成本 |
| 支持补偿和恢复 | 需要维护 effect schema |

## Verification

```text
[ ] 写动作 trace 中存在 EffectRecord
[ ] EffectRecord 有 verification_status
[ ] verified 前 final answer 不声称完成
[ ] failed / partial 时触发 Recovery Plane
```

## Invalidation Triggers

如果某类动作无法被工具或传感器直接验证，应降级为 human_confirm、external_ack 或 honest partial delivery，而不是移除 EffectRecord。
