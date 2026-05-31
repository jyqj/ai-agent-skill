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
| BR-02 上下文腐烂 | 信息会过期、丢失、被压缩污染 | observed_at / ttl / compaction policy | `../../synthesis/context-memory-state-boundaries.md` |
| BR-03 满意解 | 够好就停，不追求无限优化 | success criteria / budget_exhausted behavior | `../../toolkit/mva-planner.md` |
| BDI-01 信念来自观察 | 不要把假设当事实 | Observation / raw_refs / confidence / trust lane | `../../architecture/planes/representation/overview.md` |
| BDI-02 验证是信念修正 | verify 不是形式检查 | EffectRecord / VerificationResult | `../../synthesis/tool-effect-verification.md` |
| BDI-03 意图可持续也可修正 | 长任务需要 checkpoint 和 replan | TaskState / DecisionLog / FailureRecord | `../../architecture/planes/state/overview.md` |
| IS-01 操作表示不是现实 | Memory/Context 不是当前世界 | WorldStateSnapshot / freshness check | `../../synthesis/runtime-vs-world-state.md` |
| IS-02 工具成功不是效果成功 | tool success 不能直接 done | ToolCall.intended_effect / EffectRecord | `../../design-space/lessons-learned/tool-success-as-completion.md` |
| IS-03 地图会偏离领土 | 关键动作前 refresh | refresh-before-act / conflict record | `../../architecture/planes/world-state/overview.md` |
| EM-01 工具是认知延伸 | 工具不可用是能力降级 | ToolSpec / FailureRecord / fallback | `../../architecture/planes/tools/overview.md` |
| EM-02 能力 = 模型 × Harness | 不要只调 prompt | PromptContract + tools + control + eval | `../../architecture/planes/prompting/overview.md` |
| EM-03 环境约束能力 | 身份和权限决定能做什么 | CapabilityGrant / sandbox / approval | `../../architecture/planes/identity-capability/overview.md` |
| MC-01 表达不确定性 | 不确定要说出来 | confidence / uncertainty_format / explanation | `../../architecture/planes/explainability/overview.md` |
| MC-02 自我监控 | 失败要触发停止或换策略 | trace / loop detection / recovery action | `../../architecture/planes/recovery/overview.md` |
| MC-03 知道不知道 | 不要编造验证不可达的结论 | unverifiable_by_agent / blocked / pending | `../../toolkit/eval-planner.md` |
| AV-01 无行动不记忆 | 没执行过的东西不准写入记忆 | MemoryRecord.source 关联 ExecutionResult / evidence_refs 非空 | `../../architecture/planes/state/overview.md` |
| AV-02 无证据不放行 | 验证必须来自独立工具调用，模型推理不算 | VerificationResult 关联独立 tool_call_id / 缺工具时标 skipped | `../../synthesis/tool-effect-verification.md` |
| AV-03 无效果不交付 | 工具返回 200 不等于世界改变了 | 关键写操作配套 read_after_write / 交付前检查 EffectRecord.verification_status | `../../design-space/lessons-learned/tool-success-as-completion.md` |
| VA-01 价值漂移 | 长期运行的 Agent 行为会偏离初始设定 | 基线比较 / 偏好审计 / 角色一致性测试 | `./value-and-alignment.md` |
| VA-02 短期指令 vs 长期利益 | 用户说"快点修"不代表该打补丁 | Decision Log 记录利弊 / 推荐长期方案 / 最终决策权归用户 | `./value-and-alignment.md` |
| VA-03 偏好过拟合 | 有限交互推断的偏好不能过度泛化 | 偏好记录标注样本量和置信度 / 定期校准 | `./value-and-alignment.md` |
| VA-04 多层价值源冲突 | 用户指令、组织策略、社会规范打架时要有解决顺序 | 价值层次优先级 / 硬约束不可覆盖 / 冲突时向用户说明 | `./value-and-alignment.md` |

## 最小 eval 对应

| 义务 | 可用 fixture / test |
|---|---|
| 工具成功不等于效果成功 | `../../evaluation/fixtures/negative_tool_success_effect_failed_001.yaml` |
| 过期世界状态阻止行动 | `../../evaluation/fixtures/negative_context_rot_001.yaml` |
| prompt / tool output injection | `../../evaluation/fixtures/adversarial_tool_output_injection_001.yaml` |
| MCP confused deputy | `../../evaluation/fixtures/mcp_confused_deputy_001.yaml` |
| browser 双通道验证 | `../../evaluation/fixtures/browser_gui_grounding_001.yaml` |
| research citation chain | `../../evaluation/fixtures/research_claim_citation_001.yaml` |
| memory poisoning | `../../evaluation/fixtures/memory_poisoning_001.yaml` |
| 无执行证据不写入记忆 | `../../evaluation/fixtures/memory_poisoning_001.yaml` |
| 验证工具不可用时标记 skipped | `../../evaluation/fixtures/negative_verification_blocked_001.yaml` |
| 写操作后独立 read-back 验证 | `../../evaluation/fixtures/negative_tool_success_effect_failed_001.yaml` |
| 长期交互中角色/偏好漂移 | `../../evaluation/fixtures/companion_memory_consistency_001.yaml` |
| 用户偏好对齐 | `../../evaluation/fixtures/negative_user_preference_ignored_001.yaml` — Agent 忽略用户明确表达的偏好（如语言、格式、工具选择），仍按默认行为执行 |
| 长期价值对齐 | `../../evaluation/fixtures/negative_longitudinal_drift_001.yaml` — Agent 在多轮交互后逐渐偏离用户初始目标，优化中间指标而非最终效果 |
| 价值冲突解决与用户告知 | 待补充 |
| 偏好过拟合检测 | 待补充 |

## 设计提示

如果一个原则目前没有 eval，不代表它没价值；先把它落成 checklist 或 fixture，之后再接真实 trace。证据强度可以逐步提升，不必一开始就要求生产验证。

## Eval Fixture 倒排索引

从 fixture 反查它覆盖了哪些原则。用于新增 fixture 时确认覆盖范围，或删除 fixture 时评估影响。

| Fixture | 覆盖原则 |
|---|---|
| `negative_tool_success_effect_failed_001.yaml` | IS-02, AV-03 |
| `negative_context_rot_001.yaml` | BR-02, IS-03 |
| `adversarial_tool_output_injection_001.yaml` | EM-03, BDI-01 |
| `mcp_confused_deputy_001.yaml` | EM-03, IS-02 |
| `browser_gui_grounding_001.yaml` | BDI-01, IS-01, EM-01 |
| `research_claim_citation_001.yaml` | BDI-01, MC-01, MC-03 |
| `memory_poisoning_001.yaml` | AV-01, IS-01 |
| `negative_verification_blocked_001.yaml` | AV-02, BDI-02 |
| `companion_memory_consistency_001.yaml` | VA-01, VA-03 |
| `negative_budget_exceeded_001.yaml` | BR-01, BR-03 |
| `coding_bug_fix_with_test_001.yaml` | IS-02, AV-03, EM-02 |
| `coding_context_rot_long_task_001.yaml` | BR-02, IS-03, MC-02 |
| `ops_rollback_verification_001.yaml` | AV-03, BDI-02 |
| `data_query_result_verification_001.yaml` | IS-02, AV-02 |
| `pii_detection_redaction_001.yaml` | EM-03, VA-04 |
| `gdpr_deletion_request_001.yaml` | AV-03, VA-04 |
| `negative_user_preference_ignored_001.yaml` | VA-02 |
| `negative_longitudinal_drift_001.yaml` | VA-03 |

### 无 fixture 覆盖的原则

以下原则尚无对应 eval fixture，建议优先补充：

- ~~**VA-02**（短期指令 vs 长期利益）~~ — 已补充 `negative_user_preference_ignored_001.yaml`
- ~~**VA-03**（偏好过拟合）~~ — 已补充 `negative_longitudinal_drift_001.yaml`
- **MC-03**（知道不知道什么）——可复用 `research_claim_citation_001.yaml` 部分覆盖，但缺少专项 fixture
