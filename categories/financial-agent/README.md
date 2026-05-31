# Financial Trading Agent Architecture

> **Evidence Status** — synthesized. 基于 Step Finance $4,000 万损失事件、传统量化交易系统架构（FIX 协议、OMS/EMS）、DeFi 自动化交易实践、MiFID II / Dodd-Frank 合规要求归纳。

## Core Job

Financial Trading Agent 在真实金融市场中基于数据分析和策略规则执行交易、管理风险和维护合规，而非预测市场走势：

```text
接收市场数据 → 信号生成 → 风险评估 → 订单执行 → 成交确认 → 头寸对账 → 风险监控 → 合规报告
```

核心挑战有三个：一是在毫秒级延迟约束下做出正确决策（实时性），二是单个错误可能导致灾难性资金损失（不可逆性），三是必须满足复杂且不断变化的金融监管要求（合规性）。

## 用户模型

| 用户 | 心智模型 | 信任建立方式 | 默认交互 |
|---|---|---|---|
| 量化交易员 | 策略执行器 / 市场分析助手 | 低滑点、准确执行、实时反馈 | 策略参数配置 + 执行结果 + 滑点报告 |
| 风险经理 | 风险哨兵 / 预警系统 | 风险度量准确、阈值告警及时、零漏报 | 风险仪表板 + 阈值告警 + 压力测试 |
| 合规官 | 合规审计员 / 规则引擎 | 交易记录完整、违规检测准确 | 合规报告 + 违规告警 + 审计日志 |
| 投资组合经理 | 组合优化器 / 再平衡工具 | 执行准确、成本可控、偏差可解释 | 组合状态 + 再平衡建议 + 归因分析 |

信任建立依赖**零资金损失**：金融领域的错误操作可能在毫秒内造成不可逆的巨额损失。Agent 必须在每一步都能证明其行为在风险和合规约束内。

## 任务模型

详见 `task-model.md`。核心分类：

| 任务 | 默认深度 | 完成定义 |
|---|---|---|
| Market Analysis | D3 | 市场状态摘要 + 数据源引用 + 置信度 |
| Signal Generation | D4 | 信号 + 策略依据 + 回测证据 |
| Order Execution | D5 | 成交确认 + 滑点 < 阈值 + 头寸对账 |
| Portfolio Rebalancing | D4 | 目标权重达成 + 交易成本报告 + 偏差说明 |
| Risk Monitoring | D5 | 实时风险度量 + 阈值告警 + 自动对冲/降仓 |
| Compliance Checking | D4 | 合规状态 + 违规检测 + 报告生成 |
| Anomaly Detection | D4 | 异常事件 + 证据链 + 处置建议 |

## 表示模型

详见 `representation.md`。Financial Trading Agent 的关键表示对象包括：

```text
MarketDataSnapshot、OrderBookDepth、PortfolioState、RiskMetrics、OrderRecord、TradeRecord、RegulatoryConstraint、AlertEvent
```

设计原则：

- 市场数据是表示，不是市场本身；报价有 TTL，过期报价 = 错误决策。
- 头寸、P&L、保证金状态在每笔成交后都可能过期，必须立即刷新。
- 交易所返回数据（成交、拒单）属于 trusted external data，但仍需与本地 ledger 对账。
- 新闻、社交媒体、第三方分析为 untrusted data lane，不能直接驱动交易决策。

## 行动模型

详见 `action-model.md`。

| 动作 | 示例 | 默认风险 |
|---|---|---|
| Read | 行情查询、持仓查询、风险度量读取 | safe |
| Analyze | 信号计算、风险评估、合规检查 | safe/check |
| Execute | 下单、改单、撤单、对冲 | high/catastrophic |
| Report | 生成合规报告、交易日志、风险报告 | safe/check |

所有交易动作都应有：precondition（风险检查通过）、intended effect（目标头寸变化）、postcondition（成交确认 + 头寸对账）、verification method（交易所回报 + 本地 ledger 一致）、rollback/compensation（反向交易或人工干预）。

## 闭环模型

详见 `closed-loop.md`。

```text
Observe 市场数据流 + 组合状态 + 风险信号
  → Represent 价格/订单簿/头寸快照（ms 级新鲜度）
  → Decide 策略评估 + 风险检查 + 合规验证
  → Act 通过已验证交易所 API 提交订单
  → Verify 成交确认 + 头寸对账 + 滑点检查
  → Update 组合状态 + P&L + 风险度量 + 审计日志
```

Stop gate：

```text
[ ] 订单在风险限额内（pre-trade check 通过）
[ ] 成交价格/数量与预期一致（滑点 < 阈值）
[ ] 头寸对账通过（本地 ledger = 交易所报告）
[ ] 合规约束未被违反
[ ] 高风险操作已获人工审批
[ ] 所有交易动作已记入不可变审计日志
```

## 品类特有设计决策

详见 `design-decisions.md`。

| 决策 | 默认建议 |
|---|---|
| 延迟容忍度 | 高频策略 < 1ms；日内策略 < 100ms；组合再平衡 < 1s |
| 风险限额架构 | pre-trade + real-time + post-trade 三层检查 |
| 合规引擎集成 | 规则引擎内嵌于交易路径，非旁路；违规阻断而非仅告警 |
| 交易所连接 | 主备双通道 + 心跳检测 + 自动故障转移 |
| 头寸对账 | 每笔成交后实时对账 + 每日全量对账 |
| 人工覆盖 | 任何时候人工可冻结 Agent + 全量撤单 |
| 灾备 | Agent 失联 = 自动撤销所有挂单 + 通知运维 |

## 模块配置配方

| 模块 | Financial Agent 特化配置 | 通用参考 |
|---|---|---|
| Representation | MarketDataSnapshot、OrderBookDepth、PortfolioState、RiskMetrics | `../../architecture/planes/representation/overview.md` |
| Context | 行情/持仓/风险信号的实时装配与时效管理 | `../../architecture/planes/context/overview.md` |
| Tools | 行情 API、交易 API、风控 API、合规 API，含风险分级 + 额度阈值 | `../../architecture/planes/tools/overview.md` |
| Execution | 交易所连接、订单路由、延迟监控、故障转移 | `../../architecture/planes/execution/overview.md` |
| Control | pre-trade risk check、额度阈值、人工审批、紧急冻结 | `../../architecture/planes/control/overview.md` |
| State | 订单状态机、组合状态、风险状态、对账状态 | `../../architecture/planes/state/overview.md` |
| World State | 市场状态（开/休市）、交易所状态、监管公告 | `../../architecture/planes/world-state/overview.md` |
| Effects | 每笔交易的 effect ledger（订单→成交→头寸变化→P&L） | `../../architecture/planes/effects/overview.md` |
| Observability | 交易追踪、延迟度量、风险度量、合规审计日志 | `../../architecture/planes/observability/overview.md` |

## 参考实现映射

详见 `implementation-map.md`。

| 参考 | 重点学习 |
|---|---|
| Step Finance 事件 | 凭据隔离、交易额度阈值、不可逆操作审批门控 |
| 传统 OMS/EMS 架构 | 订单状态机、风险检查流水线、交易所连接管理 |
| DeFi 自动化交易 | 链上交易不可逆性、智能合约风险、MEV 防护 |
| MiFID II / Dodd-Frank | 交易前后透明度、最佳执行义务、市场滥用检测 |

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

设计新 Financial Trading Agent 时，再回到：

```text
../../paradigms/reasoning-paradigms.md
../../paradigms/tool-paradigms.md
../../paradigms/control-paradigms.md
../../index/design-checklist.md
```

- 不可逆操作的特殊处理：`../../design-space/lessons-learned/step-finance-40m-loss.md`
- 主观性任务的验证扩展：`../../concepts/beyond-verification.md`
