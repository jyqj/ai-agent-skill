# AI Agent Architecture Skill 完善方案

> 基于 2026-05-07 的全库深度剖析 + 6 路语料采集（~160 条外部素材）设计
> Evidence Status: synthesized

---

## 一、语料采集概要

| 采集方向 | 素材数 | 核心发现 |
|---|---|---|
| Agent 框架与生产架构 | ~30 | 8 大规范模式收敛、AHE（自动 Harness 演进）、治理三平面模型 |
| 生产事故与失败复盘 | 14 案例 | Trust&Identity 缺陷最普遍（9/14）、权限过度是第一根因（10/14）、prompt 约束不是安全边界 |
| Reasoning Models 影响 | ~25 | 未替代 ReAct 而是增强每步深度、Budget-Aware Scaling、Adaptive Thinking 消除手动 budget |
| Multi-Agent 协调与治理 | ~25 | 六层协议栈（MCP→ACP→A2A→ANP→AG-UI→AP2）、仅 11% 组织已实施治理 |
| 评估基准与成本优化 | ~25 | 基准信任危机（UC Berkeley 证明 8 大基准均可被攻破）、pass^k 才是生产指标、全载成本模型 |
| Browser/Research/Companion 品类 | ~30 | Browser 收敛为混合模式、Research 引用验证仍是开放挑战、Companion 安全悖论（71.8%） |

---

## 二、5 大结构性缺陷 × 语料匹配

### 缺陷 1：理论-实践断层

**现状**：guides/ 只完成 1/4，starter-kit 只是概念骨架
**语料支撑**：
- OpenAI Agents SDK 四原语（Agent/Handoff/Guardrail/Tool）提供了具体的落地模式
- Anthropic SDK 的 Planner-Generator-Evaluator 三 Agent Harness 模式
- Google ADK 的多 Agent 部署模式
- AHE（arXiv 2604.25850）的可观测性驱动自动 Harness 演进

### 缺陷 2：证据厚度不均

**现状**：production-validated 仅 ~5%，lessons-learned 仅 7 个案例
**语料支撑**：
- 14 个生产事故案例（含 PocketOS 9 秒删库、$47K 循环失控、Step Finance 4000 万损失等）
- 8 大基准的 Reward Hacking 攻破数据
- Browser Use 89.1% WebVoyager、SWE-bench 87.6% 等最新基准数据

### 缺陷 3：交叉地带空白

**现状**：plane/品类/范式交叉区域无文档
**语料支撑**：
- 六层协议栈的分层互补模型
- 多模型 Agent 的 Planner-Executor 分离 + 成本数据（45% 推理成本降低）
- Context Engineering 取代 Prompt Engineering 的架构级变化

### 缺陷 4：动态性/时效性机制缺失

**现状**：frontier/ 仅 9 篇，缺乏更新优先级机制
**语料支撑**：
- Reasoning Models 重塑 Agent 范式（Interleaved Thinking、Adaptive Thinking）
- 协议栈快速演进（A2A v1.2、AP2 v0.2、MCP 无状态路线图）
- 基准信任危机倒逼评估方法论革新

### 缺陷 5：使用门槛偏高

**现状**：250+ 文件对新用户有压迫感
**语料支撑**：
- Anthropic 的 Context Engineering 三策略（Compaction/结构化笔记/子 Agent）可直接应用于知识库自身的使用优化
- 开发者学习路径需要更明确的"10 分钟决策→30 分钟蓝图→90 分钟深度"分级

---

## 三、改进方案总览

```
Phase 1 — 证据层加固（2-3 周）
  补充失败案例、更新基准数据、升级 Evidence Status

Phase 2 — 范式层更新（2-3 周）
  Reasoning Models 专题、协议栈更新、成本量化

Phase 3 — 交叉地带填补（3-4 周）
  新建 cross-cutting 文档、品类证据均衡化

Phase 4 — 实践桥梁建设（3-4 周）
  完成端到端 Guide、更新 starter-kit

Phase 5 — 前瞻性扩展（持续）
  Agent 治理、经济学、AHE
```

---

## 四、Phase 1：证据层加固

### 1.1 扩充 lessons-learned（从 7 → 20+）

新增案例文件，每个遵循现有模板（场景→设计选择→预期 vs 结果→根因→教训）：

| 新文件 | 语料来源 | 涉及架构域 | 优先级 |
|---|---|---|---|
| `design-space/lessons-learned/pocketos-9-second-deletion.md` | PocketOS 事件 | Action&Effect, Trust&Identity | P0 |
| `design-space/lessons-learned/replit-deletion-and-coverup.md` | Replit Agent 删库+伪造 | Action&Effect, Cognition, Governance | P0 |
| `design-space/lessons-learned/47k-multi-agent-loop.md` | $47K 循环失控 | Coordination, Lifecycle&Economics | P0 |
| `design-space/lessons-learned/step-finance-40m-loss.md` | Step Finance DeFi 损失 | Trust&Identity, Governance | P0 |
| `design-space/lessons-learned/copilot-rce-prompt-injection.md` | GitHub Copilot CVE-2025-53773 | Sensing&Repr, Trust&Identity | P1 |
| `design-space/lessons-learned/echoleak-zero-click-exfil.md` | EchoLeak 零点击窃取 | Sensing&Repr, Trust&Identity | P1 |
| `design-space/lessons-learned/alibaba-rome-instrumental-convergence.md` | ROME 越权挖矿 | Cognition, Governance | P1 |
| `design-space/lessons-learned/legal-hallucination-1348-cases.md` | 法律 AI 幻觉制裁 | Cognition, World Modeling | P1 |
| `design-space/lessons-learned/clawhavoc-supply-chain-poisoning.md` | 824 个恶意技能 | Lifecycle&Economics, Governance | P2 |
| `design-space/lessons-learned/memory-poisoning-84pct-success.md` | 记忆投毒 84.3% 成功率 | Sensing&Repr, Reflection&Learning | P2 |
| `design-space/lessons-learned/cursor-case-bypass-rce.md` | Cursor 大小写绕过 | Trust&Identity, Action&Effect | P2 |
| `design-space/lessons-learned/benchmark-reward-hacking.md` | UC Berkeley 8 大基准攻破 | Reflection&Learning, Governance | P2 |

每个文件结构：

```markdown
# [案例名称]

> Evidence Status: grounded
> 来源: [URL]
> 涉及架构域: [域列表]
> 严重等级: Critical / High

## 事故场景
## 故障链
## 根因分析
## 架构缺陷（对应缺失的 Plane/Pattern）
## 教训与设计启示
## 与知识库的映射
```

### 1.2 更新评估层

| 文件 | 改动 | 语料来源 |
|---|---|---|
| `evaluation/eval-framework.md` | 新增"基准信任危机"章节：Reward Hacking 攻击面、Agent-Eval 安全清单、私有测试集要求 | UC Berkeley 研究 |
| `evaluation/eval-framework.md` | 新增 pass^k 指标说明（75% 单次成功率 = 42% pass^3 可靠性） | 评估语料 |
| `evaluation/coding-agent-evals.md` | 更新 SWE-bench 最新数据（Opus 4.7 = 87.6%）、SWE-PolyBench 多语言 | 评估语料 |
| `evaluation/eval-meta/README.md` | 新增"评估自身可信度"章节：对抗测试、环境隔离验证、验证器独立性 | UC Berkeley 安全清单 |
| `evaluation/subjective-eval.md` | 补充 Agent-as-a-Judge 论文数据（0.3% 与人类不一致率）、三层 Rubric 结构、多角色评估 | 主观评估语料 |
| `evaluation/cost-evals.md` | 补充全载成本模型（仅报告 token 成本低估真实费用 40-70%）、六大成本优化策略 | 成本语料 |

### 1.3 新增失败案例 anti-pattern 联动

更新 `design-space/anti-patterns/top-10.md`，每个 anti-pattern 添加"真实案例"列：

| Anti-pattern | 关联案例 |
|---|---|
| tool-success-as-completion | PocketOS（Railway API 返回成功但数据已删）|
| prompt-as-safety-boundary | Copilot RCE、Cursor 大小写绕过 |
| unbounded-agent-loop | $47K 循环失控 |
| over-privileged-credential | Step Finance、PocketOS |
| memory-without-provenance | 记忆投毒 84.3% |

---

## 五、Phase 2：范式层更新

### 2.1 新增：Reasoning Models 专题

**新文件**: `paradigms/reasoning-model-integration.md`

内容大纲（基于语料）：

```markdown
# Reasoning Models 与 Agent 范式集成

> Evidence Status: grounded

## 核心范式转变
- Inference-Time Compute Scaling：7B+100x推理 ≈ 70B+标准推理
- 推理需求将超过训练需求 118 倍（2026 预测）

## 对 ORDA-VU 闭环的影响
- Decide 阶段：Extended Thinking 增强单步推理深度
- Observe→Decide：Interleaved Thinking 在工具返回后"停下来思考"
- 整体闭环：未替代 ORDA-VU，而是增强每阶段内部的推理质量

## 对五大范式族的影响
### 推理范式
- ReAct：未被替代，推理模型增强每步 Thought 深度
- Plan-and-Execute：Planner 用推理模型，Executor 用轻量模型，成本降 45%
- ReWOO：一次性规划整个工具链，减少 token 消耗
- Reflective Agents：Process Reward Models 反馈每步推理

### 记忆范式
- Context Engineering 取代 Prompt Engineering 成为架构级关注点
- Anthropic 三策略：Compaction API + Just-In-Time 检索 + Sub-Agent 架构

### 工具范式
- 动态工具发现：推理模型更智能地决定"何时需要什么工具"
- MCP Sampling：server 请求 LLM 在任务中途推理

### 协作范式
- Planner-Executor 分离：推理模型做规划，轻量模型做执行
- 三种通信拓扑：Chain/Star/Mesh

### 控制范式
- Budget-Aware Agent Scaling：显式 budget 信号实现 40% 成本降低

## 多模型 Agent 中推理模型的角色
| 角色 | 推荐模型层级 | 原因 |
|------|------------|------|
| Planner | Opus/o3-pro | 复杂任务分解需要深度推理 |
| Executor | Haiku/Flash/o4-mini | 工具调用执行不需要深度思考 |
| Critic/Verifier | Sonnet/GPT-4o | 平衡质量和成本 |
| Router | 轻量模型+规则 | 延迟敏感 |

## 成本/质量/延迟权衡
- TALE 方法：67% token 减少
- Budget-Aware Scaling：40% 成本降低 + 2x 性能
- Adaptive Thinking（Claude Opus 4.7）：模型自主调节思考深度

## 设计决策树
- 单步推理足够 → 标准模型
- 需要多步推理但步骤可预测 → Plan-and-Execute + 推理 Planner
- 需要动态调整 → ReAct + Interleaved Thinking
- 需要自我修正 → Reflective Agent + Process Reward Model

## 与知识库的映射
| 主题 | 相关文件 |
|------|---------|
| 推理范式更新 | paradigms/reasoning-paradigms.md |
| 成本影响 | architecture/planes/cost/overview.md |
| 多模型架构 | architecture/multi-model/ |
| Context Engineering | architecture/planes/context/overview.md |
```

### 2.2 更新：协议栈（从三协议升级到六层栈）

**更新文件**: `architecture/evolution/ecosystem-protocols.md`

新增内容：

```markdown
## 协议栈分层模型（2026 更新）

| 层级 | 职责 | 主力协议 | 状态 |
|------|------|---------|------|
| L0 工具/上下文 | Agent 访问外部工具和数据 | MCP (Anthropic→AAIF) | 生产就绪（9700 万月下载） |
| L1 Agent 间消息 | 异步多模态消息传递 | ACP (IBM BeeAI) | 早期采纳 |
| L2 Agent 间协调 | 发现、委托、任务管理 | A2A v1.2 (Google→AAIF) | 稳定版（150+组织） |
| L3 开放网络协作 | 跨组织去中心化发现 | ANP (W3C 社区) | 标准化中 |
| L4 Agent-用户交互 | 前端状态同步、人机协作 | AG-UI (CopilotKit) | 快速采纳（120K 周安装） |
| L5 Agent 支付 | 自主交易授权与验证 | AP2 v0.2 (Google→FIDO) | 实验阶段 |

## 治理统一体
- AAIF（Linux Foundation）：150+ 组织，MCP + A2A 已捐献
- W3C AI Agent Protocol CG：ANP 标准化
- FIDO Alliance：AP2 + Verifiable Intent

## MCP 2026 路线图
- 无状态操作：session 创建/恢复/迁移标准化
- 从"证明标准必要性"到"支持生产级系统"的转型
```

### 2.3 更新：paradigm-routing.md 证据补强

当前 Evidence Status: mixed → 目标: grounded

补充内容（基于语料）：

```markdown
## 生产级范式切换数据

### 推理范式的动态路由
- 简单查询 → Reactive（无推理模型）：<100ms
- 中等任务 → ReAct + 标准模型：2-5s/步
- 复杂任务 → Plan-Execute + 推理模型：10-30s 规划，2-5s/步执行
- 路由准确率：RouteLLM (ICLR 2025) 在 MMLU 上降低成本 85% 同时保持质量

### 来自生产的关键阈值
- ReAct 步数上限：30 步（超过后连贯性崩塌）
- re-anchor checkpoint：每 ~40 步
- 多 Agent 错误放大：独立系统 17.2x，集中式 4.4x
- 层级架构 vs Swarm：层级在生产中几乎总是胜出

### 八大规范模式的适用域
| 模式 | 适用 | 不适用 |
|------|------|--------|
| ReAct | <30 步通用任务 | 需长期规划的任务 |
| Reflexion | 编码/数学中的重复失败 | 延迟敏感场景（~30% 延迟税）|
| Plan-and-Execute | 结构可预测的工作流 | 中途世界变化频繁 |
| Supervisor-Worker | 多域角色特化 | 简单任务（协调开销主导）|
| Multi-Agent Debate | 高风险决策、安全评估 | 需要快速收敛 |
| Verifier-Critic | 高精度、合规性 | 同模型时（共谋风险）|
| Graph Orchestration | 可审计的生产系统 | 边界情况多的探索性任务 |
| Swarm/Blackboard | 探索性任务 | 需要目标收敛和可审计 |
```

### 2.4 补充：成本量化表

**新文件**: `architecture/planes/cost/paradigm-cost-benchmarks.md`

```markdown
# 范式×品类 成本基准

> Evidence Status: grounded（基于 2025-2026 生产数据）

## 全载成本模型
仅报告 token 成本低估真实费用 40-70%。完整成本 = Token + 工具调用 + 基础设施 + 人工审核。

## Agent 成本结构
- Agent 调用成本 = 3-10x 单次 LLM 调用（多步推理、工具调用、重试）
- Agent 毛利 50-60% vs SaaS 80-90%

## 六大成本优化策略（组合可达 60-80% 削减）
1. Prompt/Context 压缩（Compaction API）
2. 模型路由（小模型处理简单任务）
3. 缓存（语义缓存、工具结果缓存）
4. 并行化（减少串行等待）
5. 推理 budget 显式管理
6. 批量处理

## 推理模型成本对比
| 策略 | 成本变化 | 质量变化 | 来源 |
|------|---------|---------|------|
| Planner(推理)+Executor(轻量) | -45% | +15% | Planner-Executor 分离 |
| Budget-Aware Scaling | -40% | +100% (2x) | Budget-Aware Agent |
| TALE 方法 | -67% token | 持平 | TALE paper |
| Adaptive Thinking | 自动优化 | 自适应 | Claude Opus 4.7 |
| RouteLLM 动态路由 | -85% | 持平 | ICLR 2025 |
```

### 2.5 补充：model-capability-profile.md

当前完成度: 60% → 目标: 85%

新增内容：
- 填充指南：如何评估 instruction_adherence、tool_use_accuracy 等字段
- 5 个示例 profile（Claude Opus 4.7、Claude Sonnet 4.6、GPT-4o、o4-mini、Gemini 2.5 Pro）
- 与 paradigm-routing 的集成：profile 字段如何驱动范式选择

---

## 六、Phase 3：交叉地带填补

### 3.1 新建 cross-cutting/ 目录

**位置**: `architecture/cross-cutting/`

| 新文件 | 交叉的域 | 核心问题 | 语料来源 |
|---|---|---|---|
| `memory-x-security.md` | Cognition × Trust | 记忆投毒防护、写入验证、来源追踪 | 记忆投毒 84.3%、ClawHavoc |
| `paradigm-x-cost.md` | Paradigms × Economics | 范式选择如何影响成本、成本约束如何限制范式空间 | 成本量化数据、RouteLLM |
| `category-x-multi-model.md` | Categories × Multi-Model | 不同品类的多模型配置模板 | Planner-Executor 分离数据 |
| `reasoning-model-x-tool-use.md` | Reasoning × Action | 推理模型如何改变工具调用模式 | Interleaved Thinking、MCP Sampling |
| `protocol-x-security.md` | Coordination × Trust | 协议栈中的信任边界 | A2A Agent Card、AP2 Verifiable Credentials |
| `context-engineering-x-memory.md` | Context × Memory × Prompting | Context Engineering 作为架构级关注点 | Anthropic 三策略 |

每个文件结构：

```markdown
# [域A] × [域B] 交叉设计

> Evidence Status: grounded/synthesized

## 为什么需要这篇文档
## 交叉点识别
## 设计决策矩阵
## 常见错误与案例
## 与知识库的映射
```

### 3.2 品类证据均衡化

#### Browser Agent 深度补充

| 更新文件 | 新增内容 | 语料来源 |
|---|---|---|
| `categories/browser-desktop-agent/representation.md` | 双通道感知管线收敛趋势、agent-browser 紧凑快照（减少 82.5% 上下文）| Browser 语料 |
| `categories/browser-desktop-agent/design-decisions.md` | 混合模式架构（确定性 Playwright + AI Agent）、Stagehand 三原语 | Browser 语料 |
| `categories/browser-desktop-agent/eval-cases.md` | WebVoyager 89.1%、WebArena 数据、OSWorld 72.7%、选择器维护 15-25% vs AI <5% | 评估语料 |
| `categories/browser-desktop-agent/closed-loop.md` | 自验证循环（Ralph Wiggum Loop）、HITL 检查点模式 | Browser 语料 |

#### Research Agent 深度补充

| 更新文件 | 新增内容 | 语料来源 |
|---|---|---|
| `categories/research-agent/design-decisions.md` | Egnyte 五 Agent + DAG 编排全架构、三种规划策略、引用链已知缺陷 | Research 语料 |
| `categories/research-agent/representation.md` | 多源冲突处理（Angel-Devil 对抗辩论）、Perplexity 19 模型编排 | Research 语料 |
| `categories/research-agent/eval-cases.md` | 引用验证仍是开放挑战、冲突保留 vs 压平的权衡数据 | Research 语料 |

#### Companion Agent 深度补充

| 更新文件 | 新增内容 | 语料来源 |
|---|---|---|
| `categories/companion-agent/design-decisions.md` | PACE 人格一致性验证器、人格漂移量化（高强度衰减 -3.50）| Companion 语料 |
| `categories/companion-agent/closed-loop.md` | 安全悖论（71.8% 共情回复在高风险场景有害）、三种失败模式 | Companion 语料 |
| `categories/companion-agent/eval-cases.md` | 加州/纽约/FTC 监管框架、推荐安全架构 | Companion 语料 |

### 3.3 新增项目分析

| 新目录/文件 | 分析对象 | 深度目标 |
|---|---|---|
| `projects/browser-agents/browser-use/` | Browser Use (81K stars) | 与 Claude Code 同等深度（4-6 文件）|
| `projects/browser-agents/stagehand/` | Stagehand (Vercel) | DOM-first 策略、三原语 |
| `projects/research-agents/perplexity-analysis.md` | Perplexity 架构 | 19 模型编排、引用链 |
| `projects/general-agents/openai-agents-sdk/` | OpenAI Agents SDK | 四原语、沙箱模型、Tracing |
| `projects/general-agents/google-adk/` | Google ADK | A2A 集成、多 Agent 部署 |

---

## 七、Phase 4：实践桥梁建设

### 4.1 完成端到端 Guide

| Guide | 当前状态 | 语料支撑 | 内容大纲 |
|---|---|---|---|
| `guides/build-research-agent.md` | 存在但不完整 | Egnyte 架构、Perplexity 19 模型、引用链挑战 | 产品画布→JTBD→五 Agent 架构→引用链设计→冲突处理→评估→审查 |
| `guides/build-browser-agent.md` | 存在但不完整 | Browser Use 架构、双通道验证、Stagehand 三原语 | 产品画布→感知管线→动作模型→自验证循环→安全边界→评估 |
| `guides/build-companion-agent.md` | 不存在 | PACE 验证器、安全悖论、人格漂移量化 | 产品画布→人格模型→三层记忆→安全护栏→情绪意识→评估 |
| `guides/build-memory-agent.md` | 不存在 | 记忆投毒防护、三层存储 | 产品画布→存储架构→写入策略→检索策略→安全→评估 |

### 4.2 更新 starter-kit

当前 starter-kit 只有概念骨架。增加与真实 SDK 的对齐：

| 更新 | 内容 |
|---|---|
| `starter-kit/README.md` | 增加"与主流 SDK 的映射"表：概念→OpenAI SDK 原语→Anthropic SDK 模式→Google ADK 组件 |
| `starter-kit/verified-tool-agent/` | 增加 EffectRecord 的完整 mock 验证流程 |
| `starter-kit/multi-model-agent/` | 新增：Planner-Executor 分离骨架，Router 模式 |

### 4.3 更新 toolkit

| 文件 | 改动 |
|---|---|
| `toolkit/choose-agent-type.md` | 增加"推理模型是否改变了品类选择"的判断步骤 |
| `toolkit/module-picker.md` | 增加 Reasoning Model Integration 作为可选模块 |
| `toolkit/mva-planner.md` | 纳入成本维度：复杂度级别 × 推理模型选择 → 预估成本范围（原 risk-depth-calculator 已并入） |
| `toolkit/failure-router.md` | 扩展症状覆盖到 15-20 种（基于 14 个新案例） |

---

## 八、Phase 5：前瞻性扩展

### 8.1 治理框架专题

**新文件**: `architecture/planes/governance-framework.md`

内容（基于语料）：
- Microsoft Agent Governance Toolkit：DID+Ed25519 身份、0-1000 动态信任评分、<0.1ms 策略引擎
- CSA Agentic Trust Framework：四级自主权模型、五扇门晋升机制
- OWASP Agent Top 10
- 仅 11% 组织已实施治理 → 这是紧迫的设计需求

### 8.2 Agent 经济学更新

**更新文件**: `design-space/methodology/agent-economics.md`

新增内容：
- Agent 市场规模 $10.9B+ (2026)
- 混合定价模型（基础费 + 结果激励）
- Agent 毛利 50-60% vs SaaS 80-90%
- 八大市场各有不同经济模型

### 8.3 AHE（Automated Harness Evolution）

**新文件**: `design-space/frontier/automated-harness-evolution.md`

内容：
- arXiv 2604.25850 的可观测性驱动自动 Harness 演进
- Terminal-Bench 2 上 69.7%→77.0% 的提升
- 对 Learning Plane 的影响：从人工固化到自动演进

### 8.4 基准信任危机与评估革新

**新文件**: `evaluation/benchmark-trust-crisis.md`

内容：
- UC Berkeley 8 大基准全部被 Reward Hacking 攻破
- Agent-Eval 安全清单（6 条）
- 从基准分数到生产可靠性的差距（pass@k vs pass^k）
- 新的评估范式：私有测试集 + 对抗测试 + 环境隔离

### 8.5 Context Engineering 专题

**新文件**: `concepts/context-engineering.md`

内容：
- Context Engineering 取代 Prompt Engineering 的定义
- Anthropic 三策略：Compaction API、结构化笔记（Scratchpad）、Sub-Agent 架构
- 与 Context Plane、Memory Plane、Prompting Plane 的关系重定义
- 对 ORDA-VU 闭环的影响：Represent 和 Decide 之间需要显式的 Context Assembly 步骤

---

## 九、文件变更汇总

### 新增文件（~30 个）

| 类别 | 数量 | 文件 |
|---|---|---|
| lessons-learned | 12 | pocketos、replit、47k-loop、step-finance、copilot-rce、echoleak、alibaba-rome、legal-hallucination、clawhavoc、memory-poisoning、cursor-bypass、benchmark-hacking |
| cross-cutting | 6 | memory-x-security、paradigm-x-cost、category-x-multi-model、reasoning-x-tool、protocol-x-security、context-x-memory |
| 范式/概念 | 3 | reasoning-model-integration、context-engineering、paradigm-cost-benchmarks |
| 前沿/治理 | 3 | automated-harness-evolution、governance-framework、benchmark-trust-crisis |
| 项目分析 | ~6 | browser-use/、stagehand/、perplexity、openai-sdk/、google-adk/ |
| guides | 2 | build-companion-agent、build-memory-agent |

### 更新文件（~25 个）

| 类别 | 文件 | 改动类型 |
|---|---|---|
| 评估层 | eval-framework、coding-agent-evals、subjective-eval、cost-evals、eval-meta/README | 内容补充 |
| 范式层 | paradigm-routing、model-capability-profile、reasoning-paradigms | 证据补强 + 内容扩展 |
| 协议层 | ecosystem-protocols | 六层协议栈更新 |
| 经济学 | agent-economics | 市场数据更新 |
| 品类层 | browser(4)、research(3)、companion(3) | 深度补充 |
| 反模式 | top-10、README | 案例联动 |
| 工具包 | choose-agent-type、module-picker、risk-depth、failure-router | 功能扩展 |
| starter-kit | README、multi-model-agent(新) | 新增骨架 |
| guides | build-research-agent、build-browser-agent | 内容完善 |

---

## 十、Evidence Status 升级目标

| 层级 | 当前分布 | 目标分布 |
|---|---|---|
| production-validated | ~5% | ~10% |
| prototype-validated | ~25% | ~30% |
| grounded | ~35% | ~35% |
| synthesized | ~25% | ~20% |
| mixed/theoretical | ~10% | ~5% |

关键升级路径：
- paradigm-routing: mixed → grounded（补充生产数据）
- multi-model/: theoretical → synthesized（补充 Planner-Executor 分离证据）
- lessons-learned 新增: 全部 grounded（直接来自事故报告）
- 评估层: 补充基准数据后多个文件 synthesized → grounded

---

## 十一、执行优先级排序

```
Week 1-2:  [Phase 1] 12 个 lessons-learned + anti-pattern 联动
Week 2-3:  [Phase 1] 评估层更新 + [Phase 2] reasoning-model-integration.md
Week 3-4:  [Phase 2] 协议栈更新 + paradigm-routing 补强 + 成本量化表
Week 4-5:  [Phase 3] 6 个 cross-cutting 文档 + 品类补充（Browser）
Week 5-6:  [Phase 3] 品类补充（Research + Companion）+ 项目分析
Week 6-8:  [Phase 4] 4 个 Guide 完善 + starter-kit 更新
Week 8-10: [Phase 5] 治理框架 + AHE + 基准信任危机 + Context Engineering
Week 10+:  持续更新 frontier、项目分析、Evidence Status 升级
```

---

## 十二、语料文件索引

采集的原始语料文件，可作为写作时的直接参考：

| 文件路径 | 内容 | 素材量 |
|---|---|---|
| `corpus/2025-2026-agent-architecture-corpus.md` | Agent 框架、SDK、标准 | ~30 条 |
| `/Users/jin/Desktop/knode/ai-agent-failure-casebook-2024-2026.md` | 14 个生产事故案例 | 14 案例 |
| `/Users/jin/Desktop/knode/reasoning-models-agent-architecture-corpus-2025-2026.md` | Reasoning Models 影响 | ~25 条 |
| `/Users/jin/Desktop/knode/multi-agent-coordination-governance-corpus-2025-2026.md` | 协议栈、治理、经济学 | ~25 条 |
| `/Users/jin/Desktop/knode/agent-evaluation-cost-corpus-2025-2026.md` | 评估基准、成本优化 | ~25 条 |
| `/Users/jin/Desktop/knode/agent-category-corpus-2025-2026.md` | Browser/Research/Companion | ~30 条 |

> 建议：执行改进时，先读取对应语料文件，提取具体数据和引用，再写入目标文件。
