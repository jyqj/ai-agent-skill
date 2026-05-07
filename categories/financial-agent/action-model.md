# Financial Trading Agent Action Model

> **Evidence Status** — synthesized. `architecture/planes/tools/overview.md`、`architecture/planes/execution/overview.md`、`architecture/planes/effects/overview.md` 与 OMS/EMS 订单管理系统、交易所 API 风控实践。

## 动作分类

| 类别 | 动作 | 典型工具 | 默认风险 |
|---|---|---|---|
| Read | 行情查询、持仓查询、历史数据、订单状态 | market data API / portfolio API | safe |
| Analyze | 信号计算、风险评估、合规检查、归因分析 | strategy engine / risk engine | safe/check |
| Execute | place_order、cancel_order、modify_order | exchange trading API | high/catastrophic |
| Hedge | hedge_position、adjust_delta | trading API + risk engine | high |
| Rebalance | rebalance_portfolio | trading API + portfolio optimizer | high |
| Alert | generate_alert、escalate_to_human | notification system | safe |
| Report | submit_regulatory_report、generate_trade_log | compliance system | check |

## 工具风险策略

| 操作 | 默认策略 | 说明 |
|---|---|---|
| 行情查询 / 持仓读取 | allow | 只读且低风险 |
| 信号计算 / 风险评估 | allow | 分析操作，不产生外部效果 |
| 合规检查 | allow | 必要的验证步骤 |
| 小额限价单（< 阈值 1） | allow with log | 风险可控，记录审计日志 |
| 中额订单（阈值 1 - 阈值 2） | ask + pre-trade check | 需要风险检查通过 |
| 大额订单（> 阈值 2） | explicit approval | 人工审批 + 多因素确认 |
| 市价单（任意金额） | ask | 市价单滑点不可控 |
| 撤单 | allow with log | 通常低风险，但需记录 |
| 改单 | ask | 可能改变风险敞口 |
| 紧急清仓 | deny unless risk_breach | 仅在风险突破时由风控系统触发 |
| 资金转移 | deny / multi-factor approval | 最高风险，参考 Step Finance 教训 |
| 策略参数修改 | ask | 可能大幅改变交易行为 |

## 风险分级

### Catastrophic（灾难性）

```text
- 超大额订单（> 账户净值的 X%）
- 未经授权的资金转移
- 批量市价单清仓
- 修改风控限额
触发条件：单笔金额 > catastrophic_threshold 或 累计 24h > daily_catastrophic_limit
控制：强制人工多因素审批 + 时间延迟 + 独立风控确认
```

### High（高风险）

```text
- 头寸变更（开仓/加仓/减仓）
- 对冲操作
- 组合再平衡
触发条件：单笔金额在 high_threshold 到 catastrophic_threshold 之间
控制：pre-trade risk check + 人工确认 + 审计日志
```

### Medium（中风险）

```text
- 分析查询（涉及策略参数）
- 历史数据拉取（可能泄露策略信息）
- 告警配置修改
控制：记录日志 + 权限验证
```

### Low（低风险）

```text
- 行情查询
- 持仓读取
- 报告生成
- 只读合规检查
控制：标准日志
```

## Action Contract

### place_order

```yaml
action:
  action_id: string
  tool_id: place_order
  target:
    exchange: binance | coinbase | NYSE | ...
    symbol: BTC-USDT
    side: buy
    type: limit
    quantity: 1.5
    price: 65000
    time_in_force: GTC
    execution_strategy: TWAP
  preconditions:
    - market_data_fresh (tick_age < strategy_ttl)
    - risk_check_passed (position_within_limits)
    - compliance_check_passed (no_trading_restrictions)
    - sufficient_margin (margin_available > required_margin)
    - order_size_within_threshold (quantity * price < position_limit)
    - fat_finger_check_passed (price within N% of market)
  intended_effect: "买入 1.5 BTC，限价 65000 USDT"
  postconditions:
    - order_acknowledged_by_exchange
    - order_record_created_in_local_ledger
    - portfolio_state_updated_on_fill
    - risk_metrics_recalculated
  verification_method:
    - exchange_order_ack (order_id returned)
    - fill_confirmation (fill report received)
    - position_reconciliation (local == exchange)
    - slippage_check (actual_avg_price vs decision_price)
  rollback:
    - cancel_order (if not filled)
    - reverse_trade (if filled, submit opposite order — 需人工确认)
```

### cancel_order

```yaml
action:
  action_id: string
  tool_id: cancel_order
  target:
    exchange: string
    order_id: string
  preconditions:
    - order_exists_and_active
    - order_belongs_to_this_agent
  intended_effect: "撤销指定订单"
  postconditions:
    - exchange_confirms_cancellation
    - order_status_updated_to_cancelled
    - if_partial_fill: remaining_quantity_cancelled
  verification_method:
    - cancel_ack_from_exchange
    - order_status_query
  rollback:
    - N/A (撤单本身是安全操作)
```

### hedge_position

```yaml
action:
  action_id: string
  tool_id: hedge_position
  target:
    hedge_instrument: string
    hedge_ratio: decimal
    trigger: risk_metric_breach | manual | scheduled
  preconditions:
    - current_exposure_exceeds_threshold
    - hedge_instrument_available_and_liquid
    - risk_check_for_hedge_trade_passed
  intended_effect: "将 delta 敞口对冲至目标水平"
  postconditions:
    - net_exposure_within_target_range
    - hedge_cost_within_budget
  verification_method:
    - post_hedge_exposure_calculation
    - hedge_effectiveness_ratio
  rollback:
    - unwind_hedge (需要人工确认)
```

### rebalance_portfolio

```yaml
action:
  action_id: string
  tool_id: rebalance_portfolio
  target:
    target_weights: map[symbol, decimal]
    tolerance: decimal
    max_turnover: decimal
    execution_strategy: TWAP | VWAP | immediate
  preconditions:
    - current_weights_outside_tolerance_band
    - all_target_instruments_tradeable
    - total_rebalance_cost_estimated
    - risk_check_for_rebalance_passed
  intended_effect: "将组合权重调整至目标，偏差 < tolerance"
  postconditions:
    - actual_weights_within_tolerance_of_target
    - turnover_within_budget
    - transaction_cost_recorded
  verification_method:
    - post_rebalance_weight_check
    - cost_vs_estimate_comparison
  rollback:
    - reverse_rebalance (需要人工确认，成本可能较高)
```

### generate_alert

```yaml
action:
  action_id: string
  tool_id: generate_alert
  target:
    alert_type: risk_breach | compliance_violation | anomaly | connectivity_loss
    severity: info | warning | critical | emergency
    recipients: [risk_manager, compliance_officer, operator]
  preconditions:
    - alert_condition_detected
    - evidence_collected
  intended_effect: "通知相关人员并记录告警"
  postconditions:
    - alert_delivered_to_recipients
    - alert_logged_in_audit_trail
  verification_method:
    - delivery_confirmation
  rollback:
    - N/A (告警是信息性动作)
```

### submit_regulatory_report

```yaml
action:
  action_id: string
  tool_id: submit_regulatory_report
  target:
    report_type: transaction_report | position_report | suspicious_activity
    regulator: SEC | FCA | MAS | ...
    period: date_range
  preconditions:
    - report_data_complete_and_validated
    - compliance_officer_approved (if required)
  intended_effect: "按监管要求提交报告"
  postconditions:
    - report_submitted_and_acknowledged
    - submission_receipt_recorded
  verification_method:
    - regulator_ack_receipt
    - internal_audit_log
  rollback:
    - submit_amendment (如果报告有误)
```

## Happy Path 工具链

```text
market_data_read → signal_calculate → risk_check → compliance_check → place_order → monitor_fill → fill_confirm → position_reconcile → risk_update → audit_log
```

## Failure Recovery

| 失败 | 立即动作 | 不要做 |
|---|---|---|
| 订单被拒 | 解析拒单原因（余额不足/限额/合规）→ 调整后重试或升级 | 盲目重试 |
| 部分成交 | 评估剩余 → 继续/撤销/调整 → 更新组合状态 | 忽略未成交部分 |
| 交易所断连 | 切换备用通道 → 查询挂单状态 → 暂停新订单 | 继续发单 |
| 滑点超限 | 暂停当前策略 → 评估市场状况 → 通知交易员 | 继续按原计划执行 |
| 风控限额触达 | 冻结新订单 → 评估需要减仓的头寸 → 通知风控 | 修改限额参数 |
| 对账不一致 | 暂停交易 → 以交易所为准修正 → 审查差异原因 | 继续基于错误头寸交易 |

## Effect Ledger for Trading

```yaml
effect_record:
  effect_id: string
  target_system: exchange | portfolio | risk_system | compliance_system
  world_object_refs:
    - exchange://binance/BTC-USDT
    - portfolio://account_001/positions
  intended_effect: "买入 1.5 BTC @ limit 65000"
  tool_calls:
    - place_order: {order_id: "...", details: "..."}
  actual_observation:
    order_status: filled
    fill_price: 64980
    fill_quantity: 1.5
    slippage: -0.03%
    fee: 0.001 BTC
  verification_status: verified | failed | partial | unverified
  reconciliation:
    local_position: 1.5 BTC
    exchange_position: 1.5 BTC
    match: true
  remaining_risks:
    - market overnight risk
    - liquidity risk if position size significant relative to daily volume
```

## 并发策略

| 并发类型 | 默认 |
|---|---|
| 多个行情源读取 | 并行 |
| 多策略信号计算 | 可并行（独立策略间） |
| 同一标的下单 | 严格串行（防止重复下单和头寸计算错误） |
| 不同标的下单 | 可并行（但需要全局风险检查串行化） |
| 风险计算 | 全局锁（基于最新组合快照） |
| 对账 | 与交易串行（对账期间暂停交易） |

## 相关通用模块

- Tool Spec：`../../architecture/planes/tools/overview.md`
- Execution Host：`../../architecture/planes/execution/overview.md`
- Control Policy：`../../architecture/planes/control/overview.md`
- Effect Verification：`../../architecture/planes/effects/overview.md`
- Concurrency：`../../architecture/planes/concurrency/overview.md`
