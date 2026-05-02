# Agentic Commerce & Protocol Maturation

> **Evidence Status** — speculative. Google Cloud AI Agent Trends 2026 Report；A2A 协议实践；Agent Payments Protocol (AP2)；本知识库 agent-protocols-and-boundaries 的演进。

## 背景

2025-2026 年，Agent 协议从概念讨论进入生产部署。三个关键变化：

1. **A2A (Agent-to-Agent)** 从协议提案变成跨组织生产基础设施
2. **MCP (Model Context Protocol)** 成为工具连接标准
3. **AP2 (Agent Payments Protocol)** 开辟 Agent 自主交易场景

## A2A 协议的生产化

### 从 Demo 到 Digital Assembly Line

```text
2024: 单 Agent + 工具调用
2025: 多 Agent 框架内协作 (LangGraph, CrewAI)
2026: 跨组织 Agent 互操作 (A2A production)
```

### A2A 解决的问题

| 问题 | A2A 的回答 |
|---|---|
| 跨框架 Agent 如何通信 | 标准消息协议 |
| 异步任务如何持久化 | Durable sessions + notifications |
| 结果如何流式返回 | Streaming support |
| 中断和取消如何传播 | Cancellation semantics |
| 用户授权如何跨 Agent 传递 | Delegation chain |

### Digital Assembly Line 模式

```text
Human Supervisor
  ↓ (intent)
Coordinator Agent
  ↓ A2A
┌─────────────┬──────────────┬──────────────┐
│ Research    │ Processing   │ Verification │
│ Agent      │ Agent        │ Agent        │
└─────────────┴──────────────┴──────────────┘
  ↓ A2A          ↓ A2A           ↓ A2A
External Tools  External APIs   External Systems
  (via MCP)      (via MCP)       (via MCP)
```

## Agent Payments Protocol (AP2)

### 新挑战

传统支付系统假设人类直接发起交易。当 Agent 代为交易时：

| 问题 | 核心挑战 |
|---|---|
| Authority Proof | 如何证明 Agent 获得了用户授权？ |
| Hallucination Risk | 商家如何确认 Agent 请求准确非幻觉？ |
| Accountability | 欺诈发生时谁负责？ |
| Pre-approval | 如何实现"符合条件时自动购买"？ |

### AP2 架构要素

```yaml
agent_payment_request:
  agent_id: string
  user_authority:
    user_id: string
    delegation_proof: signed_token
    constraints:
      max_amount: currency
      product_scope: []
      time_window: duration
  purchase_intent:
    item: object
    conditions: []          # 价格<100, 颜色=黑色 等
    verification_required: boolean
  merchant_validation:
    agent_identity_verified: boolean
    request_consistency_check: boolean
```

### 对本知识库的影响

- `Identity & Capability Plane`：增加 financial delegation 和 purchase authority
- `Effects Plane`：purchase 属于 irreversible effect，需要双重验证
- `Control Paradigms`：Agent 交易需要 pre-approval + spending limits + policy engine

## Intent-based Computing 范式

2026 年的交互模式转变：

```text
旧模式 (Instruction-based):
  用户 → 具体操作指令 → 系统执行

新模式 (Intent-based):
  用户 → 期望结果 → Agent 规划+执行 → 验证+交付
```

### 对 Agent 架构的影响

| 变化 | 架构响应 |
|---|---|
| 输入从指令变为意图 | Representation 层需要意图解析能力 |
| 执行路径由 Agent 自主决定 | 需要更强的 Planning + Verification |
| 用户角色从执行者变为监督者 | Interaction Plane 的 Progress Report + Approval UX 更关键 |
| 人类成为 Agent 团队管理者 | Orchestration 需要支持 fleet management |

## Security Agent 品类的成熟

### Semi-autonomous SOC Cycle

```text
Detection (AI) → Alert (Human) → Triage (AI) → Research (AI)
  → Analysis (AI) → Response (AI) → Recommendation (AI) → Escalation (Human)
```

关键特征：
- 多个 SOC Agent 共享安全遥测数据
- 通过 A2A + MCP 实现跨 Agent 通信
- 人类在 Alert 和 Escalation 节点介入
- 持续演化：基于真实攻击更新 Agent 策略

### 对 `categories/security-agent/` 的深化

- Task Model：从被动告警响应到主动 threat hunting
- Action Model：自动修复 + 自动升级 + playbook 执行
- 评估：误报率、响应时间、自动修复成功率

## 对本知识库的更新建议

| 现有文件 | 更新内容 |
|---|---|
| `frontier/agent-protocols-and-boundaries.md` | A2A 进入生产、AP2 新协议层 |
| `architecture/planes/identity-capability/overview.md` | Financial delegation chain |
| `categories/security-agent/README.md` | Semi-autonomous SOC cycle |
| `architecture/planes/interaction/overview.md` | Intent-based computing 交互模式 |
| `paradigms/collaboration-paradigms.md` | Digital assembly line 作为新模式 |

## 参考来源

- Google Cloud "AI Agent Trends 2026" Report
- Google Agent2Agent (A2A) Protocol
- Google Agent Payments Protocol (AP2)
- Salesforce + Google Cloud A2A Integration
- Torq Socrates: AI SOC Analyst
