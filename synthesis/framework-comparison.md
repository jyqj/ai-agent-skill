# Framework Comparison

> **Evidence Status** — synthesized. 基于 OpenAI Agents SDK / Swarm、LangGraph、CrewAI、AutoGen、Mastra 等官方文档，与本知识库的抽象层做映射。

## 定位

这篇文章不是框架评测，不比 API 细节。它回答一个问题：**如果你已经在用某个框架，这套知识库额外补的是什么？**

## 总览

| 框架 | 原生抽象中心 | 强项 | 常见盲点 | 本知识库补充的层 |
|---|---|---|---|---|
| **OpenAI Agents SDK** | hosted agent、tools、handoff、trace | 上手快、runtime 一体化 | 容易忽略品类特化的表示和效果模型 | categories、effects、evaluation |
| **Swarm** | minimal handoff / routines | 教学清晰、最小多 agent runtime | 生产控制面不够完整 | control、operations、eval、security |
| **LangGraph** | state graph、durable execution、checkpoint | 长任务、显式 state、human interrupt | 只看 graph 容易低估表示与效果验证 | representation、world-state、effects |
| **CrewAI** | agent / task / crew / flow | 角色协作、任务组织直观 | 角色好定义，但证据与信任通道常被弱化 | representation、security、evaluation |
| **AutoGen** | conversational agents、event-driven core | 多 agent 对话和事件驱动灵活 | 容易把 conversation 当成全部 state | state、world-state、control |
| **Mastra** | workflow、agents、memory、observability | workflow + agent 结合自然 | 品类闭环和评估仍需补齐 | categories、evaluation、effects |

## 术语映射

本知识库用了一套框架无关的术语。如果你更熟悉某个框架的概念，可以通过这张表做翻译：

| 本知识库 | OpenAI Agents SDK | LangGraph | CrewAI | AutoGen | Mastra |
|---|---|---|---|---|---|
| TaskEnvelope | run config / agent input | graph input state | task + flow input | message / task context | workflow input |
| ContextPack | model input + built-in tool context | graph state slice | task context | conversation state | workflow/agent context |
| EffectRecord | tool result + 需自行添加验证 | state update + post-step check | task outcome | event/result + custom verifier | step outcome + custom verifier |
| Checkpoint | session / trace / stored state | checkpoint / durable execution | flow state | event history / runtime state | workflow memory/state |

## 什么时候这套知识库特别有用

### 在框架里遇到生产问题时

常见信号：工具调用成功但现实没变、引用说不清来源、长任务做到一半断裂、多 agent 越来越乱、安全边界全靠 prompt 硬撑。

这时候通常不需要换框架，而是需要补上框架没有原生覆盖的层：`effects/`（效果验证）、`security/`（信任边界）、`categories/`（品类特化）、`evaluation/`（评估与回归）。

### 在做品类特化时

框架文档擅长回答"怎么搭 runtime"，但很少告诉你：Research Agent 的 claim/citation/freshness 怎么建模？Browser Agent 的 screenshot/DOM/effect verification 怎么设计？Coding Agent 的 diff/test/git state 怎么管理？这些是品类特有的设计问题，`categories/` 目录是专门回答这类问题的地方。

### 想从"框架熟练"升级到"架构清楚"时

框架 API 容易让人直接开始写节点或 agent，但 `categories/` + `patterns/` + `evaluation/` 会逼你回答更难的问题：这个系统处理的是哪类表示对象？什么才算 verified completion？哪些失败要进 regression？

## 结论

这套知识库提供三样框架未覆盖的东西：

1. **框架无关的架构语言** — 不管你用什么框架，design space 里的 patterns 和 principles 都适用
2. **品类特化的对象模型** — 框架告诉你怎么写 agent，categories 告诉你这类 agent 需要关注什么
3. **效果、安全和评估的工程纪律** — 这些是框架文档最容易省略，但生产上线后最容易出问题的部分
