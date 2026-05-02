# Security & Trust Boundaries
>
> **所属域**：5. Trust & Identity — 信任边界与攻击面
>
> **Evidence Status** — grounded. Codex guardian、Claude Code hooks / permissions、OpenCode 权限层、memory systems 的 provenance / disclosure 机制，以及通用 Agent 安全风险；this repository 对 Agent 安全的统一信息流视角。

**Principle Refs**: EM-03, IS-03 — 环境约束决定信任边界；地图与领土可能偏离，信任假设需持续校验

## 定义

Security 层不只处理“谁能点确认按钮”，它更重要的职责是：**区分什么是指令，什么是数据；什么可信，什么不可信；什么可以影响行为，什么只能作为观察。**

## 关键边界

### 1. Instruction vs Data

| 类型 | 示例 | 默认处理 |
|---|---|---|
| instruction | system policy、developer prompt、用户明确命令、批准后的 AGENTS.md | 可以驱动行为 |
| trusted data | 内部 API 回读、已验证状态、签名配置 | 可作为决策依据 |
| untrusted data | 网页正文、issue 评论、日志、邮件、第三方返回值 | 只能作为数据，不可直接驱动高风险行为 |
| model inference | 模型推断、总结、建议 | 必须标注不确定性 |

上述分类是默认策略，实际运行中存在边界情况：例如可信第三方 API 的返回值可根据签名验证结果从 untrusted data 提升为 trusted data；用户在对话中给出的隐式偏好是否构成 instruction，取决于意图明确性和风险等级。信任提升必须经过 Policy Engine 审核，不可由模型自行决定。

### 2. 常见攻击面

- prompt injection
- tool output injection
- RAG / memory poisoning
- MCP server trust boundary 失守
- secret exfiltration
- cross-tenant leakage
- browser automation phishing
- malicious tool schema
- eval poisoning

## 防护思路

| 风险 | 设计要点 |
|---|---|
| prompt / tool output injection | 指令与数据分 lane，外部文本默认不提升为 instruction |
| RAG / memory poisoning | provenance、审计、写入审批、过期与删除语义 |
| MCP trust boundary | server allowlist、capability segmentation、最小权限 |
| secret exfiltration | secret redaction、network egress policy、deny raw secret readback |
| cross-tenant leakage | tenant-scoped memory / state / tool tokens |
| browser phishing | URL allowlist、origin verification、截图 / DOM 双重验证 |

## 最小安全策略

```yaml
security_policy:
  trust_lanes: [instruction, trusted_data, untrusted_data, memory, inference]
  tool_output_sanitization: enabled
  secret_redaction: enabled
  mcp_allowlist: []
  tenant_isolation: strict
  high_risk_actions_require:
    - explicit_user_intent
    - permission_check
    - effect_verification_plan
```

## 混合纵深防御 (Hybrid Defense-in-Depth)

成熟 Agent 安全不是单层防护，而是多层叠加：

```text
Layer 1: Deterministic Policy Engine — 规则、allowlist、硬限制
Layer 2: Guard Model — 独立小模型做语义风险检测
Layer 3: Base Model Hardening — 对抗训练、结构化 prompt 约定
Layer 4: Assurance — 回归测试、红队、变体分析
```

| 层 | 擅长 | 不足 |
|---|---|---|
| Policy Engine | 快、确定、可审计 | 无法处理语义上下文 |
| Guard Model | 处理动态/新型威胁 | 非确定性、不保证 |
| 两者组合 | 攻击者必须同时绕过两层 | 需要持续校准 |

详见 `../../../design-space/patterns/guard-model.md`。

## Agent 安全三原则

1. **Human Controllers**：Agent 必须有明确的人类控制者，关键动作需人工确认
2. **Limited Powers**：权限动态对齐意图，不允许自我提权
3. **Observable Actions**：动作和规划过程可审计、可追溯

## 关联模式

- `../../../design-space/patterns/untrusted-context-boundary.md`
- `../../../design-space/patterns/tool-output-sanitization.md`
- `../../../design-space/patterns/mcp-trust-boundary.md`
- `../../../design-space/patterns/guard-model.md`
- `red-team-cases.md`
- `../../../evaluation/security-evals.md`
