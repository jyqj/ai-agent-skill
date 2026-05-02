# Ops / SRE Agent Architecture

> **Evidence Status** — synthesized. New Relic SRE Agent、Azure SRE Agent、Observe AI SRE、incident.io、PagerDuty AIOps、multi-agent SRE 研究。

## Core Job

在告警、日志、指标、发布和回滚之间形成闭环，帮助值班人员更快定位、缓解并验证恢复：

```text
检测异常 → 聚合关联信号 → 诊断根因 → 建议/执行缓解 → 验证恢复 → 生成复盘
```

关键原则：**辅助而非替代人工判断。** 缩小搜索空间，自动化苦力工作。

## 用户模型

| 用户 | 心智模型 | 信任建立方式 | 默认交互 |
|---|---|---|---|
| On-call 工程师 | 调查加速器 | 准确关联信号、减噪 | Slack/PagerDuty + 分析 |
| SRE 团队 | 自动化 worker | 准确执行 runbook | Dashboard + 审计 |
| 管理层 | 状态感知器 | SLA 准确、影响清晰 | 摘要 + 趋势 |

## 任务模型

| 任务 | 默认深度 | 完成定义 |
|---|---|---|
| 告警分诊 | D3-D4 | 分类+优先级+关联聚合 |
| 根因分析 | D4-D5 | 假设+证据链+置信度 |
| 自动缓解 | D5 | 执行+效果验证+回滚准备 |
| 发布/回滚 | D5-D6 | canary 分析+决策+执行+验证 |
| 事后复盘 | D4 | timeline+根因+改进建议 |

## 表示模型

```text
Alert、MetricTimeSeries、LogEntry、TraceSpan、DeployEvent、
ServiceTopology、RunbookStep、IncidentTimeline、SLI/SLO/ErrorBudget
```

## 品类特有设计决策

| 决策 | 默认建议 |
|---|---|
| 自治程度 | 诊断自主(L4-L5)，缓解需确认(L3)，高风险变更需审批(L2) |
| 架构 | Supervisor + 专业子 Agent (metrics/logs/topology/runbook) |
| 安全 | 最小权限；写操作审批；变更有自动回滚 |
| 可解释性 | 每个结论附证据链 |

## 参考实现

| 参考 | 学习点 |
|---|---|
| New Relic SRE Agent | 实时遥测诊断、拓扑感知 |
| Azure SRE Agent | 自动根因分析、always-on |
| incident.io AI | 自主调查、90%+ 准确率 |
| PagerDuty AIOps | 告警聚合去噪 |

- 主观性任务的验证扩展：`../../concepts/beyond-verification.md`
