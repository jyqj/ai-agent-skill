# Multi-Model Trust Boundary 交叉设计

> **Evidence Status** — grounded.
> 知识库映射: Trust&Identity (Plane — Security, Identity&Capability) x Coordination (Plane — Orchestration) x Cognition (Plane — Context)

## 为什么需要这篇文档

多模型 Agent 架构（Orchestrator + Specialist、Planner + Executor、Guard + Base）已成为生产主流。但当模型 A 的输出成为模型 B 的输入时，一个根本性的信任问题出现了：**模型 A 的输出应该被模型 B 当作指令还是数据？**

这不是理论问题。RSAC 2026 报告明确指出了三个未解决的关键缺口：
1. **无信任原语**：没有标准化的 agent-to-agent 委托信任机制
2. **无委托链产品**：目前没有任何产品实现了完整的委托链追踪
3. **临时身份生命周期未解决**：Agent 为完成任务创建的临时身份缺乏标准化的生命周期管理

ManyIH-Bench（2025）发现跨 5 个 Agent 的攻击链中，恶意指令通过输出传递逐步"洗白"为看似可信的上下文。Claude Agent SDK 的 7 层权限模型在 Agent-to-Agent 边界处缺乏对等的信任传递机制。本文档识别多模型架构中的信任边界问题，提供跨模型数据的信任标注协议和防御模式。

---

## 交叉点识别

| 交叉点 | Trust 侧关注 | Multi-Model 侧关注 | 冲突/张力 | 设计要求 |
|--------|------------|-------------------|----------|---------|
| 输出传递 | 模型输出是否应被下游信任 | 高效的模型间通信 | 信任验证延迟 vs 吞吐 | 输出信任标注 |
| 权限委托 | 委托链的可追溯性 | Orchestrator 分配子任务 | 委托链长度 vs 可审计性 | 权限衰减 + 委托链记录 |
| 注入传播 | 阻止恶意内容跨模型传播 | 模型间共享上下文 | 上下文完整性 vs 安全过滤 | 跨模型输出净化 |
| 身份管理 | 每个模型实例需要身份 | 模型按需创建和销毁 | 身份持久性 vs 临时性 | JIT 身份供应 |
| 信任评估 | 动态评估模型可信度 | 模型能力不对等 | 统一标准 vs 差异化评估 | 分层信任评分 |
| 审计归因 | 行为归因到具体模型 | 多模型协作产出 | 归因粒度 vs 审计成本 | 全链路 trace |

---

## 模型输出信任分层

### 跨模型数据的信任等级

不同角色的模型输出应有不同的信任等级。信任等级决定下游模型如何处理这些输出。

| 输出来源 | 信任等级 | 下游处理方式 | 可驱动的行为 |
|---------|---------|------------|------------|
| System Policy / Config | system_trusted | 直接作为约束 | 安全策略、权限边界、硬限制 |
| Orchestrator 输出 | orchestrator_trusted | 可作为任务分解和路由指令 | 子任务分配、模型选择、优先级 |
| Specialist 输出 | semi_trusted | 可作为决策参考，需验证 | 分析结论、代码建议、搜索结果 |
| External Model 输出 | untrusted | 仅作为数据，需净化 | 参考信息，不可驱动行为 |
| User-Provided Model 输出 | untrusted | 严格净化 + 隔离 | 参考信息，经审查后可用 |

### 信任等级不可自升

**关键约束**：模型不能通过声明提升自己的信任等级。信任等级由以下因素决定：
- 架构角色（Orchestrator / Specialist / Guard）
- 身份验证结果
- 历史行为信誉
- 运行时行为监控

---

## 三个关键缺口（RSAC 2026）

| 缺口 | 现状 | 后果 | 设计方向 |
|------|------|------|---------|
| **无信任原语** | 无标准化方式表达"信任你在此范围行动" | 委托全有或全无，Specialist 继承全部权限 | 结构化 delegation_grant（scope + constraints + TTL + depth） |
| **无委托链产品** | A→B→C 时无完整委托链追踪 | 末端动作无法追溯原始意图；权限可能放大 | 每跳记录 scope_snapshot；权限单调衰减 `scope(n+1) ⊆ scope(n)` |
| **临时身份无生命周期** | 动态创建的模型实例缺乏标准化身份管理 | 任务结束后仍持有凭据；身份回收延迟 | JIT 身份：task_binding + TTL + auto_revoke_on |

### Delegation Grant Schema（缺口 1 设计方向）

```yaml
delegation_grant:
  delegator: orchestrator_instance_id
  delegate: specialist_instance_id
  scope:
    resources: [crm.ticket.12345]
    actions: [read, propose]          # 不含 write
    tools: [search_api, read_api]     # 不含 write_api
  constraints:
    max_steps: 10
    max_tokens: 50000
    prohibited_patterns: [delete, send_email]
  expires_at: "2026-05-07T12:30:00Z"  # 15 分钟 TTL
  delegation_depth: 1                  # 不允许再次委托
  audit_required: true
```

### JIT Identity（缺口 3 设计方向）

每个临时模型实例分配包含 `instance_id`、`model_id`、`role`、`task_binding`、`ttl`、`auto_revoke_on`（task_complete / ttl_expire / anomaly_detected）和 `delegation_attributes` 的身份对象。

---

## 跨模型注入攻击

### 攻击模式

当弱安全模型的输出被注入到强安全模型的上下文中时，攻击面显著扩大。

| 攻击模式 | 描述 | 风险等级 |
|---------|------|---------|
| **Output-as-Instruction** | Specialist 输出包含隐藏指令，Orchestrator 将其当作可信上下文 | Critical |
| **Trust Laundering** | 恶意内容通过多跳传递逐步"洗白"，从 untrusted 变成看似 trusted | Critical |
| **Privilege Escalation via Delegation** | 低权限模型通过委托链获取超出自身范围的权限 | High |
| **Context Poisoning** | 恶意 Specialist 输出污染共享上下文，影响其他 Specialist | High |
| **Identity Spoofing** | 模型实例伪造身份标识，冒充更高权限角色 | High |

**ManyIH-Bench 发现**：攻击链越长，单点检测率越低；恶意指令在 Agent 间被"摘要"和"重述"，形态变化使签名检测失效；5-hop 链的端到端检测率显著低于单跳。

---

## 防御模式

### 模式 1: 跨模型输出净化

每个模型的输出在传递给下游模型前，必须经过净化层。

```text
Model A Output
  → 移除潜在指令模式（正则 + 语义分类器）
  → 标注信任等级和来源
  → 结构化封装（区分 data / conclusion / uncertainty）
  → 传递给 Model B
```

### 模式 2: 信任标签协议

所有跨模型数据必须携带不可篡改的信任标签，包含：`source_instance_id`、`source_role`、`trust_level`、`content_hash`（防篡改）、`delegation_chain`（完整委托链）、`max_downstream_trust`（下游信任上限，只降不升）。

### 模式 3: 角色隔离输出过滤

不同角色的模型，其输出被允许包含的内容类别不同。

| 角色 | 允许的输出类别 | 禁止的输出类别 |
|------|-------------|--------------|
| Orchestrator | 任务分解、路由、优先级 | 直接工具调用、外部通信 |
| Specialist | 分析结论、代码、建议 | 权限变更、策略修改 |
| Guard | 风险评估、审批决定 | 任务执行、数据修改 |
| Evaluator | 质量评分、改进建议 | 行为指令、权限授予 |

### 模式 4: Microsoft IATP 参考

Microsoft Inter-Agent Trust Protocol 提出基于密码学的方案：DID-based Identity（跨平台验证）、Dynamic Trust Scoring（0-1000 分，基于行为历史）、Behavioral Decay（信任分数随时间衰减）、Verifiable Credentials（能力声明通过凭证背书而非自我声明）。

---

## 常见错误与案例

### 错误 1: 隐式信任 Orchestrator 的全部输出

**表现**: 下游 Specialist 将 Orchestrator 的输出全部视为系统指令
**修正**: 只有结构化任务分配字段被视为指令，自由文本仅作为参考

### 错误 2: 委托链中权限不衰减

**表现**: Agent A 委托 Agent B 时，B 继承 A 的全部权限
**修正**: 每一跳 scope 只能缩小不能扩大；`scope(n+1) ⊆ scope(n)`

### 错误 3: 临时模型实例的凭据不回收

**表现**: 子任务模型实例在任务完成后仍持有有效凭据
**修正**: JIT 身份绑定 TTL + task_id；任务完成或 TTL 到期时自动撤销

### 错误 4: Guard Model 输出无独立通道

**表现**: Guard Model 的安全判断通过相同上下文通道传递，攻击者可伪造"安全通过"
**修正**: Guard 判断通过独立通道（带签名）传递，不混入普通上下文

---

## 设计启发

1. **模型输出默认是数据，不是指令。** 任何模型的输出在被下游模型消费时，都应被视为待验证的数据，而非可信的指令。只有经过结构化提取和信任标注的字段才能驱动行为。
2. **信任在委托链中只能衰减。** 每一跳委托都应缩小权限范围。如果末端 Agent 需要超出委托范围的权限，必须回溯到原始授权者重新获取。
3. **临时身份需要确定性生命周期。** JIT 身份的创建、使用、过期和撤销必须有明确的机制，不能依赖"垃圾回收"式的事后清理。
4. **跨模型净化是必须的，即使两个模型都"可信"。** 信任不具有传递性：Model A 可信且 Model B 可信，不意味着 A 的输出在 B 的上下文中是安全的。
5. **多跳攻击需要端到端防御。** 单点检测在长委托链中不够。需要在每个边界净化 + 端到端的委托链完整性校验。
6. **行为比身份更重要。** 静态身份验证只是基线，动态行为监控（异常输出模式、权限使用模式）是检测已被攻陷模型的关键手段。
7. **RSAC 三个缺口是当前产业的共同盲区。** 在标准化方案出现前，每个多模型系统都需要自行设计委托信任、委托链追踪和临时身份管理。

---

## 与知识库的映射

| 本文档章节 | 映射到的 Plane / 文档 | 关系说明 |
|-----------|---------------------|---------|
| 模型输出信任分层 | `architecture/planes/security/overview.md` — Instruction vs Data | 信任分道在跨模型场景的扩展 |
| RSAC 三个缺口 | `architecture/planes/identity-capability/overview.md` — CapabilityGrant | 委托信任的 schema 基础 |
| 跨模型注入 | `architecture/planes/security/overview.md` — prompt injection | 注入攻击在多模型场景的传播 |
| JIT 身份 | `architecture/planes/identity-capability/overview.md` — 身份边界 | Agent Identity 的临时化扩展 |
| 委托链 | `architecture/planes/orchestration/trust-and-attribution.md` | 多 Agent 信任与归因 |
| Guard Model | `architecture/planes/security/overview.md` — Guard Model | 独立安全模型的信任定位 |
| 角色隔离 | `architecture/multi-model/` | 多模型架构中的角色定义 |
| 行为监控 | `architecture/planes/orchestration/governance.md` | 运行时治理与行为审计 |
