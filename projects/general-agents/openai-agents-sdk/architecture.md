# OpenAI Agents SDK 架构分析

> **Evidence Status**: synthesized（基于官方文档与社区资料，非源码级分析）
> **来源**: [The next evolution of the Agents SDK | OpenAI](https://openai.com/index/the-next-evolution-of-the-agents-sdk/) | [OpenAI Agents SDK 文档](https://openai.github.io/openai-agents-python/) | [Agent Architecture Patterns Taxonomy 2026](https://www.digitalapplied.com/blog/agent-architecture-patterns-taxonomy-2026)

## 项目概述

OpenAI Agents SDK 于 2025.03 发布，作为实验性 Swarm 框架的生产继任者。设计哲学为**最小抽象 + Python-first**：提供刚好够用的原语让开发者构建 Agent 系统，不在模型和开发者之间插入过多抽象层。

SDK 已发展为 OpenAI 生态中的核心 Agent 构建框架，与 Responses API、Codex 沙箱、评估/微调/蒸馏管线深度集成。

## 核心架构

### 四原语模型

```text
Agent（指令 + 工具 + 模型配置）
  ├─ Tool（Python 函数 → 自动 schema 转换 + Pydantic 验证）
  ├─ Handoff（Agent 间任务委托 → agents-as-tools 模式）
  └─ Guardrail（输入/输出验证 → 并行执行，不阻塞主路径）
```

| 原语 | 定义 | 职责 |
|------|------|------|
| **Agent** | 配备指令和工具的 LLM 单元 | 接收任务、调用工具、生成输出 |
| **Handoff** | Agent 间任务委托机制 | 将控制权转移到更适合的 Agent |
| **Guardrail** | 输入/输出验证管道 | 在执行前后检查安全、格式、策略合规 |
| **Tool** | Python 函数自动转换为工具 | 提供 Agent 与外部世界的接口 |

### Agent Loop 内部机制

```text
while not terminal:
    1. 构建消息上下文（system prompt + 对话历史 + 工具定义）
    2. 调用 LLM（Responses API）
    3. 处理响应：
       ├─ 文本输出 → 检查 output guardrails → 返回结果
       ├─ Tool Call → 执行工具 → 将结果追加到消息 → 续行
       └─ Handoff → 切换到目标 Agent → 新 Agent 接管循环
    4. 如果有待处理的工具结果 → 继续循环
    5. 检查终止条件（最终输出 / 最大轮次 / 异常）
```

Agent Loop 是 SDK 的核心运行时——它管理工具调用、结果处理、续行逻辑和 Handoff 转移，开发者不需要手动编排这些底层细节。

### 沙箱执行模型

| 组件 | 职责 | 安全意义 |
|------|------|---------|
| **Sandbox Agents** | 在隔离工作空间中运行 Agent | 模型生成的代码无法访问宿主环境 |
| **Manifest** | 声明式定义文件、工具和依赖 | 最小权限原则 |
| **凭证隔离** | Harness 层持有凭证，沙箱层不可见 | 即使 prompt injection 成功也无法窃取凭证 |
| **可恢复会话** | 沙箱状态可持久化和恢复 | 支持长时运行任务的断点续行 |

**安全设计假设**："假设 prompt-injection 和数据窃取攻击存在"——通过分离 harness 和 compute 实现防御。

沙箱提供商生态：Blaxel, Cloudflare, Daytona, E2B, Modal, Runloop, Vercel。

### Tracing 系统

内置可视化、调试和监控能力：

- 每次 Agent 运行生成结构化 trace
- 兼容 OpenAI 评估 / 微调 / 蒸馏管线
- 支持逐步回放和断点调试
- Trace 数据可直接用于模型改进反馈循环

### Sessions 持久记忆层

| 特性 | 描述 |
|------|------|
| 跨运行持久 | Agent 运行结束后记忆不丢失 |
| 跨 Agent 共享 | 不同 Agent 可访问同一 Session |
| 结构化存储 | 不是原始对话历史，而是结构化的记忆对象 |
| 检索增强 | 支持按需检索相关记忆 |

### Provider-Agnostic 设计

默认使用 Responses API（OpenAI 原生），但支持配置非 OpenAI 模型提供商。这使得 SDK 不是锁定 OpenAI 模型的专属框架，而是一个可移植的 Agent 构建工具。

## 关键设计决策

| 决策 | 选择 | 理由 | 权衡 |
|------|------|------|------|
| 抽象层级 | 最小抽象 | "足够的原语让开发者构建"，不过度封装 | 复杂场景需要更多手动编排 |
| 语言 | Python-first | AI/ML 生态主流语言 | Web 开发者需要适配 |
| 委托模型 | Handoff（agents-as-tools） | 自然的层级委托，避免复杂路由逻辑 | 仅支持层级拓扑，不原生支持对等 |
| 验证模型 | Guardrail 并行执行 | 不阻塞主路径，减少延迟税 | 并行 guardrail 的结果可能在动作后才到达 |
| 工具定义 | Python 函数 + 自动 schema | 零配置工具注册 | 复杂工具需要手动 schema 调优 |
| 沙箱 | 分离 harness/compute | 凭证安全的根本保障 | 增加部署复杂度 |
| Tracing | 内置 + 兼容评估管线 | 闭环改进（trace → eval → finetune → deploy） | 深度绑定 OpenAI 评估生态 |

## 与知识库的映射

| Agents SDK 概念 | 知识库 Plane / Pattern |
|-----------------|----------------------|
| Agent（指令 + 工具） | Prompting Plane + Tools Plane |
| Agent Loop | ORDA-VU 闭环 — Step-loop 粒度 |
| Handoff | Orchestration Plane — `topology.md`（层级委托） |
| Guardrail | Control Plane — 输入/输出验证；Security Plane |
| Tool（自动 schema） | Tools Plane — `tool-use.md`、`tool-catalog.md` |
| Sandbox Agents | Execution Plane — `execution-env.md`（沙箱隔离） |
| Sessions | Memory Plane — 跨运行持久记忆 |
| Tracing | Observability Plane — `trace-format.md` |
| Provider-Agnostic | Interface Plane — `platform-adapter.md` |
| 凭证隔离 | Identity & Capability Plane；Security Plane |
| MCP 集成 | Tools Plane — MCP 标准化工具接入 |

## 值得学习的模式

### 1. 最小原语哲学

四个原语（Agent / Handoff / Guardrail / Tool）覆盖了 Agent 系统的核心需求。这种"最小但完备"的设计降低了学习曲线，同时保留了组合灵活性。对比 LangGraph 的图节点/边模型或 CrewAI 的角色/任务模型，Agents SDK 的抽象层级最低。

### 2. Agents-as-Tools 委托模式

Handoff 机制将 Agent 间委托简化为"一个 Agent 可以调用另一个 Agent，就像调用工具一样"。这避免了复杂的路由逻辑和消息总线，但仅适合层级拓扑。

### 3. 分离 Harness 与 Compute 的安全模型

凭证在 harness 层管理，模型生成的代码在沙箱中执行且看不到凭证。这是对 prompt injection 攻击的架构级防御——即使攻击者控制了模型输出，也无法获取敏感凭证。

### 4. Trace → Eval → Finetune 闭环

Tracing 系统生成的数据不仅用于调试，还直接进入评估、微调和蒸馏管线。这种"运行时数据驱动模型改进"的闭环是 Harness Engineering 的核心价值之一。

## 局限与注意事项

| 维度 | 具体问题 | 影响 |
|------|---------|------|
| **拓扑限制** | Handoff 仅支持层级委托，不原生支持对等/Mesh 拓扑 | 复杂多 Agent 协作需要额外编排 |
| **生态锁定风险** | Tracing/Eval 深度集成 OpenAI 管线 | Provider-Agnostic 设计在实践中的可移植性存疑 |
| **状态管理** | Agent Loop 内部状态不如 LangGraph 显式 | 复杂工作流的调试和回放能力较弱 |
| **协调开销** | 简单任务不需要 Handoff 和 Guardrail | "协调开销在简单任务上主导成本" |
| **Guardrail 时序** | 并行 Guardrail 可能在动作执行后才返回结果 | 高风险场景需要同步 Guardrail |
| **框架成熟度** | 2025.03 发布，生态仍在快速演化 | API 变更风险 |

**行业定位**：Agents SDK 在框架选型中的推荐场景是"留在 OpenAI 生态"（对比 LangGraph 适合"需要检查点、人机协作、审计轨迹的生产系统"，Google ADK 适合"Google 生态 + 多模态"）。选型决策应基于已有生态投入和具体需求，而非框架功能对比。
