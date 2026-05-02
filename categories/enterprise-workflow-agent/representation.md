# Enterprise Workflow Agent Representation Model

> **Evidence Status** — synthesized. 基于品类架构模板和通用 workflow agent 设计。

## 核心表示对象

| 表示对象 | 含义 | Freshness | Trust | Raw Ref |
|---|---|---|---|---|
| WorkflowInstance | 流程实例：模板 ID、当前步骤、参与者、历史 | 每步刷新 | config lane | 流程引擎 |
| StepState | 当前步骤状态：待处理/执行中/完成/失败/跳过 | 实时 | internal | 状态机 |
| EntityRecord | 业务实体：客户/工单/订单/发票/员工 | 写前刷新 | untrusted | API response |
| ApprovalRecord | 审批记录：审批人/时间/决定/备注 | 不可变 | high | 审批系统 log |
| AuditEntry | 审计条目：who/what/when/why/before/after | 不可变 | high | append-only log |
| SLADefinition | SLA：指标/阈值/升级规则/时钟 | 低频更新 | config lane | 策略文件 |
| RoleBinding | 权限绑定：角色/用户/权限/有效期 | 鉴权时刷新 | config lane | IAM |
| CompensationAction | 补偿动作：关联写动作/逆操作/状态要求 | 注册时绑定 | internal | 补偿栈 |

## 设计原则

- **外部系统数据是表示，不是现实。** 工单显示"已关闭"不等于问题解决了。
- **写前必须 read-after-write。** 更新 CRM 后回读确认，防止乐观锁冲突。
- **审计记录 append-only、不可篡改。** content hash 保证完整性。
- **多系统数据做 schema 对齐。** 不同系统的"客户 ID"需要 mapping。
- **时间戳统一 UTC。** 跨时区流程中时间不一致是常见 bug。
- **大附件 offload 到 blob storage，表示层只保留引用。**
