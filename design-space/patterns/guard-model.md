# Guard Model Pattern

> **Evidence Status** — grounded. Google Secure AI Agents (2025) 的混合纵深防御策略；Codex guardian；Claude Code hooks/permissions；多层安全门禁实践。

## 问题

Agent 的安全防护面临两难：
- **纯规则系统**：快、可审计、确定性强，但无法处理语义风险和上下文变化
- **纯 LLM 判断**：能理解语义，但不稳定、不可保证、易被绕过

单独使用任一方式都不够：规则可能误拦合法动作，LLM 可能被新型攻击绕过。

## 解法

**混合纵深防御 (Hybrid Defense-in-Depth)**：将确定性策略引擎与推理型防御分层组合。

```text
Agent Decision
  → Layer 1: Deterministic Policy Engine (rules, allowlists, caps)
  → Layer 2: Guard Model (classifier, risk predictor)
  → Layer 3: Base Model Hardening (adversarial training, structural prompts)
  → Layer 4: Assurance (regression testing, red team, variant analysis)
```

## Guard Model 定义

Guard Model 是一个专门训练的小型模型（或模型组），作为 Agent 主循环外的独立安全分析器：

```yaml
guard_model:
  purpose: classify | detect | predict
  input: agent_input | agent_output | proposed_plan | tool_call
  output:
    verdict: safe | suspicious | blocked
    confidence: float
    reason: string
    suggested_action: allow | require_confirmation | block | quarantine

  deployment:
    position: pre_reasoning | post_reasoning | pre_action | post_action | pre_output
    latency_budget_ms: 50
    independence: must_not_share_context_with_main_model
```

## Policy Engine（确定性层）

```yaml
policy_engine:
  rules:
    - trigger: action_type == "purchase" && amount > 500
      verdict: require_user_confirmation
    - trigger: action_type == "send_email" && recently_processed_untrusted_data
      verdict: require_user_confirmation
    - trigger: action_type == "delete" && scope == "production"
      verdict: block
    - trigger: tool_call_count > budget_limit
      verdict: block_with_explanation

  properties:
    deterministic: true
    auditable: true
    testable: true
    limitation: cannot_handle_semantic_context
```

## 推理型防御策略

| 策略 | 机制 | 覆盖面 |
|---|---|---|
| Adversarial Training | 模型训练时暴露攻击样本，学会识别和忽略 | 已知攻击模式 |
| Guard Model/Classifier | 独立小模型检测输入/输出中的异常 | 语义异常、注入检测 |
| Plan Risk Prediction | 分析 Agent 计划的风险概率 | 复杂多步计划 |
| Structural Prompt Conventions | 用分隔符/角色标记区分指令与数据 | 减少 injection 成功率 |

## 层间协作

```text
Action Request arrives
  ↓
Policy Engine: Does it violate hard rules?
  → YES → Block/Require confirmation (no model needed)
  → NO → Continue
  ↓
Guard Model: Is this suspicious in context?
  → HIGH confidence attack → Block
  → MEDIUM confidence → Escalate to user / add monitoring
  → LOW risk → Allow
  ↓
Base Model: Has it been hardened against this pattern?
  → Model-level robustness as last internal defense
  ↓
Execute action → Log for assurance review
```

## 关键设计原则

1. **独立性**：Guard Model 不与主模型共享上下文注入路径，避免同时被攻击
2. **不对称成本**：攻击者必须同时绕过规则层 AND 推理层，显著提高攻击门槛
3. **可降级**：Guard Model 失败时降级到更严格的规则策略，而非放行
4. **不阻塞合法使用**：高频低风险动作应在 Policy Engine 层快速放行
5. **持续校准**：定期用红队测试和 variant analysis 验证防御有效性

## 验证闭环

```text
Red Team → 发现新攻击向量
  → Regression Test: 加入自动化测试集
  → Variant Analysis: 生成攻击变体确认覆盖
  → Guard Model Update: 必要时重新训练 classifier
  → Policy Update: 必要时增加规则
```

## 与现有模式的关系

| 现有模式 | Guard Model 的补充 |
|---|---|
| `untrusted-context-boundary.md` | Guard Model 在 lane 分离之上增加语义检测 |
| `tool-output-sanitization.md` | 除结构清洗外增加内容语义分析 |
| `mcp-trust-boundary.md` | 对第三方工具输出做独立风险评估 |
| Control Paradigms (LLM Judge) | Guard Model 是专用、小型、低延迟的特化版本 |

## 反模式

| 反模式 | 表现 | 修复 |
|---|---|---|
| 单点防御 | 只依赖 Guard Model 或只依赖规则 | 必须分层组合 |
| Guard 与 Agent 共生 | Guard Model 被同一轮注入污染 | 严格独立部署 |
| 过度阻塞 | Guard 灵敏度过高导致用户体验差 | 校准 + graduated response |
| 无 assurance | 部署后不再测试 | 持续红队 + regression |

## 参考来源

- Google "Secure AI Agents" (2025): Hybrid Defense-in-Depth
- Google SAIF 2.0 Framework
- Codex Guardian Policy
- Claude Code Permission System + Hooks
