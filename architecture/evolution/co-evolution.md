# 模型-Harness-工具的协同演化

> **Evidence Status** — mixed
> 来源：LLM 版本升级导致 prompt 回归的工程报告；OpenAI / Anthropic 模型版本切换的社区经验；生产 Agent 在工具 API 变更后的适配实践。

## 1. 问题

Agent 系统由三个主要组件构成，它们各自独立演化：

```text
Model:   gpt-4-0613 → gpt-4-turbo → gpt-4o → o3
Harness: prompt v1 → prompt v2 → prompt v3
Tools:   API v1 → API v2（参数名变了） → API v3（语义变了）
```

当任何一个组件升级时，其他组件可能需要同步调整。不同步会导致：

- Prompt 对新模型不生效（格式偏好变化）
- 工具定义与实际 API 不匹配（参数名/类型变化）
- 验证逻辑对新模型的输出模式误判（输出格式变化）

## 2. 版本矩阵

```yaml
compatibility_matrix:
  - model: claude-3-opus
    harness: prompt-v2
    tools: api-v1
    status: production
    eval_score: 0.92
    last_validated: 2025-03-15

  - model: claude-4-opus
    harness: prompt-v2
    tools: api-v1
    status: shadow
    eval_score: 0.87  # 回归!
    regression_notes: "新模型倾向跳过工具确认步骤"

  - model: claude-4-opus
    harness: prompt-v3  # 适配后
    tools: api-v1
    status: staging
    eval_score: 0.94
    last_validated: 2025-04-01
```

版本矩阵应作为配置管理的一部分，每次组件变更时更新。

## 3. 演化策略

### 3.1 渐进升级 (Shadow Mode)

先在 shadow mode 运行新模型，对比旧模型结果：

```text
用户请求 → 同时发给:
  ├── Production (旧模型 + 旧 Harness) → 用户看到的结果
  └── Shadow     (新模型 + 旧 Harness) → 仅记录，不展示

对比两边结果:
  - 工具调用序列是否相同？
  - 输出格式是否符合 schema？
  - 验证步骤是否通过？
  - 最终结果是否一致？
```

Shadow mode 的关键是**不执行有副作用的工具调用** -- 只模拟到工具选择阶段，避免重复写入。

### 3.2 契约优先 (Contract-First)

用 PromptContract 和 ToolSpec 作为稳定接口，模型可替换：

```yaml
prompt_contract:
  input_schema:
    task_description: string
    context: object
    available_tools: list[ToolSpec]
  output_schema:
    plan: list[Step]
    confidence: float
    reasoning: string
  invariants:
    - "输出必须是合法 JSON"
    - "plan 中的工具名必须在 available_tools 中"
    - "confidence 在 [0, 1] 范围内"
  test_fixtures:
    - input: "fixture-001.json"
      expected_output_schema: "fixture-001-schema.json"
```

契约独立于具体模型。换模型时，只要新模型满足契约，Harness 不需要改。

### 3.3 回归检测 (Regression Detection)

用 eval fixture 检测行为回归：

```text
Eval Fixture:
  - 20 个典型任务（覆盖主要品类）
  - 10 个边界案例（历史出过问题的场景）
  - 5 个安全测试（对抗性输入）

升级流程:
  1. 在旧配置上运行 fixture → 基线分数
  2. 在新配置上运行 fixture → 候选分数
  3. 候选分数 < 基线分数 × 0.95 → 回归告警
  4. 任何安全测试失败 → 阻断升级
```

## 4. 常见回归类型

| 回归类型 | 表现 | 检测方法 |
|---|---|---|
| 格式回归 | 新模型输出格式变化，下游解析失败 | Schema 验证 |
| 工具选择回归 | 新模型偏好不同的工具或参数 | 工具调用序列对比 |
| 详细度回归 | 新模型更简洁/更啰嗦 | 输出长度和结构对比 |
| 安全回归 | 新模型对攻击性输入更脆弱 | 红队测试 |
| 成本回归 | 新模型 token 使用量显著增加 | token 用量统计 |
| 遵循指令回归 | 新模型对 system prompt 中某些指令遵循度下降 | 指令遵循测试 |

## 5. 工具演化的特殊挑战

工具 API 的变更比模型升级更频繁、更不可控：

```text
外部 API 变更类型:
  - 参数名重命名（非破坏性但需要更新 schema）
  - 参数类型变化（string → enum）
  - 端点废弃（需要迁移到新端点）
  - 语义变化（同名参数含义改变，最危险）
  - 认证方式变化（OAuth → API Key）
```

### 工具变更检测

```yaml
tool_change_detection:
  strategies:
    - schema_diff: "对比 ToolSpec 的 schema 变化"
    - response_diff: "对比相同输入下的响应变化"
    - error_rate_spike: "工具调用错误率突然升高"
    - deprecation_header: "HTTP 响应中的 Deprecation 头"
  actions:
    on_schema_change: update_tool_definition
    on_semantic_change: quarantine_tool + alert
    on_deprecation: plan_migration
```

## 6. 与 Operations Plane 的关系

Operations Plane 的 ConfigFingerprint 追踪版本组合：

```yaml
config_fingerprint:
  model: claude-4-opus@20250301
  harness: prompt-v3@abc123
  tools:
    - name: search_api
      version: v2.1
      schema_hash: sha256:def456
  evaluated_at: 2025-04-01
  eval_score: 0.94
```

每次任何组件变更，ConfigFingerprint 随之变化，触发回归检测流水线。

## 7. 与 Evaluation 的关系

每次升级都应触发 eval 回归。但不是所有 eval 都适合自动化：

| Eval 类型 | 自动化程度 | 阻断能力 |
|---|---|---|
| Schema 验证 | 全自动 | 阻断 |
| 工具调用序列对比 | 全自动 | 告警 |
| 输出质量评分 | 半自动（LLM-as-Judge） | 告警 |
| 安全测试 | 全自动 | 阻断 |
| 用户满意度 | 手动 | 不阻断，但影响长期决策 |

## 8. 实施检查清单

- [ ] 是否维护版本矩阵？
- [ ] 模型升级前是否有 shadow mode 对比？
- [ ] 是否定义了 PromptContract 或等效的稳定接口？
- [ ] 是否有 eval fixture 集合？
- [ ] 工具 API 变更是否有检测机制？
- [ ] ConfigFingerprint 是否在每次部署时记录？

## 延伸阅读

- `value-drift.md` -- 长期行为漂移是协同演化不充分的后果之一
- `../planes/operations/configuration-lineage.md` -- 配置追踪
- `../planes/operations/rollout-and-regression.md` -- 回归检测流程
- `../learning/skill-governance.md` -- Skill 的失效触发器包含工具变更
- `../../evaluation/` -- 评估框架
