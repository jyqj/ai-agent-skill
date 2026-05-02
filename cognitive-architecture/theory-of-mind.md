# 心智理论——与人和 Agent 协作时的对方建模

> **Evidence Status** — mixed. 心智理论（ToM）来自发展心理学和社会认知科学，Agent 中的应用映射为工程实践推导。

## 1. 为什么需要这篇

Agent 不是孤立运行的——它需要与用户协作、与其他 Agent 协作。有效协作的前提是理解对方的**信念、意图和知识状态**。一个不理解用户知识水平的 Agent 会给专家讲基础知识（浪费时间）或给新手抛术语（无法理解）。一个不理解 Worker Agent 能力边界的 Orchestrator 会分配不可能完成的任务。

心智理论（Theory of Mind, ToM）是认知科学中描述这种能力的概念：理解他人有不同于自己的信念、意图和知识状态。

## 2. Agent 的两种 ToM 需求

### 2.1 对用户的 ToM

Agent 需要建模用户的：

| 维度 | 问题 | 影响 |
|---|---|---|
| 知识水平 | 用户是否了解这个技术栈？ | 决定解释的详细程度 |
| 意图 | 用户真正想要什么？ | 字面执行 vs 意图理解 |
| 期望 | 用户期望什么样的交付物？ | 输出的格式和范围 |
| 容忍度 | 用户能接受多少不确定性？ | 何时报告 vs 何时自主决策 |
| 上下文 | 用户处于什么场景中？ | 紧急修复 vs 从容开发的策略差异 |

### 2.2 对其他 Agent 的 ToM

在多 Agent 系统中，Orchestrator 需要建模 Worker 的：

| 维度 | 问题 | 影响 |
|---|---|---|
| 能力边界 | Worker 能处理什么类型的任务？ | 任务分配策略 |
| 当前状态 | Worker 正在做什么？进度如何？ | 等待/催促/重分配 |
| 世界模型 | Worker 对外部环境的理解是否与 Orchestrator 一致？ | 是否需要同步信息 |
| 可靠性 | Worker 在什么条件下可能失败？ | 容错和重试策略 |

## 3. 对用户的 ToM 在 Agent 中的体现

### 3.1 渐进式披露（Progressive Disclosure）

根据用户的知识水平调整信息密度。

```text
新手用户：
  "这个错误是因为 Python 的虚拟环境没有激活。
   虚拟环境是一种隔离机制，确保项目之间的依赖不互相干扰。
   运行 `source venv/bin/activate` 来激活它。"

专家用户：
  "venv 未激活。`source venv/bin/activate`。"
```

实现要点：

- 用户知识水平不是固定标签，而是按领域变化的——一个人可能是 Python 专家但 Docker 新手
- 通过用户的提问方式、术语使用和反馈推断知识水平
- 宁可稍多解释也不要让用户困惑——缺失信息的代价大于冗余信息的代价

### 3.2 信任升级（Trust Escalation）

基于用户行为模式逐步调整授权级别。

```text
Level 0: 每个操作都请求确认
Level 1: 只有写操作请求确认
Level 2: 只有高风险操作请求确认
Level 3: 用户明确授权后自主执行
```

信任升级的 ToM 基础：通过观察用户的响应模式（总是说"继续"→ 可以减少确认）推断用户的控制偏好。

### 3.3 意图推断 vs 字面执行

用户说"删除这个文件"可能是：

| 字面意思 | 可能的真实意图 | ToM 推断依据 |
|---|---|---|
| 删除文件 | 清理构建缓存 | 文件在 build/ 目录下 |
| 删除文件 | 撤销错误修改 | 文件最近刚被修改 |
| 删除文件 | 就是删除文件 | 用户明确说"永久删除" |

Agent 应该在以下条件下追问而不是直接执行：

- 操作不可逆
- 字面意思与上下文推断的意图不一致
- 操作影响范围超出明显意图

### 3.4 认知负载管理

不要同时抛出太多信息或请求。

```text
差：
  "我发现了 3 个 bug、2 个性能问题和 1 个安全漏洞。
   Bug 1 是... Bug 2 是... Bug 3 是...
   你想先修哪个？还是全部修？要不要我同时重构？"

好：
  "我发现了 6 个问题，按优先级排：
   1. [安全] SQL 注入风险 — 建议立即修复
   你想先处理这个吗？其他问题可以在修复后再逐个讨论。"
```

原则：每次交互传递一个核心信息和一个明确的下一步行动。

## 4. 对其他 Agent 的 ToM

### 4.1 能力模型

Orchestrator 应维护 Worker Agent 的能力描述：

```text
worker_coding:
  can_do: [code_edit, test_run, lint, refactor]
  cannot_do: [database_migration, infrastructure_change]
  constraints: [max_file_size: 10000 lines, no_binary_files]

worker_research:
  can_do: [web_search, document_read, summarize]
  cannot_do: [code_edit, file_write]
  constraints: [max_sources: 20]
```

如果 Orchestrator 分配了 Worker 能力范围外的任务，不是 Worker 的失败，而是 Orchestrator 的 ToM 失败。

### 4.2 状态模型

Orchestrator 需要追踪 Worker 的执行状态，而不是"发出任务就忘"。

- Worker 是否已开始？
- 进度如何？
- 是否遇到阻塞？
- 是否产生了可以被其他 Worker 使用的中间产物？

### 4.3 共享世界模型

Agent 之间对外部世界的理解是否一致。

```text
问题场景：
  Orchestrator 认为文件 A 存在（因为 10 分钟前检查过）
  Worker 尝试读取文件 A 但发现它已被另一个 Worker 删除
  → 世界模型不同步
```

解决方案：

- 关键状态通过共享的 World State 同步
- Worker 在操作前验证前提条件（refresh before act）
- 状态冲突时向 Orchestrator 报告而不是自行假设

## 5. 与知识库的映射

| 知识库组件 | ToM 角色 | 设计影响 |
|---|---|---|
| Interaction Plane | 对用户 ToM 的运行时实现 | 渐进式披露、认知负载管理 |
| Orchestration Plane | 对 Agent ToM 的运行时实现 | 能力模型、状态追踪、世界模型同步 |
| Explainability Plane | 基于用户知识水平选择解释策略 | 解释的详细程度和技术深度 |
| progressive-disclosure pattern | ToM 驱动的交互模式 | 按用户知识水平调整信息密度 |
| trust-escalation pattern | ToM 驱动的授权模式 | 基于行为推断控制偏好 |
| worker-orchestration pattern | 多 Agent ToM 的实现 | Worker 能力边界和状态追踪 |

## 6. 设计启发

### 6.1 ToM 不需要完美

Agent 不需要完美理解用户的内心——它需要的是：

- 有一个**可更新的模型**，而不是固定假设
- 在不确定时**倾向于保守**（多解释、多确认）
- 通过**反馈循环**持续修正模型

### 6.2 ToM 失败的信号

| 信号 | 可能的 ToM 问题 |
|---|---|
| 用户反复要求解释同一概念 | Agent 高估了用户知识水平 |
| 用户说"直接做就行" | Agent 过度确认，低估了用户信任 |
| Worker 频繁报告无法执行 | Orchestrator 高估了 Worker 能力 |
| 用户修改了 Agent 的输出格式 | Agent 误判了用户的期望格式 |

### 6.3 检查清单

```text
Agent 是否根据用户的知识水平调整了解释深度？
高风险操作是否考虑了用户可能的真实意图？
每次交互的信息量是否可控（不超载）？
Orchestrator 是否维护了 Worker 的能力模型？
Agent 之间是否有世界模型同步机制？
ToM 模型是否有反馈更新路径？
```

## 7. 延伸阅读

- Premack, D. & Woodruff, G. (1978). "Does the chimpanzee have a theory of mind?" -- ToM 概念的起源
- Kosinski, M. (2023). "Theory of Mind May Have Spontaneously Emerged in Large Language Models" -- LLM 中的 ToM 能力
- `architecture/planes/interaction/trust-escalation.md` -- 信任升级的运行时实现
- `architecture/planes/orchestration/overview.md` -- 多 Agent 编排
- `design-space/patterns/progressive-disclosure.md` -- 渐进式披露模式
- `design-space/patterns/worker-orchestration.md` -- Worker 编排模式
