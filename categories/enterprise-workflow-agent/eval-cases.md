# Enterprise Workflow Agent Evaluation Cases

> **Evidence Status** — synthesized. 基于品类架构模板和通用 workflow agent 设计。

## 评估维度

| 维度 | 指标 | 阈值 |
|---|---|---|
| 流程完成率 | 成功/总触发 | > 95% |
| SLA 合规率 | SLA 内/总完成 | > 98% |
| 审计完整度 | 有审计的写动作/总写动作 | 100% |
| 补偿成功率 | 成功补偿/需补偿 | > 95% |

## 核心 Eval Cases

### Case 1: 标准工单审批流
```yaml
scenario: 新工单触发三级审批
assertions:
  - 审批人正确（按 RBAC）
  - 每级有独立 AuditEntry
  - SLA 时钟每级启动
```

### Case 2: 跨系统同步失败补偿
```yaml
scenario: CRM→ERP→Email 三步同步，ERP 写入失败
assertions:
  - CRM 记录已回滚
  - ERP 无脏数据
  - 审计含补偿详情
  - 升级通知已发送
```

### Case 3: 并发冲突
```yaml
scenario: 两流程同时更新同一客户
assertions:
  - 检测到乐观锁冲突
  - 后到的正确处理
  - 无数据丢失
```
