# Financial Trading Agent Closed Loop

> **Evidence Status** — synthesized. `architecture/lifecycle.md`、`architecture/kernel/agent-loop.md`、量化交易系统执行循环、交易所订单状态机与风控流水线实践。

## ORDA-VU for Financial Trading Agent

```text
Observe
  市场数据流（价格/订单簿/成交）、组合状态、风险信号、交易所状态、监管公告
Represent
  MarketDataSnapshot（ms 级新鲜度）、OrderBookDepth、PortfolioState、RiskMetrics、RegulatoryConstraint
Decide
  策略评估 → 信号生成 → pre-trade 风险检查 → 合规验证 → 执行策略选择
Act
  通过已验证交易所 API 提交订单（place / cancel / modify / hedge）
Verify
  成交确认 → 滑点检查 → 头寸对账 → 风险度量重算 → 合规状态更新
Update
  PortfolioState → P&L → RiskMetrics → StrategyState → 审计日志 → 告警（如需）
```

## Happy Path

```text
1. Market Data Intake
   - 接收实时行情 → 检查时间戳新鲜度 → 标准化 → 写入当前快照
   - 如果数据 stale → 标记 + 尝试备源 + 暂停依赖信号

2. Signal Generation
   - 基于当前快照 + 策略参数计算信号
   - 信号附带置信度 + 数据依据 + 时效性标记

3. Pre-Trade Risk Check
   - 检查项：头寸限额、集中度限制、保证金充足度、日内损失限制
   - fat-finger 检查：价格偏离市价 > N% 或数量 > 历史 P99 → 拦截
   - 合规检查：交易限制、禁止名单、报告义务
   - 任一检查未通过 → 阻断订单 + 记录原因 + 通知

4. Order Submission
   - 选择执行策略（直接 / TWAP / VWAP / 冰山）
   - 通过主连接提交 → 记录提交时间戳
   - 如果提交失败 → 尝试备连接 → 如果仍失败 → 暂停 + 告警

5. Fill Monitoring
   - 监控订单状态变更（submitted → partial_fill → filled / cancelled / rejected）
   - 成交回报 → 更新 OrderRecord → 计算滑点

6. Post-Trade Verification
   - 头寸对账：本地头寸 == 交易所查询头寸
   - 滑点检查：实际滑点 vs 预设阈值
   - P&L 更新：已实现 + 未实现
   - 风险度量重算：VaR、敞口、Greeks

7. State Update & Audit
   - 更新 PortfolioState、RiskMetrics、StrategyState
   - 写入不可变审计日志
   - 如果风险度量触发告警 → 进入风险处置流程
```

## Failure Loops

### Slippage Excess Loop

```text
实际滑点 > slippage_threshold
  → 暂停当前执行策略
  → 评估原因：流动性不足 / 市场快速变动 / 订单太大
  → 如果剩余未成交部分
      → 选项 A：撤销剩余 + 通知交易员
      → 选项 B：切换到更被动的执行策略（如限价单替代市价单）
      → 选项 C：等待市场回归后继续
  → 记录滑点事件到 effect ledger
  → 如果累计滑点 > daily_slippage_budget → 暂停该策略 + 升级
```

### Partial Fill Handling Loop

```text
订单部分成交
  → 记录已成交部分（价格、数量、时间）
  → 更新本地头寸（部分更新）
  → 评估剩余数量的处理策略：
      如果是独立订单：
        → 选项 A：维持挂单等待成交
        → 选项 B：调整价格追单
        → 选项 C：撤销剩余
      如果是对冲单：
        → 计算当前敞口不平衡
        → 如果敞口风险可接受 → 维持挂单
        → 如果敞口风险不可接受 → 市价补单（需审批）
  → 超时未成交 → 撤单 + 通知
```

### Exchange Connectivity Loss Loop

```text
交易所连接断开
  → 立即切换到备用连接
  → 查询所有挂单状态（可能在断连期间已成交/撤销）
  → 全量对账当前头寸
  → 如果备用连接也失败：
      → 进入安全模式（safe mode）
      → 暂停所有新订单
      → 启动挂单超时保护（如果交易所支持，设置 GTD/IOC）
      → 通知运维 + 交易员
      → 连接恢复后 → 全量对账 → 逐步恢复交易
```

### Fat-Finger Detection Loop

```text
订单提交前 fat-finger 检查：
  价格偏离当前市价 > N%
  OR 数量 > 历史单笔 P99 的 M 倍
  OR 金额 > 单笔阈值
    → 阻断订单
    → 标记为 fat-finger suspect
    → 请求人工确认：展示订单详情 + 市场当前状态 + 偏离度
    → 如果确认 → 放行 + 记录人工覆盖
    → 如果拒绝 → 取消 + 记录拦截事件

订单提交后异常检测：
  成交均价与提交价差异 > X%
    → 检查是否市场剧烈波动
    → 如果非市场原因 → 标记异常 + 通知运维
```

### Circuit Breaker Loop

```text
触发条件：
  - 单策略 30 分钟损失 > strategy_loss_limit
  - 全账户日内损失 > daily_loss_limit
  - 连续 N 笔交易亏损
  - 异常交易频率（短时间内下单次数 > frequency_limit）

触发动作：
  → 冻结该策略（或全账户）的新订单权限
  → 撤销所有该策略的活跃挂单
  → 计算当前头寸和风险敞口
  → 生成 circuit breaker report：
      - 触发原因 + 损失明细
      - 当前头寸 + 风险敞口
      - 建议处置方案
  → 通知风险经理 + 交易员
  → 恢复条件：人工审查 + 明确授权 + 策略参数调整
```

### Reconciliation Mismatch Loop

```text
对账发现差异（本地头寸 != 交易所头寸）
  → 暂停该标的的新订单
  → 拉取交易所完整交易历史
  → 对比本地 trade log vs 交易所 trade log
  → 定位差异源：
      漏记成交 → 补录 + 更新头寸
      幽灵成交 → 与交易所确认
      数量差异 → 以交易所为准修正 + 标记待查
  → 修正后重新验证头寸一致性
  → 记录差异事件到审计日志
  → 如果差异金额 > threshold → 升级调查
```

## Stop Gate

Financial Trading Agent 只有满足 stop gate，才能进入最终交付：

```text
[ ] 所有提交的订单已有最终状态（filled / cancelled / rejected）
[ ] 无孤立挂单（所有活跃订单在监控中）
[ ] 头寸对账通过（本地 == 交易所，或差异已标记和解释）
[ ] 风险度量在限额内（或超限已告警并获人工确认）
[ ] 合规检查通过（无未处理违规）
[ ] 滑点和交易成本在预期范围内（或偏差已解释）
[ ] 所有交易动作已记入不可变审计日志
[ ] 高风险操作已获人工审批记录
```

## Verification Strategy

| 验证 | 适合 | 证据 |
|---|---|---|
| 成交确认 | 所有订单 | 交易所回报 + order_id + fill_id |
| 头寸对账 | 每笔成交后 + 每日定时 | 本地头寸 vs 交易所查询 |
| 滑点检查 | 每笔成交 | 决策价 vs 成交均价 |
| 风险限额检查 | 每笔交易前后 | 风险度量 vs 限额配置 |
| 合规检查 | 每笔交易前 + 每日 | 规则引擎输出 + 违规清单 |
| P&L 核对 | 每日 | 本地计算 vs 交易所报告 vs 清算报告 |
| 延迟监控 | 持续 | 下单到成交的时间 + 行情延迟 |
| 备源验证 | 持续 | 主备行情源价差 < threshold |

## Final Response Contract

```text
Execution Summary
- 执行的交易清单（标的、方向、数量、成交价）

Position Update
- 交易前后头寸对比
- 对账状态

Performance Metrics
- 滑点（每笔 + 加权平均）
- 交易成本（手续费 + 滑点成本）
- 执行时间

Risk Status
- 当前风险度量（VaR、敞口、回撤）
- 是否在限额内
- 风险告警（如有）

Compliance Status
- 合规检查结果
- 违规事项（如有）

Open Items
- 未成交订单
- 待确认事项
- 后续建议
```

## 与范式层的关系

- 外层：ORDA-VU。
- 策略评估和信号生成：ReAct。
- 多步执行（如组合再平衡）：Plan-and-Execute。
- 异常诊断和故障恢复：Reflection bounded by market data / execution evidence。
- 所有交易动作：Control + Pre-trade Risk Check + Post-trade Verification。
- 高风险操作：Human-in-the-loop Approval。

相关：`../../paradigms/reasoning-paradigms.md`、`../../paradigms/control-paradigms.md`、`../../architecture/lifecycle.md`。
