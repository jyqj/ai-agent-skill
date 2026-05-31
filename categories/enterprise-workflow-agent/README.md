# Enterprise Workflow Agent Architecture

> **Evidence Status** — synthesized. enterprise automation platforms (ServiceNow、Salesforce、SAP)、审批系统、审计合规框架、workflow orchestration engines (Temporal、Inngest)、MCP/A2A 协议实践。 for core patterns; medium for edge cases。

## Core Job

Enterprise Workflow Agent 在企业权限、审批、审计和系统集成约束下推进跨系统业务流程，并留下可审计的证据链：

```text
接收触发 → 理解流程上下文 → 查询/验证前置条件 → 执行系统动作 → 验证外部效果 → 记录审计 → 推进流程状态 → 异常升级
```

Enterprise Workflow Agent 的本质是"维护外部系统对象状态并留下审计证据"，不是"写代码"也不是"回答问题"。

## 用户模型

| 用户 | 心智模型 | 信任建立方式 | 默认交互 |
|---|---|---|---|
| 业务运营人员 | 智能审批助手 / 流程推进器 | 准确执行、不遗漏步骤、有审计记录 | Slack/Teams 通知 + 审批按钮 |
| IT/流程管理员 | 自动化 worker | 遵守流程定义、异常正确升级、可审计 | 配置面板 + 日志 |
| 合规/审计人员 | 流程审计器 | 完整 audit trail、不可篡改、可回放 | 审计报告 + trace |
| 部门经理 | 进度追踪器 | SLA 达标、异常可见、不阻塞流程 | Dashboard + 摘要通知 |

信任阶梯：先从只读查询 → 低风险更新 → 标准审批链动作 → 跨系统联动，通过合规审计逐步升级权限。

## 任务模型

详见 `task-model.md`。核心分类：

| 任务 | 默认深度 | 完成定义 |
|---|---|---|
| 工单路由/分派 | D4 | 工单已分配正确处理人 + 通知已发送 + 审计记录 |
| 审批链推进 | D4-D5 | 审批请求已发送 + 结果回收 + 状态更新 + 超时升级 |
| 跨系统数据同步 | D4 | 源/目标一致性验证 + 冲突解决 + 审计 |
| 合同/发票处理 | D5 | 数据提取 + 校验 + 系统录入 + 审批 + 付款触发 |
| 员工入/离职流程 | D5-D6 | 多系统账号管理 + 设备 + 权限 + 知识交接 |
| SLA 监控与升级 | D4 | 违约检测 + 自动升级 + 补偿动作 + 记录 |

## 表示模型

详见 `representation.md`。Enterprise Workflow Agent 的关键表示对象：

```text
WorkflowInstance、StepState、ApprovalRecord、AuditEntry、
EntityRecord (Customer/Employee/Order/Invoice)、
SystemCredential、RoleBinding、SLADefinition、
EscalationRule、CompensationAction
```

设计原则：

- 每个外部系统对象都有 freshness 标记；写前必须 read-after-write 确认。
- 审批记录是不可变 append-only log。
- 工单/表单字段来自外部系统，属于 untrusted data lane，需要 schema 验证。
- 流程定义和权限策略属于 config lane，变更需要版本管理。

## 行动模型

详见 `action-model.md`。

| 动作 | 示例 | 默认风险 |
|---|---|---|
| Read | 查询工单状态、获取客户信息、检查审批链 | safe |
| Write | 更新工单、创建记录、发送通知、触发审批 | check |
| Financial | 触发付款、修改合同、变更权限 | approval |
| Irreversible | 删除记录、发送外部通知、提交监管报告 | approval + confirmation |

所有写动作必须声明：precondition、intended effect、postcondition、verification method、compensation action（补偿事务）。

## 闭环模型

详见 `closed-loop.md`。

```text
Observe trigger (webhook / message / schedule / ticket)
  → Represent workflow context + entity states + permissions
  → Decide next step + risk assessment + escalation need
  → Act via system APIs (CRM / Ticket / ERP / Email / Calendar)
  → Verify effect (read-back entity state + audit log)
  → Update workflow state / escalate / compensate / close
```

Stop gate：

```text
[ ] 流程当前步骤的目标已达成（外部系统状态已验证）
[ ] 审计记录完整（who/what/when/why/result）
[ ] 未越过权限边界
[ ] 异常已按升级规则处理
[ ] SLA 合规状态已检查
[ ] 下一步参与者已通知
```

## 品类特有设计决策

详见 `design-decisions.md`。

| 决策 | 默认建议 |
|---|---|
| 执行环境 | 企业内网或 VPN 隔离；API 凭证通过 vault 管理 |
| 并发 | 同一工单/实体串行写入；跨实体可并行；乐观锁 + 冲突检测 |
| 上下文 | 流程定义 + 当前步骤 + 实体快照 + 审批历史；大附件 offload |
| 记忆 | 流程模板、常见异常处理策略、企业特定规则进入长期记忆 |
| 控制 | RBAC/ABAC 强制执行；财务/法务/客户动作必须审批；dry-run 模式 |
| 审计 | 全量 trace；每个写动作的 before/after snapshot；不可篡改 |
| 补偿 | 每个写动作注册补偿事务；失败时按逆序执行补偿 |

## 模块配置配方

| 模块 | 品类特化配置 | 通用参考 |
|---|---|---|
| Interface | Slack/Teams/Webhook/Email/Scheduled trigger 多入口统一 | `../../architecture/planes/interface/overview.md` |
| Representation | WorkflowInstance、EntityRecord、ApprovalRecord、AuditEntry | `../../architecture/planes/representation/overview.md` |
| Tools | CRM/Ticket/ERP/Email/Calendar/Payment API + MCP servers | `../../architecture/planes/tools/overview.md` |
| Execution | 企业 API gateway、凭证 vault、网络隔离 | `../../architecture/planes/execution/overview.md` |
| Control | RBAC/ABAC、审批链、dry-run、escalation rule | `../../architecture/planes/control/overview.md` |
| State | WorkflowState + StepCheckpoint + CompensationStack | `../../architecture/planes/state/overview.md` |
| World State | 外部系统实体状态回读 + 版本检测 + SLA 时钟 | `../../architecture/planes/world-state/overview.md` |
| Effects | effect ledger + read-after-write + 补偿事务 + 审计 log | `../../architecture/planes/effects/overview.md` |
| Observability | SLA 指标、异常率、审批延迟、流程完成率 | `../../architecture/planes/observability/overview.md` |
| Security | 凭证轮换、tenant isolation、PII masking、audit tamper-proof | `../../architecture/planes/security/overview.md` |

## 参考实现映射

详见 `implementation-map.md`。

| 参考 | 重点学习 |
|---|---|
| ServiceNow Flow Designer | 可视化流程定义、审批链、SLA 管理 |
| Temporal / Inngest | durable execution、补偿事务、checkpoint、replay |
| MCP + A2A | 工具标准化接入 + 跨 Agent 协作协议 |
| n8n / Zapier | 多系统集成模式、webhook 触发、错误处理 |

## 阅读路径

```text
README.md
  → task-model.md
  → representation.md
  → action-model.md
  → closed-loop.md
  → design-decisions.md
  → eval-cases.md
  → implementation-map.md
```

- 主观性任务的验证扩展：`../../concepts/beyond-verification.md`
