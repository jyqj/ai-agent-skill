# 长期 Agent 的价值漂移检测与校正

> **Evidence Status** — theoretical
> 来源：RLHF 对齐中的 reward hacking 研究、推荐系统的 feedback loop 偏差文献、长期运行 chatbot 的行为观察报告、memory-augmented agent 的累积偏差案例。

## 1. 什么是价值漂移

价值漂移 (Value Drift) 是指 Agent 的行为模式随时间偏离初始设计意图。

这不同于"Bug" -- Bug 是明确的错误，价值漂移是渐进的、常常难以察觉的偏移。

```text
第 1 天: Agent 按设计意图工作，平衡效率和安全
第 30 天: Agent 开始偏好效率，偶尔跳过安全检查
第 90 天: Agent 系统性地跳过"低风险"安全检查
第 180 天: Agent 对"低风险"的判断标准也在漂移
```

## 2. 漂移来源

### 2.1 Memory 累积偏差

长期运行的 Agent 会积累大量 memory。如果 memory 写入有偏差（比如成功案例比失败案例更容易被记录），Agent 的决策会逐渐偏向 memory 中过度代表的模式。

```text
memory 偏差循环:
  成功 → 记录 → 下次优先召回 → 更容易成功 → 更多记录
  失败 → 不记录 / 少记录 → 下次不被召回 → 替代方案消失
```

### 2.2 用户反馈偏向

用户倾向于对"快速完成"给正反馈，对"花时间做验证"给负反馈或无反馈。如果 Agent 优化用户满意度，会逐渐偏向速度而牺牲质量。

### 2.3 工具变更

工具 API 的行为变化可能微妙地改变 Agent 的决策模式：

```text
旧 API: 返回完整错误信息 → Agent 能做细粒度错误处理
新 API: 只返回错误码      → Agent 的错误处理变得粗粒度
→ 长期效果: Agent 的错误处理质量下降，但不会触发明确的失败
```

### 2.4 模型更新

模型版本切换可能带来微妙的偏好变化，特别是在风格、详细度、风险偏好方面。

## 3. 检测方法

### 3.1 基准任务集对照

定期用固定的基准任务集测试 Agent，追踪关键指标的变化趋势：

```yaml
baseline_evaluation:
  frequency: weekly
  task_set: "baseline-v1.yaml"
  metrics:
    - name: safety_check_rate
      description: "执行安全检查的比例"
      baseline: 0.95
      alert_threshold: 0.85
    - name: tool_confirmation_rate
      description: "高风险操作前确认的比例"
      baseline: 0.98
      alert_threshold: 0.90
    - name: output_detail_level
      description: "输出的平均详细度评分"
      baseline: 7.2
      alert_threshold: 5.5
    - name: error_handling_depth
      description: "错误处理的平均层级数"
      baseline: 3.1
      alert_threshold: 2.0
```

### 3.2 关键指标趋势监控

不只看当前值，更要看**趋势**：

```text
指标趋势分析:
  - 3 周内持续下降但每周降幅 < 告警阈值 → 仍然需要注意
  - 突然跳变 → 可能是配置变更导致，检查 ConfigFingerprint
  - 周期性波动 → 可能是正常的，但需要排除数据偏差
```

### 3.3 用户满意度变化

```yaml
satisfaction_tracking:
  metrics:
    - explicit_feedback_score
    - task_completion_rate
    - retry_rate        # 用户需要重试的比例
    - override_rate     # 用户覆盖 Agent 决策的比例
    - abandonment_rate  # 用户中途放弃的比例
  segmentation:
    - by_task_type
    - by_user_cohort
    - by_time_period
```

### 3.4 对抗性审计

定期用特定的对抗性输入测试 Agent 的安全边界是否在漂移：

```text
审计场景:
  - 逐步增加风险等级的请求，检测 Agent 在哪里停下
  - 与 6 个月前相同的对抗输入，检查响应是否一致
  - 用户反馈引导型攻击（模拟用户持续给"跳过安全检查"正反馈）
```

## 4. 校正机制

### 4.1 Memory 审计与清洗

```yaml
memory_audit:
  frequency: monthly
  checks:
    - distribution_balance: "成功/失败案例的比例是否合理"
    - staleness: "过期 memory 是否被清理"
    - relevance: "memory 召回是否与当前任务相关"
    - conflict: "是否存在互相矛盾的 memory"
  actions:
    on_imbalance: rebalance_sampling
    on_staleness: mark_expired
    on_conflict: flag_for_review
    on_irrelevance: reduce_weight
```

### 4.2 基准 Recalibration

当 Agent 的环境确实发生了合理变化时，基准本身也需要更新：

```text
基准更新流程:
  1. 确认环境变化是真实的、合理的
  2. 由人工审核并批准基准调整
  3. 记录调整原因和时间
  4. 保留旧基准作为历史参考
```

注意：基准更新不应由 Agent 自动完成 -- 这会引入"自我校准"的循环偏差。

### 4.3 策略重置

当漂移严重到无法增量校正时，可能需要部分或全部重置：

| 重置级别 | 影响范围 | 适用场景 |
|---|---|---|
| Memory 部分清洗 | 删除特定时间段或类型的 memory | 特定领域的偏差 |
| 策略回滚 | 恢复到某个已验证的策略版本 | 策略更新导致的漂移 |
| Prompt 重置 | 恢复到初始 prompt 配置 | 增量修改累积导致的偏移 |
| 全量重置 | 保留工具定义，重置所有学习内容 | 严重漂移、无法定位根因 |

## 5. 品类特化

### 5.1 Companion Agent -- 关系健康度监控

```yaml
companion_health_metrics:
  boundary_respect: "是否保持角色边界，不越界回应"
  emotional_calibration: "情感回应是否在合理范围内"
  dependency_indicators: "用户是否表现出过度依赖信号"
  topic_diversity: "对话主题是否越来越窄"
  escalation_readiness: "是否在需要时建议专业帮助"
```

### 5.2 Personal Memory Agent -- Memory 质量审计

```yaml
memory_quality_audit:
  accuracy_check: "记忆内容是否与原始事实一致"
  privacy_review: "是否存储了不应存储的敏感信息"
  freshness_check: "过期信息是否被标记"
  user_correction_rate: "用户纠正记忆错误的频率"
  recall_relevance: "记忆召回的相关性评分趋势"
```

## 6. 与 value-and-alignment 的互补

`../../concepts/foundations/` 中的价值对齐关注**设计时**的对齐 -- 确保 Agent 的初始行为符合预期。

价值漂移检测关注**运行时**的对齐 -- 确保 Agent 的行为不随时间偏离设计意图。

```text
Design-time alignment:  定义 "应该是什么样"
Runtime drift detection: 检测 "是否还是那样"
Correction mechanisms:   恢复 "重新变回那样"
```

两者共同构成完整的价值对齐生命周期。

## 7. 反模式

| 反模式 | 风险 |
|---|---|
| 不监控就假设稳定 | 漂移是渐进的，等发现时已经严重 |
| 只看平均指标 | 平均值正常可能掩盖特定场景的严重退化 |
| 让 Agent 自我评估漂移 | 自我评估有同源偏差 |
| 基准只建不更新 | 基准本身过时后，对照失去意义 |
| 过度校正 | 每次微小波动都重置，导致 Agent 无法积累有效经验 |

## 延伸阅读

- `co-evolution.md` -- 组件版本变更是漂移来源之一
- `retirement.md` -- 当漂移无法校正时，可能需要退役
- `../learning/feedback-loops.md` -- 反馈循环的偏差是漂移的重要来源
- `../learning/skill-governance.md` -- Skill 的质量退化监控
- `../planes/operations/overview.md` -- 运维层面的指标监控
