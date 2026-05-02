# Agent 间信任与输出可信度传播

> **所属域**：6. Coordination — 多 Agent 协作与通信
>
> **Evidence Status** — synthesized. 来自 identity-capability plane 的信任层级模型、ecosystem-protocols 的信任生命周期、security plane 的信任边界、MCP trust boundary 模式的综合抽象。

**Principle Refs**: IS-03, EM-03 — 身份与能力声明是表征而非事实，存在地图-领土偏差风险；环境约束定义实际可用能力

## 核心问题

Agent 之间如何建立和维护信任？当 Agent-A 信任 Agent-B 的输出时，这个信任应该传递给 Agent-C 吗？信任如何在多跳链中衰减？跨组织的 Agent 如何在没有共同权威的情况下建立互信？

信任不是二元的"信"或"不信"，而是一个连续的、动态的、有条件的量。一个 Agent 可能信任另一个 Agent 的代码审查能力但不信任其安全评估能力。信任会因成功交互而增长，因失败或异常而衰减，因安全事件而被立即撤销。


## 1. Agent 间信任模型

### 1.1 信任的维度

信任不是单一数值。一个 Agent 对另一个 Agent 的信任至少包含以下维度：

| 维度 | 含义 | 示例 |
|---|---|---|
| Competence Trust | 对方有能力完成特定类型的任务 | "Agent-B 擅长代码审查" |
| Integrity Trust | 对方会按照声明的方式行事，不会欺骗或隐瞒 | "Agent-B 不会伪造审查结果" |
| Availability Trust | 对方会在承诺的时间内响应 | "Agent-B 通常在 30 秒内响应" |
| Boundary Trust | 对方会遵守权限边界，不越权操作 | "Agent-B 只会读取被授权的文件" |

### 1.2 信任生命周期

```text
Unknown（未知）
  → 身份验证通过 → Provisional（临时信任）
  → 沙箱期内成功交互 → Established（已建立）
  → 持续成功 + 历史积累 → High（高信任）
  → 长期无交互 → Decayed（衰减）
  → 失败/异常 → Degraded（降级）
  → 安全事件 → Revoked（撤销）
```

```yaml
trust_record:
  truster: agent_id
  trustee: agent_id
  dimensions:
    competence:
      level: float  # 0.0 - 1.0
      domain: string  # 信任的具体能力域
      evidence_count: integer
      last_success: datetime
      last_failure: datetime|null
    integrity:
      level: float
      violations: integer
    availability:
      level: float
      avg_response_time: duration
      timeout_count: integer
    boundary:
      level: float
      boundary_violations: integer
  overall_trust: float  # 加权综合
  status: unknown | provisional | established | high | decayed | degraded | revoked
  updated_at: datetime
```

### 1.3 信任更新规则

信任的增长应慢于衰减——建立信任需要多次成功交互，但一次严重失败就可以大幅降低信任。

```yaml
trust_update_rules:
  success:
    increment: 0.02          # 每次成功交互增加 2%
    max: 0.95                # 永远不到 100%——不存在无条件信任
    requires: verified_outcome  # 必须验证实际结果，不只是"工具返回成功"
  failure:
    decrement: 0.10          # 每次失败减少 10%
    severity_multiplier:
      low: 1.0
      medium: 2.0
      high: 5.0              # 高严重性失败直接减 50%
  decay:
    rate: 0.01_per_day       # 每天无交互衰减 1%
    floor: 0.20              # 不低于 20%——保留历史信誉基线
    reactivation: one_success  # 一次成功交互可恢复到衰减前水平
  revocation:
    triggers:
      - security_violation
      - integrity_breach
      - unauthorized_escalation
    recovery: requires_human_review
```


## 2. 输出可信度传播

### 2.1 问题

Agent-A 请求 Agent-B 做代码审查。Agent-B 返回"代码没有问题"。Agent-A 应该以什么置信度接受这个结论？

如果 Agent-A 对 Agent-B 在代码审查维度的信任是 0.8，那么 Agent-B 输出的置信度上限就是 0.8。即使 Agent-B 自称"100% 确定代码没有问题"，Agent-A 看到的有效置信度也只能是 0.8。

### 2.2 信任衰减公式

在多跳链中，信任按乘法衰减：

```text
Agent-A → Agent-B → Agent-C → Agent-D

A 对 B 的信任: 0.9
B 对 C 的信任: 0.8
C 对 D 的信任: 0.7

A 对 D 输出的有效信任: 0.9 × 0.8 × 0.7 = 0.504
```

这意味着三跳之后，即使每一跳的信任都很高（0.7-0.9），综合信任也会降到 0.5 左右。这是一个有用的自然约束——它防止系统过度信任经过多次转手的信息。

### 2.3 可信度传播的标注

每个 Agent 的输出应携带可信度元数据：

```yaml
output_trustworthiness:
  producer: agent_id
  claim: string
  self_confidence: float          # 产出者的自评置信度
  evidence_refs: []
  verification_status: unverified | self_verified | peer_verified | human_verified
  trust_chain:
    - agent_id: agent_b
      trust_at_time: 0.85
      role: producer
    - agent_id: agent_a
      trust_at_time: 0.90
      role: consumer
  effective_confidence: float     # self_confidence × trust_chain 乘积
```

### 2.4 信任衰减的实际影响

| effective_confidence | 建议处理 |
|---|---|
| > 0.8 | 可直接使用 |
| 0.5 - 0.8 | 标记为 needs_review，建议独立验证 |
| 0.3 - 0.5 | 只作为参考信息，不作为决策依据 |
| < 0.3 | 等同于未验证信息 |


## 3. 身份联邦

### 3.1 问题

当 Agent 跨组织协作时，没有共同的身份权威。Organization-A 的 Agent 凭什么相信 Organization-B 的 Agent 的身份声明？Organization-B 的能力声明可信吗？

### 3.2 联邦身份模型

```text
Organization-A                    Organization-B
├── Identity Provider-A            ├── Identity Provider-B
├── Agent-A1                       ├── Agent-B1
├── Agent-A2                       ├── Agent-B2
└── Capability Registry-A          └── Capability Registry-B
         │                                  │
         └────── Federation Protocol ───────┘
                      │
              Trust Anchor / Bridge
```

联邦协作需要解决三个层面的问题：

| 层面 | 问题 | 解决方式 |
|---|---|---|
| 身份验证 | 对方 Agent 是它声称的那个吗？ | 跨组织证书交换、OAuth 2.0 federation、DID |
| 能力声明 | 对方 Agent 真的有它声称的能力吗？ | 能力注册表互认、第三方能力认证 |
| 行为约束 | 对方 Agent 会遵守我们的策略吗？ | 协作契约、sandbox 执行、行为审计 |

### 3.3 联邦信任的启动

跨组织信任从零开始，不能继承组织内部的信任等级：

```yaml
federation_trust_bootstrap:
  step_1_identity:
    method: mutual_tls | oauth2_federation | did_verification
    result: identity_verified
  step_2_capability:
    method: capability_advertisement + sandbox_test
    result: capabilities_validated
  step_3_contract:
    method: signed_collaboration_contract
    content:
      - data_handling_policy
      - failure_responsibility
      - audit_access_rights
      - dispute_resolution_mechanism
    result: contract_established
  step_4_probation:
    duration: configurable
    restrictions: read_only | sandboxed_actions
    monitoring: enhanced
    result: probation_passed
  step_5_operational:
    trust_level: established
    monitoring: standard
    review_cadence: periodic
```

### 3.4 能力声明标准化

跨组织协作需要标准化的能力声明格式，使得不同组织的 Agent 可以理解彼此的能力：

```yaml
capability_declaration:
  agent_id: string
  organization: string
  protocol_versions: ["mcp/1.1", "a2a/0.9"]
  capabilities:
    - domain: code_review
      languages: ["python", "typescript"]
      confidence: 0.85
      throughput: "10 files / minute"
      certification: self_declared | org_certified | third_party_certified
    - domain: security_audit
      standards: ["owasp_top_10"]
      confidence: 0.70
      certification: third_party_certified
      certifier: "security-cert-org"
  constraints:
    max_context_size: 128000
    supported_modalities: ["text", "code"]
    data_residency: ["us", "eu"]
```


## 4. 信任与权限的关系

### 4.1 信任不等于权限

信任是对 Agent 行为可预测性的评估；权限是对 Agent 被允许执行的动作的约束。高信任不意味着高权限，低信任不意味着零权限。

```text
信任高 + 权限高 → 正常高效运行
信任高 + 权限低 → 安全但可能低效（over-constrained）
信任低 + 权限高 → 危险（under-monitored）← 必须避免
信任低 + 权限低 → 安全但功能有限
```

### 4.2 信任作为权限调节器

信任不直接决定权限，但影响权限授予的决策：

```yaml
trust_to_permission_policy:
  - condition: "trust.overall >= 0.8 AND trust.boundary >= 0.9"
    effect: "允许自动授予 read_write 权限"
  - condition: "trust.overall >= 0.5 AND trust.overall < 0.8"
    effect: "read_write 权限需要人工审批"
  - condition: "trust.overall < 0.5"
    effect: "限制为 read_only，提升需要人工审批 + 增强监控"
  - condition: "trust.integrity < 0.3"
    effect: "暂停所有非读权限，触发安全审查"
```

### 4.3 与 Identity & Capability Plane 的映射

Identity & Capability Plane 的 `CapabilityGrant` 定义了静态权限边界。信任模型在此基础上提供动态调节：

```text
CapabilityGrant（静态上限）
  × trust_level（动态调节）
  → effective_permission（实际可用权限）
```

一个 Agent 可能被授予了 `write` 权限（CapabilityGrant），但如果当前信任等级低于阈值，实际执行时会被降级为 `propose`——它可以提出写操作的提案，但需要人工或高信任 Agent 审批后才能执行。


## 5. 与 MCP Trust Boundary 的关系

MCP 场景下的信任边界是本模型的一个具体实例：

| 本模型概念 | MCP 场景对应 |
|---|---|
| Competence Trust | MCP Server 的 tool 能力声明 |
| Integrity Trust | MCP Server 是否诚实返回结果 |
| Boundary Trust | MCP Server 是否遵守权限沙箱 |
| 联邦身份 | 第三方 MCP Server 的身份验证 |
| 信任衰减 | MCP Server 长期不使用后的权限降级 |
| 可信度传播 | MCP 工具输出进入 Agent 推理链后的置信度标注 |

MCP 的 trust boundary 核心原则——"第三方输出是 untrusted data，不能提升为 instruction"——在本模型中对应的是：外部 Agent 的输出 `effective_confidence` 永远受到信任链衰减的约束，永远不会达到与本地产出相同的置信度。

详见 `../../../design-space/patterns/mcp-trust-boundary.md`。


## 评审清单

```text
[ ] Agent 间信任是否有明确的维度划分（能力/诚信/可用性/边界）？
[ ] 信任更新是否非对称——增长慢、衰减快？
[ ] 信任是否有上限（< 1.0）——是否存在无条件信任？
[ ] 多跳信任链的 effective_confidence 是否按乘法衰减？
[ ] 低 effective_confidence 的输出是否被标记为 needs_review？
[ ] 跨组织协作是否有联邦身份验证机制？
[ ] 能力声明是否有认证层级（自声明/组织认证/第三方认证）？
[ ] 信任与权限是否独立管理但关联调节？
[ ] 信任降级是否触发权限收缩？
[ ] MCP 第三方工具输出是否遵循信任衰减约束？
```

相关文件：`governance.md`、`overview.md`、`communication.md`、`../identity-capability/overview.md`、`../security/overview.md`、`../../../design-space/patterns/mcp-trust-boundary.md`、`../../../architecture/evolution/ecosystem-protocols.md`。
