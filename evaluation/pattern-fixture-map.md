# 设计模式 → 推荐验证 Fixture 映射

> **Evidence Status** — synthesized. 基于 33 个设计模式和 25 个 eval fixtures 的交叉分析。

采用某个设计模式后，用哪些 fixture 来验证它是否正确实现。

---

## 为什么需要这张图

当前 patterns（`design-space/patterns/`）和 evaluation fixtures（`evaluation/fixtures/`）分别组织在两个目录，缺少"采用了这个模式后应该跑哪些测试"的直接映射。没有这张表，开发者在实现一个模式后往往不知道用什么来验证，或者只验证了 happy path 而遗漏关键失败场景。

---

## 映射表

| 设计模式 | 推荐验证 Fixture | 必备检查维度 |
|---|---|---|
| effect-ledger | `crm_update_effect_001`, `negative_tool_success_effect_failed_001` | 效果验证、Ghost Success 检测 |
| self-verification | `negative_verification_blocked_001`, `coding_bug_fix_with_test_001` | 验证门覆盖、阻塞处理 |
| checkpoint-hydration | `negative_context_rot_001`, `negative_orchestration_timeout_001` | 中断恢复、状态连续性 |
| compaction | `negative_context_rot_001`, `coding_context_rot_long_task_001` | 压缩后信息保留、质量不降 |
| tool-registry | `mcp_confused_deputy_001`, `negative_tool_success_effect_failed_001` | 工具选择正确、权限隔离 |
| guard-model | `mcp_prompt_injection_001`, `memory_poisoning_001` | 注入防护、信任边界 |
| mcp-trust-boundary | `mcp_prompt_injection_001`, `mcp_confused_deputy_001` | MCP 权限隔离、输出消毒 |
| citation-chain | `research_claim_citation_001`, `research_conflict_resolution_001` | 断言-证据绑定、冲突保留 |
| dual-channel-gui-verification | `browser_gui_grounding_001`, `browser_checkout_guard_001` | DOM+视觉双通道、语义一致 |
| layered-memory | `companion_memory_consistency_001`, `memory_poisoning_001` | 记忆一致性、注入防护 |
| worker-orchestration | `negative_orchestration_timeout_001` | Worker 生命周期、超时处理 |
| conflict-preserving-synthesis | `research_conflict_resolution_001` | 冲突不被压平 |
| untrusted-context-boundary | `mcp_prompt_injection_001`, `memory_poisoning_001`, `adversarial_indirect_prompt_injection_001` | 信任车道分离 |
| depth-budgeting | `negative_budget_exceeded_001` | 预算耗尽处理 |
| loop-detection | `negative_orchestration_timeout_001` | 循环检测和停止 |
| tool-output-sanitization | `mcp_prompt_injection_001`, `adversarial_tool_output_injection_001` | 输出消毒 |
| contract-agent | `crm_update_effect_001` | 合约验收 |
| tool-output-offloading | `negative_context_rot_001` | 大输出不污染上下文 |
| frozen-snapshot | `research_freshness_refresh_001` | 快照不可变、引用稳定 |
| subagent | `negative_orchestration_timeout_001`, `mcp_confused_deputy_001` | 子 Agent 生命周期、权限继承 |
| layered-tool-host | `mcp_confused_deputy_001`, `adversarial_tool_output_injection_001` | 分层权限、输出隔离 |
| property-based-agent-testing | `coding_refactor_no_regression_001` | 属性不变性、回归检测 |
| milestone-gated-execution | `negative_budget_exceeded_001`, `negative_orchestration_timeout_001` | 里程碑门控、超时处理 |
| scratchpad-progress-file | `coding_context_rot_long_task_001` | 进度持久化、长任务恢复 |
| multi-window | `browser_gui_grounding_001` | 多窗口状态同步 |
| shadow-mode-regression | （需新 fixture） | 灰度对比 |
| hook-system | （通用，按 hook 类型选 fixture） | hook 触发正确 |
| progressive-disclosure | （需新 fixture） | 渐进展开不丢信息 |
| decision-log | （需新 fixture） | 决策追溯 |
| feature-list-progress | （需新 fixture） | 进度追踪 |
| convention-discovery | （需新 fixture） | 约定发现 |
| skill-crystallization | （需新 fixture） | 技能固化 |

---

## 反向索引：Fixture → 覆盖的模式

便于从 eval 结果反查哪些模式可能存在问题。

| Fixture | 覆盖的模式 |
|---|---|
| `crm_update_effect_001` | effect-ledger, contract-agent |
| `negative_tool_success_effect_failed_001` | effect-ledger, tool-registry |
| `negative_verification_blocked_001` | self-verification |
| `coding_bug_fix_with_test_001` | self-verification |
| `negative_context_rot_001` | checkpoint-hydration, compaction, tool-output-offloading |
| `coding_context_rot_long_task_001` | compaction, scratchpad-progress-file |
| `negative_orchestration_timeout_001` | checkpoint-hydration, worker-orchestration, loop-detection, subagent, milestone-gated-execution |
| `mcp_confused_deputy_001` | tool-registry, mcp-trust-boundary, subagent, layered-tool-host |
| `mcp_prompt_injection_001` | guard-model, mcp-trust-boundary, untrusted-context-boundary, tool-output-sanitization |
| `memory_poisoning_001` | guard-model, layered-memory, untrusted-context-boundary |
| `research_claim_citation_001` | citation-chain |
| `research_conflict_resolution_001` | citation-chain, conflict-preserving-synthesis |
| `research_freshness_refresh_001` | frozen-snapshot |
| `browser_gui_grounding_001` | dual-channel-gui-verification, multi-window |
| `browser_checkout_guard_001` | dual-channel-gui-verification |
| `companion_memory_consistency_001` | layered-memory |
| `negative_budget_exceeded_001` | depth-budgeting, milestone-gated-execution |
| `adversarial_tool_output_injection_001` | tool-output-sanitization, layered-tool-host |
| `adversarial_indirect_prompt_injection_001` | untrusted-context-boundary |
| `coding_refactor_no_regression_001` | property-based-agent-testing |
| `ops_incident_diagnosis_001` | （未直接映射到通用模式，属品类专属 eval） |
| `ops_rollback_verification_001` | （未直接映射到通用模式，属品类专属 eval） |
| `data_sql_injection_guard_001` | （未直接映射到通用模式，属品类专属 eval） |
| `data_query_result_verification_001` | （未直接映射到通用模式，属品类专属 eval） |
| `ocr_invoice_parse_001` | （未直接映射到通用模式，属品类专属 eval） |

---

## 无对应 Fixture 的模式

以下模式目前没有直接对应的 fixture，建议后续补充：

| 模式 | 缺失的 Fixture 类型 | 建议优先级 |
|---|---|---|
| shadow-mode-regression | 灰度对比 fixture：新旧路径输出差异检测 | 高——灰度发布是生产安全网 |
| progressive-disclosure | 渐进展开 fixture：验证展开层级不丢失信息 | 中 |
| decision-log | 决策追溯 fixture：验证日志完整性和可回溯性 | 中 |
| feature-list-progress | 进度追踪 fixture：验证完成度计算准确性 | 低 |
| convention-discovery | 约定发现 fixture：验证约定推断的准确率 | 中 |
| skill-crystallization | 技能固化 fixture：验证固化后的技能可重放 | 中 |
| hook-system | 通用 hook fixture：按 hook 类型（pre/post/error）分别验证 | 中——可复用现有 fixture 组合覆盖 |

---

## 使用指南

1. 在 `design-space/patterns/` 中选择了一个模式后，查本表找到推荐 fixture。
2. 在 `evaluation/fixtures/` 中找到对应 YAML 文件。
3. 使用 eval-runner 运行验证（参见 `evaluation/eval-runner/README.md`）。
4. 如果模式标注为"需新 fixture"，先使用 `evaluation/fixtures/` 中的模板创建品类适配版本，再运行。
5. eval 失败时，使用反向索引确认失败影响的模式范围，避免只修局部。

---

## 延伸阅读

- `../design-space/patterns/README.md` — 设计模式总览
- `./fixtures/README.md` — Fixture 索引
- `./eval-runner/README.md` — 运行 eval
- `../concepts/foundations/principle-obligation-eval-map.md` — 原则 → 义务 → eval 映射（互补视角）
- `../index/category-pattern-matrix.md` — 品类 × 模式采用矩阵
