# Cross-Cutting 交叉地带文档索引

> 最后更新: 2026-05-07
> 本目录包含 ai-agent-architecture-skill 知识库中跨域交叉设计文档。

## 为什么需要交叉地带文档

知识库的 9 个域、24 个 Plane 按职责划分，但生产级 Agent 系统中最复杂的设计问题往往发生在域与域的交界处。交叉地带文档识别这些交界处的设计张力、提供联合设计矩阵、记录跨域失败案例。

---

## 文档索引

| # | 文档 | 交叉域 | 核心问题 | Evidence Status |
|---|------|--------|---------|----------------|
| 1 | [memory-x-security.md](./memory-x-security.md) | Memory x Security | 记忆投毒防护、写入验证、来源追踪 | grounded |
| 2 | [paradigm-x-cost.md](./paradigm-x-cost.md) | Paradigms x Economics | 范式选择如何影响成本；成本驱动的范式降级 | grounded |
| 3 | [category-x-multi-model.md](./category-x-multi-model.md) | Categories x Multi-Model | 不同品类的多模型配置与模型角色分配 | synthesized |
| 4 | [reasoning-model-x-tool-use.md](./reasoning-model-x-tool-use.md) | Reasoning x Action | 推理模型改变工具调用模式；Interleaved Thinking | grounded |
| 5 | [protocol-x-security.md](./protocol-x-security.md) | Coordination x Trust | 协议栈中的信任边界；Confused Deputy 问题 | grounded |
| 6 | [context-engineering-x-memory.md](./context-engineering-x-memory.md) | Context x Memory x Prompting | 三层信息管理的边界重定义与流转协议 | synthesized |
| 7 | [state-x-world-state.md](./state-x-world-state.md) | State x World Modeling | 任务状态与外部世界状态的一致性裂缝 | synthesized |
| 8 | [effects-x-recovery.md](./effects-x-recovery.md) | Effects x Lifecycle | 效果验证失败时的补偿/接受/升级决策 | grounded |
| 9 | [multi-model-trust-boundary.md](./multi-model-trust-boundary.md) | Multi-Model x Trust | 多模型间的信任边界、委托链、临时身份 | grounded |
| 10 | [learning-x-safety.md](./learning-x-safety.md) | Learning x Safety | 技能结晶化中的供应链投毒与安全门控 | grounded |
| 11 | [control-identity-security-boundary.md](./control-identity-security-boundary.md) | Governance x Trust | Control/Identity/Security 三层的介入时序与职责划分 | synthesized |

---

## 按问题域导航

### 安全相关

如果你的设计问题涉及安全、信任、攻击防御：

- **记忆层安全** → [memory-x-security.md](./memory-x-security.md)
  - 记忆投毒 84.3% 攻击成功率的防御
  - 写入验证协议和来源追踪字段设计
  - 四层纵深防御模型

- **协议层安全** → [protocol-x-security.md](./protocol-x-security.md)
  - 六层协议栈的攻击面矩阵
  - Confused Deputy 在协议层的五种表现
  - 协议间信任传递链

- **多模型信任边界** → [multi-model-trust-boundary.md](./multi-model-trust-boundary.md)
  - 跨模型输出的信任分层与净化协议
  - RSAC 2026 三个关键缺口（信任原语、委托链、临时身份）
  - 跨模型注入攻击与 Trust Laundering

- **技能安全** → [learning-x-safety.md](./learning-x-safety.md)
  - ClawHavoc ~1,200 恶意技能的供应链投毒防御
  - 六阶段安全门控（candidate → quarantine → shadow → activated → monitored → retired）
  - 记忆投毒 → 技能投毒的传导链阻断

### 成本相关

如果你的设计问题涉及成本优化、预算管理：

- **范式与成本** → [paradigm-x-cost.md](./paradigm-x-cost.md)
  - 范式 x 成本矩阵（ReAct/Plan-and-Execute/ReWOO/Hybrid/Reflective）
  - Budget 耗尽时的降级策略
  - 成本优化组合效果（60-80% 总成本削减）

- **上下文与成本** → [context-engineering-x-memory.md](./context-engineering-x-memory.md)
  - Context Rot 的量化模型
  - Anthropic 三策略的统一实现
  - 上下文窗口 n^2 缩放的应对

### 架构设计

如果你的设计问题涉及模型选择、架构模式：

- **品类与模型** → [category-x-multi-model.md](./category-x-multi-model.md)
  - 四大品类的多模型配置（Coding/Research/Browser/Companion）
  - 品类感知的模型路由决策树
  - 品类 x 关键设计维度矩阵

- **推理与工具** → [reasoning-model-x-tool-use.md](./reasoning-model-x-tool-use.md)
  - 五种推理-工具交互模式对比
  - Interleaved Thinking 的工具间推理详解
  - 推理-行动平衡的成本影响

### 状态与一致性

如果你的设计问题涉及状态管理、一致性、恢复：

- **任务状态 vs 世界状态** → [state-x-world-state.md](./state-x-world-state.md)
  - Stale-Read / Write-After-Read / Phantom Completion 等一致性裂缝
  - 乐观 vs 悲观一致性策略矩阵
  - Refresh-Before-Write / Version-Gated Execution 缓解模式

- **效果验证与恢复** → [effects-x-recovery.md](./effects-x-recovery.md)
  - 效果类型 x 可逆性 x 影响半径 x 时间 → 补偿/重试/升级/接受决策
  - 部分效果的选择性补偿协议
  - 异步验证超时的截止时间升级

---

## 交叉引用关系

```
memory-x-security ←→ protocol-x-security
    记忆投毒是 Memory-Aided Confused Deputy

memory-x-security ←→ context-engineering-x-memory
    记忆注入 Context 时的安全检查

paradigm-x-cost ←→ reasoning-model-x-tool-use
    推理深度与成本的 effort 动态调整

paradigm-x-cost ←→ category-x-multi-model
    品类决定范式选择，范式决定成本结构

category-x-multi-model ←→ reasoning-model-x-tool-use
    品类的工具使用模式受推理模型能力影响

context-engineering-x-memory ←→ paradigm-x-cost
    上下文管理策略影响范式的实际成本

state-x-world-state ←→ effects-x-recovery
    世界状态不一致导致效果验证失败，触发恢复决策

effects-x-recovery ←→ paradigm-x-cost
    恢复/补偿消耗 Recovery Budget，影响任务总成本

multi-model-trust-boundary ←→ protocol-x-security
    多模型信任边界是协议层 Confused Deputy 的扩展

multi-model-trust-boundary ←→ memory-x-security
    跨模型输出传递可被利用为记忆投毒向量

learning-x-safety ←→ memory-x-security
    记忆投毒 → 技能投毒的传导链

learning-x-safety ←→ multi-model-trust-boundary
    恶意技能可能通过多模型委托链传播
```

---

## 引用的关键数据源

| 数据点 | 来源语料 | 引用文档 |
|--------|---------|---------|
| 记忆投毒 84.3% 攻击成功率 | ai-agent-failure-casebook 案例 14 | memory-x-security |
| ClawHavoc 824 恶意技能 | ai-agent-failure-casebook 案例 11 | memory-x-security, protocol-x-security |
| RouteLLM -85% 成本 | agent-evaluation-cost-corpus 3.2 | paradigm-x-cost |
| TALE -67% token | reasoning-models-corpus 6.1 | paradigm-x-cost |
| Budget-Aware -40%+2x | reasoning-models-corpus 6.2 | paradigm-x-cost |
| Planner-Executor -45% 成本 | reasoning-models-corpus 3.1 | category-x-multi-model |
| Interleaved Thinking 54% 改进 | reasoning-models-corpus 5.1 | reasoning-model-x-tool-use |
| A2A Agent Card 签名 | multi-agent-coordination-corpus 2.2 | protocol-x-security |
| AP2 Verifiable Credentials | multi-agent-coordination-corpus 7.3 | protocol-x-security |
| Anthropic 三策略 | agent-evaluation-cost-corpus 3.3 | context-engineering-x-memory |
| Context 64x 成本放大 | agent-evaluation-cost-corpus 3.1 | context-engineering-x-memory |
| RSAC 2026 三个信任缺口 | multi-agent-coordination-corpus | multi-model-trust-boundary |
| ManyIH-Bench 多跳注入 | multi-agent-coordination-corpus | multi-model-trust-boundary |
| Microsoft IATP DID 信任 | multi-agent-coordination-corpus | multi-model-trust-boundary |
| ClawHavoc ~1,200 恶意技能 | ai-agent-failure-casebook 案例 11 | learning-x-safety |
| MINJA 95% 注入成功率 | ai-agent-failure-casebook 案例 14 | learning-x-safety |
| SkillsBench 自生成 -1.3pp | arXiv 2602.20867 | learning-x-safety |
