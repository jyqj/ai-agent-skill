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

---

## 填充指南

如何评估 Profile 中每个字段，使其可复现、可对比。

### reasoning_depth

| 字段 | 评估方法 |
|------|---------|
| `level` | 在 GAIA / SWE-bench 上运行多步推理任务，统计正确率在第几步开始显著下降（>10% 跌幅）。3 步内下降 -> shallow；4-7 步 -> moderate；8+ 步仍稳定 -> deep |
| `reliable_steps` | 取"正确率保持在 baseline 90% 以上"的最大步数。建议使用至少 50 个多步任务样本，取 p25 值（保守估计） |

### instruction_adherence

| 字段 | 评估方法 |
|------|---------|
| `score` | 使用标准化指令遵从测试集（IFEval 或自建）。构造 100+ 条含显式约束的指令（格式、长度、否定约束、条件分支），计算完全遵从率 |
| `failure_mode` | 对失败样本聚类分析。常见模式：ignores negative constraints（忽略"不要做X"）、format drift（长输出后格式退化）、over-compliance（过度解读约束导致遗漏信息） |

### tool_call_reliability

| 字段 | 评估方法 |
|------|---------|
| `success_rate` | 运行 200+ 次工具调用（覆盖串行/并行/多轮），计算格式正确且参数完整的比率。推荐使用 BFCL 或 LiveMCPBench 子集 |
| `common_errors` | 对失败调用分类统计。按频次排序取 top-3。典型错误：missing_required_param、hallucinated_tool_name、malformed_json、wrong_param_type |

### context_utilization

| 字段 | 评估方法 |
|------|---------|
| `effective_window` | Needle-in-a-Haystack 测试：在不同长度的上下文中嵌入关键信息，测量检索准确率。取准确率 > 90% 的最大上下文长度 |
| `degradation_curve` | 在 25%/50%/75%/100% 标称窗口长度处分别测量任务准确率，拟合退化曲线形态。常见模式：linear_after_X（线性退化）、cliff_at_X（悬崖式下跌）、gradual（缓慢下降） |

### output_consistency

| 字段 | 评估方法 |
|------|---------|
| `temperature_sensitivity` | 在 temperature=0 / 0.3 / 0.7 / 1.0 下各运行同一组 50 个任务 3 次。计算跨温度的输出方差。方差 < 0.1 (temp <= 0.3) -> stable_below_0.3；方差始终 > 0.3 -> high_variance |

### cost

| 字段 | 评估方法 |
|------|---------|
| `input_per_1k` / `output_per_1k` | 直接取模型提供商的官方定价。注意区分标准 token 和推理 token（reasoning models 通常分开计费）。每月核查一次，价格变动频繁 |

### latency

| 字段 | 评估方法 |
|------|---------|
| `ttft_p50_ms` | 发送标准长度 prompt（~2000 token），测量首 token 到达时间。至少 100 次采样取 p50。注意地域差异（选择生产部署区域测试） |
| `throughput_tps` | 请求生成 1000+ token 的输出，计算 sustained tokens/second。取 p50 值。推理模型需要分别记录"思考阶段 tps"和"输出阶段 tps" |

### 评估节奏建议

- 模型版本更新后 48 小时内完成重新 profiling
- 无版本更新时，每 30 天复测一次（捕获静默变更）
- 定价字段每月核查一次

---

## 示例 Profile

以下 5 个 Profile 基于 2026 年 5 月的公开数据和实测结果。

### Claude Opus 4.7（推理型，Adaptive Thinking）

```yaml
model_capability_profile:
  model_id: "claude-opus-4-20260301"

  reasoning_depth:
    level: deep
    reliable_steps: 12

  instruction_adherence:
    score: 0.95
    failure_mode: "over-compliance on ambiguous constraints"

  tool_call_reliability:
    success_rate: 0.97
    common_errors:
      - wrong_param_type
      - redundant_tool_call

  context_utilization:
    effective_window: 180000
    degradation_curve: "gradual_after_150k"

  output_consistency:
    temperature_sensitivity: "stable_below_0.3"

  cost:
    input_per_1k: 0.015
    output_per_1k: 0.075

  latency:
    ttft_p50_ms: 1800
    throughput_tps: 60

  last_evaluated: 2026-05-01T00:00:00Z
```

**定位**：最强推理能力 + Adaptive Thinking 自主调节推理深度。SWE-bench Verified 87.6%。适合作为 Planner、复杂 ReAct Agent 的核心模型。成本高，应通过模型路由仅在复杂任务时使用。Interleaved thinking 在工具调用间自动停下思考，对 agentic 工作流至关重要。

### Claude Sonnet 4.6（平衡型）

```yaml
model_capability_profile:
  model_id: "claude-sonnet-4-20250514"

  reasoning_depth:
    level: moderate
    reliable_steps: 7

  instruction_adherence:
    score: 0.92
    failure_mode: "format drift in long outputs"

  tool_call_reliability:
    success_rate: 0.95
    common_errors:
      - missing_required_param
      - malformed_json

  context_utilization:
    effective_window: 160000
    degradation_curve: "linear_after_120k"

  output_consistency:
    temperature_sensitivity: "stable_below_0.3"

  cost:
    input_per_1k: 0.003
    output_per_1k: 0.015

  latency:
    ttft_p50_ms: 800
    throughput_tps: 90

  last_evaluated: 2026-05-01T00:00:00Z
```

**定位**：成本/性能最优平衡点。GAIA 74.6% (Sonnet 4.5 数据)。适合中等复杂度的 ReAct Agent、受约束循环。作为 Executor 模型或中等路由层级的默认选择。5x 低于 Opus 的成本使其成为大流量场景的首选。

### GPT-4o（多模态通用）

```yaml
model_capability_profile:
  model_id: "gpt-4o-2025-08-06"

  reasoning_depth:
    level: moderate
    reliable_steps: 6

  instruction_adherence:
    score: 0.90
    failure_mode: "ignores negative constraints"

  tool_call_reliability:
    success_rate: 0.93
    common_errors:
      - hallucinated_tool_name
      - missing_required_param

  context_utilization:
    effective_window: 100000
    degradation_curve: "cliff_at_110k"

  output_consistency:
    temperature_sensitivity: "moderate_variance"

  cost:
    input_per_1k: 0.0025
    output_per_1k: 0.010

  latency:
    ttft_p50_ms: 600
    throughput_tps: 100

  last_evaluated: 2026-05-01T00:00:00Z
```

**定位**：多模态能力最强（图像/音频/视频理解原生支持）。适合涉及多模态输入的 Agent 任务（GUI 交互、文档分析、视觉推理）。指令遵从度略低，需要更严格的 prompt 工程（正向约束替代否定约束）。价格极具竞争力。

### o4-mini（推理型，低成本）

```yaml
model_capability_profile:
  model_id: "o4-mini-2025-04-16"

  reasoning_depth:
    level: deep
    reliable_steps: 10

  instruction_adherence:
    score: 0.88
    failure_mode: "over-reasoning on simple tasks"

  tool_call_reliability:
    success_rate: 0.91
    common_errors:
      - malformed_json
      - wrong_param_type
      - redundant_tool_call

  context_utilization:
    effective_window: 100000
    degradation_curve: "linear_after_80k"

  output_consistency:
    temperature_sensitivity: "high_variance"

  cost:
    input_per_1k: 0.0011
    output_per_1k: 0.0044

  latency:
    ttft_p50_ms: 2500
    throughput_tps: 45

  last_evaluated: 2026-05-01T00:00:00Z
```

**定位**：低成本推理模型。推理 token 隐藏不可见，调试困难。深度推理能力强但指令遵从度略低（over-reasoning 倾向），简单任务可能过度思考导致浪费。适合作为 Planner-Executor 中的低成本 Planner，或 Budget-Constrained 场景的推理核心。注意：推理 token 独立计费，实际成本高于标称 token 价格。

### Gemini 2.5 Pro（长上下文，动态思考）

```yaml
model_capability_profile:
  model_id: "gemini-2.5-pro-preview-05-06"

  reasoning_depth:
    level: deep
    reliable_steps: 9

  instruction_adherence:
    score: 0.89
    failure_mode: "verbose output exceeding constraints"

  tool_call_reliability:
    success_rate: 0.90
    common_errors:
      - hallucinated_tool_name
      - missing_required_param
      - malformed_json

  context_utilization:
    effective_window: 800000
    degradation_curve: "gradual_after_500k"

  output_consistency:
    temperature_sensitivity: "moderate_variance"

  cost:
    input_per_1k: 0.00125
    output_per_1k: 0.010

  latency:
    ttft_p50_ms: 1200
    throughput_tps: 70

  last_evaluated: 2026-05-01T00:00:00Z
```

**定位**：超长上下文窗口（1M token 标称，有效利用 ~800K）。动态思考模式根据 prompt 复杂度自动调整推理深度（类似 Claude 的 Adaptive Thinking）。适合需要处理大量文档/代码库的 Agent 任务。内置 Google 生态工具集成。工具调用可靠性稍弱，建议配合 retry/repair 层。

---

## 与 paradigm-routing 的集成

Profile 字段如何驱动范式选择——以下映射表供 Harness routing 层实现参考。详细的路由决策树见 `paradigm-routing.md`。

### 核心路由映射表

| Profile 条件 | 路由目标范式 | 理由 |
|-------------|------------|------|
| `reasoning_depth.level = deep` AND `reliable_steps >= 8` | **完整 ReAct** / **Reflexion** | 模型能独立维持多步推理链，自我纠错能力强 |
| `reasoning_depth.level = moderate` AND `reliable_steps 4-7` | **受约束 ReAct**（step limit + 格式校验） | 推理能力中等，需要 Harness 辅助防止推理链断裂 |
| `reasoning_depth.level = shallow` OR `reliable_steps < 4` | **DAG Workflow** / **ReWOO** | 模型不可靠地维持多步推理，Harness 预定义执行图 |
| `tool_call_reliability.success_rate >= 0.95` | 允许 **独立工具密集型任务** | 工具调用可信，无需额外 retry/repair 层 |
| `tool_call_reliability.success_rate < 0.90` | 强制 **retry/repair 层** + 格式校验 | 工具调用错误率高，每次调用后需要格式和结果验证 |
| `context_utilization.effective_window >= 200k` | 可用于 **长文档/代码库分析** Agent | 上下文足够大，无需分块处理 |
| `context_utilization.effective_window < 50k` | 强制 **Compaction** + **Sub-Agent 分块** | 上下文不足，必须通过压缩或分治处理长输入 |
| `cost.output_per_1k >= 0.05` | 路由仅在 **复杂任务** 时使用 | 成本高，通过模型路由限制使用频率 |
| `cost.output_per_1k < 0.01` | 可作为 **Executor** / **高频任务** 默认模型 | 成本低，适合大流量场景 |
| `latency.ttft_p50_ms > 2000` | 不适合 **实时交互** 场景 | 首 token 延迟高，用户体验差 |
| `instruction_adherence.score >= 0.93` | 可用 **简洁自然语言指令** | 模型自身理解能力强，无需过度工程化 prompt |
| `instruction_adherence.score < 0.88` | 强制 **JSON schema + few-shot + 正向约束** | 指令遵从度低，需要严格约束和示例 |

### 多模型路由示例

基于上述 5 个示例 Profile 的典型路由配置：

```yaml
routing_config:
  tiers:
    - name: "complex_reasoning"
      model: "claude-opus-4-20260301"
      conditions:
        - task_complexity: high
        - requires_planning: true
        - budget_per_task: ">= $1.00"
      paradigm: "Plan-and-Execute (Planner role)"

    - name: "balanced_execution"
      model: "claude-sonnet-4-20250514"
      conditions:
        - task_complexity: medium
        - tool_intensive: true
      paradigm: "ReAct with step limit"

    - name: "multimodal_tasks"
      model: "gpt-4o-2025-08-06"
      conditions:
        - has_image_input: true
        - has_audio_input: true
      paradigm: "ReAct with format validation"

    - name: "budget_reasoning"
      model: "o4-mini-2025-04-16"
      conditions:
        - task_complexity: high
        - budget_per_task: "< $0.50"
      paradigm: "Budget-Aware ReAct"

    - name: "long_context"
      model: "gemini-2.5-pro-preview-05-06"
      conditions:
        - input_tokens: "> 200000"
      paradigm: "Single-pass or minimal ReAct"

  fallback:
    model: "claude-sonnet-4-20250514"
    paradigm: "Constrained ReAct"
```

### Profile 字段与成本优化策略的联动

Profile 不仅驱动范式选择，还驱动成本优化策略的启用：

| Profile 信号 | 触发的优化策略 | 参见 |
|-------------|-------------|------|
| `cost.output_per_1k` 高 | 启用模型路由，复杂任务才用该模型 | `cost/model-routing.md` |
| `context_utilization.effective_window` 小 | 启用 Compaction + Sub-Agent 分块 | `cost/paradigm-cost-benchmarks.md` |
| `reasoning_depth.reliable_steps` 低 | 使用 DAG Workflow 减少不必要的推理循环 | `cost/token-budgeting.md` |
| `tool_call_reliability.success_rate` 低 | 启用 retry 层（增加成本但避免更昂贵的失败） | `cost/cost-quality.md` |
| `latency.ttft_p50_ms` 高 | 启用 Prompt Caching 降低重复请求延迟 | `cost/caching.md` |
