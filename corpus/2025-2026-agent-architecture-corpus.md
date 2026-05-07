# AI Agent 架构语料汇总 (2025-2026)

> 采集时间：2026-05-07
> 覆盖范围：生产级 Agent 架构模式、主流框架、Harness 工程、开放标准

---

## 一、生产级 Agent 架构模式

### 1.1 八大规范模式（2026 分类学）

2024-2026 年间，Agent 架构词汇围绕 **4 象限 × 8 模式** 稳定下来：

| 象限 | 模式 | 核心特征 | 适用场景 | 关键限制 |
|------|------|---------|---------|---------|
| 单 Agent | **ReAct** | thought-action-observation 交替循环 | 30 步以内的通用任务 | 超 50 步后连贯性崩塌，无自我纠错 |
| 单 Agent | **Reflexion** | ReAct + 显式自我批评，追加到上下文 | 编码/数学推理中的重复失败 | ~30% 延迟税；过度纠正导致振荡 |
| 协作多 Agent | **Plan-and-Execute** | 规划器生成有序计划，执行器逐步执行 | 结构可预测的工作流 | 执行中途世界变化时脆弱 |
| 协作多 Agent | **Supervisor-Worker** | 监督者分解任务路由给专业 Worker | 需要角色特化的多域任务 | 协调开销在简单任务上主导成本 |
| 对抗多 Agent | **Multi-Agent Debate** | 多 Agent 辩论不同立场，独立裁判综合结论 | 高风险决策、安全关键评估 | 过早收敛；裁判偏好冗长论证 |
| 对抗多 Agent | **Verifier-Critic** | 生成器产出 → 批评者按评分标准打分 → 修订 | 高精度输出、合规性检查 | 同模型时生成-批评共谋 |
| 编排拓扑 | **Graph Orchestration** | Agent 作为有向图节点，显式边定义控制流 | 需要可调试/可审计的生产系统 | 图复杂度增长快，边界情况激增 |
| 编排拓扑 | **Swarm/Blackboard** | 对等拓扑，无监督者，共享消息总线 | 探索性任务，正确分解未知 | 目标漂移、协调死锁、调试困难 |

**生产建议**：从单 Agent 开始，仅当单 Agent 在可测量质量维度触顶时才升级到多 Agent。ReAct + Reflexion + 每 ~40 步 re-anchor checkpoint 是升级前的基线栈。

**关键研究发现**：独立多 Agent 系统相比单 Agent 基线放大错误 17.2 倍，而集中式架构通过编排器验证将放大比降至 4.4 倍。

> 来源：[Agent Architecture Patterns: 2026 Taxonomy Guide](https://www.digitalapplied.com/blog/agent-architecture-patterns-taxonomy-2026)

### 1.2 五大架构家族

| 架构 | 定义 | 生产级关键点 |
|------|------|------------|
| **Reactive** | 当前条件 → 预定义动作，简单规则映射 | 成本最优、确定性强、合规友好 |
| **Deliberative** | 维护显式世界模型，生成替代方案后选择最优序列 | 2-5 秒延迟/决策，仅用于高价值决策 |
| **Hybrid/Layered** | 快速反应回路 + 慢速审议层并行运行 | 当前工业标准，各层可独立更新 |
| **Neural-Symbolic** | 深度学习感知 + 符号 AI 可追溯决策路径 | EU AI Act 合规刚需，提供审计轨迹 |
| **Multi-Agent** | 跨专业化自治组件分配工作负载 | 必须集中式编排器，否则错误放大 |

**治理三平面模型**：Build Plane（开发部署）→ Orchestration Plane（运行时协调）→ Governance Plane（策略执行，独立于执行逻辑）。

> 来源：[AI Agent Architecture From Patterns to Governance | Galileo](https://galileo.ai/blog/ai-agent-architecture)

---

## 二、OpenAI Agents SDK

### 2.1 核心原语

OpenAI 于 2025 年 3 月发布 Agents SDK，作为实验性 Swarm 框架的生产继任者。设计哲学为 **最小抽象 + Python-first**：

- **Agent**：配备指令和工具的 LLM 单元
- **Handoff**：Agent 间任务委托，实现 agents-as-tools 模式
- **Guardrail**：输入/输出验证，支持并行执行
- **Tool**：Python 函数自动转换为工具 schema，Pydantic 验证

### 2.2 关键架构特性

| 特性 | 描述 |
|------|------|
| **Agent Loop** | 内置工具调用、结果处理、续行逻辑管理 |
| **Sandbox Agents** | 隔离工作空间，manifest 定义文件，可恢复会话 |
| **Sessions** | 跨 Agent 运行的持久记忆层 |
| **MCP 集成** | 内置 Model Context Protocol 服务器工具调用 |
| **Human-in-the-Loop** | 跨 Agent 运行的人工介入机制 |
| **Realtime Agents** | 基于 `gpt-realtime-1.5` 的语音 Agent，支持中断检测 |
| **Tracing** | 内置可视化、调试和监控，兼容 OpenAI 评估/微调/蒸馏 |
| **Provider-Agnostic** | 默认 Responses API，可配置非 OpenAI 模型提供商 |

### 2.3 沙箱执行模型

Agents SDK 原生支持沙箱执行，Agent 可在受控计算环境中运行，具备所需文件、工具和依赖。支持自带沙箱或使用内置集成：Blaxel, Cloudflare, Daytona, E2B, Modal, Runloop, Vercel。

**安全设计**：假设 prompt-injection 和数据窃取攻击存在，通过分离 harness 和 compute 将凭证隔离在模型生成代码的执行环境之外。

> 来源：[The next evolution of the Agents SDK | OpenAI](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)、[OpenAI Agents SDK 文档](https://openai.github.io/openai-agents-python/)

---

## 三、Anthropic Claude Agent SDK & Context Engineering

### 3.1 Claude Agent SDK 架构

Claude Code SDK 已更名为 **Claude Agent SDK**，反映其超越编码任务的通用性。核心架构为 **反馈循环**：

```
gather context → take action → verify work → repeat
```

**上下文收集**：
- 文件系统导航 + bash 工具（grep, tail）的 agentic search
- 语义搜索作为辅助
- 子 Agent 实现并行化和上下文隔离
- 接近 token 限制时自动 context compaction

**动作执行**：
- 自定义工具作为主要决策驱动
- Bash 命令提供灵活计算机访问
- MCP 服务器提供标准化第三方集成（Slack, GitHub, Google Drive, Asana），无需自行管理 OAuth

**验证**：
- 规则式反馈（linting）
- 视觉反馈（UI 任务）
- LLM-as-judge（模糊标准评估）

### 3.2 Context Engineering 框架

Anthropic 提出 context engineering 取代 prompt engineering 的范式转移：

**核心原则**：
- **上下文是有限资源**：模型存在 "context rot"，性能随 token 数增加而退化；transformer 的 n² 成对 token 关系在长序列下承压
- **高信号 token 优化**："找到最小的高信号 token 集合，最大化期望结果的似然"

**长程上下文管理三策略**：

| 策略 | 机制 | 适用场景 |
|------|------|---------|
| **Compaction** | 接近窗口限制时摘要对话内容，用摘要初始化新窗口 | 单 Agent 长任务 |
| **结构化笔记** | Agent 写入外部持久化笔记（如 NOTES.md），后续检索 | 跨多步复杂任务 |
| **子 Agent 架构** | 专门 Agent 在干净窗口中深度探索（10,000+ tokens），返回浓缩摘要（1,000-2,000 tokens） | 多域信息综合 |

**工具设计原则**：自包含、容错、用途明确；最小化功能重叠；避免膨胀工具集带来的歧义决策点。

**Just-In-Time 上下文检索**：维护轻量标识符（文件路径、存储查询、链接），通过工具调用动态加载，实现"渐进式披露"。

> 来源：[Effective context engineering for AI agents | Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

### 3.3 三 Agent Harness 架构（长时运行应用）

Anthropic 为前端/全栈开发引入 **Planner-Generator-Evaluator** 三 Agent 架构：

| Agent | 职责 | 关键设计 |
|-------|------|---------|
| **Planner** | 将 1-4 句需求扩展为完整产品规格 | 强调功能范围而非实现细节，避免级联错误 |
| **Generator** | 按 sprint 增量构建应用 | 每 sprint 实现一项功能后自评并交接 QA |
| **Evaluator** | 通过 Playwright MCP 实际操作应用 | 按功能/设计/代码质量评分，识别真实 bug |

**核心洞察**：
- "分离做事的 Agent 和评判的 Agent 是解决输出过度乐观问题的强力杠杆"
- 评估器通过 few-shot 学习校准评分标准（设计质量、原创性、工艺、功能性）
- 契约机制：sprint 前生成器与评估器约定可验证交付物和测试标准

**成本对比**：单 Agent（20 分钟，$9）vs 完整 harness（6 小时，$200）——后者成本高 20 倍但核心功能实际可用。

**演进洞察**：随着模型能力提升，harness 需定期"去肥"（remove unnecessary components），避免过度工程化。升级到 Opus 4.6 后，单连续会话 + 自动 compaction 即可处理之前需要跨 session 上下文重置的长任务。

> 来源：[Effective harnesses for long-running agents | Anthropic](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)、[Harness design for long-running apps | Anthropic](https://www.anthropic.com/engineering/harness-design-long-running-apps)、[InfoQ 报道](https://www.infoq.com/news/2026/04/anthropic-three-agent-harness-ai/)

---

## 四、主流框架对比（LangGraph / CrewAI / AutoGen）

### 4.1 架构范式对比

| 维度 | LangGraph | CrewAI | AutoGen (AG2) |
|------|-----------|--------|---------------|
| **架构模型** | 有向图：节点=函数/LLM调用，边=控制流 | 角色式团队：Agent 有 role/backstory/goal | 对话式协作：共享对话中选择发言者 |
| **状态管理** | typed dict 显式传递 | 隐式，2025 新增 Flows 事件驱动管道 | AG2 v0.4 重写：事件驱动核心 + async-first |
| **协调模式** | 图遍历 + 条件分支 | 线性工作流最佳，循环调试体验差 | GroupChat 选择器决定发言顺序 |
| **可观测性** | LangSmith 集成：逐步 trace + token 计数 + 任意断点回放 | 日志"仍然平庸" | 有限 |
| **生产就绪度** | 2026 初 GitHub stars 超过 CrewAI，企业采用驱动 | 快速原型优势 | "实质上处于维护模式"，Microsoft 转向更广泛 Agent Framework |

### 4.2 性能基准

| 任务复杂度 | LangGraph | CrewAI | AutoGen | Smolagents |
|-----------|-----------|--------|---------|-----------|
| 复杂任务（5+ 工具调用） | **62%** | 54% | — | — |
| 中等任务（3-5 工具调用） | **76%** | 71% | 68% | 73% |

在生产规模下 8 个百分点的差距是显著的。

### 4.3 选型建议

- **需要检查点、人机协作、审计轨迹的生产系统** → LangGraph
- **快速原型多 Agent 团队，开发速度优先于精细控制** → CrewAI
- **对话式推理的特定模式** → AutoGen（但需考虑维护风险）
- **留在 OpenAI 生态** → OpenAI Agents SDK
- **Google 生态 + 多模态** → Google ADK

**成本控制**：所有框架都需要"每个循环显式设置最大迭代次数"和"每次运行的 token 消耗监控"。

> 来源：[CrewAI vs LangGraph vs AutoGen 2026 | DEV Community](https://dev.to/emperorakashi20/crewai-vs-langgraph-vs-autogen-which-multi-agent-framework-should-you-use-in-2026-5h2f)、[Best Multi-Agent Frameworks 2026](https://gurusup.com/blog/best-multi-agent-frameworks-2026)

---

## 五、Harness Engineering（Agent = Model + Harness）

### 5.1 定义与起源

**Harness Engineering** 由 Mitchell Hashimoto（HashiCorp/Terraform 创始人）于 2026 年 2 月首次提出，OpenAI Ryan Lopopolo 同月正式定义：

> **Agent = Model + Harness**
>
> AI 的定义性瓶颈不再是模型原始能力，而是 **Agent Harness**——围绕模型的运行时基础设施，将概率性推理转化为可靠、确定性行动，管理上下文、工具执行、安全控制和会话记忆。

### 5.2 三层架构

| 层级 | 名称 | 功能 | 示例 |
|------|------|------|------|
| L1 | **约束 Harness（前馈）** | 生成前缩小解空间 | AGENTS.md/CLAUDE.md 规则文件、lint 配置、类型系统、"taste invariants" |
| L2 | **反馈回路（纠正）** | 结构化错误信号实现自主纠错 | lint 消息须指定修复方案；禁用 `// eslint-disable-next-line` 防止 Agent 压制而非修复 |
| L3 | **质量门（执行）** | CI 强制阻止不合规合并 | 依赖新鲜度检查、SAST 安全扫描、域特定失败检测 |

### 5.3 与 Prompt/Context Engineering 的区分

| 维度 | Prompt Engineering | Context Engineering | Harness Engineering |
|------|-------------------|-------------------|-------------------|
| **作用域** | 单次交互 | 单个上下文窗口 | 完整 Agent 系统/生命周期 |
| **控制** | 指令措辞 | Token 选择/排序 | 工具编排、状态持久化、验证循环 |
| **时间边界** | 一轮对话 | 窗口内多轮 | 跨多个上下文窗口 |

### 5.4 Plan-Execute-Verify (PEV) 模式

PEV 在每个转换处设置门控，解决多步 Agent 推理的非确定性：
- **Plan**：显式分解 + 验收标准
- **Execute**：工具调用受 harness 门控约束（参数验证、路径限制、权限检查）
- **Verify**：执行前 + 运行时 + 执行后 + 计划对齐检查

**核心差异**：与 generate-and-check 不同，PEV 能捕获测试套件不可见的架构违规。

### 5.5 生产度量

| 指标 | 描述 |
|------|------|
| **任务解决率** | 每次提交的自动化测试通过率 |
| **代码流失率** | 每周被丢弃/重写的代码百分比 |
| **验证税** | 审查时间开销抵消生成速度的比例 |
| **Harness 约束效果** | 环境变化带来的成功率提升 |
| **缺陷逃逸率** | AI 生成的缺陷到达生产的比例 |
| **Pass@1 率** | 无重试首次正确率 |

**基线参考**：顶级 Agent 在 SWE-bench-verified Python 任务上达 65-76.8%，但 METR 发现许多基准通过的 PR 在真实代码库中不会被合并。

### 5.6 OpenAI Codex 实证

OpenAI 内部团队从 2025 年 8 月起仅用 Codex Agent 构建生产软件，合并约 1,500 个 PR，生成约 100 万行代码，报告开发速度提升约 10 倍。

> 来源：[Augment Code Harness Engineering Guide](https://www.augmentcode.com/guides/harness-engineering-ai-coding-agents)、[Medium: Agent Harness Engineering](https://medium.com/@adnanmasood/agent-harness-engineering-the-rise-of-the-ai-control-plane-938ead884b1d)

### 5.7 Agentic Harness Engineering (AHE) — 学术突破

arXiv 2604.25850 提出 **可观测性驱动的自动 Harness 演进**：

**三大可观测性支柱**：

| 支柱 | 机制 |
|------|------|
| **组件可观测性** | 7 类可编辑组件（system prompt, tool descriptions, implementations, middleware, skills, sub-agent configs, long-term memory）；"每种故障模式映射到单一组件类" |
| **经验可观测性** | 将原始轨迹 token 蒸馏为分层、可钻取的证据语料 |
| **决策可观测性** | 每次编辑配对自声明预测（预期修复和回归），下一轮验证预测 vs 观察结果，创建可证伪契约 |

**实证结果（Terminal-Bench 2）**：
- 基线：69.7% pass@1
- 10 轮 AHE 迭代后：**77.0% pass@1**
- 超越人工设计的 Codex-CLI（71.9%）和自演进基线

**组件消融**：
- Long-term memory: +5.6 pp
- Tools: +3.3 pp
- Middleware: +2.2 pp
- System prompt alone: -2.3 pp
- 组件交互非加性，堆叠产生冗余验证开销

**跨模型迁移（无需重新演进）**：DeepSeek-v4-flash +10.1 pp, Qwen-3.6-plus +6.3 pp, Gemini-3.1-flash-lite +5.1 pp

> 来源：[arXiv 2604.25850 — Agentic Harness Engineering](https://arxiv.org/abs/2604.25850)

---

## 六、Google Agent Development Kit (ADK)

### 6.1 概述

Google 于 Cloud NEXT 2025 发布 ADK，开源的 code-first 框架，覆盖 Agent 构建/交互/评估/部署全生命周期。

### 6.2 核心架构

| 组件 | 描述 |
|------|------|
| **LlmAgent** | 主要 Agent 类型，使用语言模型决策 |
| **Workflow Agents** | Sequential / Parallel / Loop 三种确定性管道模式 |
| **Hierarchical Agents** | 子 Agent 通过 description-driven routing 实现委托 |
| **Tool System** | Python 函数 + docstring 通信；支持预置工具（Search, Code Exec）、MCP 工具、第三方库（LangChain, LlamaIndex）、Agent-as-tool |
| **状态管理** | 维护 Agent 状态并协调工具调用 |
| **评估框架** | 内置系统性评估，支持最终响应和执行轨迹双维度 |
| **流式能力** | 双向音视频流，支持丰富多模态对话 |

### 6.3 差异化特性

- **模型灵活性**：针对 Gemini 优化，但 model-agnostic（通过 LiteLLM 支持 Anthropic, Meta, Mistral 等）
- **多语言支持**：Python, TypeScript, Go, Java
- **部署选项**：本地 / Cloud Run / GKE / Vertex AI Agent Engine
- **开发者体验**：CLI 工具 + 可视化 Web UI，支持逐步执行检查

> 来源：[Google Developers Blog](https://developers.googleblog.com/en/agent-development-kit-easy-to-build-multi-agent-applications/)、[ADK 官网](https://adk.dev/)

---

## 七、开放标准与生态整合

### 7.1 AGENTS.md

OpenAI 于 2025 年 8 月发布，为 AI 编码 Agent 提供项目级指导的通用标准：
- 设计哲学：**极致简单**——单文件、纯 Markdown、可选元数据、人类优先、工具无关
- 已被 **60,000+ 开源项目**和主流 Agent 框架采用（Amp, Codex, Cursor, Devin, Factory, Gemini CLI, GitHub Copilot, Jules, VS Code）
- 三种加载模式：`always_apply`（自动加载）、`agent_requested`（Agent 按需）、`manual`（显式调用）

### 7.2 Model Context Protocol (MCP)

Anthropic 提出的连接 AI 工具与外部数据源的开放标准：
- 标准化第三方集成，自动处理认证和 API 调用
- 消除自定义集成代码和 OAuth 管理
- 已被 OpenAI Agents SDK、Google ADK、LangGraph 等主流框架集成

### 7.3 Agentic AI Foundation (AAIF)

2025 年 12 月由 Anthropic、OpenAI、Block 在 Linux Foundation 下联合创立：
- 整合 **MCP**（Anthropic）、**AGENTS.md**（OpenAI）、**Goose**（Block）
- 推动供应商中立、可互操作的 Agent 基础设施
- 标志着 AI Agent 从实验原型向生产系统的转型

> 来源：[Linux Foundation AAIF 公告](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation)、[OpenAI AAIF 公告](https://openai.com/index/agentic-ai-foundation/)

---

## 八、合规与安全

### 8.1 EU AI Act 时间线

| 时间 | 事件 |
|------|------|
| 2025 年 8 月 | GPAI 规则生效 |
| 2026 年 8 月 | 高风险系统要求生效：人工监督、准确性指标、稳健性标准、网络安全保护 |

违规罚款：最高 3,500 万欧元或全球营收 7%。

### 8.2 零信任 Agent 安全要求

- 工具访问验证
- 记忆系统保护
- 外部数据验证
- 动作执行前运行时安全卫士
- Prompt injection 仍是 OWASP 首要漏洞

### 8.3 88% 失败率

高达 88% 的企业 AI Agent 项目未能到达生产。原因：行业多年来发展了强大的"大脑"（模型），但忽视了大脑与真实世界交互所需的"神经系统"和"外骨骼"。

---

## 九、关键趋势总结

1. **2025 = Agents, 2026 = Agent Harnesses**：焦点从模型能力转向运行时基础设施
2. **三层工程学**：Prompt Engineering → Context Engineering → Harness Engineering，作用域逐层扩大
3. **图 + 层级 = 生产默认**：Swarm/黑板模式几乎不在生产中使用
4. **治理前置**：治理必须从设计阶段内置，而非后期改造
5. **可观测性为第一原则**：AHE 论文证明可观测性（而非 Agent 能力）是限制性瓶颈
6. **标准融合**：MCP + AGENTS.md + AAIF 推动跨框架互操作
7. **模型升级反推 harness 简化**：随着模型能力提升（如 Opus 4.6），harness 需定期"去肥"
8. **成本意识**：单 Agent $9 vs 三 Agent harness $200，生产中需要明确的成本-质量权衡
