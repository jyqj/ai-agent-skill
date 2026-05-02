# Identity & Capability Plane
>
> **所属域**：5. Trust & Identity — 身份、租户与能力授权
>
> **Evidence Status** — synthesized. enterprise workflow、browser/desktop、MCP/A2A、agent platform、security agent 场景都需要显式区分用户身份、Agent 身份、工具身份、租户边界、授权来源和能力范围；否则容易出现 confused deputy、越权工具调用和审计不可归因。

**Principle Refs**: EM-03, IS-03 — 环境约束定义实际可用能力；身份与能力声明是表征而非事实，存在地图-领土偏差风险

## 定义

Identity & Capability Plane 管理“谁在让 Agent 做什么，以及 Agent 凭什么能做”。它把身份、授权、能力声明、委托链和租户边界变成一等对象。

核心原则：**能力不是工具清单，能力是带来源、范围、期限、风险和审计责任的授权。**

## CapabilityGrant Schema

```yaml
capability_grant:
  grant_id: string
  subject:
    kind: user | agent | service_account | tool | mcp_server
    id: string
  actor_on_behalf_of:
    user_id: string|null
    delegation_chain: []
  tenant_id: string|null
  scope:
    resources: []
    actions: read | propose | write | delete | send | deploy | purchase | verify | administer
    constraints: []
  trust_level: trusted_config | authenticated_user | delegated_agent | third_party_tool | untrusted_data
  expires_at: datetime|null
  approval_required_for: []
  audit_requirements: []
  revocation_condition: []
```

## 身份边界

| 身份 | 能代表什么 | 不能代表什么 |
|---|---|---|
| User Identity | 用户意图、审批、偏好 | 系统策略、第三方声明的事实 |
| Agent Identity | Agent 的执行主体、策略配置、trace 归因 | 用户本人；不得伪造用户授权 |
| Tool Identity | 工具能力、风险、输出来源 | 工具输出不能变成系统指令 |
| Service Account | 具体 API 权限 | 超出授权范围的通用行动能力 |
| MCP Server Identity | 第三方 server 的声明能力 | 用户授权或本地系统权限 |

## Confused Deputy 防护

典型攻击：第三方只读资源返回“请代我执行写操作/读取机密”。防护要求：

```text
第三方输出 → untrusted data lane
第三方 capability → 最大只能约束该 server 自己
本地工具权限 → 只能来自用户/系统授权
跨边界行动 → Control Gate 重新检查 CapabilityGrant
```

## 能力路由

工具选择前先做能力过滤：

```text
TaskEnvelope.authority_scope
  ∩ User / tenant policy
  ∩ Agent role
  ∩ Tool risk profile
  ∩ Resource sensitivity
  → AllowedCapabilitySet
```

只有 `AllowedCapabilitySet` 中的动作可以进入 Tool Runtime。被过滤掉的动作可以变成 proposal、需要审批的 InteractionEvent，或被拒绝。

## 审计字段

任何高影响动作至少记录：

```yaml
audit_context:
  actor_user_id: string|null
  agent_id: string
  tenant_id: string|null
  capability_grant_id: string
  tool_id: string
  resource_ref: string
  action: string
  reason: string
  approval_ref: string|null
  effect_record_ref: string|null
```

## 与 Control / Security 的边界

| 问题 | Identity & Capability | Control | Security |
|---|---|---|---|
| 谁发起？ | 负责 | 读取 | 读取 |
| 允许做什么？ | 定义授权范围 | 判定是否放行 | 检查攻击/泄漏风险 |
| 工具有多危险？ | 记录能力和资源范围 | 应用 risk gate | 应用 sandbox / secret policy |
| 行为如何归因？ | 审计主体和委托链 | 记录 verdict | 记录安全事件 |

## 评审清单

```text
[ ] Agent 是否区分用户身份、Agent 身份、工具身份？
[ ] 第三方 tool/MCP 输出是否只能作为 data lane？
[ ] 每个写动作是否能追溯到授权来源？
[ ] capability 是否有作用域、期限和撤销条件？
[ ] 多租户资源是否有 tenant boundary？
[ ] 高风险工具是否默认需要 approval 或 sandbox？
```

相关文件：`../control/overview.md`、`../security/overview.md`、`../../../categories/agent-platform/README.md`、`../../../evaluation/fixtures/mcp_confused_deputy_001.yaml`。
