# Runtime Data Flow

> **Evidence Status** — synthesized. runtime-data-model、agent-loop、effects、world-state、observability 与 eval-runner 中的数据对象归纳；用于补足“对象列表”之外的数据流、触发关系和生命周期。

## 主数据流

```text
RawInputRef
  → Observation
  → TaskEnvelope
  → PromptContract + ContextPack
  → Decision
  → PolicyVerdict / SecurityVerdict / ResourceDecision
  → ToolCall
  → ExecutionResult
  → EffectRecord / VerificationResult
  → TaskCheckpoint + WorldStateSnapshot + TraceEvent
  → InteractionEvent / AgentMessage / EvalCaseCandidate
  → Deliverable
```

## 触发关系

### Gateway Boundary

多平台 Agent 先经过 gateway 边界，再进入通用 Agent run：

```text
PlatformEvent → SessionEnvelope → GatewayPolicy → AgentRun
```

其中 `SessionEnvelope` 负责身份、平台、会话、线程、交付目标和媒体引用；`GatewayPolicy` 负责平台权限、审批通道、PII 策略和中断/排队规则。Gateway 是 Interface、Identity、Control、Interaction 的组合边界，不只是 UI 适配器。

| 对象变化 | 触发什么 | 原因 |
|---|---|---|
| RawInputRef 新增 | Representation build | 原始输入必须转成可处理表示 |
| Observation confidence 低 | Interaction 或 extra tool read | 低置信不应直接进入最终结论 |
| TaskEnvelope risk 升高 | Control / Approval gate | 高风险动作需要更强授权 |
| ContextPack 压缩 | Trace compaction event | 防止压缩后证据不可回查 |
| WorldStateSnapshot 过期 | refresh 或 stop gate | 不能用过期状态执行写动作 |
| ToolCall 被拒绝 | InteractionEvent 或 partial deliver | 用户需要知道阻塞原因 |
| ExecutionResult 成功但 postcondition 未达成 | EffectRecord failed + Recovery | 工具成功不等于现实成功 |
| EffectRecord partially_verified | Compensation 或 human confirm | 防止 partial effect 被误报完成 |
| FailureRecord repeated | Eval fixture candidate | 重复失败应进入回归 |
| User correction | TaskState / Memory candidate | 纠错改变当前任务或候选学习内容 |

## 生命周期

| 对象 | 创建 | 更新 | 过期/归档 | 不变量 |
|---|---|---|---|---|
| RawInputRef | Interface | 不更新，只追加 | 任务归档后仍可引用 | raw ref 不被摘要替代 |
| Observation | Representation | 可追加 transform | freshness TTL 到期 | 有 source、trust、confidence |
| TaskEnvelope | Intake / depth controller | 用户改目标或权限时更新 | 任务结束 | success criteria 明确 |
| ContextPack | Context builder | 每轮可重建 | 每轮后可丢弃 | 不是事实来源 |
| Decision | Kernel | append-only | trace 归档 | 有输入 refs 和 reason |
| ToolCall | Tool runtime | append-only | trace 归档 | 有 tool schema 和 risk |
| ExecutionResult | Execution host | append-only | trace 归档 | 不直接等同完成 |
| EffectRecord | Effects plane | 验证状态可变更 | verified/failed 后归档 | 写动作必须关联 effect |
| WorldStateSnapshot | World-state plane | refresh 生成新快照 | TTL 到期 | 有 observed_at 和 source |
| TaskCheckpoint | State plane | 每里程碑更新 | 任务关闭后归档 | 可恢复，不依赖上下文 |
| FailureRecord | Recovery plane | 状态可更新 | recovered/stopped 后归档 | 有分类和下一步 |
| TraceEvent | Observability | append-only | eval/incident 使用 | 能重放关键路径 |

## 数据所有权

| Producer | 拥有对象 | Consumer 不应做什么 |
|---|---|---|
| Interface | RawInputRef | 不应丢弃 raw 引用 |
| Representation | Observation | 不应把模型推断写回 observation |
| Context | ContextPack | 不应把 ContextPack 当长期状态 |
| Kernel | Decision | 不应直接执行动作 |
| Tools | ToolCall | 不应伪造执行结果 |
| Execution | ExecutionResult | 不应声明业务完成 |
| Effects | EffectRecord | 不应跳过验证状态 |
| World State | WorldStateSnapshot | 不应无 TTL 复用 |
| State | TaskCheckpoint | 不应存储无 provenance 结论 |
| Observability | TraceEvent | 不应把 trace 当用户可见解释的唯一来源 |

## 最小 Trace 要求

```yaml
trace_event:
  event_id: string
  task_id: string
  phase: observe | represent | decide | act | verify | update | recover | deliver
  timestamp: datetime
  input_refs: []
  output_refs: []
  actor_ref: string
  policy_refs: []
  cost: object|null
  risk: object|null
  evidence_refs: []
```

相关文件：`runtime-data-model.md`、`planes/observability/trace-format.md`、`planes/effects/overview.md`、`planes/recovery/overview.md`。
