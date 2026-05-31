# Financial Trading Agent Implementation Map

> **Evidence Status** — synthesized. Step Finance 事件分析、传统量化交易系统架构、DeFi 自动化交易实践与知识库 patterns/lessons-learned 映射。

## 关键案例覆盖

| 案例/来源 | 重点学习 |
|---|---|
| Step Finance $4,000 万损失 | 凭据隔离、交易额度阈值、不可逆操作门控、零信任架构 |
| 传统 OMS/EMS | 订单状态机、风险检查流水线、执行策略、对账机制 |
| FIX 协议 | 订单消息标准化、执行回报、状态管理 |
| DeFi AMM/DEX | 链上交易不可逆性、MEV 风险、智能合约风险 |
| MiFID II | 最佳执行义务、交易报告、头寸限制 |
| Dodd-Frank | 衍生品清算、大额交易报告、市场滥用检测 |

## 品类模块 → 证据映射

| 品类模块 | 参考来源 | 观察 |
|---|---|---|
| Representation | FIX 消息模型 / 交易所 API schema | 行情、订单、成交的标准化表示是交易系统的基础；时间戳精度和 freshness 直接影响决策质量 |
| Context | 量化交易系统数据管道 | 行情数据的实时装配、多源聚合和时效管理是核心能力；与 coding agent 的上下文工程对应 |
| Tools | 交易所 API / OMS / EMS | 下单、撤单、查询是核心工具；每个工具必须有风险分级和 precondition 检查 |
| Execution | 交易所连接管理 / 订单路由 | 主备双通道、故障转移、延迟监控决定了系统的可靠性 |
| Control | pre-trade risk check / 合规引擎 | 风险和合规检查必须内嵌于交易路径而非旁路；人工覆盖始终可用 |
| State | 订单状态机 / 组合状态 | 订单从创建到最终状态的完整生命周期管理；头寸的实时一致性 |
| Effects | 成交记录 / P&L / 头寸变化 | 每笔交易的完整效果链必须记录且可追溯；effect ledger 是金融 Agent 的强制组件 |
| Observability | 交易监控 / 审计日志 | 每个决策和操作的完整审计链是合规要求；延迟和异常监控是运维要求 |

## 核心 Pattern 映射

### Effect Ledger（强制）

> 参考：`../../architecture/planes/effects/overview.md`

在 Financial Agent 中，effect ledger 是**强制组件**：

```text
每笔交易必须记录：
  - 触发信号（signal_id + 数据依据）
  - 风险检查结果（passed / blocked + 原因）
  - 合规检查结果
  - 订单提交详情（时间、价格、数量、交易所）
  - 成交回报（fill_id、成交价、成交量、手续费）
  - 头寸变化（before → after）
  - P&L 变化
  - 对账结果
  - 时间戳（每个步骤的精确时间）
```

用途：
- 交易审计和合规报告
- 异常调查和根因分析
- 策略性能归因
- 争议处理（如价格争议）

### Circuit Breaker（强制）

> 参考：`../../architecture/planes/concurrency/overview.md`

```text
触发条件（任一）：
  - 单策略 N 分钟内损失 > strategy_loss_limit
  - 全账户日内损失 > daily_loss_limit
  - 连续 M 笔交易亏损
  - 异常交易频率 > frequency_limit
  - 市场波动率 > volatility_limit

触发动作：
  1. 冻结新订单
  2. 撤销所有活跃挂单
  3. 生成 circuit breaker report
  4. 通知风险经理 + 交易员
  5. 等待人工审查和重启授权
```

### Guard Model（推荐）

> 参考：`../../design-space/patterns/guard-model.md`

```text
独立于交易 Agent 的小模型/规则引擎，检查：
  - 订单是否合理（price/quantity/timing）
  - 是否存在市场操纵模式（spoofing / layering / wash trading）
  - 是否存在异常资金流向
  - 是否存在策略间冲突

Guard Model 的输出：
  - pass → 放行
  - suspect → 增加检查 + 降低自治等级
  - block → 阻断 + 告警
```

### 额度阈值分层（强制）

> 参考：`../../design-space/lessons-learned/step-finance-40m-loss.md` 教训 1

```text
层级          单笔上限          累计上限（24h）     审批要求
────────     ─────────────    ──────────────    ──────────
Tier 1       < $1,000         < $10,000         自动执行 + 日志
Tier 2       < $10,000        < $50,000         pre-trade check + 通知
Tier 3       < $100,000       < $200,000        人工确认
Tier 4       >= $100,000      >= $200,000       多因素审批 + 时间延迟

注意：具体阈值应根据组织规模和风险容忍度调整。
DeFi 场景（不可逆）应将阈值降低 1-2 个等级。
```

### 凭据隔离（强制）

> 参考：`../../design-space/lessons-learned/step-finance-40m-loss.md` 教训 2

```text
- 每个 Agent 实例独立 API key / 钱包
- 每个 key 配置最小权限（交易 key 不能提现、提现 key 不能交易）
- key 定期轮换且互不影响
- key 存储在 HSM / Vault，不在 Agent 进程内明文持有
- 一个 key 泄露 = 单 Agent 隔离，不影响其他 Agent
```

## 反模式与本品类的关联

| 反模式 | 在金融 Agent 中的表现 | 对策 |
|---|---|---|
| Tool Success as Completion | 下单成功 ≠ 交易成功（未对账、未检查滑点） | effect ledger + 对账验证 |
| Trust Everything | 信任所有行情数据和交易所回报 | 交叉验证 + 异常检测 |
| Runaway Deletion → Runaway Trading | Agent 失控持续下单导致巨额损失 | circuit breaker + 频率限制 + kill switch |
| Single Model Judge | 单一策略模型决定所有交易 | guard model + 独立风控 |
| Infinite Context as Memory | 将历史行情全部保留在上下文中 | 时效性管理 + 摘要 + 归档 |

## 与知识库其他部分的关系

| 关联主题 | 文件路径 |
|---|---|
| Step Finance 详细分析 | `../../design-space/lessons-learned/step-finance-40m-loss.md` |
| Effect Ledger 设计 | `../../architecture/planes/effects/overview.md` |
| Circuit Breaker 模式 | `../../architecture/planes/concurrency/overview.md` |
| Guard Model 模式 | `../../design-space/patterns/guard-model.md` |
| Control Paradigms | `../../paradigms/control-paradigms.md` |
| Security Plane | `../../architecture/planes/security/overview.md` |
| Identity-Capability Plane | `../../architecture/planes/identity-capability/overview.md` |
| Economics Plane | `../../architecture/planes/economics/overview.md` |
| Failure Taxonomy | `../../evaluation/failure-taxonomy.md` |
| Anti-Patterns Top 10 | `../../design-space/anti-patterns/top-10.md` |

## 实现建议矩阵

| 建议 | 优先级 | 原因 |
|---|---|---|
| Pre-trade risk check（内嵌于交易路径） | P0 | 无风检 = 无限制损失 |
| Effect ledger（每笔交易完整记录） | P0 | 合规要求 + 审计 + 异常调查 |
| 凭据隔离（每 Agent 独立 key） | P0 | Step Finance 教训，单点失效防护 |
| 额度阈值（分层限额） | P0 | Step Finance 教训，防止灾难性损失 |
| Circuit breaker（连续亏损熔断） | P0 | 防止策略失控导致持续亏损 |
| 头寸对账（实时 + 每日） | P0 | 防止头寸漂移导致风险失控 |
| Kill switch（紧急停止） | P0 | 最后防线，人工始终可接管 |
| 市场数据 TTL + stale 检测 | P1 | 防止基于过期数据交易 |
| 备用交易所连接 | P1 | 防止单点故障 |
| Guard model（独立风控检查） | P1 | 额外安全层 |
| 合规引擎（inline） | P1 | 监管要求 |
| Shadow mode / paper trading | P1 | 上线前验证 |
| 异常检测（多维） | P2 | 防止未知风险模式 |
| 策略间冲突检测 | P2 | 多策略环境必要 |

## 待补证据

- 真实 LLM-based trading agent 的生产表现数据（当前多为传统量化系统）。
- 不同延迟要求下 LLM 推理的适用性边界。
- DeFi 场景下 Agent 的 MEV 防护实践。
- 多交易所环境下的统一对账方案。
- 合规规则的版本管理和热加载机制。
- Agent 协作场景下的全局风险管理（如多个 Agent 管理同一账户的不同策略）。
