# Cost & Resource Plane
>
> **所属域**：7. Lifecycle & Economics — 成本工程与模型路由
>
> **Evidence Status** — synthesized. Depth Budget、Observability cost report、model/tool routing 的生产约束；本知识库将成本从”事后账单”提升为运行时策略层。

**Principle Refs**: BR-01, BR-03 — 成本平面本身即预算约束的载体；满意即停优于无限优化，预算感知的停止策略是核心

成本不是事后复盘的指标，而是运行时的控制输入。不管理成本的 Agent 系统在生产中会费用失控——模型调用、工具调用和 Worker 并发都需要预算约束。

## 1. 定义

Cost & Resource Plane 负责模型路由、token 预算、工具预算、缓存、延迟、质量目标和资源回压。

核心原则：

```text
Cost is not a log. Cost is a control input.
```

## 2. ResourcePlan

```yaml
resource_plan:
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
  caching:
    observation_cache: enabled
    tool_result_cache: enabled
    embedding_cache: enabled
  stop_policy:
    budget_exhausted_behavior: ask_user | partial_deliver | stop | switch_strategy
```

## 3. 成本控制点

| 阶段 | 控制 |
|---|---|
| Representation | OCR/ASR/embedding 是否缓存，是否低成本预解析 |
| Context | token 预算、compaction、offloading |
| Prompting | few-shot 数量、输出长度、推理模式 |
| Kernel | 小模型规划、大模型处理复杂分支 |
| Tools | 工具调用上限、批处理、去重、缓存 |
| Orchestration | worker 数量、并发上限、合并策略 |
| Verification | 高风险用强验证，低风险用轻验证 |
| Interaction | 成本接近阈值时让用户选择质量/速度/价格 |

## 4. 成本反模式

- Always-Big-Model：所有步骤都用最强模型。
- Infinite Retrieval：检索越多越好，无边际收益判断。
- No Cache：重复 OCR、重复 embedding、重复读相同外部对象。
- Hidden Worker Explosion：多 Agent 并发创建但无资源上限。
- Verify Everything Equally：高低风险都用同等验证深度。

## 5. 关联文档

- `benchmarking.md`
- `../../../evaluation/cost-evals.md`
- `../../../design-space/anti-patterns/hidden-cost-explosion.md`
