# Trace Format

> **Evidence Status** — synthesized. ToolCall、ExecutionResult、EffectRecord、StateCheckpoint、EvalEvent 等运行时对象。

## 1. TraceEvent

```yaml
trace_event:
  trace_id: trace_...
  task_id: task_...
  timestamp: datetime
  event_type: intake | represent | prompt_build | context_build | decision | policy_gate | interaction | agent_message | tool_call | execution_result | effect_record | verify | state_update | cost_gate | deliver
  actor: interface | representation | prompting | context | kernel | tool | execution | control | security | cost | human | agent | operations
  refs:
    observation_ids: []
    prompt_id: string|null
    context_id: string|null
    decision_id: string|null
    tool_call_id: string|null
    effect_id: string|null
    interaction_id: string|null
  metrics:
    latency_ms: integer|null
    token_count: integer|null
    cost: number|null
  redaction_status: none | partial | full
```

## 2. Trace 必须能回答

```text
模型看见了什么？
PromptContract 是什么？
为何选择这个工具？
权限和安全 gate 是否通过？
用户是否批准或纠正？
外部效果是否验证？
成本为何增长？
如果重放，会在哪一步分歧？
```
