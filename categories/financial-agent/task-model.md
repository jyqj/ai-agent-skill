# Financial Trading Agent Task Model

> **Evidence Status** — synthesized. 量化交易系统任务分类、OMS/EMS 工作流、DeFi 交易 Agent 操作模式与 `evaluation/failure-taxonomy.md` 的任务/失败抽象。

## 任务类型

| 类型 | 用户输入示例 | 默认深度 | 默认自治 | 成功定义 |
|---|---|---|---|---|
| Market Analysis | "分析 BTC 近 4 小时的价量结构" | D3 | L2-L3 | 市场状态摘要 + 数据源引用 + 置信度 |
| Signal Generation | "基于均线交叉策略生成交易信号" | D4 | L3 | 信号（方向/强度/时效）+ 策略依据 + 历史表现 |
| Order Execution | "按 TWAP 策略买入 100 ETH" | D5 | L3-L4 | 成交确认 + 滑点 < 阈值 + 头寸对账通过 |
| Portfolio Rebalancing | "将组合调整到目标权重" | D4 | L3 | 目标权重达成 + 交易成本 < 预算 + 偏差说明 |
| Risk Monitoring | "监控组合 VaR 不超过 5%" | D5 | L4 | 实时风险度量 + 阈值触发告警/对冲 + 零漏报 |
| Compliance Checking | "检查今日交易是否合规" | D4 | L3-L4 | 合规状态报告 + 违规清单（如有）+ 修复建议 |
| Anomaly Detection | "监控异常交易模式" | D4 | L3-L4 | 异常事件 + 证据链 + 置信度 + 处置建议 |

## TaskEnvelope

Financial Trading Agent 接受任务时应生成或补全 TaskEnvelope：

```yaml
task_envelope:
  task_type: market_analysis | signal_generation | order_execution | portfolio_rebalancing | risk_monitoring | compliance_checking | anomaly_detection
  user_goal: string
  success_criteria:
    - observable outcome
  constraints:
    - max_slippage: 0.1%
    - max_position_size: $100,000
    - trading_hours_only: true
    - compliance_rules: [MiFID_II, position_limits]
  allowed_actions:
    market_data_read: true
    order_placement: ask | allow | deny
    position_modification: ask
    emergency_liquidation: deny_unless_risk_breach
  risk_level: low | medium | high | catastrophic
  depth_target: D0 | D1 | D2 | D3 | D4 | D5
  autonomy_level: L0 | L1 | L2 | L3 | L4
  verification_plan:
    - fill_confirmation
    - position_reconciliation
    - pnl_check
  stop_gate:
    - all_orders_confirmed_or_cancelled
    - position_reconciled_with_exchange
    - risk_metrics_within_limits
    - compliance_check_passed
    - audit_log_recorded
```

## 成功标准

| 成功维度 | 问题 | 证据 |
|---|---|---|
| Goal Fit | 是否达成交易/分析目标？ | 成交记录与目标映射、分析结论与数据一致 |
| Execution Quality | 执行质量是否可接受？ | 滑点、市场冲击、成交率 |
| Risk Compliance | 是否始终在风险限额内？ | pre-trade / real-time / post-trade 风险检查记录 |
| Regulatory Compliance | 是否满足监管要求？ | 合规检查报告、审计日志 |
| Timeliness | 是否在延迟要求内完成？ | 订单提交到成交的延迟度量 |
| Auditability | 每个决策是否可追溯？ | 完整的决策链 + 数据依据 + 时间戳 |

## 失败分类

| 失败 | 表现 | 恢复策略 |
|---|---|---|
| Slippage Excess | 实际成交价远偏离预期 | 暂停执行 → 评估市场冲击 → 调整策略或升级人工 |
| Partial Fill | 订单仅部分成交 | 评估剩余数量 → 决策继续/撤销/调整价格 |
| Stale Price | 基于过期行情决策 | 刷新行情 → 重新评估信号 → 必要时取消订单 |
| Risk Limit Breach | 头寸或损失超过限额 | 立即冻结新订单 → 触发减仓/对冲 → 通知风控 |
| Exchange Connectivity Loss | 交易所连接中断 | 切换备用通道 → 检查挂单状态 → 暂停新订单 |
| Fat-Finger Order | 订单数量/价格明显异常 | pre-trade 检查拦截 → 如已发出则立即撤单 |
| Regulatory Violation | 违反头寸限制或交易规则 | 立即停止违规操作 → 生成违规报告 → 升级合规官 |
| Market Manipulation Detection | 交易模式疑似操纵市场 | 暂停策略 → 审查交易历史 → 升级合规 |
| Reconciliation Mismatch | 本地头寸与交易所不一致 | 暂停交易 → 全量对账 → 以交易所为准修正 |
| Looping | 策略反复触发矛盾信号 | 检测震荡 → 暂停策略 → 通知交易员 |

## 金融特有失败模式

### 滑点（Slippage）

```text
预期成交价与实际成交价的差异。在流动性不足或大单执行时尤为严重。
控制策略：TWAP/VWAP 分拆、限价单、滑点阈值保护。
```

### 部分成交（Partial Fill）

```text
订单仅成交一部分，剩余数量需要决策。
关键问题：剩余部分是否继续？是否调整价格？是否取消？
风险：如果是对冲单的部分成交，可能导致敞口不平衡。
```

### 市场冲击（Market Impact）

```text
大单执行本身推动价格向不利方向移动。
控制策略：分拆执行、时间加权、暗池路由。
度量：实际执行价 vs 决策时刻的中间价。
```

### 监管违规（Regulatory Violation）

```text
超过头寸限制、违反交易时间规则、涉嫌市场操纵。
后果：罚款、交易资格暂停、刑事责任。
控制策略：pre-trade 合规检查必须在交易路径上而非旁路。
```

## 任务分解原则

```text
Market Analysis：单步分析，ReAct 即可。
Signal Generation：策略评估 + 回测验证，需要多步证据收集。
Order Execution：pre-trade check → 下单 → 监控 → 成交确认 → 对账，严格流水线。
Portfolio Rebalancing：计算目标 → 生成交易清单 → 按优先级逐笔执行 → 验证偏差。
Risk Monitoring：持续循环，每个检测点独立但共享组合状态。
Compliance Checking：规则遍历 + 证据收集，可并行检查不同规则。
```

## 输出契约

最终回答至少包含：

```text
1. 执行了什么：订单/操作列表、成交明细
2. 验证了什么：对账结果、风险检查结果、合规状态
3. 成本和质量：滑点、交易成本、执行时间
4. 还剩什么：未成交订单、待确认操作、风险提示
5. 审计入口：完整交易日志、决策链、时间戳
```

相关：`../../evaluation/failure-taxonomy.md`、`../../design-space/methodology/autonomy-and-depth.md`、`../../design-space/lessons-learned/step-finance-40m-loss.md`。
