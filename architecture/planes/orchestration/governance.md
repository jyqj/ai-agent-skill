# Multi-Agent Governance

> **所属域**：6. Coordination — 多 Agent 协作与通信
>
> **Evidence Status** — synthesized. 多 Agent 编排、冲突仲裁、级联失败处理的跨项目抽象；来自 orchestration plane 现有模式、recovery plane 的故障传播模型、identity-capability plane 的授权归因机制。

**Principle Refs**: BR-01, IS-03 — 多 Agent 协作需要预算在子代理间显式传播；各模型对世界的表征可能彼此偏离

## 核心问题

多 Agent 协作中的治理机制如何设计？当多个 Agent 共同产出一个结果时，谁对错误负责？当 Agent 之间的决策或世界状态矛盾时，由谁仲裁？当一个 Agent 崩溃时，依赖链上的其他 Agent 如何保护自己？

治理不是编排的附属功能——编排决定"谁做什么"，治理决定"出了问题谁负责、怎么解决、如何防止扩散"。没有治理的多 Agent 系统，在正常路径上可能看起来很好，但在异常路径上会快速退化为不可审计、不可归因、不可恢复的混沌状态。


## 1. 责任归因（Attribution）

### 1.1 问题

三个 Agent 协作完成一个代码修改：Planner 拆分任务、Coder 写代码、Reviewer 审查通过。上线后出了 bug。谁负责？

如果归因不可追溯，系统会出现两种退化：所有人都不负责（因为"是协作的结果"），或者所有人都被惩罚（因为无法区分）。两种情况都会破坏协作激励。

### 1.2 归因链

每个协作产出都应有一条可追溯的归因链（Attribution Chain），记录每个参与 Agent 的角色、权限范围和关键决策：

```yaml
attribution_chain:
  task_id: string
  final_output_ref: string
  contributions:
    - agent_id: planner
      role: task_decomposition
      authority_scope: propose      # 只有提案权，不直接执行
      decisions_made:
        - "将任务拆分为 3 个子任务"
        - "分配 coder-1 处理核心逻辑"
      evidence_refs: []
    - agent_id: coder-1
      role: implementation
      authority_scope: act           # 有执行权
      decisions_made:
        - "选择递归实现而非迭代"
      artifacts: ["diff_ref_001"]
      evidence_refs: []
    - agent_id: reviewer
      role: verification
      authority_scope: verify        # 有验证权
      decisions_made:
        - "审查通过，未发现边界条件问题"
      verdict: approved
```

### 1.3 authority_scope 与归因的关系

`AgentMessage.authority_scope` 不只是权限控制工具，它也是归因的关键维度：

| authority_scope | 归因权重 | 含义 |
|---|---|---|
| read_only | 低 | 只读取信息，不影响决策 |
| propose | 中 | 提出方案但不执行，方案被采纳后共担责任 |
| act | 高 | 直接执行，对执行结果负主要责任 |
| verify | 高 | 验证通过即为背书，对遗漏负责 |
| arbitrate | 最高 | 仲裁决定是最终决策，对裁决结果负责 |

### 1.4 归因反模式

- **Diffusion of Responsibility**：协作链过长，没有任何 Agent 觉得自己对最终结果负责。
- **Shadow Decision**：某个 Agent 实际上影响了决策但不在归因链中（例如通过间接修改 World State）。
- **Authority-Responsibility Mismatch**：有执行权但不承担后果，或承担后果但没有执行权。


## 2. 冲突仲裁机制

### 2.1 冲突类型

| 冲突类型 | 表现 | 严重性 |
|---|---|---|
| World State 冲突 | 两个 Agent 对同一外部对象持有不同快照 | medium — 可通过 refresh 解决 |
| 决策冲突 | 两个 Agent 对同一问题给出矛盾的方案 | high — 需要仲裁 |
| 资源冲突 | 多个 Agent 竞争同一有限资源（token 预算、工具访问） | medium — 需要调度 |
| 目标冲突 | Agent 的子目标之间互相矛盾 | critical — 需要上游修正 |

### 2.2 仲裁策略

```text
冲突发生
  → 分类（World State / 决策 / 资源 / 目标）
  → 选择仲裁策略
  → 执行仲裁
  → 记录 ArbitrationDecision
  → 通知相关 Agent
```

| 策略 | 机制 | 适用 | 风险 |
|---|---|---|---|
| Priority | 预定义 Agent 优先级，高优先覆盖 | 有明确权威来源 | 低优先级 Agent 的有效信息被忽略 |
| Voting | 多 Agent 投票，多数决 | 同质 Agent、可量化决策 | 同族模型错误相关性高 |
| Negotiation | Agent 交换论据和证据，迭代协商 | 复杂决策需多视角 | 收敛慢、可能死锁 |
| Evidence-based | 按证据强度和来源可信度裁决 | 事实性争议 | 证据质量本身难评 |
| Escalation | 升级到人类或更高权限 Agent | 影响大或无法自动解决 | 人类成为瓶颈 |
| Delegation | 交给独立仲裁 Agent | 需要中立第三方 | 仲裁 Agent 也可能出错 |

### 2.3 ArbitrationDecision

```yaml
arbitration_decision:
  decision_id: string
  conflict_ref: conflict_id
  strategy_used: priority | voting | negotiation | evidence_based | escalation | delegation
  participating_agents: []
  decision: string
  reason: string
  evidence_refs: []
  authority: agent_id | human_id
  dissenting_opinions: []         # 不同意见也要保留
  reversibility: reversible | compensable | irreversible
  review_trigger: string|null     # 何时需要复审
```

### 2.4 仲裁的元问题

谁来决定用哪种仲裁策略？这是治理的递归问题。实践中通常在系统初始化时预定义仲裁策略选择规则：

```yaml
arbitration_policy:
  world_state_conflict: refresh_then_priority
  decision_conflict_low_impact: voting
  decision_conflict_high_impact: escalation
  resource_conflict: priority_with_fairness
  goal_conflict: always_escalate
  default: escalation
```


## 3. 级联失败（Cascading Failure）

### 3.1 问题

Agent-A 产出数据 → Agent-B 基于数据做决策 → Agent-C 执行决策。如果 Agent-A 崩溃：

- 最好情况：Agent-B 检测到输入缺失，停止等待。
- 次好情况：Agent-B 使用缓存的旧数据继续，但标记为 degraded。
- 最差情况：Agent-B 因超时而产出错误决策，Agent-C 执行了这个错误决策并产生不可逆后果。

### 3.2 断路器模式（Circuit Breaker）

借鉴微服务的断路器，Agent 间的依赖调用应有三种状态：

```text
Closed（正常）
  → 依赖调用正常通过
  → 连续 N 次失败 → 切换到 Open

Open（断开）
  → 依赖调用直接快速失败，不实际调用
  → 返回 fallback 或 degraded 结果
  → 等待 cooldown 期 → 切换到 Half-Open

Half-Open（试探）
  → 允许少量调用通过试探
  → 成功 → 切换回 Closed
  → 失败 → 切换回 Open
```

```yaml
circuit_breaker:
  dependency: agent_id
  state: closed | open | half_open
  failure_threshold: 3
  cooldown_seconds: 30
  half_open_max_calls: 1
  fallback_strategy: cache | degrade | skip | escalate
```

### 3.3 隔离策略

| 策略 | 机制 | 适用 |
|---|---|---|
| Bulkhead | 将 Agent 按功能域分组，一组失败不影响其他组 | 功能域独立性高 |
| Timeout Budget | 每个 Agent 有独立 timeout，不允许无限等待上游 | 所有依赖链 |
| Blast Radius Limit | 预定义单个 Agent 失败最多影响的范围 | 关键系统 |
| Graceful Degradation | 上游不可用时切换到降级模式而非完全失败 | 可接受部分质量下降 |

### 3.4 故障传播模型

```text
Agent-A failure
  ├─ Agent-B (direct dependency)
  │   ├─ circuit breaker: OPEN → fallback
  │   └─ Agent-D (indirect dependency)
  │       └─ receives degraded input, marks output as degraded
  └─ Agent-C (direct dependency)
      └─ timeout → partial_deliver with explanation
```

关键规则：**失败的影响应该衰减，而不是放大。** 每经过一个依赖节点，失败应被包装为降级信号而非崩溃信号。如果依赖链中任何一个节点把上游的降级信号放大为自身的崩溃，那就是设计缺陷。


## 4. 治理拓扑

### 4.1 中心化治理

一个专门的 Governance Agent 负责所有治理职能：仲裁、归因审计、故障隔离策略执行。

```text
优点：一致性高、策略统一、审计简单
缺点：单点故障、可扩展性差、治理者本身可能被攻击或出错
适用：Agent 数量少、信任边界单一的系统
```

### 4.2 分布式治理

每个 Agent 自带治理逻辑，通过共享规则和信号自组织。

```text
优点：无单点故障、可扩展
缺点：一致性难保证、审计分散、规则冲突
适用：Agent 数量大、跨组织协作
```

### 4.3 混合治理（推荐）

日常治理分布式执行，高影响事件升级到中心仲裁：

```text
Layer 0: 自治 — 每个 Agent 自带 circuit breaker、timeout、local policy
Layer 1: 对等协商 — Agent 间直接协商解决低影响冲突
Layer 2: 域仲裁 — 功能域内的仲裁 Agent 处理域内冲突
Layer 3: 全局仲裁 — Governance Agent 或人类处理跨域/高影响冲突
```

```yaml
governance_topology:
  default_layer: 0
  escalation_triggers:
    - severity >= high
    - cross_domain_conflict
    - irreversible_action_disputed
    - budget_impact > threshold
  escalation_path: [self, peer, domain_arbiter, global_arbiter, human]
```


## 5. 与 Control Plane 和 Identity-Capability Plane 的关系

| 问题 | Governance | Control Plane | Identity & Capability |
|---|---|---|---|
| 谁有权仲裁？ | 定义仲裁权分配 | 执行仲裁决定的放行/拦截 | 验证仲裁者的身份和权限 |
| 责任归属 | 维护归因链 | 记录 verdict 的执行历史 | 提供 actor 身份和委托链 |
| 故障隔离 | 定义隔离策略和断路器规则 | 执行隔离动作 | 调整故障 Agent 的能力授权 |
| 冲突升级 | 定义升级路径和条件 | 路由升级请求 | 验证升级目标的权限 |
| 审计 | 归因链 + 仲裁记录 | 动作 verdict 记录 | actor + delegation_chain |

Governance 是策略层，Control 是执行层，Identity & Capability 是身份和权限的事实来源。三者协同工作：Governance 定义规则，Identity 提供凭据，Control 执行决策。


## 评审清单

```text
[ ] 每个协作任务是否有归因链（attribution chain）？
[ ] authority_scope 是否匹配实际的责任分配？
[ ] 冲突仲裁策略是否按冲突类型预定义？
[ ] 仲裁决定是否记录 dissenting opinions？
[ ] Agent 间依赖是否有 circuit breaker？
[ ] 单个 Agent 失败的 blast radius 是否有限制？
[ ] 故障信号是否在依赖链中衰减而非放大？
[ ] 治理拓扑中的升级路径是否明确？
[ ] 高影响仲裁是否最终能升级到人类？
[ ] 归因链和仲裁记录是否可供事后审计？
```

相关文件：`overview.md`、`communication.md`、`topology.md`、`shared-world-model.md`、`trust-and-attribution.md`、`../recovery/overview.md`、`../identity-capability/overview.md`、`../control/overview.md`、`../../../paradigms/collaboration-paradigms.md`、`../../../design-space/frontier/multi-agent-governance.md`。
