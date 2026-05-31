# Model Capability

> **Evidence Status** — synthesized. 跨模型（Claude / GPT / Gemini / open-weight）在相同 Harness 下的行为差异观察，以及多个生产 Agent 系统的 routing 实践。


## 核心观点

模型不是同质的执行引擎。不同模型在推理深度、指令遵从、工具调用可靠性、多语言能力、上下文利用效率上差异显著。Harness 设计需要将模型能力作为显式输入，而非隐式假设。

当前知识库将模型定位为"处理表示的推理核心"，这在架构层面没有问题，但在工程层面忽略了一个事实：**同一个 Harness 接入不同模型，行为可能天差地别**。一个为 Claude 3.5 Sonnet 调优的 ReAct loop，换成 GPT-4o-mini 可能在第三步就开始幻觉工具参数；一个为 Gemini 2.5 Pro 设计的长上下文策略，换成 128k 窗口但注意力衰减严重的模型就会丢失关键信息。

解决方案是引入 **Model Capability Profile** 作为一等对象，让 Harness 在范式选择、prompt 策略、retry 逻辑和评估方案上都能参考模型的真实能力边界。

## Model Capability Profile 定义

| 维度 | 说明 | 对 Harness 的影响 |
|---|---|---|
| reasoning_depth | 多步推理的可靠步数 | 决定任务分解粒度和子代理深度 |
| instruction_adherence | 对 system prompt 指令的遵从度 | 影响 prompt 策略（严格 schema vs 自由格式） |
| tool_call_reliability | 工具调用格式的正确率 | 决定是否需要 retry/repair 层 |
| context_utilization | 长上下文中信息提取的衰减曲线 | 影响 compaction 策略和上下文预算分配 |
| output_consistency | 相同输入下输出的稳定性 | 影响 self-verification 和 voting 策略 |
| cost_per_token | 每 token 成本 | 影响 routing 和预算分配 |
| latency_profile | 首 token 延迟和吞吐 | 影响用户交互模式和超时设置 |

完整的 schema 定义和使用场景见 `../paradigms/model-capability-profile.md`。

## 与范式决策树的关系

当前的范式选择决策树（见 `../paradigms/` 下的相关文件）假设范式效果与模型无关，选 ReAct 还是 DAG workflow 主要看任务结构和不确定性程度。但实际上，模型能力是范式选择的隐含前提：

- **弱推理模型不适合 ReAct**。ReAct 依赖模型在每一步正确地推理"下一步该做什么"并生成合法的工具调用。reasoning_depth 不足的模型会在 3-5 步后开始跑偏：重复调用相同工具、遗忘之前的观察、编造不存在的工具参数。这类模型更适合 DAG workflow，由 Harness 预定义执行路径，模型只负责每个节点内的局部推理。
- **强推理模型可以用更少的 Harness 约束达到相同效果**。一个 reasoning_depth = deep 的模型可能只需要简单的 tool list + goal 描述就能完成任务，而同等任务交给 moderate 模型则需要 few-shot examples、structured output schema 和 step-by-step 指令。过度约束强模型反而可能降低其灵活性。
- **同一 size class 内不同模型的 tool_call_reliability 差异可达 20%+**。这意味着不能用"70B 级别模型"这样的粗粒度分类来决定 Harness 策略，必须针对具体模型做 profiling。

## 实践建议

- **在 runtime config 中声明 model_capability_profile**。不要把模型能力假设埋在代码逻辑里，而是作为显式配置项，方便切换模型时快速调整 Harness 行为。
- **routing 层根据 profile 选择执行策略**。简单任务 route 到低成本模型，复杂推理任务 route 到高 reasoning_depth 模型，长上下文任务 route 到 context_utilization 衰减最小的模型。
- **评估套件按 profile 分组，避免"一个 eval 判所有模型"**。不同模型的能力边界不同，用同一套 pass/fail 阈值评估所有模型会掩盖真实的能力差异。按 profile 分组后，可以精确识别"模型 X 在场景 Y 下回归了"。
- **profile 需要定期更新**。模型供应商的 API 更新、微调版本切换、甚至 temperature 参数调整都可能改变 profile。建议将 profiling 纳入 CI/CD 流程。
