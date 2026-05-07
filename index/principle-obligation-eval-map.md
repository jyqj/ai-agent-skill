# Principle → Obligation → Eval Map

> **Evidence Status** — synthesized. 将哲学原则压缩为开发者可检查的运行时义务，并连接到 checklist、starter-kit 或 eval fixture。此表用于降低“哲学层很好但不知道怎么落地”的认知负荷。

## 使用方法

设计或 review 时不要全文阅读哲学文档。先用本表判断：

```text
原则是否触发？
→ 对应运行时义务是什么？
→ 哪个对象/字段承载？
→ 怎么检查？
```

## 核心映射

| 原则 | 开发者要记住的话 | 运行时义务 | 检查入口 |
|---|---|---|---|
| BR-01 显式预算 | Agent 不能无限思考和无限调用工具 | ResourcePlan / Depth Budget / stop policy | `design-checklist.md#3-执行深度` |
| BR-02 上下文腐烂 | 信息会过期、丢失、被压缩污染 | observed_at / ttl / compaction policy | `../synthesis/context-memory-state-boundaries.md` |
| BR-03 满意解 | 够好就停，不追求无限优化 | success criteria / budget_exhausted behavior | `../toolkit/mva-planner.md` |
| BDI-01 信念来自观察 | 不要把假设当事实 | Observation / raw_refs / confidence / trust lane | `../architecture/planes/representation/overview.md` |
| BDI-02 验证是信念修正 | verify 不是形式检查 | EffectRecord / VerificationResult | `../synthesis/tool-effect-verification.md` |
| BDI-03 意图可持续也可修正 | 长任务需要 checkpoint 和 replan | TaskState / DecisionLog / FailureRecord | `../architecture/planes/state/overview.md` |
| IS-01 操作表示不是现实 | Memory/Context 不是当前世界 | WorldStateSnapshot / freshness check | `../synthesis/runtime-vs-world-state.md` |
| IS-02 工具成功不是效果成功 | tool success 不能直接 done | ToolCall.intended_effect / EffectRecord | `../design-space/lessons-learned/tool-success-as-completion.md` |
| IS-03 地图会偏离领土 | 关键动作前 refresh | refresh-before-act / conflict record | `../architecture/planes/world-state/overview.md` |
| EM-01 工具是认知延伸 | 工具不可用是能力降级 | ToolSpec / FailureRecord / fallback | `../architecture/planes/tools/overview.md` |
| EM-02 能力 = 模型 × Harness | 不要只调 prompt | PromptContract + tools + control + eval | `../architecture/planes/prompting/overview.md` |
| EM-03 环境约束能力 | 身份和权限决定能做什么 | CapabilityGrant / sandbox / approval | `../architecture/planes/identity-capability/overview.md` |
| MC-01 表达不确定性 | 不确定要说出来 | confidence / uncertainty_format / explanation | `../architecture/planes/explainability/overview.md` |
| MC-02 自我监控 | 失败要触发停止或换策略 | trace / loop detection / recovery action | `../architecture/planes/recovery/overview.md` |
| MC-03 知道不知道 | 不要编造验证不可达的结论 | unverifiable_by_agent / blocked / pending | `../toolkit/eval-planner.md` |

## 最小 eval 对应

| 义务 | 可用 fixture / test |
|---|---|
| 工具成功不等于效果成功 | `../evaluation/fixtures/negative_tool_success_effect_failed_001.yaml` |
| 过期世界状态阻止行动 | `../evaluation/fixtures/negative_context_rot_001.yaml` |
| prompt / tool output injection | `../evaluation/fixtures/adversarial_tool_output_injection_001.yaml` |
| MCP confused deputy | `../evaluation/fixtures/mcp_confused_deputy_001.yaml` |
| browser 双通道验证 | `../evaluation/fixtures/browser_gui_grounding_001.yaml` |
| research citation chain | `../evaluation/fixtures/research_claim_citation_001.yaml` |
| memory poisoning | `../evaluation/fixtures/memory_poisoning_001.yaml` |

## 设计提示

如果一个原则目前没有 eval，不代表它没价值；先把它落成 checklist 或 fixture，之后再接真实 trace。证据强度可以逐步提升，不必一开始就要求生产验证。
