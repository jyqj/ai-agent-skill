# Tool System
>
> **所属域**：4. Action & Effect — 工具注册与调用边界
>
> **Evidence Status** — grounded. Claude Code、Codex、OpenCode、Augment、Hermes、VCPToolBox 对 tool registry、schema、risk policy、host layer 的实现；this repository 对工具边界、效果边界和验证契约的统一抽象。

**Principle Refs**: EM-01, IS-02 — 工具是认知延伸，工具成功 ≠ 世界状态确认。

## 定义

Tool Runtime 管理 Agent 与外部世界交互。工具面决定 Agent 能做什么，工具设计质量决定做得有多可靠。

工具设计的目标是给 Agent 一个稳定、可控、可审计、可验证的行动界面，而不只是暴露 API。

## 模块接口

**输入**：Agent Kernel 的 tool call（tool_id + args + intended_effect）
**输出**：Standard Tool Observation + Effect Candidate
**内部流程**：Schema Validation → Policy Check → Host Routing → Execute → Normalize → Effect Recording → Trace

## 工具规格 (Tool Spec)

每个工具必须定义：

```yaml
tool_id: update_ticket
capability_domain: crm
host_layer: local | remote | sidecar | mcp
risk_level: safe | check | approval | forbidden
effect_type: read | write | send | delete | deploy | purchase | notify
input_schema:
  ticket_id: string
  status: string
output_schema:
  updated: boolean
  ticket_snapshot: object | null
permission_required: [crm.write]
idempotent: false
preconditions:
  - actor_has_crm_scope
  - ticket_exists
postconditions:
  - ticket.status == "resolved"
verification_method: read_back
reversibility: reversible | compensatable | irreversible
world_state_refs: [crm.ticket]
consistency_model: strong | eventual | unknown
timeout_ms: 5000
retry_policy:
  max_retries: 1
  retry_on: [timeout, transient_io]
failure_modes: [not_found, permission_denied, timeout, stale_revision]
audit_log: true
trust_policy:
  output_tier: trusted_data | untrusted_data
```

## 设计原则

| 原则 | 含义 |
|---|---|
| Narrow Capability | 工具职责要窄，避免万能工具 |
| Typed Boundary | 输入输出必须结构化 |
| Explicit Risk | 每个工具声明风险等级与 effect type |
| Preconditions First | 写动作前明确需要满足什么 |
| Postconditions Required | 工具设计要告诉系统“成功后世界应该是什么样” |
| Observable Result | 返回值能用于推理、验证和恢复 |
| Idempotency First | 可重复执行的工具优先幂等 |
| Failure Is Data | 失败也要结构化返回 |
| Read-after-Write | 写动作默认需要回读或外部确认 |
| Untrusted Output Handling | 外部文本默认不进入 instruction lane |

## Standard Tool Observation

```yaml
tool_call_id: string
tool_id: string
status: success | failed | partial | blocked
summary: string
result: object
raw_result_refs: []
artifacts:
  - type: file | diff | url | log | screenshot | dom | row
    uri: string
side_effects:
  - type: file_write | api_write | email_send | browser_click | none
failure_mode: string | null
recoverable: boolean
suggested_recovery: string | null
normalized_as: representation_id | null
```

## Effect Ledger

工具调用结束后，不代表任务已经完成。对所有写动作，建议记录 Effect Ledger：

```yaml
effect_id: string
tool_call_id: string
target_system: github | filesystem | crm | email | calendar | browser | robot
world_object_refs: []
intended_effect: string
actual_observation: string | null
verification_status: unverified | verified | failed | partially_verified
verification_evidence: []
rollback_or_compensation: string | null
risk_level: safe | check | approval | irreversible
```

## 常见失败

| 失败 | 表现 | 修复 |
|---|---|---|
| Wrong Tool | 选错工具 | 工具描述优化 + router eval |
| Bad Arguments | 参数错误 | schema validation + 示例 |
| Tool Failure Loop | 失败后重复同一调用 | failure_mode 分类 + retry budget |
| Output Misinterpretation | 错误理解工具结果 | standard observation + parser |
| Success Without Effect | tool success 但现实没变 | postcondition + read-after-write |

## 设计模式

| 模式 | 详见 |
|---|---|
| Tool Registry | `../../../design-space/patterns/tool-registry.md` |
| Layered Tool Host | `../../../design-space/patterns/layered-tool-host.md` |
| Tool Output Sanitization | `../../../design-space/patterns/tool-output-sanitization.md` |
| MCP Trust Boundary | `../../../design-space/patterns/mcp-trust-boundary.md` |
| Effect Ledger | `../../../design-space/patterns/effect-ledger.md` |

## 参考实现

- **Claude Code**：60+ 工具、并发控制、MCP 客户端，见 `projects/coding-agents/claude-code/execution-layer.md`
- **Codex**：审批 + 沙箱 + orchestrator，见 `projects/coding-agents/codex/`
- **OpenCode**：schema 验证、权限上下文、7 个内置 agent，见 `projects/coding-agents/opencode/tool-system.md`
- **Augment**：Remote / Local / Sidecar / MCP 四层 host，见 `projects/coding-agents/augment/README.md`
- **VCPToolBox**：插件系统和分布式工具，见 `projects/tool-platforms/vcptoolbox/plugin-system.md`
