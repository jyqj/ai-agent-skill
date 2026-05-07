# Reasoning Model Integration

> **Evidence Status** — grounded。基于 2025-2026 年间 Anthropic、OpenAI、Google 推理模型的公开文档、ICLR 2025/2026 论文、ACL 2025 论文及多篇工程实践文章，与 `paradigms/reasoning-paradigms.md`、`architecture/planes/` 及 ORDA-VU 闭环的交叉综合。

---

## 核心范式转变：Inference-Time Compute Scaling

传统范式追求"训练更大的模型"来提升性能。2025-2026 年的核心转变是 **Inference-Time Compute Scaling**——在推理阶段分配更多计算资源，让模型"给自己更多时间思考"。

**关键实验数据**：

| 发现 | 来源 | 意义 |
|------|------|------|
| 7B 参数模型 + 100x 推理计算 ≈ 70B 模型 + 标准推理 | ICLR 2025 | 小模型通过推理时间换空间，逼近大模型性能 |
| 性能随 token 预算对数增长 | Anthropic Extended Thinking | 收益递减但单调增长 |
| 无单一 test-time scaling 策略普遍占优 | Scaling Test-Time Compute | 策略选择依赖任务特征 |
| 2026 年推理需求将超过训练需求 118 倍 | Zylos Research | 推理成本成为主导成本 |

**对 Agent 架构的根本影响**：

1. **模型选择从静态变为动态**——同一模型可通过 effort/budget 参数调节推理深度，不再需要为每个任务部署不同规模的模型。
2. **成本结构从可预测变为可变**——可变长度的推理 token 使单次调用成本难以提前确定。
3. **架构设计需要"推理预算管理"作为一等公民**——与延迟、可靠性并列。

---

## 三大厂商策略对比

| 维度 | Anthropic (Claude) | OpenAI (o-series / GPT) | Google (Gemini) |
|------|-------------------|------------------------|-----------------|
| **推理方式** | Extended Thinking + Adaptive Thinking | 专用推理模型 o1/o3/o4-mini | 动态思考模式（自动调整） |
| **控制粒度** | `effort` 参数 (low/medium/high/xhigh/max) | 模型选择（o4-mini vs o3-pro） | `thinking_budget` 数值 |
| **可见性** | summarized / omitted 两种模式 | 推理过程不可见（隐藏 reasoning tokens） | 可选可见 |
| **工具集成** | Interleaved thinking（工具间推理） | 原生 agentic 工具调用 | 内置 Google 生态 |
| **成本模型** | 按实际推理 token 计费 | 推理 token 独立计费（与 completion 分开） | 按 thinking budget 计费 |
| **Agent SDK 理念** | tool-use-first，子 Agent 作为 Tool | 结构化原语（agents, handoffs, guardrails） | A2A + MCP，面向企业部署 |

**策略选型启发**：

- 需要精细控制推理深度且重视调试可见性 → Anthropic
- 需要在推理模型与通用模型间硬切换 → OpenAI
- 需要与 Google 生态深度集成且偏好自动调节 → Google

---

## 对 ORDA-VU 闭环各阶段的影响

ORDA-VU（Observe → Represent → Decide → Act → Verify → Update）是本知识库的外层生命周期。推理模型对每个阶段都产生了结构性影响：

| 阶段 | 传统模式 | 推理模型增强 | 具体变化 |
|------|---------|------------|---------|
| **Observe** | 被动接收输入和工具结果 | 主动评估信息完整度，决定是否需要更多观察 | Interleaved thinking 让模型在每次工具返回后重新评估 |
| **Represent** | 将输入映射为上下文 | 推理模型能生成更结构化的中间表示 | Think tool 用于在表示阶段显式组织信息 |
| **Decide** | 单步推理选择下一步行动 | 多步内部推理，考虑更多候选方案和后果 | Extended thinking 在此阶段价值最大 |
| **Act** | 执行工具调用 | 行动前进行推理验证（pre-flight check） | 推理模型能预判工具调用可能的失败模式 |
| **Verify** | 结果校验 | 深度自我批评（Self-Critique） | Think tool + Reflective Agent 模式 |
| **Update** | 状态更新 | 推理驱动的策略调整（continual planning） | 偏差超过阈值时触发重新规划 |

**关键洞察**：推理模型让 Decide 和 Verify 阶段从"浅层模式匹配"升级为"深层因果推理"，但 Observe 和 Act 阶段仍依赖环境交互——纯推理无法替代真实世界反馈。

---

## 对五大范式族的影响

### 推理范式

推理模型最直接的影响对象。Extended Thinking 让 ReAct 循环中每步 Thought 的深度大幅增加，减少了"浅层推理 → 错误行动 → 纠正"的往复。但 ReAct 的核心价值——将推理锚定在真实世界反馈中——不可替代。纯推理模型"经常给出自信但错误的答案"，ReAct 通过环境验证降低幻觉风险。Plan-and-Execute 中，推理模型驱动的 Planner 能生成更精确的 DAG 任务分解，执行阶段可交由轻量模型完成。

### 记忆范式

推理模型影响记忆的**检索策略**而非存储结构。更强的推理能力意味着模型能更准确地判断"何时需要什么记忆"，减少不必要的检索。但推理过程本身消耗大量 token，与长上下文窗口形成张力——Context Engineering 成为关键（参见 `concepts/context-engineering.md`）。Compaction 和结构化笔记是缓解手段。

### 工具范式

推理模型让动态工具发现（Tool Search API）变得更实用——模型能更智能地决定"何时需要什么工具"，无需全量加载工具定义。MCP Sampling 允许工具执行中途请求额外推理，形成"工具调用 → 推理 → 再工具调用"的交错模式。Interleaved thinking 是此模式的原生实现。

### 协作范式

多模型 Agent 架构因推理模型而成为主流：重型推理模型做 Planner/Critic，轻量模型做 Executor/Router。从"开放式多 Agent 聊天循环"转向"显式工作流图"。Anthropic 的"单核心 Agent + 模块化子 Agent"模式成为生产最佳实践。

### 控制范式

推理模型引入了新的控制维度——**推理深度控制**（effort/budget 参数）。这与传统的执行深度控制（Execution Depth）、自主级别控制（Autonomy Level）形成三维控制空间。Budget-Aware Agent Scaling 证明显式 budget 信号可实现 40% 成本降低和 2x 性能提升。

---

## Interleaved Thinking vs Adaptive Thinking

两者是 Claude 推理模型集成的核心机制，容易混淆，需要精确区分：

| 维度 | Interleaved Thinking | Adaptive Thinking |
|------|---------------------|-------------------|
| **定义** | 工具调用之间插入思考步骤 | 模型自主决定是否/多少使用 extended thinking |
| **触发方式** | 每次工具返回结果后自动触发 | 根据请求复杂度自动判断 |
| **控制机制** | 无独立开关（随 adaptive thinking 自动启用） | `effort` 参数提供软指导 |
| **核心价值** | 工具结果的深度分析和策略调整 | 避免简单任务过度推理，复杂任务充分推理 |
| **典型场景** | 多步 agentic 工作流（搜索 → 分析 → 再搜索） | 混合复杂度的请求流（简单问答与深度分析交替） |
| **与 Think Tool 的关系** | 互补——interleaved 是自动的，think tool 是显式的 | Adaptive thinking 决定何时启用 extended thinking |
| **成本影响** | 增加中间推理 token，但减少错误重试 | 总体降低成本（简单任务少思考） |

**Think Tool 的独特定位**：

Think Tool 不属于上述任何一种机制，而是一个**显式思考工具**——模型在执行过程中主动调用它来"停下来想一想"。三大应用场景：

1. 工具输出分析：处理复杂工具返回值，可能需要改变策略
2. 策略密集环境：遵循复杂指南并验证合规性
3. 顺序决策：每步建立在前一步基础上，错误代价高

实验结果：tau-Bench 航空领域 + Think Tool + 优化提示实现 54% 相对改进（0.370 → 0.570）。

---

## 多模型 Agent 中推理模型的角色

| 角色 | 推荐模型层级 | 职责 | 推理需求 | 成本敏感度 |
|------|------------|------|---------|-----------|
| **Planner** | 重型推理模型（Opus + extended thinking, o3-pro） | DAG 任务分解、依赖识别、资源分配 | 高（deep thinking） | 低（调用频次少） |
| **Executor** | 轻量模型（Haiku, o4-mini, Gemini Flash） | 工具调用执行、数据处理 | 低（无 thinking） | 高（调用频次多） |
| **Critic** | 中/重型推理模型（Sonnet + think tool, o3） | 结果审核、错误检测、质量评估 | 中-高（reflection） | 中 |
| **Router** | 轻量模型或规则引擎 | 复杂度评估、请求分流 | 极低 | 极高 |

**层级化推理架构**：

```
简单任务 → 快速推理（单步，无 thinking）      → Haiku / Flash / o4-mini
中等任务 → 标准推理（Few-shot）                → Sonnet / GPT-4o
复杂任务 → Extended Reasoning（多步 + 验证）   → Opus / o3-pro
```

**核心设计原则**：Planner 和 Critic 用推理模型（调用少、价值高），Executor 和 Router 用轻量模型（调用多、成本敏感）。分离可减少推理成本达 45%。

---

## 成本 / 质量 / 延迟权衡

### 关键数据点

| 技术 / 框架 | 核心效果 | 来源 |
|-------------|---------|------|
| **TALE**（Token-Budget-Aware LLM Reasoning） | 减少 67% token，降低 59% 成本 | ACL 2025 |
| **Budget-Aware Agent Scaling** | 40.4% 更少搜索调用，2x 性能提升 | arXiv 2511.17006 |
| **RouteLLM** | 通过模型路由降低 85% 成本 | 综合来源 |
| **蒸馏部署** | 1/10 GPU 时间达到纯 RL 性能 | DeepSeek-R1 |
| **Prompt Caching** | 缓存 token 成本降至 0.1x | Anthropic |
| **组合优化** | 压缩 + 路由 + 缓存 = 60-80% 总成本削减 | Zylos Research |

### 统一成本度量

```
Total Agent Cost = Token Cost + (Tool Calls x Provider Pricing)

其中 Token Cost = Input Tokens x Input Price
               + Output Tokens x Output Price
               + Reasoning Tokens x Reasoning Price
```

注意：仅报告 token 成本通常低估真实费用 40-70%。全载成本还须包含基础设施、人工审核和工程维护。

### 推理模型的成本困境

| 挑战 | 数据 |
|------|------|
| 准确性门槛 | 33% 组织认为精度是生产部署主要障碍 |
| 延迟惩罚 | 20% 因响应时间受困；推理增加秒到分钟级延迟 |
| 成本不可预测 | 可变思考时间使成本预测困难 |

**缓解策略**：蒸馏部署（1/10 成本）、混合切换（快速/深度推理动态切换 + 常见模式缓存）、层级化推理（战略规划 → 战术执行 → 细节验证）。

---

## 设计决策树

按任务复杂度选择推理策略：

```text
任务到达
│
├─ 复杂度评估（Router 或规则引擎）
│  │
│  ├─ 简单（单步可完成，无工具或单工具）
│  │  → 快速模型，effort=low，无 extended thinking
│  │  → 范式：Direct Answer / Tool-Augmented Direct
│  │
│  ├─ 中等（多步但结构清晰）
│  │  ├─ 时敏？ → ReAct + 标准模型，effort=medium
│  │  └─ 非时敏？ → Plan-and-Execute，Planner effort=high
│  │
│  ├─ 复杂（多步、依赖、需验证）
│  │  ├─ 可分解？ → Planner（推理模型）+ Executor（轻量模型）
│  │  │           Budget Tracker 监控，偏差触发重规划
│  │  └─ 不可分解？ → 单一推理模型 + Interleaved Thinking
│  │                  effort=high/max + Think Tool
│  │
│  └─ 高风险不可逆
│     → Plan + Human Approval + Verification + Recovery
│     → Critic 使用推理模型独立审核
│
├─ Budget 检查
│  ├─ 充裕 → 按上述策略执行
│  └─ 受限 → 降级策略：
│     ├─ 推理模型 → 蒸馏模型
│     ├─ extended thinking → 标准推理
│     └─ 并行探索 → 顺序执行
│
└─ 持续监控
   ├─ 推理 token 占比 > 阈值 → 告警
   ├─ 工具调用超 budget → 触发 stop gate
   └─ 结果偏差超阈值 → 触发 replan
```

---

## 反模式

| 反模式 | 表现 | 根因 | 修复 |
|--------|------|------|------|
| **过度使用推理模型** | 所有任务都用 effort=max | 未做复杂度评估 | Router 分流 + effort 动态调整 |
| **忽略 budget 管理** | 推理 token 失控，成本不可预测 | 缺少 token budget 监控 | Budget Tracker + 逐 trace 成本可观测性 |
| **推理替代验证** | 模型深度推理但不做环境验证 | 过度信任推理能力 | Verify 阶段强制 effect check |
| **全量工具加载** | 将所有工具定义注入上下文 | 未使用动态工具发现 | Tool Search API + 按需加载 |
| **静态模型绑定** | 固定 Planner=Opus, Executor=Haiku | 未考虑任务粒度变化 | 动态路由 + 层级化推理架构 |
| **推理不可观测** | 推理过程对调试不可见 | 选择了隐藏 reasoning 的厂商/模式 | 使用 summarized 模式或 think tool |
| **蒸馏滞后** | 长期依赖大型推理模型而不蒸馏 | 缺少蒸馏工程投入 | 定期将高频推理模式蒸馏为专用模型 |
| **单一推理策略** | 所有任务用相同推理深度 | 未区分任务特征 | 范式选择矩阵 + 决策树 |

---

## RouteLLM 与模型路由实践

模型路由是将推理模型的高质量与轻量模型的低成本结合的关键工程手段。核心思路是在请求到达模型之前，用一个轻量级 Router 判断"这个请求是否值得调用推理模型"。

**三种路由策略**：

| 策略 | 机制 | 适用场景 | 代表实现 |
|------|------|---------|---------|
| **静态规则路由** | 基于 prompt 长度、关键词、任务标签分流 | 任务类型明确且稳定 | 自定义规则引擎 |
| **动态置信度路由** | 轻量模型先生成候选答案，置信度低于阈值时升级到推理模型 | 任务复杂度分布不均 | RouteLLM |
| **学习型路由** | 基于历史数据训练路由模型 | 有充足的历史 trace 数据 | 自定义 ML 模型 |

**成本数据**：前沿推理模型与轻量模型的成本差可达 190x。通过路由将 70-85% 的请求导向轻量模型，即使路由本身有成本，总体仍可节省 85% 以上。

**与 Agent 架构的集成**：Router 通常部署在 Agent Loop 的最外层，在 ORDA-VU 的 Decide 阶段之前做模型选择。对于多模型架构，Router 可细分为任务级路由（选择 Planner 或 Executor）和步骤级路由（同一 Agent 内根据步骤复杂度切换模型）。

---

## 具体架构设计模式速览

### 模式 1：Adaptive Reasoning Router

```
用户请求 → 复杂度评估器
    → 简单：Fast Model（无 thinking）→ 直接响应
    → 中等：Standard Model（moderate thinking）→ ReAct Loop
    → 复杂：Reasoning Model（deep thinking）→ Plan-and-Execute
```

### 模式 2：Planner-Executor with Budget Awareness

```
Reasoning Model (Planner)
    → 生成 DAG 步骤 + 预算分配
    → Budget Tracker 监控

Fast Model (Executor)
    → 逐步执行工具调用
    → 反馈偏差 → 触发 Planner 重新规划
```

### 模式 3：Interleaved Thinking Agent Loop

```
User → [Adaptive Thinking] → Tool Call 1
    → [Thinking about result] → Tool Call 2
    → [Thinking about result] → ... → Final Response

effort 动态调整：简单步骤 low，关键决策 high
```

### 模式 4：Self-Critique Reflective Agent

```
Agent Output v1
    → Self-Critique（使用 think tool）
    → 逐约束反向检查
    → SUCCESS / CONTINUE / PIVOT 决策
    → Agent Output v2
```

---

## 与知识库的映射

| 本文主题 | 知识库对应文件 | 关系 |
|---------|--------------|------|
| ORDA-VU 闭环影响 | `paradigms/reasoning-paradigms.md` | 扩展 ORDA-VU 在推理模型时代的运作方式 |
| 五大范式族影响 | `paradigms/reasoning-paradigms.md`, `paradigms/memory-paradigms.md`, `paradigms/tool-paradigms.md`, `paradigms/collaboration-paradigms.md`, `paradigms/control-paradigms.md` | 横切视角——推理模型如何改变每个范式族 |
| 多模型架构 | `architecture/multi-model/` | 角色定位表直接对接多模型架构设计 |
| 成本/质量/延迟 | `architecture/planes/` | Token 经济学影响 Context Plane、Prompting Plane |
| Adaptive Thinking | `architecture/controllers/execution-depth/overview.md` | effort 参数是 Execution Depth 的新控制维度 |
| 设计决策树 | `paradigms/decision-trees.md` | 本文决策树是 decision-trees 在推理模型场景下的特化 |
| Context Engineering | `concepts/context-engineering.md` | 推理模型的 token 消耗加剧上下文管理需求 |
| 反模式 | `design-space/lessons-learned/` | 推理模型特有的反模式补充 |
| MCP 与工具集成 | `architecture/planes/tool-integration/` | 推理模型与 MCP 的交错使用模式 |

---

相关文件：`../paradigms/reasoning-paradigms.md`、`../architecture/kernel/agent-loop.md`、`../architecture/lifecycle.md`、`../concepts/context-engineering.md`、`../paradigms/decision-trees.md`。
