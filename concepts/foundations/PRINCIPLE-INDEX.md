# Principle Index -- 从哲学到运行时的编号原则体系

> **Evidence Status** — synthesized

本文件为每条基础哲学原则分配唯一 ID，并建立到 runtime schema 字段和 plane 的双向映射。用途：设计评审时按 ID 检索原则、故障排查时定位违反了哪条原则、新 plane 设计时确认覆盖了哪些原则义务。

---

## 快查表

| ID | 原则 | 主要影响 Plane |
|---|---|---|
| **BR-01** | Agent 必须在显式资源预算下运行 | Cost, Control, Context |
| **BR-02** | 上下文腐烂是结构性后果——信息会过期和丢失 | Context, World State, State |
| **BR-03** | 满意解优于最优解——预算内够好 > 超预算完美 | Cost, Control |
| **BDI-01** | 信念必须从观察构建，不可假设 | Representation, World State |
| **BDI-02** | 验证是信念修正机制，不是完成检查 | Effects, Control |
| **BDI-03** | 意图跨步持久但可被新证据修正 | State, Recovery |
| **IS-01** | Agent 操作的是表示，不是现实本身 | Representation, World State |
| **IS-02** | 工具成功是执行反馈，不是世界状态确认 | Effects, Execution, Control |
| **IS-03** | 地图（Agent 模型）与领地（外部世界）可能静默分离 | World State, Effects, Observability |
| **EM-01** | 工具是认知延伸，不是外部插件 | Tools, Execution |
| **EM-02** | Agent 能力 = 模型能力 × Harness 工程 | Tools, Prompting, Control |
| **EM-03** | 环境塑造并约束可能的行动 | Identity & Capability, Security, Execution |
| **MC-01** | Agent 必须显式表达不确定性，而非编造 | Representation, Interaction, Explainability |
| **MC-02** | 自我监控使提前终止和策略切换成为可能 | Control, Cost, Recovery |
| **MC-03** | 知道自己不知道什么 > 虚假自信 | Representation, Interaction |

---

## Bounded Rationality (BR-)

来源：`bounded-rationality.md` — Simon 有界理性、满意解、Harness 必然性

### BR-01 — Agent 必须在显式资源预算下运行

> 步数、token、时间、成本——所有资源都有上限。无上限的 Agent 不是更强，而是更危险。

**运行时义务**
- Harness **必须**在任务开始时注入 `ResourcePlan`，包含 `budget.max_cost`、`budget.max_tokens`、`budget.max_tool_calls`、`budget.max_latency_ms`。
- 每步循环**必须**检查剩余预算；预算耗尽时按 `stop_policy.budget_exhausted_behavior` 行动。
- Depth Budget 必须暴露给决策层，不可仅作为 Harness 内部参数。

**关联 schema 字段**
- `ResourcePlan.budget.*`
- `ResourcePlan.stop_policy.budget_exhausted_behavior`
- `TaskEnvelope`（任务边界）

**主要 Plane**：Cost, Control, Context

---

### BR-02 — 上下文腐烂是结构性后果

> 上下文窗口有限，信息会过期。这不是 bug，是有界理性在时间维度的必然表现。

**运行时义务**
- 所有 Observation **必须**携带 `freshness.observed_at` 和 `freshness.ttl`。
- `WorldStateSnapshot` **必须**标注 ttl；关键决策前 **必须** refresh 过期快照。
- Compaction 策略必须保留"足够做出下一步决策"的信息，而非追求全量保留。

**关联 schema 字段**
- `Observation.freshness.observed_at`、`.ttl`
- `WorldStateSnapshot`（tracked + ttl）
- `ContextPack`（ephemeral snapshot）

**主要 Plane**：Context, World State, State

---

### BR-03 — 满意解优于最优解

> 在有限资源下，找到第一个满足阈值的方案就停下来。停止条件是设计决策，不是妥协。

**运行时义务**
- `TaskEnvelope` **必须**定义 success criteria——什么算"够好"。
- `ResourcePlan.stop_policy` **必须**明确预算耗尽行为。
- 范式选择（paradigm-routing）应选"对当前任务够用"的最小范式，而非"最强"范式。

**关联 schema 字段**
- `TaskEnvelope`（success criteria）
- `ResourcePlan.stop_policy`
- `ResourcePlan.quality_target`

**主要 Plane**：Cost, Control

---

## BDI & Active Inference (BDI-)

来源：`bdi-and-active-inference.md` — BDI 模型、主动推断、ORDA-VU 认识论根基

### BDI-01 — 信念必须从观察构建，不可假设

> Observe → Represent 是信念的形成过程。跳过 Represent 就是把原始数据当作事实。

**运行时义务**
- 原始输入 **必须**经过 `Observation.transform_chain` 转换后才可进入决策。
- 每个 Observation **必须**携带 `confidence`、`trust.lane`、`trust.source_authority`。
- `WorldStateSnapshot` 的每个字段应可追溯到产生它的 Observation。

**关联 schema 字段**
- `Observation.transform_chain`、`.confidence`、`.trust`
- `Observation.raw_refs`
- `WorldStateSnapshot`

**主要 Plane**：Representation, World State

---

### BDI-02 — 验证是信念修正机制，不是完成检查

> Verify 回答的是"世界是否按预期改变了"，而非"工具是否返回了 200"。预测误差累积意味着世界模型已偏离现实。

**运行时义务**
- 每个 `ToolCall` **必须**声明 `intended_effect`（含 `postconditions`）。
- `EffectRecord` **必须**记录 `intended_effect` vs `actual_observation_refs` 的比较结果。
- `VerificationResult` **必须**写入显式状态（`verified | failed | partially_verified`），不可留空。
- 连续预测误差超过阈值时 **应该**触发策略调整（连接 MC-02）。

**关联 schema 字段**
- `ToolCall.intended_effect`、`.verification_method`
- `EffectRecord.verification_status`、`.verification_evidence`
- `VerificationResult`

**主要 Plane**：Effects, Control

---

### BDI-03 — 意图跨步持久但可被新证据修正

> 一旦形成意图，Agent 不需每步重新审视全部选项。但新证据（验证失败、环境变化）可以且应该触发意图修正。

**运行时义务**
- `Decision` 作为 append-only 日志记录意图形成和修正。
- `TaskCheckpoint` **必须**在关键决策点持久化，使恢复无需从头开始。
- `FailureRecord` 产生时 **必须**评估是否需要 `recovery_action: replan`。

**关联 schema 字段**
- `Decision`（append-only）
- `TaskCheckpoint`（tracked state）
- `FailureRecord.recovery_action`

**主要 Plane**：State, Recovery

---

## Intentional Stance (IS-)

来源：`intentional-stance.md` — Dennett 三种立场、拟人化陷阱、功能性目标

### IS-01 — Agent 操作的是表示，不是现实本身

> Agent 的"信念"是 World State 中的快照，不是外部世界的实时镜像。混淆二者是幻觉的根源。

**运行时义务**
- `WorldStateSnapshot` **必须**标注 `ttl`；消费方 **必须**检查是否过期。
- `Observation.trust.lane` **必须**区分 `trusted_data` 和 `generated_summary`、`inference`。
- 所有从 Memory 读取的信息 **应该**标注为推断或历史，而非当前事实。

**关联 schema 字段**
- `WorldStateSnapshot`（tracked + ttl）
- `Observation.trust.lane`
- `MemoryRecord`

**主要 Plane**：Representation, World State

---

### IS-02 — 工具成功是执行反馈，不是世界状态确认

> API 返回 200 ≠ 数据真的写入了。exit code 0 ≠ commit 真的存在。

**运行时义务**
- `ExecutionResult` 只记录工具返回；世界状态变更 **必须**通过独立的 `EffectRecord` + 验证确认。
- `ToolCall.verification_method` **必须**指定验证手段（`read_after_write | test | external_ack | human_confirm | sensor_readback`）。
- `EffectRecord.consistency_model` **必须**标注一致性模型（`strong | eventual | unknown`）。

**关联 schema 字段**
- `ExecutionResult`
- `EffectRecord.verification_status`、`.consistency_model`
- `ToolCall.verification_method`

**主要 Plane**：Effects, Execution, Control

---

### IS-03 — 地图与领地可能静默分离

> Agent 的世界模型可能在它不知情的情况下偏离外部现实。这种分离不会自动报错。

**运行时义务**
- 关键决策前 **必须**执行 refresh-before-act（重新观察而非依赖缓存）。
- `Observation.conflicts_with` 字段在新旧观察冲突时 **必须**被填充，不可静默覆盖。
- `TraceEvent` **应该**记录决策依赖的 WorldState 版本，支持事后审计地图-领地偏差。

**关联 schema 字段**
- `Observation.conflicts_with`
- `Observation.freshness`
- `TraceEvent`
- `WorldStateSnapshot`

**主要 Plane**：World State, Effects, Observability

---

## Embodiment & Situation (EM-)

来源：`embodiment-and-situation.md` — 具身认知、延展心智、情境认知

### EM-01 — 工具是认知延伸，不是外部插件

> 移除一个工具不是"少了一个功能"，而是"截断了一种认知能力"。工具不可用时 Agent 应评估影响并显式降级。

**运行时义务**
- 工具不可用时 **必须**产生 `FailureRecord`（category: `tool_error`），而非静默跳过。
- `InteractionEvent`（type: `escalation`）**应该**在关键工具缺失时通知用户能力降级。
- 工具返回值 **应该**结构化且包含足够上下文，支持高质量推理。

**关联 schema 字段**
- `FailureRecord`（category: `tool_error`）
- `InteractionEvent`（type: `escalation`）
- `ToolCall`、`ExecutionResult`

**主要 Plane**：Tools, Execution

---

### EM-02 — Agent 能力 = 模型能力 × Harness 工程

> 模型再强，Harness 设计差（prompt 模糊、无验证、无回退），Agent 表现也差。反之，好的 Harness 可以让弱模型做到更多。

**运行时义务**
- `PromptContract` **必须**明确 `reasoning_mode`、`output_contract`、`expected_failure_modes`。
- `ResourcePlan.routing` **应该**根据任务复杂度选择模型类别（`small | medium | large | specialist`）。
- Harness 设计评审应独立于模型评估——同一模型在不同 Harness 下表现可能完全不同。

**关联 schema 字段**
- `PromptContract.reasoning_mode`、`.output_contract`、`.debug.expected_failure_modes`
- `ResourcePlan.routing.default_model_class`

**主要 Plane**：Tools, Prompting, Control

---

### EM-03 — 环境塑造并约束可能的行动

> 可用工具、权限等级、执行环境（沙箱 vs 生产）、网络状况——这些情境因素动态决定 Agent 能做什么。

**运行时义务**
- `CapabilityGrant` **必须**在任务开始时注入，明确 `scope.resources`、`scope.actions`、`trust_level`。
- `CapabilityGrant.expires_at` 和 `approval_required_for` **必须**被运行时检查，不可仅做静态配置。
- 情境变化（权限撤销、工具下线）时 **必须**触发重新评估。

**关联 schema 字段**
- `CapabilityGrant.scope`、`.trust_level`、`.expires_at`
- `CapabilityGrant.approval_required_for`

**主要 Plane**：Identity & Capability, Security, Execution

---

## Metacognition (MC-)

来源：`metacognition.md` — 置信度校准、Depth 判断、策略选择意识

### MC-01 — Agent 必须显式表达不确定性，而非编造

> 过度自信（Confidence 总是 high、UnknownRecord 为空）是最隐蔽的元认知失败。不确定时说"不确定"比编造答案可靠得多。

**运行时义务**
- `Observation.confidence` **必须**基于多信号综合（证据数量、来源权威性、新鲜度、冲突），不可硬编码。
- `PromptContract.output_contract` **必须**定义 `uncertainty_format`——Agent 如何表达不确定。
- `InteractionEvent`（type: `clarification`、trigger: `uncertainty`）**应该**在置信度低于阈值时触发。

**关联 schema 字段**
- `Observation.confidence`
- `PromptContract.output_contract.uncertainty_format`
- `InteractionEvent`（trigger: `uncertainty`）

**主要 Plane**：Representation, Interaction, Explainability

---

### MC-02 — 自我监控使提前终止和策略切换成为可能

> 监控进度、资源消耗和预测误差趋势。连续失败时不要原地重试——切换策略。

**运行时义务**
- 循环中 **必须**追踪连续失败计数；超过 `retry_budget_remaining` 时 **必须**切换 `recovery_action`。
- `FailureRecord.recovery_action` **必须**支持策略升级路径（`retry → refresh → replan → escalate → stop`）。
- `ResourcePlan.routing.escalation_triggers` 和 `downgrade_triggers` **必须**被定义和检查。

**关联 schema 字段**
- `FailureRecord.retry_budget_remaining`、`.recovery_action`、`.status`
- `ResourcePlan.routing.escalation_triggers`、`.downgrade_triggers`
- `ResourcePlan.stop_policy`

**主要 Plane**：Control, Cost, Recovery

---

### MC-03 — 知道自己不知道什么 > 虚假自信

> Agent 应主动识别认知缺口——Unobserved、Stale、Conflicted、Low-confidence——并在决策前标记。

**运行时义务**
- `Observation.trust.source_authority` 为 `unknown` 或 `low` 时，**必须**在 Decide 阶段降低该信息的权重。
- `Observation.conflicts_with` 非空时，**必须**保留冲突记录而非静默合并。
- `InteractionEvent`（type: `clarification`）**应该**在关键认知缺口阻塞决策时触发。

**关联 schema 字段**
- `Observation.trust.source_authority`
- `Observation.conflicts_with`
- `InteractionEvent`（type: `clarification`、trigger: `uncertainty`）

**主要 Plane**：Representation, Interaction

---

## 交叉引用

### 原则间的依赖

```text
BR-02 (上下文腐烂) ──→ IS-03 (地图-领地分离) ──→ BDI-02 (验证即信念修正)
BR-01 (资源预算)   ──→ BR-03 (满意解)         ──→ MC-02 (策略切换)
BDI-01 (信念从观察构建) ──→ IS-01 (操作表示非现实) ──→ MC-01 (显式不确定)
EM-01 (工具是认知) ──→ EM-02 (能力=模型×Harness)
EM-03 (环境约束)   ──→ BR-01 (资源预算)
```

### 按 ORDA-VU 阶段索引

| ORDA-VU 阶段 | 主要原则 |
|---|---|
| Observe | BDI-01, EM-01, EM-03 |
| Represent | BDI-01, IS-01, MC-01, MC-03 |
| Decide | BR-01, BR-03, MC-02, BDI-03 |
| Act | EM-01, EM-02, EM-03, IS-02 |
| Verify | BDI-02, IS-02, IS-03 |
| Update | BDI-03, BR-02, IS-03 |

## 延伸阅读

- 各基础文件：`./bounded-rationality.md`、`./bdi-and-active-inference.md`、`./intentional-stance.md`、`./embodiment-and-situation.md`、`./metacognition.md`
- Runtime Data Model：`../../architecture/runtime-data-model.md`
- 认识论对象：`../agent-epistemics.md`
- 范式路由：`../../paradigms/paradigm-routing.md`
