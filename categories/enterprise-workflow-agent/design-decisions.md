# Enterprise Workflow Agent Design Decisions

> **Evidence Status** — synthesized. 基于品类架构模板和通用 workflow agent 设计。

## 核心设计决策

| 决策 | 默认建议 | 升级触发器 |
|---|---|---|
| 执行环境 | 企业内网/VPN；API 凭证通过 vault | 跨组织 → mTLS + API gateway |
| 并发 | 同一实体串行写；跨实体并行；乐观锁 | 高并发 → 分布式锁 |
| 上下文 | 流程定义+步骤+实体快照+审批历史 | 长流程 → context compaction |
| 记忆 | 流程模板、异常策略、企业规则入长期记忆 | 跨流程学习 → pattern extraction |
| 控制 | RBAC/ABAC；财务/法务必须审批；dry-run | 高风险 → 双人审批 |
| 审计 | 全量 trace；每写动作 before/after snapshot | 合规 → 签名+公证 |
| 补偿 | 每写动作注册补偿；SAGA 逆序 | 跨组织 → 协调者模式 |

## 80/20 设计原则

- **80% 确定性执行：** 标准流程走状态机，不需要 LLM。
- **20% 非确定性决策：** 异常处理、歧义解析、优先级判断用 LLM。

## 关键陷阱

- **God Workflow：** 一个 Agent 管所有流程 → 上下文爆炸。按业务域拆分。
- **审计后补：** 先功能再审计 → 缺失。审计必须是写动作的一等公民。
- **忽略补偿：** 只考虑 happy path → 失败后状态不一致。
- **凭证硬编码：** 必须用 vault + 轮换。
