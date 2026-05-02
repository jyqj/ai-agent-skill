# Glossary

> **Evidence Status** — mixed. 术语来自本知识库各模块（runtime、memory、tooling、control、evaluation 等），为跨模块一致性而维护的统一词表。

当团队成员在不同语境下使用相同术语却各自理解不同时，设计讨论的效率会急剧下降。这份术语表为整个知识库提供统一的词汇基础。遇到不熟悉的术语时，可在此查阅定义和所属模块，然后跟随"所在模块"列的链接深入了解。术语按 Agent 系统的逻辑层次分组，从核心概念逐层展开到评估。

## 核心概念

以下七个术语是整个知识库的地基，其他所有概念都建立在它们之上：

| 术语 | 定义 | 所在模块 |
|---|---|---|
| Agent | 具有自主决策闭环的系统：Observe → Represent → Decide → Act → Verify | 全局 |
| Harness | Model 之外的一切：接口、表示、上下文、状态、工具、控制、执行、记忆、评估 | 全局 |
| Runtime | Agent 运行时系统，负责把任务推进为一系列可控行动 | `architecture/` |
| Agent Kernel | Runtime 的核心主循环 | `architecture/` |
| Representation（表示） | 现实输入的机器可处理表示 | `architecture/planes/representation/` |
| World State（世界状态） | 对外部对象当前状态的可刷新快照 | `architecture/planes/world-state/` |
| Effect（效果） | 一次外部动作期望造成的现实变化 | `architecture/planes/effects/` |

## 产品层

核心概念定义了 Agent 系统的基本构成。当这些要素落到具体产品中，就需要一组面向产品设计的概念来衔接：

| 术语 | 定义 | 所在模块 |
|---|---|---|
| User Job | 用户雇 Agent 完成的具体工作，产品设计的起点 | `categories/` |
| Product Blueprint（产品蓝图） | 特定产品形态的模块组合配方和关键设计决策 | `categories/` |
| Autonomy Level（自治等级） | Agent 的自主性等级 L0-L5，从只回答到长时自治 | `concepts/autonomy-levels.md` |
| Execution Depth（执行深度） | Agent 需要深入到的执行层级 D0-D6 | `architecture/controllers/execution-depth/` |
| Deliverable（交付物） | Agent 最终交付给用户的产物（diff、报告、状态变更等） | `categories/` |

## 运行时入口

产品定义了"做什么"，运行时则负责"怎么做"。以下是输入进入 Agent 系统时最先经过的入口模块：

| 术语 | 定义 | 所在模块 |
|---|---|---|
| Interface Gateway（接口网关） | 把 Chat / CLI / IDE / API / Webhook 等入口转换成统一 Task Envelope 的模块 | `architecture/planes/interface/` |
| Perception Adapter（感知适配器） | 把 screenshot / DOM / OCR / ASR / sensor / db event 转成原始输入引用的模块 | `architecture/planes/interface/` |
| Task Envelope（任务信封） | 标准化任务描述对象 | `architecture/planes/interface/` |
| Raw Input Ref（原始输入引用） | 对原始输入材料的引用（文件、截图、网页、音频、事件） | `architecture/planes/representation/` |

## 表示与观察

输入进入系统后，需要被转化为模型能处理的形式。以下术语描述从原始输入到结构化表示的转化过程：

| 术语 | 定义 | 所在模块 |
|---|---|---|
| Representation Record（表示记录） | 一条规范化表示记录，含 raw ref、parser、transform chain、trust tier | `architecture/planes/representation/` |
| Transform Chain（转换链） | 原始输入到当前表示经历的转换链 | `architecture/planes/representation/` |
| Trust Tier（信任分层） | 指令、可信数据、不可信数据、摘要、记忆、推断等语义分层 | `architecture/planes/representation/` |
| Raw Observation（原始观察） | 原始世界切片 | `architecture/planes/representation/observation-semantics.md` |
| Parsed Observation（解析观察） | 解析后的结构化观察 | `architecture/planes/representation/observation-semantics.md` |
| Summary（摘要） | 有损压缩的概括 | `architecture/planes/representation/observation-semantics.md` |
| Claim（主张） | 可检验的主张 | `architecture/planes/representation/observation-semantics.md` |
| Inference（推断） | 模型推断 | `architecture/planes/representation/observation-semantics.md` |

## 执行深度

有了表示，Agent 还需要控制自己在任务中执行到多深。以下术语覆盖执行深度的度量和控制：

| 术语 | 定义 | 所在模块 |
|---|---|---|
| Depth Controller（深度控制器） | 控制 Agent 继续深入、验证、恢复、审批还是停止的组件 | `architecture/controllers/execution-depth/` |
| Required Depth（目标深度） | 任务需要达到的目标深度（D0-D6） | `architecture/controllers/execution-depth/` |
| Task Graph（任务图） | 把任务拆解为 milestone 和 subtask 的结构化表示 | `architecture/controllers/execution-depth/` |
| Milestone Gate（里程碑关卡） | milestone 之间的检查点 | `architecture/controllers/execution-depth/` |
| Depth Budget（深度预算） | 多维预算（step/tool/token/risk/time/branch/retry/attention/freshness） | `architecture/controllers/execution-depth/` |
| Decision Log（决策日志） | 记录关键决策和排除方案的结构化日志 | `design-space/patterns/decision-log.md` |
| Evidence（证据） | 证明任务完成的产物：测试结果、diff、截图、日志等 | `evaluation/` |

## 上下文、记忆与状态

执行过程中，Agent 需要持续管理当前上下文、长期记忆和任务状态来保持连贯性：

| 术语 | 定义 | 所在模块 |
|---|---|---|
| Context Engine（上下文引擎） | 管理模型当前可见信息的模块 | `architecture/planes/context/` |
| Context Pack（上下文包） | 为特定 milestone 装配的上下文子集 | `architecture/planes/context/` |
| Context Rot（上下文腐化） | 上下文填满后推理和任务完成能力下降的现象 | `architecture/planes/context/` |
| Memory Engine（记忆引擎） | 管理跨会话、跨任务持续性的模块 | `architecture/planes/memory/` |
| Memory Provenance（记忆溯源） | 记忆的来源标记 | `architecture/planes/memory/` |
| State Engine（状态引擎） | 管理任务当前状态的模块 | `architecture/planes/state/` |
| Checkpoint（检查点） | 可恢复的任务状态快照 | `architecture/planes/state/` |
| Hydration（状态恢复） | 从 checkpoint 恢复任务状态并重建最小上下文的过程 | `architecture/planes/state/` |
| World State Snapshot（世界状态快照） | 对外部对象状态的带时效快照 | `architecture/planes/world-state/` |

## 工具、执行与效果

内部状态就绪后，Agent 通过工具调用和执行环境作用于外部世界，并验证效果：

| 术语 | 定义 | 所在模块 |
|---|---|---|
| Tool Surface（工具面） | Agent 可调用工具的集合及其权限、Schema、风险边界 | `architecture/planes/tools/` |
| Tool Runtime（工具运行时） | 管理工具注册、选择、调用、返回和审计的模块 | `architecture/planes/tools/` |
| Tool Spec（工具规格） | 单个工具的完整定义 | `architecture/planes/tools/` |
| Host Layer（宿主层） | 工具的执行宿主：Local / Remote / Sidecar / MCP | `architecture/planes/tools/` |
| Standard Tool Observation（标准工具观察） | 工具返回的标准化结果格式 | `architecture/planes/tools/` |
| Execution Engine（执行引擎） | 管理沙箱、Shell、文件和代码运行的模块 | `architecture/planes/execution/` |
| Effect Ledger（效果账本） | 记录 intended effect、verification status、rollback 的账本 | `architecture/planes/effects/` |
| Read-after-Write（写后读验证） | 写动作后回读或确认外部状态的验证方式 | `architecture/planes/effects/` |
| Postcondition（后置条件） | 动作完成后世界应满足的条件 | `architecture/planes/tools/` |

## 控制、安全、协作与运维

行动需要边界和治理。以下术语覆盖控制策略、安全防护、多 Agent 协作和长期运维：

| 术语 | 定义 | 所在模块 |
|---|---|---|
| Control Policy Engine（控制策略引擎） | 对 Agent 行动进行前馈约束、反馈验证和纠错的模块 | `architecture/planes/control/` |
| Verification Gate（验证关卡） | 检查阶段产物是否满足退出条件的关卡 | `architecture/planes/control/` |
| Security Boundary（安全边界） | 区分指令、可信数据、不可信内容、秘密和租户范围的边界 | `architecture/planes/security/` |
| Untrusted Context Lane（不可信内容通道） | 承载外部文本、日志、网页、issue 等不可信内容的通道 | `design-space/patterns/untrusted-context-boundary.md` |
| Orchestration Engine（编排引擎） | 管理子代理、Worker、多窗口的模块 | `architecture/planes/orchestration/` |
| Operations（运维） | 配置追踪、回归、灰度、事故处理等长期运维能力 | `architecture/planes/operations/` |
| Canary Rollout（金丝雀发布） | 先小流量验证再全量的上线方式 | `architecture/planes/operations/rollout-and-regression.md` |

## 评估

最终，Agent 的表现需要被系统性地衡量和迭代：

| 术语 | 定义 | 所在模块 |
|---|---|---|
| Eval（评估） | 用可重复任务集评估 Agent 能力和失败模式的方法 | `evaluation/` |
| Eval Case（评估用例） | 单个评估用例，包含任务、表示要求、effect 验证、失败注入 | `evaluation/eval-framework.md` |
| Failure Taxonomy（失败分类） | Agent 失败模式的分类体系 | `evaluation/failure-taxonomy.md` |
| Scorecard（评分卡） | 对 Agent 表现的多维量化评分 | `evaluation/eval-framework.md` |

## 新增核心术语

以下术语随架构演进新增，尚未归入上述分组，但在多个模块中频繁出现：

| 术语 | 定义 |
|---|---|
| PromptContract（Prompt 契约） | Prompting Plane 产生的指令、示例、推理模式、输出契约快照。 |
| InteractionEvent（交互事件） | 用户中断、审批、纠错、教学、进度、拒绝等交互事件。 |
| AgentMessage（Agent 消息） | 多 Agent 协作时的结构化消息，包含 authority_scope 和 evidence_refs。 |
| ResourcePlan（资源计划） | 成本、token、模型路由、缓存和预算策略。 |
| FlowRun（流式执行记录） | 批量、流式或管道式 Agent 任务的执行记录。 |
| ConfigFingerprint（配置指纹） | 运行时行为配置的指纹，用于审计和回归，不代表 skill 自身状态。 |
| UnknownRecord（未知记录） | 显式记录不可知、低置信、过期、冲突或不可验证状态。 |
