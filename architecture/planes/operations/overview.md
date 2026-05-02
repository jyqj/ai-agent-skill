# Operations Plane
>
> **所属域**：7. Lifecycle & Economics — 上线、回归与事故响应
>
> **Evidence Status** — synthesized. 生产 Agent 系统对配置追踪、回归、灰度、回滚、事故响应的需求；本知识库对 Agent 运维面的统一抽象。

**Principle Refs**: MC-02, BR-01 — 运维层监控预算合规与系统健康；自监控异常触发回滚和事故响应

Agent 系统上线后，模型升级、prompt 变更、tool schema 调整都可能导致静默回归。Operations 层使每一次行为变化可追溯、可回滚、可定位。

## 定义

Operations 层负责让 Agent 稳定上线、可回归、可灰度、可回滚、可事故响应。

它不表达 skill 自身的状态标签。它表达的是：一次 Agent 行为由哪些模型、prompt、tool schema、policy、eval suite 和运行配置共同产生。

## 运维面最少要包含

| 能力 | 为什么需要 |
|---|---|
| Configuration Lineage | 知道当前行为由哪些配置产生 |
| Eval Regression | 变更前后比较，不靠感觉 |
| Canary Rollout | 先在小流量验证，再全量 |
| Shadow Mode | 新策略在旧流量上 dry-run 比较差异 |
| Incident Response | 出问题能定位、暂停、补偿和回滚 |
| SLO / Budget | 成本、时延、成功率、人工打扰次数 |
| Data Retention | trace、memory、artifact、secret 的保留和删除 |

## 入口文档

- `configuration-lineage.md`
- `rollout-and-regression.md`
- `incident-response.md`
