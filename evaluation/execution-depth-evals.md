# Execution Depth Evals

> **Evidence Status** — synthesized. 评估框架与场景来自多个产品形态的共性需求。

执行深度评估不看 Agent “回答得像不像完成”，而看它是否真的推进到要求深度，并留下足够证据。

## 1. 核心指标

| 指标 | 含义 | 目标 |
|---|---|---|
| Required Depth Match | 实际达到深度是否满足 required_depth | 不低于目标深度 |
| Milestone Completion Rate | 里程碑完成比例 | 高 |
| Verification Coverage | 有验证的 milestone 比例 | D4+ 接近 100% |
| Evidence Completeness | 最终输出证据是否完整 | 高 |
| Recovery Success Rate | 失败后换策略并恢复的比例 | 高 |
| Repeated Failure Rate | 同一失败重复发生比例 | 低 |
| Context Survival Rate | 压缩/恢复后关键事实保留比例 | 高 |
| Approval Efficiency | 用户审批是否必要且合并合理 | 高 |
| Cost-to-Depth Ratio | 达到目标深度所需成本 | 合理 |

## 2. Eval Case 模板

```yaml
case_id: coding_fix_auth_refresh
product_type: coding_agent
required_depth: D5
task: Fix token refresh failure in login flow
initial_context:
  - repo_snapshot
  - failing_test_hint
success_criteria:
  - identifies relevant files
  - edits minimal code path
  - runs targeted tests
  - explains diff and risk
injected_failures:
  - first test command fails due to wrong path
expected_recovery:
  - locate correct test command
  - retry with corrected path
scoring:
  depth_reached: 0-6
  milestone_completion: 0-1
  verification_coverage: 0-1
  recovery_quality: 0-1
  final_evidence: 0-1
```

## 3. 深度专项测试集

| 测试 | 检查什么 |
|---|---|
| Shallow Trap | 用户要求“帮我修”，Agent 是否只给建议 |
| Tool Failure Recovery | 工具失败后是否分类并换策略 |
| Context Compression Survival | 压缩后是否保留目标、约束、失败尝试 |
| Approval Boundary | 高风险动作是否请求审批，低风险动作是否批处理 |
| Multi-Worker Merge | 多 Worker 输出是否能合并并处理冲突 |
| Evidence Delivery | 最终是否包含行动、验证、风险和未解决项 |
| Budget Exhaustion | 预算耗尽时是否能停止并交付部分证据 |

## 4. 评分 Rubric

| 分数 | 表现 |
|---|---|
| 0 | 没有理解任务或完全不执行 |
| 1 | 只回答建议，无工具/证据 |
| 2 | 做了少量检查，但无计划或验证 |
| 3 | 有计划和产物，但未执行真实动作 |
| 4 | 执行了真实动作，但验证不足 |
| 5 | 执行并验证，能处理简单失败 |
| 6 | 多阶段推进、checkpoint、恢复、证据完整 |

## 5. 最终交付检查

```text
[ ] 是否声明 required_depth 和 reached_depth？
[ ] 是否列出完成的 milestone？
[ ] 是否列出工具动作和产物？
[ ] 是否列出验证结果？
[ ] 是否列出失败尝试和恢复策略？
[ ] 是否列出剩余风险？
[ ] 是否说明是否需要用户下一步确认？
```
