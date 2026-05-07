# Concepts

> **Evidence Status** — mixed. 保存 Agent 的稳定本体论、认识论和边界概念，部分经实践验证。

如果跳过概念层直接进入架构设计，团队很快会陷入术语混乱：一个人说的"Agent"是自主闭环系统，另一个人说的是带了工具的 Chatbot；一边在讨论"记忆"，另一边理解成了"上下文窗口"。概念不对齐，后续的架构选型、范式决策和评估标准都会在空中打转。

这个目录是整个知识树中最底层的一层，回答的是"Agent 到底是什么"这个根本问题。它不涉及具体的架构模块或实现细节，而是建立一组稳定的本体论（ontology）基础：什么算 Agent、什么不算，Agent 如何感知和影响现实，Agent 面对不确定性时的认识论（epistemics）立场是什么。这些概念一旦理清，后续在 `paradigms/`（范式选择）和 `architecture/`（模块设计）中做决策时，才有共同的语言基础。

## 主线阅读

建议按以下顺序阅读，每篇文档解答一个核心问题：

| 问题 | 文件 |
|---|---|
| Agent 是什么、和 Chatbot / Workflow / Copilot 的边界是什么？ | `what-is-agent.md` |
| Agent 如何通过表示和接口影响现实？ | `representation-and-effects.md` |
| Agent 如何处理不确定性、置信度和不知道自己不知道？ | `agent-epistemics.md` |
| 当 postcondition 不是终极标准时——审美/情感/创造性任务的验证 | `beyond-verification.md` |
| 术语表 | `glossary.md` |

## 哲学基础

`foundations/` 子目录回答更深一层的问题——"为什么 Agent 架构**必须**是这样"：

| 问题 | 文件 |
|---|---|
| 为什么 Harness 必然存在？ | `foundations/bounded-rationality.md` |
| "Agent 有目标"是什么意思？ | `foundations/intentional-stance.md` |
| ORDA-VU 的认识论根基是什么？ | `foundations/bdi-and-active-inference.md` |
| Agent 如何知道自己不知道什么？ | `foundations/metacognition.md` |
| 从"不该做什么"到"该做什么" | `foundations/value-and-alignment.md` |
| Agent 的"身体"是什么？ | `foundations/embodiment-and-situation.md` |

这些不是学术阅读材料，而是架构决策的哲学根基。一线开发者可以跳过，但做长程系统决策时建议回来看。

## 方法论已迁移

历史上本目录混入了方法论文档（如 Harness 工程、自治等级、决策框架等）。为保持层级清晰，`harness-engineering.md`、`autonomy-levels.md`、`decision-frameworks.md` 和 `agent-product-model.md` 已迁移到 `../design-space/methodology/` 目录，`design-principles.md` 迁移到 `../design-space/principles/core-design-principles.md`。历史文件仍保留以兼容旧链接，但新内容应优先写入迁移后的位置。
