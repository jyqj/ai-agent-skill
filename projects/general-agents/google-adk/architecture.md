# Google ADK 架构分析

> **Evidence Status**: synthesized
> **来源**: [Google Developers Blog](https://developers.googleblog.com/en/agent-development-kit-easy-to-build-multi-agent-applications/) | [ADK 官网](https://adk.dev/) | [A2A Protocol](https://a2a-protocol.org/latest/) | [Developers Guide to AI Agent Protocols](https://developers.googleblog.com/developers-guide-to-ai-agent-protocols/)

## 项目概述

Google Agent Development Kit (ADK) 于 Cloud NEXT 2025 发布，是 Google 推出的开源 code-first Agent 构建框架。定位为覆盖 Agent 构建、交互、评估、部署全生命周期的一站式解决方案。

ADK 的核心差异化：原生集成 A2A（Agent-to-Agent）协议、MCP 工具接入、多语言支持（Python / TypeScript / Go / Java），以及从本地开发到 Vertex AI 的无缝部署路径。

## 核心架构

### Agent 类型体系

```text
Agent
  ├─ LlmAgent（主力类型）
  │    └─ 使用语言模型进行决策
  │    └─ 通过 description-driven routing 委托子 Agent
  │
  ├─ Workflow Agents（确定性管道）
  │    ├─ SequentialAgent（串行执行）
  │    ├─ ParallelAgent（并行执行）
  │    └─ LoopAgent（循环执行直到条件满足）
  │
  └─ Custom Agents（自定义逻辑）
```

| Agent 类型 | 决策方式 | 适用场景 |
|-----------|---------|---------|
| **LlmAgent** | LLM 推理 | 需要自然语言理解和动态决策 |
| **SequentialAgent** | 确定性串行 | 步骤顺序固定的工作流 |
| **ParallelAgent** | 确定性并行 | 独立子任务可同时执行 |
| **LoopAgent** | 确定性循环 | 迭代精炼直到质量达标 |
| **Custom Agent** | 开发者自定义 | 特殊控制流需求 |

### 工具系统

ADK 的工具系统是四层开放设计：

| 层级 | 工具来源 | 示例 |
|------|---------|------|
| **原生工具** | ADK 预置 | Google Search, Code Execution |
| **Python 函数** | 开发者定义 + docstring 通信 | 任意 Python 函数 → 自动 schema |
| **MCP 工具** | Model Context Protocol 服务器 | 任何 MCP 兼容工具 |
| **第三方库** | LangChain, LlamaIndex 工具 | 复用已有生态 |
| **Agent-as-Tool** | 其他 Agent 作为工具调用 | 子 Agent 封装为可调用工具 |

Python 函数通过 docstring 描述用途和参数，LLM 读取 docstring 决定何时调用、传什么参数。这是最低摩擦的工具注册方式。

### 层级 Agent 与路由

子 Agent 通过 **description-driven routing** 实现委托：

1. 父 Agent 持有多个子 Agent 的 description
2. LLM 根据当前任务匹配最相关的子 Agent description
3. 任务委托到匹配的子 Agent
4. 子 Agent 独立执行并返回结果

这种机制不需要显式路由规则，依赖 LLM 的语义理解进行动态分配。

### A2A 协议原生集成

ADK 原生支持 Google 主导的 A2A（Agent-to-Agent）协议：

| A2A 组件 | ADK 集成方式 |
|----------|------------|
| **Agent Card** | ADK Agent 可发布为 A2A Agent Card（`/.well-known/agent.json`） |
| **Task** | ADK 任务映射到 A2A Task 状态机 |
| **传输层** | 支持 JSON-RPC / gRPC / HTTP+REST |
| **能力发现** | 子 Agent description 映射到 A2A 技能声明 |

A2A 使 ADK Agent 可以与任何兼容 A2A 的 Agent（包括非 ADK 构建的 Agent）进行跨框架协作。

### MCP 集成

ADK 的 MCP 集成让 Agent 可以访问 10,000+ 活跃 MCP 服务器提供的工具和数据源，无需自行实现集成代码。MCP 工具在 ADK 中与原生工具的调用方式一致。

## 关键设计决策

| 决策 | 选择 | 理由 | 权衡 |
|------|------|------|------|
| 模型策略 | Gemini 优化 + model-agnostic | Google 生态优先，LiteLLM 支持其他模型 | 非 Gemini 模型的集成质量可能参差 |
| 语言支持 | Python / TypeScript / Go / Java | 覆盖主流开发者生态 | 多语言维护成本高 |
| 工具注册 | Docstring 驱动 | 零配置、最低摩擦 | 复杂工具的 docstring 可能不够精确 |
| 协议集成 | A2A + MCP 原生 | 拥抱开放标准、跨框架互操作 | 协议本身仍在演化 |
| 路由方式 | Description-driven | 灵活、无需硬编码规则 | 路由准确性依赖 description 质量和 LLM 能力 |
| 部署路径 | 本地 → Cloud Run → GKE → Vertex AI | 渐进式扩展，降低入门门槛 | Vertex AI 路径深度绑定 GCP |

## 与知识库的映射

| ADK 概念 | 知识库 Plane / Pattern |
|---------|----------------------|
| LlmAgent | Prompting Plane + Tools Plane（LLM 决策单元） |
| Workflow Agents（Sequential/Parallel/Loop） | Orchestration Plane — `topology.md`（确定性管道） |
| Description-driven routing | Orchestration Plane — 语义路由模式 |
| 工具系统（四层） | Tools Plane — `tool-use.md`、`tool-catalog.md` |
| Agent-as-Tool | Orchestration Plane — agents-as-tools 模式 |
| A2A 集成 | Orchestration Plane — `communication.md`（跨框架协调） |
| MCP 集成 | Tools Plane — MCP 标准化接入 |
| 评估框架 | Evaluation — 响应 + 轨迹双维度 |
| 状态管理 | State Plane — Agent 状态协调 |
| 部署选项 | Operations Plane — `rollout-and-regression.md` |
| 流式音视频 | Interface Plane — 多模态交互 |
| Agent Card 发布 | Identity & Capability Plane — 能力声明 |

## 值得学习的模式

### 1. 确定性管道 + LLM 决策的混合

Workflow Agents（Sequential / Parallel / Loop）提供确定性的控制流，LlmAgent 在需要动态决策的节点介入。这种混合模式避免了"全靠 LLM 决策"的不确定性，同时保留了 AI 的灵活性。对应知识库中 Hybrid/Layered 架构模式。

### 2. 双协议栈（A2A + MCP）

A2A 解决 Agent 间协调，MCP 解决 Agent 与工具/数据源的连接。双协议栈覆盖了"协议三角"中的两个核心层（L0 工具接入 + L2 Agent 协调），是面向未来的互操作策略。

### 3. 评估框架内置

ADK 内置系统性评估能力，同时评估最终响应质量和执行轨迹合理性。这种"结果 + 过程"双维度评估对应知识库中 Evaluation 层的核心理念：仅看结果不够，还需审计决策路径。

### 4. 渐进式部署路径

从本地开发（CLI + Web UI）到 Cloud Run（容器化）到 GKE（Kubernetes）到 Vertex AI Agent Engine（全托管），提供了清晰的扩展阶梯。每一步都有明确的触发条件（规模、SLO 要求、团队能力），避免过早过度工程化。

### 5. Docstring-as-Contract

工具函数的 docstring 既是人类文档、也是 LLM 的工具描述、也是路由信号。这种"单一真相源"的设计减少了文档与代码的不一致风险。

## 局限与注意事项

| 维度 | 具体问题 | 影响 |
|------|---------|------|
| **Gemini 偏向** | 虽标榜 model-agnostic，但 Gemini 的集成深度和优化程度最高 | 使用非 Gemini 模型可能体验下降 |
| **GCP 绑定** | Vertex AI 部署路径深度绑定 Google Cloud | 多云策略受限 |
| **Description 路由脆弱性** | 路由准确性完全依赖 description 质量 | description 模糊时路由可能错误 |
| **多语言一致性** | 4 种语言的功能对等性和更新节奏可能不同 | 非 Python 用户可能遇到功能滞后 |
| **A2A 协议成熟度** | A2A v1.2 刚达到稳定版 | 协议演化可能带来破坏性变更 |
| **框架 vs 平台边界** | ADK 在框架和平台之间摇摆 | 开发者需要判断哪些功能来自 ADK、哪些来自 GCP |

**行业定位**：ADK 的推荐场景是"Google 生态 + 多模态"（对比 OpenAI Agents SDK 适合"OpenAI 生态"，LangGraph 适合"需要检查点和审计轨迹的生产系统"）。选型的核心因素是已有云投入和模型偏好。

**与 A2A/MCP 的关系**：ADK 是协议的实现载体（A2A 和 MCP 已分别捐献给 Linux Foundation AAIF），其价值在于提供这些协议的最佳实践参考实现。
