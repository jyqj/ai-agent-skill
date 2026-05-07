# Agent 记忆投毒攻击 84.3% 成功率

> **Evidence Status** — grounded. 来自 Agent Security Bench 评估（2024-2026 持续研究）、MINJA 攻击论文（NeurIPS 2025）、Palo Alto Unit42 记忆投毒研究、MemoryGraft 攻击框架。
> https://arxiv.org/abs/2601.05504
> https://unit42.paloaltonetworks.com/indirect-prompt-injection-poisons-ai-longterm-memory/
> https://arxiv.org/html/2512.16962v1

---

## 研究背景

Agent Security Bench 对 27 种攻防组合进行系统性评估，发现 Agent 记忆投毒的平均攻击成功率达到 **84.30%**。这意味着：当攻击者通过间接渠道向 Agent 提交恶意内容时，超过 8 成的概率可以成功将恶意指令持久化到 Agent 的长期记忆中，并在后续每个会话中作为系统指令自动生效。

### 与现有 `memory-injection-attack.md` 的区别

现有文件侧重于 MINJA 攻击机制和 MCP 供应链投毒向量。本文件聚焦于：
- Agent Security Bench 的系统性评估结果和量化数据
- 攻击的持久化机制和跨会话传播
- 防御体系的设计原则和权衡
- 记忆系统的信任模型重建

### 受影响的生产系统

| 系统 | 验证时间 | 攻击向量 |
|------|---------|---------|
| ChatGPT | 2024-05, 2024-09 | 对话注入、文档元数据 |
| Amazon Bedrock Agents | 2025 | memory-enabled 配置下的间接注入 |
| Gemini | 2025-02 | 邮件/文档中的嵌入指令 |
| Claude | 2026-04 | 间接 Prompt Injection |

---

## 攻击链

```text
1. 攻击者构造恶意内容——嵌入在 Agent 会处理的合法载体中
   │  ├─ 邮件正文/附件中的隐藏指令
   │  ├─ 网页中的不可见文本
   │  ├─ 文档元数据（标题、作者、注释字段）
   │  └─ 代码注释中的嵌入指令
   │
2. Agent 在正常工作流中处理该内容
   │  （Agent 无法区分"用户意图的内容"和"攻击者嵌入的指令"）
   │
3. Agent 的记忆写入机制将恶意内容提取为"有用信息"存入长期记忆
   │  ├─ XML 标签伪造：伪造 </conversation> 和 <conversation> 标签绕过会话边界
   │  ├─ 摘要欺骗：恶意内容被 Agent 的摘要机制"合法化"
   │  └─ 优先级操纵：伪造为"用户偏好"或"重要指令"类型
   │
4. 投毒记忆在后续每个会话中作为系统上下文自动注入
   │  （记忆检索机制无法区分"真实记忆"和"注入记忆"）
   │
5. 持久化自主执行——攻击者不需要再次交互
   │  ├─ 窃取后续对话内容
   │  ├─ 修改 Agent 的行为模式
   │  ├─ 注入虚假偏好/指令
   │  └─ 传播到其他 Agent（通过共享记忆）
```

### 攻击成功率数据

| 评估维度 | 数值 | 来源 |
|----------|------|------|
| MINJA 注入成功率 | 95%+ | NeurIPS 2025 |
| MINJA 攻击成功率（端到端） | 70%+ | NeurIPS 2025 |
| Agent Security Bench 平均攻击成功率 | **84.30%** | 27 种攻防组合 |
| MemoryGraft 跨会话持久化率 | 89% | arXiv 2512.16962 |

---

## 根因分析

**核心根因：Agent 的记忆系统将所有来源的信息视为同等可信，缺乏信任分层和来源追踪。**

### 信任模型缺陷

```text
当前记忆系统的隐式信任模型：

  用户直接输入  ──→ 记忆写入 ──→ 记忆检索 ──→ 系统上下文
  外部文档内容  ──→ 记忆写入 ──→ 记忆检索 ──→ 系统上下文
  邮件内容      ──→ 记忆写入 ──→ 记忆检索 ──→ 系统上下文
  网页内容      ──→ 记忆写入 ──→ 记忆检索 ──→ 系统上下文

所有来源 → 同等信任 → 同等权重注入上下文
```

应有的信任模型：

```text
  用户直接输入（高信任）──→ 验证 ──→ 带信任标注的记忆写入
  外部文档内容（中信任）──→ 消毒 + 验证 ──→ 带来源标注的记忆写入
  邮件内容（低信任）    ──→ 消毒 + 隔离 ──→ 受限记忆区（不注入系统上下文）
  网页内容（最低信任）  ──→ 消毒 + 隔离 ──→ 受限记忆区（不注入系统上下文）

不同来源 → 分层信任 → 差异化权重 → 信任感知检索
```

### 具体违反的原则

- **原则 BDI-01 违反**：信念必须从观察构建，不可假设——记忆内容被无条件视为"已验证的信念"
- **原则 IS-01 违反**：操作的是表示，不是现实——记忆中的内容是外部输入的"表示"，不应等同于事实
- **原则 MC-01 违反**：显式表达不确定性——记忆检索结果不携带置信度和来源信任标注

---

## 架构缺陷

| 缺失的 Plane / Pattern | 对应知识库位置 | 说明 |
|------------------------|---------------|------|
| Memory Write Verification | Memory Plane | 记忆写入无独立验证机制 |
| Source Trust Tagging | Representation Plane | 记忆条目不携带来源信任标注 |
| Trust-Aware Retrieval | Memory Plane | 记忆检索不考虑来源信任等级 |
| Session Boundary Enforcement | Security Plane | XML 标签伪造可绕过会话边界 |
| Memory Integrity Audit | Observability Plane | 无机制检测记忆内容是否被投毒 |
| Content Sanitization | Representation Plane | 外部内容未经消毒即进入记忆写入流程 |
| Memory Decay / Expiry | Memory Plane | 无时间衰减机制，投毒记忆永久有效 |

---

## 设计教训

1. **Agent 的记忆是攻击面，不是安全存储。** 长期记忆系统在设计上应被视为"不可信存储"——每条记忆的检索和使用都需要经过信任评估，类似数据库的输入验证。记忆不应被隐式信任。

2. **每条记忆必须携带来源信任标注（provenance tag）。** 记忆的创建来源（用户直接输入 vs. 外部文档 vs. 网页）决定了其信任等级。检索时应按信任等级过滤和加权，低信任来源的记忆不应被注入系统级上下文。

3. **记忆写入需要独立的验证门控。** 不是所有 Agent 处理的内容都应该进入长期记忆。记忆写入应该是显式、可审计的操作，而非 Agent 的隐式自动行为。高风险内容（来自外部渠道）的记忆写入应需要额外验证。

4. **会话边界必须在系统层面强制执行，不能依赖标记解析。** XML 标签伪造攻击说明：会话边界不能用可被伪造的文本标记来划分。会话隔离应在架构层面（进程隔离、加密签名的会话令牌）实现。

5. **记忆系统需要时间衰减和定期审计。** 投毒记忆的持久性是其最危险的特征。记忆条目应有 TTL（生存时间）和使用频率跟踪。长期未被验证的记忆应自动降低信任等级或标记为待审核。

6. **防御的设计必须平衡安全和功能。** Agent Security Bench 的研究同时表明：过于激进的记忆过滤会导致正常功能退化。防御体系需要精细的信任阈值校准，而非简单的全面拦截。这是一个持续的工程权衡。

7. **跨 Agent 共享记忆是攻击传播的乘数。** 如果多个 Agent 共享记忆存储，一个 Agent 的记忆被投毒会传播到所有共享该记忆的 Agent。共享记忆需要额外的隔离和验证机制。

---

## 与知识库的映射

| 知识库位置 | 关联内容 | 本案例的具体关系 |
|-----------|---------|----------------|
| `concepts/foundations/PRINCIPLE-INDEX.md` — BDI-01 | 信念从观察构建 | 记忆内容被无条件视为已验证信念 |
| `concepts/foundations/PRINCIPLE-INDEX.md` — IS-01 | 操作表示非现实 | 记忆是外部输入的表示，不等于事实 |
| `concepts/foundations/PRINCIPLE-INDEX.md` — MC-01 | 显式不确定性 | 记忆检索不携带信任标注 |
| `architecture/planes/memory/overview.md` | 记忆层 | 写入验证、信任检索、时间衰减缺失 |
| `architecture/planes/representation/overview.md` | 表示层 | 来源信任标注和内容消毒缺失 |
| `architecture/planes/security/overview.md` | 安全层 | 会话边界强制执行缺失 |
| `architecture/planes/observability/overview.md` | 可观测层 | 记忆完整性审计缺失 |
| `design-space/anti-patterns/memory-as-database.md` | 记忆即数据库反模式 | 记忆系统被隐式信任为权威存储 |
| `design-space/anti-patterns/trust-everything.md` | 信任一切反模式 | 所有来源的记忆同等信任 |
| `./memory-injection-attack.md` | 记忆注入攻击 | 本文是其量化评估和防御体系的补充 |

---

## 关联文件

- `../../architecture/planes/memory/overview.md` — 记忆层
- `../../architecture/planes/representation/overview.md` — 表示层
- `../../architecture/planes/security/overview.md` — 安全层
- `../../concepts/foundations/PRINCIPLE-INDEX.md` — BDI-01, IS-01, MC-01
- `../../design-space/anti-patterns/memory-as-database.md` — 记忆即数据库反模式
- `../../design-space/anti-patterns/trust-everything.md` — 信任一切反模式
- `./memory-injection-attack.md` — 记忆注入攻击（本文是量化评估和防御体系的补充）
