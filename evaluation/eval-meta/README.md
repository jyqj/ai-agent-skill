# Eval Meta-Evaluation

> **Evidence Status** — synthesized. 从 eval-framework.md 和 eval-runner 的设计中提炼出的自举性问题。eval 元评估在行业中尚无标准化实践。

## 1. 问题

评估框架能评估 Agent，但谁来评估评估框架本身？

当前评估体系存在三个自举问题：

1. **Fixture 覆盖率盲区**：fixture 是手工编写的，无法量化"还有多少重要场景没有覆盖"
2. **Eval 与生产的相关性**：eval 通过了不代表生产不会出问题
3. **Eval 漂移**：模型升级、工具变更、环境变化可能使旧 eval 不再有效

## 2. 覆盖率分析

### 2.1 覆盖率维度

```text
Fixture Coverage = f(品类覆盖, Plane 覆盖, 失败类型覆盖, 深度覆盖)

品类覆盖    = 有 fixture 的品类数 / 总品类数
Plane 覆盖  = 有 fixture 的 Plane 数 / 总 Plane 数
失败类型覆盖 = 有 fixture 的失败类型数 / failure-taxonomy 中的总类型数
深度覆盖    = 有 fixture 的执行深度级别数 / D0-D6 总级别数
```

### 2.2 覆盖率矩阵模板

| 维度 | 已覆盖 | 缺失 | 覆盖率 |
|---|---|---|---|
| 品类（11 类） | coding, research, browser, enterprise, memory, security | ops, data, companion, embodied, platform | 55% |
| Plane（25 个） | representation, effects, security, tools, memory | world-state, interaction, orchestration, cost, recovery... | ~25% |
| 失败类型 | tool_error, effect_failed, injection, ocr_parse | stale_snapshot, plan_expired, context_rot, budget_exceeded... | ~30% |
| 执行深度 | D2, D3, D4 | D0, D1, D5, D6 | 43% |

### 2.3 覆盖率提升优先级

```text
优先级 = 生产失败频率 × 影响严重度 × (1 - 当前覆盖率)
```

高优先级缺口（建议优先补充 fixture）：
1. 上下文窗口压力导致的质量下降（context_rot）
2. 长任务中断后的恢复（state_recovery）
3. 成本超限时的行为（budget_exceeded）
4. 多 Agent 协作中的通信失败（orchestration_failure）

## 3. 有效性回测

### 3.1 回测方法

将 eval 结果与真实生产行为做相关性分析：

```text
Eval Validity = correlation(eval_pass_rate, production_success_rate)

方法：
1. 收集最近 N 次部署的 eval 结果和生产指标
2. 计算 eval 通过率与生产成功率的相关系数
3. 分析 eval 通过但生产失败的案例（false negative）
4. 分析 eval 失败但生产正常的案例（false positive）
```

### 3.2 有效性指标

| 指标 | 定义 | 目标 |
|---|---|---|
| False Negative Rate | eval 通过但生产失败的比例 | < 10% |
| False Positive Rate | eval 失败但生产正常的比例 | < 20% |
| Correlation | eval 分数与生产指标的相关系数 | > 0.7 |
| Incident Coverage | 生产事故被 eval 预测到的比例 | > 60% |

### 3.3 回测触发条件

- 每次模型版本升级后
- 每次 eval fixture 批量更新后
- 生产出现 eval 未预测到的失败后
- 每季度定期回测

## 4. Eval 漂移检测

### 4.1 漂移类型

| 类型 | 原因 | 表现 |
|---|---|---|
| 模型漂移 | 模型升级改变了行为模式 | 旧 fixture 的通过率突变 |
| 工具漂移 | 外部工具 API 变更 | fixture 中的 mock 不再匹配真实行为 |
| 环境漂移 | 运行环境配置变化 | fixture 在新环境中行为不一致 |
| 标准漂移 | 用户期望或业务需求变化 | eval 通过但用户不满意 |

### 4.2 漂移检测方法

```text
DriftScore = |eval_result(t) - eval_result(t-1)| / baseline_variance

if DriftScore > threshold:
    flag_for_review(fixture, drift_type)
```

具体操作：
1. 每次 eval 运行记录完整结果快照
2. 与上次运行结果对比
3. 标记通过率变化 > 2σ 的 fixture
4. 人工复审被标记的 fixture

### 4.3 漂移修复流程

```text
检测到漂移
  → 分类漂移类型
  → 如果是模型漂移：更新 fixture 的期望行为，或调整 eval rubric
  → 如果是工具漂移：更新 mock world，或重新录制 fixture
  → 如果是环境漂移：修复环境配置，或增加环境约束
  → 如果是标准漂移：与用户确认新标准，更新 eval 目标
  → 记录变更原因到 eval changelog
```

## 5. Eval Changelog

每次修改 eval fixture 或评分标准时，记录变更：

```yaml
change_id: string
date: datetime
fixture_affected: list[string]
change_type: new_fixture | updated_expectation | removed | rubric_change
reason: model_upgrade | tool_change | false_negative_incident | coverage_gap
description: string
reviewed_by: string
```

## 6. 元评估仪表盘

建议追踪的顶层指标：

```text
┌─────────────────────────────────────────┐
│ Eval Health Dashboard                    │
├──────────────────┬──────────────────────┤
│ Fixture Count    │ 13 (+2 since last)   │
│ Coverage Score   │ 38% (target: 60%)    │
│ False Negative   │ 12% (target: <10%)   │
│ Drift Alerts     │ 2 pending review     │
│ Last Full Run    │ 2026-04-28           │
│ Last Backtest    │ 2026-03-15           │
│ Changelog Entries│ 7 this quarter       │
└──────────────────┴──────────────────────┘
```

## 7. 实施清单

```text
[ ] 建立覆盖率矩阵，标记当前缺口
[ ] 在 eval-runner 中增加结果快照存储
[ ] 实现 DriftScore 计算和告警
[ ] 建立 Eval Changelog 格式和流程
[ ] 定义回测触发条件和频率
[ ] 为最高优先级覆盖率缺口补充 fixture
[ ] 季度回测流程文档化
```

## 8. 与其他模块的关系

| 模块 | 关系 |
|---|---|
| `eval-framework.md` | 本文档评估 eval-framework 本身的健康度 |
| `eval-runner/` | 需要增加结果快照和漂移检测功能 |
| `failure-taxonomy.md` | 失败类型覆盖率的基准 |
| `fixtures/` | 被评估的对象 |
| `../../architecture/planes/operations/` | 模型升级和环境变更的信号来源 |
| `../../architecture/planes/observability/` | 生产指标的来源，用于有效性回测 |

## Evidence Status

理论框架。覆盖率分析、漂移检测和有效性回测的概念已在软件测试领域成熟，但在 Agent eval 领域尚未有标准化实践。本文档将这些概念适配到 Agent 评估的特定上下文。
