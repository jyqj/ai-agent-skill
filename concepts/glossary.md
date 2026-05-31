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
| Representation（表示） | 现实输入的机器可处理表示 | `architecture/planes/sensing-representation/` |
| World State（世界状态） | 对外部对象当前状态的可刷新快照 | `architecture/planes/world-state/` |
| Effect（效果） | 一次外部动作期望造成的现实变化 | `architecture/planes/effects/` |

## 产品层

核心概念定义了 Agent 系统的基本构成。当这些要素落到具体产品中，就需要一组面向产品设计的概念来衔接：

| 术语 | 定义 | 所在模块 |
|---|---|---|
| User Job | 用户雇 Agent 完成的具体工作，产品设计的起点 | `categories/` |
| Product Blueprint（产品蓝图） | 特定产品形态的模块组合配方和关键设计决策 | `categories/` |
| Autonomy Level（自治等级） | Agent 的自主性等级 L0-L5，从只回答到长时自治 | `concepts/autonomy-levels.md` |
| Execution Depth（执行深度） | Agent 需要深入到的执行层级 D0-D6 | `architecture/kernel/execution-depth-controller/` |
| Deliverable（交付物） | Agent 最终交付给用户的产物（diff、报告、状态变更等） | `categories/` |

## 运行时入口

产品定义了"做什么"，运行时则负责"怎么做"。以下是输入进入 Agent 系统时最先经过的入口模块：

| 术语 | 定义 | 所在模块 |
|---|---|---|
| Interface Gateway（接口网关） | 把 Chat / CLI / IDE / API / Webhook 等入口转换成统一 Task Envelope 的模块 | `architecture/planes/sensing-representation/` |
| Perception Adapter（感知适配器） | 把 screenshot / DOM / OCR / ASR / sensor / db event 转成原始输入引用的模块 | `architecture/planes/sensing-representation/` |
| Task Envelope（任务信封） | 标准化任务描述对象 | `architecture/planes/sensing-representation/` |
| Raw Input Ref（原始输入引用） | 对原始输入材料的引用（文件、截图、网页、音频、事件） | `architecture/planes/sensing-representation/` |

## 表示与观察

输入进入系统后，需要被转化为模型能处理的形式。以下术语描述从原始输入到结构化表示的转化过程：

| 术语 | 定义 | 所在模块 |
|---|---|---|
| Representation Record（表示记录） | 一条规范化表示记录，含 raw ref、parser、transform chain、trust tier | `architecture/planes/sensing-representation/` |
| Transform Chain（转换链） | 原始输入到当前表示经历的转换链 | `architecture/planes/sensing-representation/` |
| Trust Tier（信任分层） | 指令、可信数据、不可信数据、摘要、记忆、推断等语义分层 | `architecture/planes/sensing-representation/` |
| Raw Observation（原始观察） | 原始世界切片 | `architecture/planes/representation/observation-semantics.md` |
| Parsed Observation（解析观察） | 解析后的结构化观察 | `architecture/planes/representation/observation-semantics.md` |
| Summary（摘要） | 有损压缩的概括 | `architecture/planes/representation/observation-semantics.md` |
| Claim（主张） | 可检验的主张 | `architecture/planes/representation/observation-semantics.md` |
| Inference（推断） | 模型推断 | `architecture/planes/representation/observation-semantics.md` |

## 执行深度

有了表示，Agent 还需要控制自己在任务中执行到多深。以下术语覆盖执行深度的度量和控制：

| 术语 | 定义 | 所在模块 |
|---|---|---|
| Depth Controller（深度控制器） | 控制 Agent 继续深入、验证、恢复、审批还是停止的组件 | `architecture/kernel/execution-depth-controller/` |
| Required Depth（目标深度） | 任务需要达到的目标深度（D0-D6） | `architecture/kernel/execution-depth-controller/` |
| Task Graph（任务图） | 把任务拆解为 milestone 和 subtask 的结构化表示 | `architecture/kernel/execution-depth-controller/` |
| Milestone Gate（里程碑关卡） | milestone 之间的检查点 | `architecture/kernel/execution-depth-controller/` |
| Depth Budget（深度预算） | 多维预算（step/tool/token/risk/time/branch/retry/attention/freshness） | `architecture/kernel/execution-depth-controller/` |
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
| FailureRecord（失败记录） | 记录一次失败的结构化数据，含 phase、category（parse_error / tool_error / stale_world_state / budget_exhausted 等）、severity、evidence_refs、reversibility 和 recovery_action。详见 `architecture/runtime-data-model.md`。 |
| UnknownRecord（未知记录） | 显式记录不可知、低置信、过期、冲突或不可验证状态。 |

---

## 术语统一表

> 以下 5 个术语在知识库中存在多种叫法，导致跨文件阅读时产生歧义。本节给出规范名称、定义、已知别名和所有出现位置，其他文件应引用本表而非自行定义。

### GhostSuccess

**定义** — 工具报告执行成功，但实际效果未达成。典型场景：API 返回 200 但数据库字段未变更，点击提交按钮但页面状态未改变。这是生产系统中最常见的静默失败模式。

**别名**
- `tool_success_as_completion` — 反模式名，强调"把工具成功等同于任务完成"
- `IS-02` — PRINCIPLE-INDEX 中的原则编号
- `Phantom Completion` — cross-cutting 文件中的等价表述
- `ghost_success` — 运行时数据模型中的 EffectRecord category 值

**关联文件**
- `architecture/kernel/effect-verification.md` — 主定义，含状态机、检测逻辑、决策分支
- `architecture/kernel/tool-lifecycle.md` — 工具生命周期中的 GhostSuccess 状态节点
- `architecture/kernel/README.md` — kernel 索引中的条目说明
- `architecture/kernel/execution-depth-controller/overview.md` — BN-07 效果验证缺口
- `architecture/planes/effects/overview.md` — Effects Plane 的验证矩阵和 FileStateCache 案例
- `architecture/cross-cutting/state-x-world-state.md` — Phantom Completion 映射
- `synthesis/tool-effect-verification.md` — 横向对比：Stop Gate 不能只看 tool_result.status
- `synthesis/runtime-vs-world-state.md` — 运行时状态与世界状态分离的第一失败模式
- `evaluation/failure-taxonomy.md` — 失败分类条目
- `evaluation/pattern-fixture-map.md` — 对应评估 fixture
- `concepts/agent-typology.md` — 行动型 Agent 的典型失败模式
- `design-space/lessons-learned/replit-deletion-and-coverup.md` — `tool_success_as_completion` 别名出现
- `categories/financial-agent/implementation-map.md` — `tool_success_as_completion` 别名出现

### Context Rot

**定义** — 随着对话推进，上下文窗口中早期信息的注意力权重持续稀释，导致指令遵循率下降。本质是 transformer 注意力在长序列上的分布退化：信息被"淹没"而非被"删除"。

**别名**
- `token budget depletion` — 侧重预算维度的表述（搜索未命中独立出现，但语义等价）
- `指令不跟随` — 中文别名，出现于 `architecture/kernel/context-budget.md`
- `上下文腐化` — 本文件"上下文、记忆与状态"分组中的中文译名

**关联文件**
- `architecture/planes/context/context-rot-model.md` — 主定义，含衰减模型
- `architecture/planes/context/overview.md` — Context Plane 概述中的核心概念
- `architecture/planes/context/compression-strategies.md` — 对抗 Context Rot 的压缩策略
- `architecture/planes/context/context-assembly-algorithm.md` — 上下文装配中的腐化感知
- `architecture/kernel/context-budget.md` — kernel 层预算管理，`指令不跟随`出现处
- `architecture/kernel/execution-depth-controller/overview.md` — 深度控制中的上下文压力
- `architecture/controllers/execution-depth/overview.md` — 同上（旧路径）
- `architecture/cross-cutting/context-engineering-x-memory.md` — 上下文与记忆的交叉关注
- `cognitive-architecture/working-memory-dynamics.md` — 工作记忆动态中的退化现象
- `evaluation/failure-taxonomy.md` — 失败分类条目
- `evaluation/fixtures/coding_context_rot_long_task_001.yaml` — 正向评估 fixture
- `evaluation/fixtures/negative_context_rot_001.yaml` — 负向评估 fixture
- `design-space/patterns/subagent.md` — 子代理模式中对 Context Rot 的缓解
- `design-space/patterns/tool-output-offloading.md` — 工具输出卸载缓解上下文压力
- `design-space/frontier/long-horizon-runtime.md` — 长时运行时的核心挑战
- `design-space/lessons-learned/infinite-context-as-memory.md` — 无限上下文并不能解决 Context Rot
- `design-space/lessons-learned/persona-drift-in-companions.md` — 伴侣型 Agent 中的上下文腐化
- `synthesis/context-memory-state-boundaries.md` — 上下文/记忆/状态边界
- `concepts/foundations/bounded-rationality.md` — 有限理性基础中的关联
- `categories/coding-agent/design-decisions.md` — 编码 Agent 设计决策
- `categories/creative-agent/design-decisions.md` — 创意 Agent 设计决策
- `paradigms/memory-paradigms.md` — 记忆范式中的关联
- `corpus/2025-2026-agent-architecture-corpus.md` — 语料索引

### Map-Territory Gap

**定义** — Agent 内部表示（map）与外部实际状态（territory）之间的偏差。Agent 基于过时或不准确的内部模型做出决策，导致行动在现实中失败。名称源自 Korzybski 的"地图不是领地"认识论原则。

**别名**
- `Stale World State` — 侧重"过时"语义，运行时数据模型中的 FailureRecord category 值
- `IS-03 地图-领地分离` — PRINCIPLE-INDEX 中的原则编号
- `map-territory separation` — 英文原则名

**关联文件**
- `concepts/foundations/PRINCIPLE-INDEX.md` — IS-03 原则定义，含 map-territory 和 stale world state
- `concepts/foundations/principle-category-heatmap.md` — 原则热力图中的 IS-03 条目
- `architecture/planes/world-state/overview.md` — World State Plane，IS-03 的架构落地
- `architecture/planes/state/overview.md` — State Plane 中的 stale world state 处理
- `architecture/planes/recovery/overview.md` — stale_world_state 作为 FailureRecord category
- `architecture/planes/recovery/recovery-decision-tree.md` — stale_world_state 的恢复路径
- `architecture/planes/concurrency/overview.md` — 并发场景下的 stale world state 风险
- `architecture/planes/concurrency/cancellation-tokens.md` — 取消令牌中的 stale state 触发
- `architecture/runtime-data-model.md` — FailureRecord.category 包含 `stale_world_state`
- `architecture/complexity-levels.md` — 复杂度分级中的 stale state 考量
- `architecture/cross-cutting/state-x-world-state.md` — 内部状态与世界状态的交叉分析
- `design-space/lessons-learned/cursor-case-bypass-rce.md` — IS-03 违反的实际案例
- `design-space/patterns/property-based-agent-testing.md` — 属性测试中的 stale world state 注入
- `evaluation/failure-taxonomy.md` — 失败分类条目
- `index/design-checklist.md` — 设计检查表中的 stale world state 检查项

### evidence_refs

**定义** — 验证证据的结构化引用字段。出现在 AgentMessage、MemoryRecord、LearningRecord、EvidenceRef 等多个运行时数据结构中，用于将决策、记忆、学习与可追溯的证据绑定。核心纪律：Memory 写入前必须检查 `evidence_refs` 非空。

**别名**
- `verification_evidence` — 早期别名，出现在 effects/tools/kernel 等模块，侧重效果验证场景
- `raw_refs` — 表示层别名，出现在 representation/sensing-representation/observability 等模块，侧重原始输入引用

**关联文件**
- `architecture/runtime-data-model.md` — 主定义，AgentMessage/FailureRecord/ResourcePlan 中均包含此字段
- `architecture/runtime-data-flow.md` — 数据流中的 evidence_refs 传递
- `architecture/module-boundaries.md` — 模块边界检查：多 Agent 消息是否有 evidence_refs
- `architecture/kernel/effect-verification.md` — verification_evidence 别名出现
- `architecture/planes/effects/overview.md` — verification_evidence 别名出现
- `architecture/planes/tools/overview.md` — verification_evidence 别名出现
- `architecture/planes/explainability/overview.md` — EvidenceRef 结构中的 evidence_refs
- `architecture/planes/observability/overview.md` — raw_refs 别名出现
- `architecture/planes/sensing-representation/overview.md` — raw_refs 别名出现（原 representation/overview.md 已合并）
- `architecture/planes/representation/representation-contract.md` — raw_refs 别名出现
- `architecture/planes/sensing-representation/overview.md` — raw_refs 别名出现
- `architecture/planes/learning-adaptation/overview.md` — LearningRecord 中的 evidence_refs
- `architecture/planes/orchestration/communication.md` — AgentMessage 的 claim 类型包含 evidence_refs
- `architecture/planes/orchestration/trust-and-attribution.md` — 信任归因中的 evidence_refs
- `architecture/planes/orchestration/governance.md` — 治理记录中的 evidence_refs
- `architecture/planes/recovery/overview.md` — FailureRecord 中的 evidence_refs
- `architecture/learning/skill-governance.md` — 技能治理记录
- `architecture/learning/online-adaptation.md` — 在线适应记录
- `architecture/learning/feedback-loops.md` — 反馈循环记录
- `concepts/foundations/PRINCIPLE-INDEX.md` — AV-01 原则：MemoryRecord.evidence_refs 非空
- `concepts/foundations/action-verification.md` — 行动验证纪律
- `concepts/foundations/principle-obligation-eval-map.md` — raw_refs 在原则-义务映射中的出现
- `design-space/frontier/multi-agent-governance.md` — 多 Agent 治理中的 evidence_refs 要求
- `design-space/frontier/observability-control-plane.md` — 可观测性控制面
- `design-space/frontier/long-horizon-runtime.md` — raw_refs 在长时运行时中的出现
- `paradigms/collaboration-paradigms.md` — 协作范式中的 evidence_refs
- `index/design-checklist.md` — 子 Agent 输出检查项
- `SKILL.md` — 技能速查卡中的 raw_refs

### budget_exhausted

**定义** — Agent 的资源预算（token / cost / step / time 任一维度）已耗尽的信号。触发后 Agent 必须按 `stop_policy.budget_exhausted_behavior` 指定的策略行动（ask_user / partial_deliver / stop / switch_strategy），而非继续消耗隐藏预算。

**别名**
- `budget_consumed` — 语义等价的动词形式（搜索未命中独立出现）
- `max steps reached` / `max_steps` — 侧重步数维度的表述，出现在 agent-loop、goal-hierarchy 等文件
- `BR-03 满意解` — PRINCIPLE-INDEX 中关联的有限理性原则："够好就停"

**关联文件**
- `architecture/kernel/execution-depth-controller/overview.md` — 主定义，`budget_exhausted → STOP_WITH_EVIDENCE` 决策路径
- `architecture/kernel/agent-loop.md` — 主循环中的 `finish_budget_exhausted` 和 `max_steps` 检查
- `architecture/kernel/context-budget.md` — 上下文预算管理
- `architecture/controllers/execution-depth/overview.md` — 旧路径，同深度控制器
- `architecture/controllers/README.md` — 控制器索引中的 `budget_exhausted` 示例代码
- `architecture/runtime-data-model.md` — FailureRecord.category 和 ResourcePlan.stop_policy 中的定义
- `architecture/planes/cost/overview.md` — Cost Plane 的 `budget_exhausted_behavior` 和压力注入
- `architecture/planes/recovery/overview.md` — FailureRecord category、恢复策略表
- `architecture/planes/recovery/recovery-decision-tree.md` — 恢复决策树中的 budget_exhausted 行
- `architecture/planes/concurrency/cancellation-tokens.md` — 取消令牌的 reason 之一
- `concepts/foundations/PRINCIPLE-INDEX.md` — BR-03 满意解原则，`budget_exhausted_behavior` 定义
- `concepts/foundations/principle-obligation-eval-map.md` — BR-03 在原则-义务映射中的出现
- `cognitive-architecture/goal-hierarchy.md` — max_steps 在目标层级中的出现
- `architecture/cross-cutting/multi-model-trust-boundary.md` — 多模型信任边界中的 max_steps
- `evaluation/fixtures/negative_budget_exceeded_001.yaml` — 预算超支负向评估 fixture
- `starter-kit/react-llm-agent/agent_runtime.py` — 参考实现中的 max_steps

### Plugin Manifest
插件的声明式元数据文件（如 `openclaw.plugin.json`），描述 capability、依赖、auth 需求。Runtime 扫描 manifest 决定加载策略，避免 import-time side effects。参见 `patterns/manifest-first-plugin.md`。

### Thin Gateway Protocol
数据优先、无环依赖的 RPC 协议设计。所有新方法/事件/字段只能添加（additive-only），不能删除或修改语义。参见 `patterns/gateway-control-plane.md`。

### Channel Adapter
将异构消息渠道统一为标准 inbound/outbound 接口的适配层。参见 `patterns/channel-adapter.md`。

### ACP (Agent Control Plane)
OpenClaw 的本地执行权限管理系统。提供 session-scoped approval、persistent bindings 和 tool-call-time policy enforcement。

### DM Pairing
个人 assistant 的设备配对安全模型。默认拒绝陌生人 DM，通过配对码机制授权。

### Memory Plugin Slot
同一时间只有一个 memory plugin 激活的设计模式。运行时可切换 memory backend。参见 `patterns/layered-memory.md` 的 Memory Plugin Slot 段落。

### Prepared Runtime Facts
启动时预计算频繁使用的运行时值（model refs, provider IDs, channel IDs），通过 context 传递避免 hot path 重复发现。参见 `patterns/prepared-runtime-facts.md`。

### Breadcrumb State Machine
每轮 AI 交互注入当前工作流状态的模式。Hook 读取 task status，提取对应状态块内容注入 prompt。参见 `projects/tool-platforms/trellis/breadcrumb-state-machine.md`。
