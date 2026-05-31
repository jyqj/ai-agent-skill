# LangGraph 架构分析

> **Evidence Status**: synthesized. 基于 LangGraph 官方文档与社区资料的架构综合，非源码级分析。
> **来源**: [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/) | [LangChain State of AI Agents 2026](https://www.langchain.com/stateofaiagents) | [Agent Architecture Patterns Taxonomy 2026](https://www.digitalapplied.com/blog/agent-architecture-patterns-taxonomy-2026)

## 项目概述

LangGraph 是 LangChain 生态中面向生产级 Agent 系统的编排框架，月下载量超过 9000 万次，已被 Uber、JPMorgan、BlackRock、Cisco 等企业用于生产环境。核心设计哲学是**有向图 + 类型化状态**：将 Agent 系统建模为显式的图拓扑，节点是函数或子 Agent，边支持条件路由和动态分支。

LangGraph 在框架选型中的典型定位：需要检查点、人机协作、审计轨迹的生产系统。LangChain 2026 报告显示 60%+ 生产事故与状态管理相关，这恰好是 LangGraph 显式状态模型的核心优势。

## 核心架构

### 有向图 + 类型化状态

```text
StateGraph(TypedState)
  ├─ Node（函数 / Agent / 子图）
  │    └─ 接收 State，返回 State 更新
  ├─ Edge（静态 / 条件路由）
  │    ├─ 静态边 → 固定连接
  │    └─ 条件边 → 根据 State 动态选择下一节点
  ├─ Reducer（状态合并策略）
  │    └─ 处理并发写入冲突
  └─ Checkpointer（持久化层）
       └─ PostgreSQL / Redis / 自定义后端
```

| 概念 | 定义 | 职责 |
|------|------|------|
| **StateGraph** | 类型化的有向图定义 | 声明节点、边和状态 schema |
| **Node** | 图中的计算单元（函数或 Agent） | 接收当前 State，执行逻辑，返回 State 更新 |
| **Edge** | 节点间的连接（静态或条件） | 控制执行流，条件边根据 State 动态路由 |
| **Reducer** | 状态合并函数 | 解决并发节点对同一字段的写入冲突 |
| **Checkpointer** | 状态持久化后端 | 支持断点恢复、时间旅行调试、人机协作 |

### 多 Agent 编排模式

| 模式 | 拓扑 | 适用场景 |
|------|------|---------|
| **Supervisor** | 中心调度：一个管理者节点路由到多个工作节点 | 任务分类明确、需要集中管控 |
| **Scatter-Gather** | 并行扇出 + 合并：任务拆分到多个节点并行执行，结果汇聚 | 独立子任务可并行处理 |
| **Fan-out / Fan-in** | 通用的分支-汇聚拓扑 | 需要灵活的并行-串行组合 |
| **Conditional Routing** | 条件边动态选择路径 | 分支逻辑依赖运行时 State |
| **Deferred Nodes** | 延迟执行节点，等待同步屏障 | 需要跨分支协调的同步点 |

### 状态管理

状态管理是 LangGraph 的核心差异化能力：

| 特性 | 描述 |
|------|------|
| **共享状态对象** | 所有节点通过统一的 TypedState 共享数据 |
| **持久化检查点** | PostgreSQL / Redis Checkpointer，支持断点恢复 |
| **时间旅行调试** | 可回溯到任意检查点，重放或分叉执行 |
| **人机协作** | 在图执行中插入人工审核节点，等待人类输入后继续 |
| **Reducer 合并** | 并发节点写入同一字段时，Reducer 定义合并策略 |

### 中间件系统（v1.1）

v1.1 引入的中间件机制用于处理横切关注点：

| 中间件类型 | 用途 | 示例 |
|-----------|------|------|
| **重试中间件** | 指数退避重试 | LLM API 调用失败时自动重试 |
| **内容审核中间件** | 输入/输出审查 | 在节点执行前后检查合规性 |
| **日志中间件** | 结构化日志 | 记录每个节点的输入、输出、延迟 |
| **自定义中间件** | 开发者扩展 | 任意横切逻辑注入 |

中间件模式使横切关注点与业务逻辑解耦，避免在每个节点中重复实现重试、审核等逻辑。

### 并发模型

```text
Superstep 执行模型：
  1. 检测无依赖的节点集合
  2. 同一 Superstep 内的节点并行执行
  3. Superstep 完成后，Reducer 合并状态
  4. 基于合并后的 State 确定下一个 Superstep
```

- **Fan-out 自动检测**：从同一节点出发的多条边自动触发并行执行
- **Send API**：动态创建独立执行路径，不需要在编译时确定并行度
- **Reducer 冲突解决**：当多个并行节点写入同一 State 字段时，开发者定义的 Reducer 决定如何合并

### 流式协议（v3）

| 特性 | 描述 |
|------|------|
| **Content-block 粒度** | 流式输出以内容块为单位，非 token 级 |
| **多节点并行流** | 并行执行的节点可同时产生流式输出 |
| **事件流** | 图执行过程中的每个状态变更都作为事件发出 |
| **Event Compaction** | 压缩历史事件，减少 token 消耗 |

Event Compaction 是针对长运行图的必要优化：随着执行步骤增加，历史事件的累积会显著增加 token 消耗，Compaction 通过摘要替代原始事件来控制上下文窗口。

## 关键设计决策

| 决策 | 选择 | 理由 | 权衡 |
|------|------|------|------|
| 核心抽象 | 有向图 + 类型化状态 | 显式拓扑使执行路径可预测、可审计 | 简单场景的图定义冗余 |
| 状态模型 | 共享 TypedState + Reducer | 统一状态接口降低节点间协调复杂度 | 状态 schema 变更影响所有节点 |
| 持久化 | Checkpointer 抽象 + 多后端 | 断点恢复和人机协作的基础 | 额外的存储和延迟开销 |
| 并发 | Superstep 自动并行 | 无需手动管理线程/协程 | Reducer 设计不当可能导致数据丢失 |
| 横切关注 | v1.1 中间件 | 解耦业务逻辑与重试/审核等通用逻辑 | 中间件链过长时调试复杂度上升 |
| 流式输出 | v3 content-block 粒度 | 比 token 级流式更适合结构化输出 | 对实时性要求极高的场景可能需要 token 级 |
| 模型无关 | 不绑定特定 LLM | 可组合多个模型提供商 | LangChain 集成层增加间接成本 |

## 与知识库的映射

| LangGraph 概念 | 知识库 Plane / Pattern |
|---------------|----------------------|
| StateGraph（有向图拓扑） | Orchestration Plane — `topology.md`（显式图编排） |
| TypedState + Reducer | State Plane — 类型化状态管理 + 冲突解决 |
| Checkpointer | State Plane — 持久化检查点；Memory Plane — 跨运行恢复 |
| 条件边路由 | Orchestration Plane — 动态路由模式 |
| Supervisor 模式 | Orchestration Plane — `topology.md`（层级拓扑） |
| Scatter-Gather | Orchestration Plane — `concurrency.md`（并行扇出 + 合并） |
| Superstep 并行 | Concurrency Plane — 自动并行调度 |
| 中间件 | Control Plane — 横切关注点（重试、审核、日志） |
| 人机协作节点 | Interaction Plane — `human-in-loop.md` |
| Event Compaction | Memory Plane — token 预算管理 |
| v3 流式协议 | Interface Plane — 流式输出协议 |
| Send API | Orchestration Plane — 动态执行路径 |

### ORDA-VU 映射

图节点可自然映射到 ORDA-VU 闭环的各阶段：

| ORDA-VU 阶段 | LangGraph 对应 |
|-------------|---------------|
| **Observe** | 接收输入的入口节点 |
| **Represent** | 状态解析和结构化节点 |
| **Decide** | 条件边路由 / LLM 决策节点 |
| **Act** | 工具调用节点 / 外部 API 调用节点 |
| **Verify** | 输出验证节点 / 审核中间件 |
| **Update** | Reducer 合并 + Checkpointer 持久化 |

## 值得学习的模式

### 1. 状态图是复杂工作流最自然的建模方式

有向图 + 类型化状态将隐式的执行流显式化：每个节点的输入输出类型、每条边的路由条件都是可检查的。这使得复杂多步工作流的调试、审计和回放成为可能。LangChain 2026 报告中 60%+ 生产事故与状态管理相关，间接验证了显式状态管理的必要性。

### 2. 中间件模式解决横切关注点

v1.1 的中间件机制借鉴了 Web 框架（Express、Koa）的经典模式，将重试、内容审核、日志等横切关注点从业务逻辑中解耦。这是 Agent 框架从"实验工具"走向"生产基础设施"的标志性特征。

### 3. Deferred Execution 实现同步屏障

Deferred Nodes 允许在并行分支中设置同步点，某些节点等待其他分支完成后再执行。这解决了"扇出容易、汇聚难"的经典并发问题。

### 4. Checkpointer 是人机协作的基础

持久化检查点不仅用于故障恢复，更是人机协作的必要条件。Agent 执行到审核节点时暂停，人类审核后从检查点恢复继续。没有 Checkpointer，人机协作只能靠轮询等待。

## 局限与注意事项

| 维度 | 具体问题 | 影响 |
|------|---------|------|
| **学习曲线** | 图编程模型对非图论背景的开发者不直观 | 入门门槛高于 CrewAI 等角色驱动框架 |
| **状态爆炸** | 复杂图的 TypedState 字段可能快速膨胀 | 状态 schema 维护成本上升 |
| **Reducer 陷阱** | Reducer 设计不当导致并发数据丢失 | 需要开发者理解并发合并语义 |
| **调试复杂度** | 条件边 + 并行 + 中间件的组合使执行路径难以追踪 | 需要依赖 tracing 工具 |
| **LangChain 耦合** | 与 LangChain 生态深度集成 | 独立使用时仍需引入 LangChain 基础依赖 |
| **冷启动开销** | 图编译 + 状态初始化的固定成本 | 简单任务的延迟税 |
| **Learning / Identity 弱** | 缺乏内置学习和身份管理机制 | 需要外部系统补充 |

**行业定位**：LangGraph 在框架选型中的推荐场景是"需要检查点、人机协作、审计轨迹的生产系统"（对比 OpenAI Agents SDK 适合"OpenAI 生态"，Google ADK 适合"Google 生态 + 多模态"，CrewAI 适合"快速原型 + 非技术利益相关者沟通"）。常见迁移路径是从 CrewAI 原型验证后迁移到 LangGraph 获得更精细的状态管理。
