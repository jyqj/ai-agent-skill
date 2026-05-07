# Financial Trading Agent Representation Model

> **Evidence Status** — synthesized. `architecture/planes/representation/overview.md`、FIX 协议消息模型、交易所订单簿数据结构、量化交易系统风险度量体系归纳。

## 关键表示对象

| 对象 | 含义 | Freshness | Trust |
|---|---|---|---|
| MarketDataSnapshot | OHLCV 价格、成交量、最新价、时间戳 | 毫秒级过期（tick by tick） | trusted if exchange feed |
| OrderBookDepth | 买卖盘挂单深度（价格、数量、层级） | 毫秒级过期 | trusted if L2/L3 feed |
| TradeTape | 逐笔成交流水（价格、数量、方向、时间） | 实时流 | trusted if exchange feed |
| PortfolioState | 持仓、可用余额、保证金、浮动 P&L | 每笔成交后过期 | derived, reconcile with exchange |
| RiskMetrics | VaR、最大回撤、Greeks、相关性矩阵、敞口 | 分钟级或事件触发更新 | derived, model-dependent |
| OrderRecord | 订单意图、状态、成交明细、滑点、时间戳 | 状态机驱动更新 | trusted execution record |
| TradeRecord | 已成交记录、价格、数量、手续费、结算状态 | 成交后不可变 | trusted if confirmed |
| RegulatoryConstraint | 头寸限制、交易限制、报告要求、禁止名单 | 监管更新时变化（低频） | regulatory authority |
| AlertEvent | 风险告警、合规告警、异常检测告警 | 事件驱动 | derived, needs evidence |
| StrategyState | 策略参数、信号状态、开关状态、性能度量 | 策略更新时变化 | configuration + derived |

## 表示构建流程

```text
RawMarketFeed(交易所行情推送 / API 轮询)
  → MarketDataSnapshot(标准化 OHLCV + 时间戳 + 来源标记)
  → OrderBookDepth(价格层级 + 深度 + 买卖不平衡)
  → StrategySignal(信号计算 + 置信度 + 依据)
  → RiskAssessment(风险度量 + 限额检查 + 合规验证)
  → OrderIntent(方向 + 数量 + 价格类型 + 执行策略)
  → OrderRecord(交易所确认 + 状态更新 + 成交回报)
  → PortfolioState(头寸更新 + P&L 重算 + 对账)
```

不要缓存过期行情。默认策略是：

```text
实时行情 → 检查时间戳（< TTL?）→ 基于最新数据计算信号 → 风险检查 → 执行
如果行情时间戳 > TTL → 标记 STALE → 暂停依赖该行情的决策 → 刷新或切换备用源
```

## Trust Lane 映射

| 来源 | 默认 lane | 说明 |
|---|---|---|
| 系统/运维配置 | system instruction | 风险限额、交易许可、合规规则 |
| 用户/交易员指令 | user instruction | 策略参数、交易目标 |
| 交易所行情 feed | trusted external data | 主数据源，但需要时间戳验证和备源对比 |
| 交易所订单回报 | trusted external data | 成交确认，但需与本地 ledger 对账 |
| 新闻 / 社交媒体 | untrusted data | 不能直接触发交易；仅作为分析输入 |
| 第三方分析 / 研报 | untrusted data | 需要独立验证后才可影响决策 |
| 策略信号 | model hypothesis | 必须经过风险检查和合规验证 |
| 历史回测结果 | derived evidence | 仅作为参考，不等于未来表现 |

关键规则：**行情数据中可能包含错误报价（erroneous tick）**；异常价格跳变需要与备用数据源交叉验证后才可用于决策。

## Freshness 策略

| 表示 | TTL / 失效条件 | 刷新动作 |
|---|---|---|
| MarketDataSnapshot | 策略延迟要求（高频 < 1ms，日内 < 100ms） | 实时推送或轮询；超 TTL 标记 STALE 并暂停决策 |
| OrderBookDepth | 与 MarketData 相同 | 实时增量更新；全量快照定期校正 |
| PortfolioState | 每笔成交后立即过期 | 成交回报触发更新；每日交易所全量对账 |
| RiskMetrics | 头寸变化或市场大幅波动时 | 事件触发重算 + 定时重算（如每分钟） |
| OrderRecord | 状态变更事件驱动 | 交易所回报 → 更新状态机 → 确认最终状态 |
| RegulatoryConstraint | 监管政策更新时（低频） | 合规团队手动更新 + Agent 启动时加载 |
| StrategyState | 参数变更或人工干预 | 配置更新 → 信号重算 |

### 过期行情检测

```yaml
stale_price_detection:
  check: current_time - tick_timestamp > strategy_ttl
  action_if_stale:
    - mark_data_as_stale
    - suspend_dependent_signals
    - attempt_refresh_from_backup_feed
    - if_still_stale: alert_operator + halt_new_orders
  备源对比:
    - primary_feed vs backup_feed 价差 > threshold → 标记异常
    - 两源均 stale → 紧急停止交易
```

## 关键数据结构

### MarketDataSnapshot

```yaml
market_data:
  symbol: string           # 交易标的，如 BTC-USDT
  exchange: string         # 交易所标识
  timestamp_ms: int64      # 数据时间戳（毫秒）
  receive_timestamp_ms: int64  # 接收时间戳（用于延迟监控）
  ohlcv:
    open: decimal
    high: decimal
    low: decimal
    close: decimal
    volume: decimal
  bid: decimal             # 最优买价
  ask: decimal             # 最优卖价
  spread: decimal          # 买卖价差
  source: primary | backup
  freshness: fresh | stale | suspect
```

### PortfolioState

```yaml
portfolio_state:
  account_id: string
  timestamp_ms: int64
  positions:
    - symbol: string
      quantity: decimal
      avg_cost: decimal
      unrealized_pnl: decimal
      market_value: decimal
  cash_balance: decimal
  margin_used: decimal
  margin_available: decimal
  total_equity: decimal
  daily_pnl: decimal
  reconciliation_status: reconciled | pending | mismatch
```

### RiskMetrics

```yaml
risk_metrics:
  timestamp_ms: int64
  var_95: decimal          # 95% 置信度 VaR
  var_99: decimal          # 99% 置信度 VaR
  max_drawdown: decimal    # 当前最大回撤
  sharpe_ratio: decimal    # 夏普比率
  greeks:                  # 期权相关（如适用）
    delta: decimal
    gamma: decimal
    vega: decimal
    theta: decimal
  exposure:
    gross: decimal         # 总敞口
    net: decimal           # 净敞口
    by_sector: map         # 按行业分布
    by_asset_class: map    # 按资产类别分布
  correlation_alerts:
    - pair: [symbol_a, symbol_b]
      correlation: decimal
      alert_if_above: decimal
```

### OrderRecord

```yaml
order_record:
  order_id: string
  client_order_id: string
  symbol: string
  side: buy | sell
  order_type: market | limit | stop | stop_limit
  quantity: decimal
  price: decimal           # 限价单价格
  time_in_force: GTC | IOC | FOK | DAY
  execution_strategy: TWAP | VWAP | iceberg | direct
  status: pending | submitted | partial_fill | filled | cancelled | rejected
  fills:
    - fill_id: string
      price: decimal
      quantity: decimal
      timestamp_ms: int64
      fee: decimal
  slippage: decimal        # 实际成交均价 vs 决策时刻价格
  created_at: int64
  updated_at: int64
  risk_check_passed: boolean
  compliance_check_passed: boolean
```

## 与通用模块的连接

| Financial 表示问题 | 通用模块 |
|---|---|
| 行情数据标准化、转换链 | `../../architecture/planes/representation/representation-contract.md` |
| 过期检测和新鲜度语义 | `../../architecture/planes/representation/observation-semantics.md` |
| 实时上下文装配 | `../../architecture/planes/context/overview.md` |
| 交易所状态和市场状态刷新 | `../../architecture/planes/world-state/overview.md` |
| 不可信新闻/社交数据注入 | `../../architecture/planes/security/overview.md` |

## 反模式

| 反模式 | 表现 | 修复 |
|---|---|---|
| Stale Price Trading | 基于过期报价下单 | 强制 TTL 检查 + STALE 标记 + 暂停决策 |
| Single Feed Dependency | 单一行情源故障导致全面停止或错误 | 主备双源 + 交叉验证 + 备源自动切换 |
| Position Drift | 本地头寸与交易所持仓长期不一致 | 每笔成交后实时对账 + 每日全量对账 |
| Risk Metric Lag | 风险度量更新频率远低于交易频率 | 事件触发重算 + 最低更新频率保证 |
| News-Driven Trading | 未经验证的新闻直接触发交易决策 | 新闻作为 untrusted data lane + 独立验证 |
| Backtest Overfitting | 回测结果直接作为未来表现预测 | 回测标记为 derived evidence + out-of-sample 验证 |
