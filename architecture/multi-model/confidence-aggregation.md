# 多模型置信度聚合

> **Evidence Status** — mixed
> 来源：ensemble learning 理论、LLM-as-Judge 实践、multi-agent debate 研究（Du et al. 2023、Liang et al. 2023）；生产系统中多模型校验的工程经验。

## 1. 问题

当多个模型对同一问题给出不同答案时，系统应该如何决策？

```text
Planner (Model-A): "应该先查数据库，再调用 API"
Critic  (Model-B): "应该先调用 API，数据库查询可以延后"
Guard   (Model-C): "API 调用涉及敏感数据，需要先检查权限"
```

直觉性的"取多数"策略在很多场景下不够用。需要更系统化的聚合框架。

## 2. 聚合策略

### 2.1 投票 (Majority Voting)

```text
Model-A: 答案 X
Model-B: 答案 X
Model-C: 答案 Y
→ 选择 X（2:1）
```

| 优点 | 缺点 |
|---|---|
| 实现简单 | 不区分模型能力差异 |
| 对随机错误有鲁棒性 | 当所有模型共享同一类偏差时失效 |
| 适合有明确正确答案的场景 | 不适合开放性、创造性任务 |

适用场景：分类、事实判断、格式校验。

### 2.2 加权平均 (Weighted Aggregation)

按模型在该任务类型上的历史准确率加权：

```yaml
aggregation:
  weights:
    model_a: 0.45  # 历史准确率 90%
    model_b: 0.35  # 历史准确率 70%
    model_c: 0.20  # 历史准确率 40%
  method: weighted_vote
  threshold: 0.6   # 加权得分超过 0.6 才采纳
```

权重应动态更新 -- 模型在特定领域的表现会随时间变化。

### 2.3 级联 (Cascade)

先用小模型处理，不确定时升级到大模型：

```text
Step 1: Small model → 置信度 0.9 → 直接采纳
Step 1: Small model → 置信度 0.4 → 升级到 Large model
Step 2: Large model → 置信度 0.85 → 采纳
Step 2: Large model → 置信度 0.3 → 标记为 Uncertain，请求人工
```

级联的关键是小模型的**置信度校准** -- 如果小模型总是高置信但经常错，级联就失效了。

### 2.4 分歧保留 (Disagreement Preservation)

不强行合并，而是将分歧作为信号传递给下游：

```yaml
aggregation_result:
  consensus: false
  positions:
    - model: planner
      answer: "先查数据库"
      confidence: 0.7
      reasoning: "减少 API 调用次数"
    - model: critic
      answer: "先调 API"
      confidence: 0.6
      reasoning: "数据库可能有缓存延迟"
  recommended_action: escalate_to_human
  disagreement_type: strategy_conflict
```

## 3. 何时保留分歧而不强行合并

| 条件 | 原因 | 处理 |
|---|---|---|
| 高风险决策 | 错误代价大，不值得赌 | 向用户展示分歧，让人决定 |
| 主观判断 | 没有客观正确答案 | 展示多个选项及其理由 |
| 创造性任务 | 分歧本身可能激发更好的方案 | 保留所有方案供选择 |
| 信息不足 | 模型分歧可能源于信息缺口 | 先补充信息，再重新评估 |
| 安全相关 | Guard 模型的否决应具有一票否决权 | Guard 的 deny 不参与投票 |

## 4. 置信度校准

模型报告的"置信度"往往不可靠。需要校准：

### 4.1 校准方法

| 方法 | 说明 |
|---|---|
| 温度缩放 (Temperature Scaling) | 在验证集上学习最优温度参数 |
| 历史追踪 | 记录模型在每个置信度区间的实际准确率 |
| 对比校准 | 用已知答案的问题定期校准 |
| 自洽性检查 | 同一问题多次采样，一致性作为置信度代理 |

### 4.2 校准指标

```yaml
calibration_record:
  model_id: string
  task_type: string
  reported_confidence_bin: [0.8, 0.9]
  actual_accuracy: 0.72
  sample_size: 150
  last_updated: datetime
  calibration_gap: 0.13  # 过度自信 13%
```

## 5. 聚合策略选择指南

```text
任务有明确正确答案？
├── 是 → 有足够的历史数据？
│        ├── 是 → 加权投票
│        └── 否 → 简单投票
└── 否 → 任务风险高？
         ├── 是 → 分歧保留 + 人工决策
         └── 否 → 分歧保留 + 默认采纳最高置信度
```

```text
成本敏感？
├── 是 → 级联（小模型优先）
└── 否 → 并行投票（多模型同时运行）
```

## 6. 与其他模块的关系

### 与 Representation Plane

`../planes/representation/observation-semantics.md` 处理多源观察的融合（如 API 返回值 vs DOM 快照 vs 日志）。多模型置信度聚合是另一个层次的融合 -- 不是数据源不同，而是"解释者"不同。

两者适用相同的核心原则：

- 标注来源和置信度
- 冲突不静默合并
- 保留 raw evidence

### 与 Agent Epistemics

`../../concepts/agent-epistemics.md` 定义的 Conflicted 类型（多个来源冲突）正是多模型分歧的运行时表示。聚合策略决定了 Conflicted 状态何时被解消、何时被保留。

### 与 Control Plane

Policy Engine 可以定义聚合规则：

```yaml
policy:
  - when: guard_model_denies
    action: deny  # Guard 一票否决
  - when: models_disagree_on_high_risk
    action: escalate_to_human
  - when: all_models_agree
    action: accept_with_confidence_floor
```

## 7. 反模式

| 反模式 | 风险 |
|---|---|
| 无条件信任最强模型 | 最强模型也有系统性盲区 |
| 把 log-prob 直接当置信度 | 未校准的概率分布不可靠 |
| 分歧时总是取平均 | 平均值可能不在任何合理选项上 |
| 投票后丢弃少数意见 | 少数意见可能在特定上下文下更正确 |

## 延伸阅读

- `model-role-allocation.md` -- 角色分配决定了哪些模型参与聚合
- `../planes/representation/observation-semantics.md` -- 多源观察融合
- `../../concepts/agent-epistemics.md` -- Conflicted 类型的认识论处理
- `../planes/control/overview.md` -- Policy Engine 定义聚合规则
- `../planes/cost/model-routing.md` -- 级联策略的成本考量
