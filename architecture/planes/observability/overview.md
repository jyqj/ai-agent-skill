# Observability & Evaluation Integration
>
> **所属域**：8. Reflection & Learning — trace、采样与评估事件
>
> **Evidence Status** — grounded. Claude Code、OpenCode 等系统对 usage、trace、runtime events 的记录；本知识库对”表示、效果、世界状态、配置指纹”全链路 trace 的统一抽象。

**Principle Refs**: MC-02, IS-03 — 自监控需要 trace 支撑以实现早期终止；观测数据本身是地图而非领土，需检测偏差

无法观测的系统无法调试、无法评估、无法改进。没有 Observability，Agent 无法从”能跑”过渡到”可运维”。

## 定义

Observability 模块负责 Trace、日志、监控和评估数据采集。State 用于恢复，Trace 用于分析、评估和事故处理。

## 模块接口

**输入**：所有模块的事件（representation、prompt、tool call、decision、effect、error、checkpoint、approval、config）
**输出**：结构化 trace、成本报告、评估数据、告警信号
**配置**：trace 粒度、采样策略、告警规则、保留期限

## Trace 事件类型

| 事件 | 数据 |
|---|---|
| task_start | task_id, product_type, required_depth |
| representation_built | raw_refs, parser, lossy, confidence, trust_tier |
| prompt_built | prompt_id, purpose, output_contract |
| world_state_read | object_ref, observed_at, ttl, stale |
| tool_call | tool_id, args, result, latency, cost |
| effect_recorded | effect_id, intended_effect, verification_status |
| interaction | interaction_id, type, trigger |
| agent_message | sender, receiver, message_type, authority_scope |
| decision | decision_id, rationale_summary, alternatives |
| milestone_complete | milestone_id, verification_result |
| error | error_type, failure_mode, recovery_action |
| checkpoint | checkpoint_id, state_summary |
| config_fingerprint | model_ref, prompt_ref, tool_schema_refs, policy_refs |
| task_complete | reached_depth, artifacts, evidence |

## 成本与质量追踪

```yaml
cost_report:
  tokens_input: int
  tokens_output: int
  tool_calls: int
  api_calls: int
  wall_time: duration
  human_interruptions: int
  effect_verifications: int
  stale_state_refreshes: int
```

## 与评估和运维的关系

- Trace 数据是评估的原材料。
- 配置指纹进入 trace，才能做回归定位。
- incident response 依赖 representation / effect / world state 事件回放。

## 入口文档

- `trace-format.md`
- `sampling.md`

## 参考实现

- **Claude Code**：usage tracking 和 cost reporting，见 `projects/coding-agents/claude-code/state-ui-layer.md`
- **OpenCode**：runtime 级别 trace，见 `projects/coding-agents/opencode/orchestration.snippet.md`
