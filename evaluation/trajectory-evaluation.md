# Trajectory Evaluation

> **Evidence Status** — grounded. Google Agents Companion (2025) 的 Trajectory Evaluation 框架；Gulli (2025) *Agentic Design Patterns* Ch19；AgentBench、τ-bench 等基准；本知识库 eval-framework 的补充。

## 定义

Trajectory Evaluation 评估 Agent 到达最终结果的**路径质量**，而非仅评估最终输出。它关心：
- Agent 选择了哪些动作
- 动作顺序是否合理
- 是否有冗余或遗漏步骤
- 工具使用是否高效

## 为什么需要轨迹评估

最终结果正确不代表过程合理：
- 同样正确的答案，一个用了 3 步，另一个用了 30 步
- 一个路径安全可控，另一个触发了不必要的高风险操作
- 一个路径成本 $0.02，另一个 $2.00

轨迹评估让开发者能：
1. Debug Agent 的决策过程
2. 发现效率瓶颈
3. 验证安全约束被遵守
4. 比较不同版本的行为变化

## 六维轨迹指标

| 指标 | 定义 | 适用场景 |
|---|---|---|
| **Exact Match** | 预测轨迹完全镜像参考轨迹 | 严格流程（合规、安全操作） |
| **In-Order Match** | 包含所有关键步骤且顺序正确，允许额外步骤 | 有序工作流 |
| **Any-Order Match** | 包含所有必要步骤，不要求顺序 | 并行或灵活流程 |
| **Precision** | 预测轨迹中有多少步是参考中存在的 | 检测冗余动作 |
| **Recall** | 参考轨迹中有多少关键步骤被预测包含 | 检测遗漏动作 |
| **Single-Tool Use** | 特定工具是否出现在轨迹中 | 验证 Agent 学会使用新工具 |

## 评估实施

### 1. 定义参考轨迹

```yaml
reference_trajectory:
  task_id: string
  steps:
    - action: tool_call | decision | observation
      tool_id: string | null
      args_pattern: object | null
      critical: boolean     # 是否为必须步骤
      order_sensitive: boolean
  acceptable_extra_steps: integer  # 允许的额外步骤数
  max_total_steps: integer         # 步数上限
```

### 2. 计算指标

```python
def trajectory_precision(predicted, reference):
    """预测轨迹中有多少步是相关的"""
    relevant = [s for s in predicted if s in reference]
    return len(relevant) / len(predicted) if predicted else 0

def trajectory_recall(predicted, reference):
    """参考轨迹中有多少关键步骤被捕获"""
    critical_ref = [s for s in reference if s.critical]
    captured = [s for s in critical_ref if s in predicted]
    return len(captured) / len(critical_ref) if critical_ref else 1.0

def in_order_match(predicted, reference):
    """关键步骤是否按正确顺序出现"""
    critical_ref = [s for s in reference if s.critical]
    pred_filtered = [s for s in predicted if s in critical_ref]
    return pred_filtered == critical_ref
```

### 3. 综合 Scorecard

```yaml
trajectory_scorecard:
  exact_match: float
  in_order_match: float
  any_order_match: float
  precision: float
  recall: float
  tool_coverage:
    - tool_id: string
      used: boolean
  step_count: integer
  cost: float
  wall_time: duration
  safety_violations: integer
```

## 多 Agent 系统的轨迹评估

多 Agent 轨迹更复杂，需要额外关注：

| 维度 | 评估问题 |
|---|---|
| Cooperation | Agent 之间是否有效协作 |
| Plan Adherence | 子 Agent 是否偏离主计划 |
| Agent Selection | 是否选择了正确的 Agent |
| Scalability | 增加 Agent 是否提升质量/效率 |
| Dead-end Detection | 子 Agent 是否陷入死循环 |

## 与现有评估框架的关系

| 现有模块 | Trajectory Eval 的补充 |
|---|---|
| `eval-framework.md` | 增加轨迹维度：不只评 what，也评 how |
| `tool-use-evals.md` | 工具选择精度和召回率的量化 |
| `execution-depth-evals.md` | 步数效率和深度预算遵守 |
| `cost-evals.md` | 轨迹长度直接影响成本 |
| `coding-agent-evals.md` | coding 任务的工具调用序列评估 |

## 局限性

- 需要参考轨迹，构造成本高
- 多种合理路径时 exact match 过于严格
- 无法评估创造性偏离是否有价值

## 补充方法

| 方法 | 适用 |
|---|---|
| Agent-as-Judge | 无参考轨迹时用 LLM 评估路径合理性 |
| Autorater + Rubric | 定义评分准则，用 LLM 打分 |
| Process-based Evaluation | 关注推理过程而非仅结果 |
| Human-in-the-Loop | 复杂/主观场景的人工校准 |

## LLM-as-a-Judge

用高能力 LLM 评估其他 Agent 的输出质量，替代或补充人工评估。

**评估维度**：Clarity & Precision / Neutrality & Bias / Relevance & Focus / Completeness / Appropriateness for Audience。

**评估方法对比**：

| 方法 | 优势 | 局限 |
|---|---|---|
| **Human Eval** | 捕获细微行为和主观质量 | 难以规模化、成本高、耗时 |
| **LLM-as-a-Judge** | 可扩展、一致、高效 | 可能遗漏中间步骤、受 LLM 能力限制 |
| **Automated Metrics** | 可扩展、客观 | 可能无法完整反映能力 |

最佳实践：三种方法分层使用——Automated Metrics 做门控过滤，LLM-as-a-Judge 做批量评估，Human Eval 做校准和边界案例。

## Contractor Model（承包商模型）

将 Agent 从不可预测的工具转化为可信赖、可问责的承包商。四大支柱：

1. **Formalized Contract**：详细规范的单一信息源，例如"20 页 PDF，欧洲 Q1 市场，5 个可视化，含同比对比，包括供应链风险评估"。
2. **Dynamic Negotiation**：Agent 可分析合同条款、标记歧义/风险。执行前解决误解。
3. **Quality-Focused Iterative Execution**：生成多方案 → 测试 → 评分 → 提交通过版本。优先正确性和质量，非低延迟。
4. **Hierarchical Decomposition**：主合同 → 子合同（项目管理模式）。每个子合同独立完整，可分配给专特化 Agent。

**与 eval-framework 的关系**：Contractor Model 的 "Contract" 可视为 eval case 的 `expected_output` 的强化版——不仅定义期望结果，还定义交付规范、范围和质量标准。

## Drift Detection（漂移检测）

监测 Agent 输出质量随时间衰减：

| 漂移类型 | 触发因素 | 检测方式 |
|---|---|---|
| 概念漂移 | 输入数据分布变化 | 输入特征分布监控 |
| 环境漂移 | 运营环境改变（API 变更、工具行为变化） | 工具成功率、API 响应变化监控 |
| 模型漂移 | 基础模型更新/退化 | 固定 benchmark 定期重跑 |

**实施建议**：定期在固定 fixture 集上运行 trajectory evaluation，绘制趋势图。当 precision/recall 跌破阈值时触发告警。

## 参考来源

- Google "Agents Companion" (2025): Evaluating Trajectory and Tool Use
- Gulli, A. (2025). *Agentic Design Patterns*, Ch19: Evaluation and Monitoring.
- Berkeley Function-Calling Leaderboard (BFCL)
- τ-bench: Common Tool-calling Mistakes
- AgentBench: End-to-end Agent Evaluation
