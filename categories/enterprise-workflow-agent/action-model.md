# Enterprise Workflow Agent Action Model

> **Evidence Status** — synthesized. 基于品类架构模板和通用 workflow agent 设计。

## 动作分类

| 动作类别 | 示例 | 默认风险 | Precondition | Postcondition | Verification |
|---|---|---|---|---|---|
| Read | 查询工单、获取客户记录 | safe | API 凭证有效 | 数据已获取 | response 非空且合法 |
| Notify | 发送 Slack/Email/Teams 消息 | check | 收件人存在 | 消息已送达 | delivery receipt |
| Update | 更新工单字段、修改状态 | check | 实体未锁定 | 字段已变更 | read-after-write |
| Create | 创建工单、新建记录 | check | 去重检查通过 | 记录已创建 | 回读确认 |
| Approve | 触发审批、记录结果 | check/approval | 审批人有权限 | 审批不可变写入 | 状态已更新 |
| Financial | 触发付款、修改合同 | approval | 金额校验、预算检查 | 交易已提交 | 交易 ID + 回读 |
| Delete | 删除记录 | approval+confirm | 无关联依赖 | 记录不可见 | 回读 404 |

## 补偿事务（SAGA 模式）

```text
动作链: A → B → C
补偿栈: [compensate_C, compensate_B, compensate_A]

C 失败 → compensate_B() → compensate_A() → 审计记录 → 升级
```

## 幂等性要求

每个写动作必须幂等或有 idempotency key。网络超时重试不应产生重复记录。
