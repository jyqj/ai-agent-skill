# Causal World Model

> **Evidence Status** — synthesized. 从 world-state/overview.md 的快照模型出发，结合 Ops/SRE Agent（因果诊断）、Coding Agent（修改影响预测）、Embodied Robot Agent（物理因果链）的需求扩展。因果世界模型在 Agent 领域仍处于前沿探索阶段。

## 1. 问题

`overview.md` 定义的 WorldStateSnapshot 是**快照式**设计，回答"对象现在是什么状态"，但不回答：

- **如果我做了 A，对象 B 会怎样变化？**（前向因果）
- **对象 B 变成这样，是因为谁做了什么？**（回溯因果）
- **如果我选了另一条路，会发生什么？**（反事实推理）
- **在我行动期间，其他 actor 会改变什么？**（环境动力学）

这四个能力在 D4+ 长任务中直接影响规划质量和风险评估。

## 2. 扩展模型

```text
WorldModel = WorldStateSnapshot          ← 已有：对象当前状态
           + CausalEdge[]                ← 新增：动作→效果的因果边
           + DynamicsEstimate[]          ← 新增：外部变化的预测
           + CounterfactualEvaluation[]  ← 新增：备选方案的预期结果
```

### 2.1 CausalEdge

记录"动作→效果"的经验性因果关系。

```yaml
edge_id: string
action_type: string           # e.g. "git_push", "api_call", "file_edit"
precondition:
  object: string
  required_state: object
effect:
  object: string
  expected_state_change: object
side_effects:                  # 副作用传播
  - object: string
    expected_change: object
    confidence: float
confidence: float              # 0.0-1.0
evidence_source: observed | documented | inferred
observed_count: int            # 被观察到多少次
last_observed: datetime
failure_rate: float            # 历史失败比例
```

**关键约束**：
- 因果边是从 EffectRecord 历史中归纳的经验性关系，而非硬编码规则
- 每条边必须有 `evidence_source` 和 `confidence`
- `inferred` 类型的边置信度上限为 0.6

### 2.2 DynamicsEstimate

预测"在我行动期间，外部世界如何变化"。

```yaml
estimate_id: string
target_object: string
predicted_change: object
time_horizon: duration         # 预测时间窗口
probability: float
basis: historical_pattern | scheduled_event | concurrent_actor | unknown
invalidated_by: list[string]   # 哪些事件会使此预测失效
```

**使用场景**：
- Ops Agent：预测告警是否会自动恢复
- Coding Agent：预测 CI 队列是否会堵塞
- Browser Agent：预测页面元素是否会异步加载
- Enterprise Agent：预测审批人是否在线

### 2.3 CounterfactualEvaluation

在 Plan-and-Execute 的规划阶段，评估"如果选择了另一条路"。

```yaml
evaluation_id: string
decision_point: string         # 在哪个决策点
chosen_action: string
alternative_actions:
  - action: string
    expected_outcome:
      target: string
      expected_state: object
    expected_cost: float
    expected_risk: string
    confidence: float
comparison_basis: causal_edge | llm_inference | historical_analogy
```

**关键约束**：
- 反事实推理结果只用于辅助决策，不作为事实
- 必须标注 `comparison_basis`
- LLM 推断的反事实评估置信度上限为 0.5

## 3. 因果图的构建

因果图通过**渐进式**积累构建：

### 3.1 来源

| 来源 | 构建方式 | 置信度 |
|---|---|---|
| EffectRecord 历史 | 从 action→effect 对中统计归纳 | high（observed） |
| 工具文档 / API spec | 从 precondition/postcondition 提取 | medium（documented） |
| LLM 推断 | 让模型推断未观察到的因果关系 | low（inferred） |
| 用户教学 | 用户通过 Interaction 告知因果关系 | medium-high（documented） |

### 3.2 维护

```text
CausalEdge 生命周期：
  创建 → 观察验证 → 置信度上升 → 定期衰减 → 矛盾时降级 → 长期未观察时归档
```

- 每次 EffectRecord 匹配已有因果边，该边的 `observed_count` +1，`confidence` 按贝叶斯更新
- 每次 EffectRecord 与预期不符，该边的 `failure_rate` 更新
- `failure_rate > 0.3` 的边降级为 `needs_review`
- `last_observed` 超过 TTL 的边降级为 `stale`

## 4. 有限因果推理

目标是在关键决策点支持**有限因果推理**，而非构建完美的物理模拟器。

### 4.1 推理场景

| 场景 | 推理深度 | 示例 |
|---|---|---|
| 单步影响预测 | 1-hop | "如果我编辑 config.py，哪些测试可能失败？" |
| 多步因果链 | 2-3 hop | "如果我修改 API schema → 客户端会报错 → CI 会失败" |
| 副作用检测 | 1-hop side_effects | "git force-push 会影响其他人的本地分支" |
| 回滚可行性 | 反向遍历 | "删除文件后能否通过 git checkout 恢复？" |

### 4.2 推理限制

```text
最大推理深度 = 3 hop
最大副作用扇出 = 5
低于 confidence 0.3 的边不参与推理
inferred 类型的边最多参与 1 hop
```

超出这些限制时，Agent 应该：
1. 明确告知用户"无法可靠预测更远的影响"
2. 建议分步执行 + 逐步验证
3. 或请求人工评估

## 5. 与已有模块的关系

| 模块 | 关系 |
|---|---|
| `world-state/overview.md` | CausalEdge 建立在 WorldStateSnapshot 之上，不替代它 |
| `effects/overview.md` | EffectRecord 是因果边的主要证据来源 |
| `state/overview.md` | TaskState 的 checkpoint 应包含当前因果图的关键路径 |
| `recovery/overview.md` | 回滚可行性分析依赖反向因果遍历 |
| `cost/overview.md` | CounterfactualEvaluation 的 expected_cost 用于预算规划 |
| `learning-adaptation/` | 因果边的积累是一种经验学习 |
| `../../../paradigms/paradigm-routing.md` | 因果推理失败可以作为范式切换的触发信号 |

## 6. 常见失败

| 失败 | 表现 | 修复 |
|---|---|---|
| 因果幻觉 | Agent 编造不存在的因果关系 | 所有因果边必须有 evidence_source |
| 过度推理 | 推理链太长导致错误累积 | 限制推理深度和置信度阈值 |
| 确定性偏差 | 把低置信度因果当成确定规则 | UI/输出中明确显示置信度 |
| 遗忘副作用 | 只看直接效果，忽略 side_effects | 推理时强制检查 side_effects 扇出 |
| 因果图膨胀 | 边数无限增长 | TTL + 归档 + 定期裁剪低频边 |

## 7. 实施建议

```text
Phase 1（MVA-3/4）：
  - 只实现 1-hop CausalEdge，从 EffectRecord 自动归纳
  - 副作用检测限于工具文档中的显式声明
  - 不实现 DynamicsEstimate 和 CounterfactualEvaluation

Phase 2（MVA-5）：
  - 增加 2-3 hop 因果链
  - 增加 DynamicsEstimate（基于历史模式）
  - 增加简单的 CounterfactualEvaluation（基于因果边）

Phase 3（MVA-6）：
  - LLM 辅助因果推断（带置信度上限）
  - 多 Agent 共享因果图
  - 因果边的自动验证和修正
```

## Evidence Status

理论框架。CausalEdge 的基本概念在 Ops/SRE Agent 的根因分析和 Coding Agent 的影响分析中有间接实践，但完整的因果世界模型尚未在参考项目中被显式实现。
