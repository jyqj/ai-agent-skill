# Error & Recovery Plane
>
> **所属域**：7. Lifecycle & Economics — 错误恢复与补偿
>
> **Evidence Status** — synthesized. 工具超时、LLM 输出不可解析、外部状态过期、写动作部分成功、长任务中断是 coding、workflow、browser、ops、research agent 中反复出现的共同失败模式；本文件将分散在 execution、effects、state、operations 中的恢复逻辑抽象为横切 plane。

**Principle Refs**: BDI-03, MC-02 — 意图跨故障持续存在且可修正；自监控检测失败并触发恢复

## 定义

Recovery Plane 管理 Agent 在失败时如何分类、止损、恢复、补偿和交付部分结果。它把失败当作一等运行时对象：每次失败都需要记录原因、影响范围、是否需要新证据、下一步恢复策略和停止条件。

```text
Failure observed
  → classify failure
  → assess risk and reversibility
  → choose recovery action
  → execute recovery under budget and policy
  → verify recovered state or surface partial delivery
  → update trace / state / eval fixture
```

## FailureRecord Schema

```yaml
failure_record:
  failure_id: string
  task_id: string
  phase: observe | represent | decide | act | verify | update | deliver
  category: parse_error | tool_error | timeout | stale_world_state | policy_block | effect_failed | partial_effect | conflict | user_interruption | budget_exhausted | unknown
  severity: low | medium | high | critical
  evidence_refs: []
  affected_objects: []
  reversibility: reversible | compensable | irreversible | unknown
  requires_new_evidence: bool
  recovery_action: retry | refresh | replan | compensate | rollback | ask_user | escalate | partial_deliver | stop
  retry_budget_remaining: integer
  compensation_refs: []
  status: open | recovering | recovered | escalated | stopped
```

## 错误分类与默认恢复

| 失败类型 | 典型表现 | 默认恢复 | 禁止做法 |
|---|---|---|---|
| parse_error | 模型输出不是目标 schema | 用结构化修复 prompt 重试一次 | 无限“请重新输出 JSON” |
| tool_error | 工具返回错误或异常 | 检查参数、前置条件、权限，再重试 | 不读错误详情直接换工具 |
| timeout | 工具或流程超时 | 退避、缩小范围、分片执行 | 原样快速重试导致放大负载 |
| stale_world_state | 快照过期或写前状态改变 | refresh world state，再 replan | 用旧快照继续写 |
| policy_block | 控制层拒绝动作 | 解释原因、降级为提案或请求审批 | 绕过 policy |
| effect_failed | 工具执行成功但后置条件不成立 | readback 诊断，补偿或 replan | 把 tool success 当作 done |
| partial_effect | 多步写入只成功一部分 | 进入 compensation stack | 再执行后续步骤掩盖问题 |
| conflict | 多 Agent / 多来源结果冲突 | 保留冲突，仲裁或请人确认 | 静默合并成单一结论 |
| budget_exhausted | token、费用、时间或工具次数耗尽 | partial deliver 或请求预算升级 | 继续消耗隐藏预算 |

## Recovery Budget

恢复必须有预算，否则系统会从“会自修复”退化成“会死循环”。

```yaml
recovery_budget:
  max_total_retries: 3
  max_same_action_retries: 1
  require_new_evidence_for_retry: true
  max_compensation_steps: 5
  escalation_after: high_severity | budget_exhausted | irreversible_risk
  partial_delivery_allowed: true
```

## 恢复动作的验证

恢复动作本身也必须被验证：

| 恢复动作 | 验证方式 |
|---|---|
| retry | 新 observation 与旧失败不同，或错误已消失 |
| refresh | WorldStateSnapshot 的 observed_at / freshness 已更新 |
| replan | 计划引用新证据，且旧失败原因被处理 |
| compensate | 外部对象回到可接受状态，或补偿状态已记录 |
| rollback | rollback 后 health/test/readback 通过 |
| ask_user | InteractionEvent 记录用户选择和授权范围 |
| partial_deliver | 未完成项、风险和阻塞原因明确列出 |

## 与其他 Plane 的关系

| Plane | Recovery 读取 | Recovery 写入 |
|---|---|---|
| Execution | ExecutionResult、stderr、timeout | retry / cancel / backoff |
| Effects | EffectRecord、postcondition | compensation / rollback result |
| World State | Snapshot freshness、conflict | refresh request |
| State | checkpoint、open step | FailureRecord、replan reason |
| Control | policy verdict、approval requirement | escalation request |
| Interaction | user interruption、correction | clarification / approval event |
| Observability | trace, spans | recovery span、failure label |
| Evaluation | failure taxonomy | regression fixture candidate |

## 评审清单

```text
[ ] 每类工具错误是否有分类，而不是只有 "failed"？
[ ] retry 是否要求新证据或参数变化？
[ ] 部分效果是否有 compensation stack？
[ ] 不可验证或不可逆动作是否会请求人工确认？
[ ] budget exhausted 时是否能诚实部分交付？
[ ] 失败 trace 是否能转化成 regression fixture？
```

FailureRecord 由 Recovery Plane 生成并记录，由 [Learning Plane](../../learning/incident-driven-evolution.md) 消费，用于驱动 Harness 演化和 eval fixture 扩张。

相关文件：`../../lifecycle.md`、`../effects/overview.md`、`../execution/overview.md`、`../operations/incident-response.md`、`../../../evaluation/failure-taxonomy.md`、`../../../design-space/anti-patterns/infinite-retry.md`。
