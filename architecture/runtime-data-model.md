# Runtime Data Model

> **Evidence Status** — synthesized. 参考项目中的 tool schema、memory record、checkpoint、trace、compaction、policy、approval、execution result 等结构；本知识库对生产级 Agent 数据资产的统一 schema 抽象。

## 1. 数据对象总览

| 对象 | 类型 | 持久化 | 所属模块 | 用途 |
|---|---|---:|---|---|
| RawInputRef | immutable ref | 是 | Interface | 指向原始输入 |
| PerceptionEvent | event | 是 | Interface | 描述采集事件 |
| Observation | immutable/tracked | 是 | Representation | 机器可处理表示 |
| PromptContract | immutable snapshot | 是 | Prompting | 指令结构、输出契约和 few-shot 选择 |
| TaskEnvelope | immutable | 是 | Depth / Interface | 任务边界与权限 |
| ContextPack | ephemeral snapshot | 可选 | Context | 当前模型输入 |
| Decision | append-only | 是 | Kernel | 下一步意图 |
| CapabilityGrant | tracked | 是 | Identity & Capability | 授权来源、范围、期限、租户和委托链 |
| ToolCall | append-only | 是 | Tools | 结构化行动 |
| ExecutionResult | append-only | 是 | Execution | 工具/宿主返回 |
| EffectRecord | append-only | 是 | Effects | 预期和实际效果 |
| VerificationResult | append-only | 是 | Control | 验证结论 |
| FailureRecord | tracked | 是 | Recovery | 失败分类、影响范围和恢复策略 |
| InteractionEvent | append-only | 是 | Interaction | 用户中断、审批、教学、反馈 |
| AgentMessage | append-only | 是 | Orchestration | Agent 间通信协议 |
| ResourcePlan | stateless config | 是 | Cost | 成本预算、模型路由、缓存策略 |
| FlowRun | append-only | 是 | Dataflow | 批量、流式、管道任务的执行记录 |
| TaskCheckpoint | tracked state | 是 | State | 恢复任务 |
| WorldStateSnapshot | tracked + ttl | 是 | World State | 外部对象状态 |
| MemoryRecord | tracked state | 是 | Memory | 跨任务知识 |
| TraceEvent | append-only | 是 | Observability | 调试、审计、评估 |
| ConfigFingerprint | immutable identity | 是 | Operations | 行为配置追踪，不代表 skill 自身状态 |
| CandidateRecord | tracked | 是 | Learning & Adaptation | 候选经验、作用域、证据和失效条件 |

## 2. 关键 schema

### 2.1 Observation

```yaml
observation:
  observation_id: obs_...
  raw_refs: []
  modality: text | image | audio | video | event | structured_data
  transform_chain:
    - step: asr | ocr | html_parse | chunk | summarize | embed | rerank | normalize
      lossy: true
      confidence: 0.86
  payload: object
  confidence: 0.0-1.0
  freshness:
    observed_at: datetime
    happened_at: datetime|null
    ttl: duration|null
  trust:
    lane: trusted_instruction | user_instruction | trusted_data | untrusted_data | generated_summary | memory | inference
    source_authority: high | medium | low | unknown
  replayable: true
  conflicts_with: []
```

### 2.2 PromptContract

```yaml
prompt_contract:
  prompt_id: prompt_...
  purpose: plan | act | verify | summarize | recover | ask_user
  instruction_layers:
    system: ref
    developer: ref
    policy: ref
    task: ref
  reasoning_mode: direct | tool_use | react | plan_execute | reflection | critique
  few_shot_policy:
    selected_examples: []
    selection_reason: string
    excluded_examples: []
  output_contract:
    schema: object
    refusal_format: object
    uncertainty_format: object
  debug:
    expected_failure_modes: []
    prompt_risk: low | medium | high
```

### 2.3 CapabilityGrant

```yaml
capability_grant:
  grant_id: cap_...
  subject:
    kind: user | agent | service_account | tool | mcp_server
    id: string
  actor_on_behalf_of:
    user_id: string|null
    delegation_chain: []
  tenant_id: string|null
  scope:
    resources: []
    actions: read | propose | write | delete | send | deploy | purchase | verify | administer
    constraints: []
  trust_level: trusted_config | authenticated_user | delegated_agent | third_party_tool | untrusted_data
  expires_at: datetime|null
  approval_required_for: []
  audit_requirements: []
```

### 2.4 ToolCall and EffectRecord

```yaml
tool_call:
  tool_call_id: call_...
  tool_id: string
  args: object
  preconditions: []
  intended_effect:
    effect_type: read | write | send | delete | deploy | notify | move | compute
    target_objects: []
    postconditions: []
  reversibility: reversible | compensatable | irreversible | unknown
  verification_method: read_after_write | test | external_ack | human_confirm | sensor_readback | none
```

```yaml
effect_record:
  effect_id: eff_...
  tool_call_id: call_...
  intended_effect: object
  actual_observation_refs: []
  verification_status: unverified | verified | failed | partially_verified | pending | not_required
  verification_evidence: []
  consistency_model: strong | eventual | unknown
  compensation:
    available: true
    method: string|null
    executed: false
```

### EffectRecord 状态迁移

```text
unverified ──→ pending ──→ verified
    │              │           │
    │              ↓           ↓
    │          failed      （终态）
    │              │
    ↓              ↓
 expired     compensated
```

迁移规则：
- `unverified → pending`：Agent 发起验证请求（readback / test / sensor query）
- `pending → verified`：验证通过（postcondition 成立）
- `pending → failed`：验证失败（postcondition 不成立），触发 FailureRecord 创建
- `unverified → expired`：超过 TTL 未发起验证，标记为过期
- `failed → compensated`：补偿操作成功执行
- 时间约束：`pending` 状态最长保持 T_verify（由品类定义，默认 30s），超时自动转 `failed`

### 2.5 FailureRecord

```yaml
failure_record:
  failure_id: fail_...
  task_id: task_...
  phase: observe | represent | decide | act | verify | update | deliver
  category: parse_error | tool_error | timeout | stale_world_state | policy_block | effect_failed | partial_effect | conflict | user_interruption | budget_exhausted | unknown
  severity: low | medium | high | critical
  evidence_refs: []
  affected_objects: []
  reversibility: reversible | compensable | irreversible | unknown
  requires_new_evidence: bool
  recovery_action: retry | refresh | replan | compensate | rollback | ask_user | escalate | partial_deliver | stop
  retry_budget_remaining: integer
  status: open | recovering | recovered | escalated | stopped
```

### FailureRecord 状态迁移

```text
open ──→ retrying ──→ resolved
  │          │
  ↓          ↓
escalated  abandoned
```

迁移规则：
- `open → retrying`：Recovery 模块选择重试策略，消耗 retry budget
- `retrying → resolved`：重试成功
- `retrying → open`：重试失败，回到 open，再次评估策略
- `open → escalated`：retry budget 耗尽或风险过高，升级为人工处理
- `open/retrying → abandoned`：任务整体被取消或超时

### 2.6 InteractionEvent

```yaml
interaction_event:
  interaction_id: int_...
  task_id: task_...
  type: progress | approval_request | clarification | correction | teaching | refusal | escalation | completion
  trigger: risk | uncertainty | blocked | budget | milestone | user_initiated | policy
  message_summary: string
  information_density: low | medium | high
  required_response: none | approve | choose | provide_data | correct | confirm
  user_response: object|null
  state_update_refs: []
```

### 2.7 AgentMessage

```yaml
agent_message:
  message_id: msg_...
  conversation_id: conv_...
  sender_agent: string
  receiver_agent: string
  message_type: task_request | observation | claim | plan | result | conflict | arbitration | heartbeat | cancel
  payload: object
  evidence_refs: []
  world_state_refs: []
  authority_scope: read_only | propose | act | verify | arbitrate
  ttl: duration|null
  correlation_id: string
```

### 2.8 ResourcePlan

```yaml
resource_plan:
  plan_id: cost_...
  task_id: task_...
  quality_target: minimal | standard | high | critical
  budget:
    max_cost: number|null
    max_tokens: integer|null
    max_latency_ms: integer|null
    max_tool_calls: integer|null
  routing:
    default_model_class: small | medium | large | specialist
    escalation_triggers: []
    downgrade_triggers: []
  cache_policy:
    cacheable_observations: []
    cacheable_tool_results: []
    ttl_by_type: object
  stop_policy:
    budget_exhausted_behavior: ask_user | partial_deliver | stop | switch_strategy
```

## 3. 数据所有权规则

| 规则 | 含义 |
|---|---|
| Producer owns format | 谁生产对象，谁维护 schema 和兼容性 |
| Consumer cannot mutate source | 消费者只能引用或生成新对象，不能偷偷改原对象 |
| Append-only for audit objects | Decision、ToolCall、ExecutionResult、EffectRecord、Trace 不应覆盖 |
| Context is disposable | ContextPack 可重建，不应成为唯一事实来源 |
| Raw refs outrank summaries | 原始引用优先于摘要、压缩和模型推断 |
| Fresh observations outrank stale memory | 最新可信观察优先于长期记忆 |
| Verification writes explicit status | 未验证、部分验证、失败都必须显式记录 |
| Interaction is state-changing | 用户纠正、审批、教学会改变任务或记忆状态 |
| Cost is a design object | 成本预算不是日志字段，而是执行策略输入 |


### 2.9 CandidateRecord

```yaml
candidate_record:
  candidate_id: cand_...
  source: trace | user_correction | eval_failure | project_file | human_review
  scope: global | tenant | project | user | task_type
  content_type: convention | tool_recipe | prompt_fragment | recovery_strategy | memory | eval_fixture
  evidence_refs: []
  preconditions: []
  validation_required: []
  safety_checks: []
  activation_state: candidate | active | quarantined | retired
  invalidation_triggers: []
  last_validation_evidence: []
```

## 4. 数据流入口

对象流转、触发关系和生命周期见 `runtime-data-flow.md`。plane 之间的读写关系见 `plane-interaction-matrix.md`。
