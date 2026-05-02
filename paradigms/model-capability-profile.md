# Model Capability Profile

> **Evidence Status** — synthesized. 多个生产 Agent 系统的 model routing 实践、跨模型 benchmark 差异数据、以及 Harness 适配层的工程经验。


## 定义

Model Capability Profile 是描述模型行为特征的结构化对象，供 Harness 在范式选择、routing、预算分配和评估时使用。

它不是模型的 benchmark 分数汇总，而是面向 Harness 工程的操作性描述——每个字段直接对应一个 Harness 决策点。概念层面的讨论见 `../concepts/model-capability.md`。

## Schema

```yaml
model_capability_profile:
  model_id: string                # e.g. "claude-sonnet-4-20250514"

  reasoning_depth:
    level: shallow | moderate | deep
    reliable_steps: int           # 可靠推理的最大步数，超过此步数错误率显著上升

  instruction_adherence:
    score: float                  # 0-1，基于标准化指令遵从测试集
    failure_mode: string          # 典型失败模式，e.g. "ignores negative constraints"

  tool_call_reliability:
    success_rate: float           # 0-1，工具调用格式正确率
    common_errors:                # 常见错误类型
      - missing_required_param
      - hallucinated_tool_name
      - malformed_json

  context_utilization:
    effective_window: int         # 有效利用的 token 数（非标称窗口大小）
    degradation_curve: string     # e.g. "linear_after_80k" / "cliff_at_120k"

  output_consistency:
    temperature_sensitivity: string  # e.g. "stable_below_0.3" / "high_variance"

  cost:
    input_per_1k: float           # USD per 1k input tokens
    output_per_1k: float          # USD per 1k output tokens

  latency:
    ttft_p50_ms: int              # time to first token, p50
    throughput_tps: int           # tokens per second, sustained

  last_evaluated: timestamp       # profile 最后一次评估时间
```

## 使用场景

### 1. 范式路由

routing 层根据 `reasoning_depth` 决定将任务分配给哪种执行范式。`reasoning_depth.level = deep` 且 `reliable_steps >= 8` 的模型可以运行完整的 ReAct loop，由模型自主决定每一步的观察-推理-行动；`level = shallow` 或 `reliable_steps < 4` 的模型则应走 DAG workflow，Harness 预定义执行图，模型只负责每个节点内的局部生成。介于两者之间的 moderate 模型适合受约束的 ReAct——给出明确的 step limit、强制 structured output、并在每步做格式校验。

### 2. Prompt 策略适配

`instruction_adherence` 决定 prompt 的约束强度。高遵从度模型（score > 0.9）可以使用简洁的自然语言指令，依赖模型自身理解意图；低遵从度模型需要更多工程手段：严格的 JSON schema 约束、few-shot examples、negative examples（"不要做 X"）、以及输出格式的 post-validation。`failure_mode` 字段帮助 Harness 开发者针对性地设计防御——如果模型倾向于忽略否定约束，就把"不要做的事"改写成"只做以下事情"的正向约束。

### 3. 评估分层

将 eval suite 按 profile 分组运行，而不是所有模型跑同一套 fixture。这样可以精确识别回归：当某个模型版本更新后 `tool_call_reliability.success_rate` 从 0.95 降到 0.87，routing 层可以自动将该模型从"可独立执行工具密集型任务"降级为"需要 retry/repair 层"。`last_evaluated` 字段确保 profile 不会过期——如果距上次评估超过一定时间（建议不超过模型版本更新周期），系统应触发重新 profiling。
