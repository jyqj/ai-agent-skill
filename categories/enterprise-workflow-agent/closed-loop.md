# Enterprise Workflow Agent Closed Loop

> **Evidence Status** — synthesized. 基于品类架构模板和通用 workflow agent 设计。

## Happy Path

```text
1. Observe: 接收触发（webhook / Slack / schedule）
2. Represent: 加载流程定义 + 查询当前步骤 + 回读实体状态
3. Decide: 判断下一步 + 风险评估 + 是否需审批
4. Act: 执行系统写操作（通过 API / MCP）
5. Verify: read-after-write 验证 + 审计记录写入
6. Update: 推进流程状态 + 通知下一参与者 + 更新 SLA
```

## Failure + Recovery

| 失败类型 | 检测方式 | 恢复策略 |
|---|---|---|
| API 超时 | timeout | 指数退避重试（3 次）→ 升级 |
| 写冲突 | version mismatch / 409 | 回读 → 合并 → 重试 |
| 审批超时 | SLA 时钟到期 | 提醒 → 升级 → 替代审批人 |
| 部分写入 | 补偿栈检查 | SAGA 逆向补偿 → 审计 → 升级 |
| 权限不足 | 403 | 记录 → 请求提权 → 人工 |

## Stop Gate

```text
[ ] 当前步骤目标已达成（外部系统状态已验证）
[ ] 审计记录完整（who/what/when/why/before/after）
[ ] 未越过权限边界
[ ] 异常已按升级规则处理
[ ] SLA 合规
[ ] 下一参与者已通知
```

## 长流程 Checkpoint

```text
WorkflowCheckpoint {
  instance_id, current_step, step_state,
  entity_snapshots, compensation_stack,
  sla_deadlines, pending_approvals,
  last_verified_at, retry_count
}
```
