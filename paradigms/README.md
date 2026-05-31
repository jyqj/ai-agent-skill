# Agent Paradigms

> **Evidence Status** — synthesized. `architecture/` 的运行时抽象、`projects/` 的参考实现、`design-space/` 的模式库。


## 这一层回答什么

`paradigms/` 回答范式选择问题：

```text
面对一个新 Agent 任务，应该选择哪种基本做法？
为什么用这种做法，而不是另一种？
这些做法如何组合到 ORDA-VU 闭环和五层运行时里？
```

范式层位于知识树中的第三层：

```text
concepts/foundations/       为什么 Agent 架构必须是这样（哲学基础）
  ↓
concepts/                   Agent 是什么、边界是什么
  ↓
cognitive-architecture/     Agent 的认知应该如何组织（认知架构）
  ↓
paradigms/                  有哪些根本不同的构建思路、何时选哪种
  ↓
categories/                 某类 Agent 的完整品类架构
  ↓
architecture/               通用运行时模块、多模型架构、演化机制
  ↓
projects/                   真实项目中的实现证据
```

认知架构层（`cognitive-architecture/`）回答"Agent 的认知应该如何组织"，包括工作记忆动力学、目标层级、推理模式、心智理论、元认知控制。它是范式选择的认知科学基础：为什么需要区分演绎和类比推理、为什么目标冲突时需要层级优先、为什么 Agent 需要知道何时该反思何时该行动。

## 核心范式族

| 范式族 | 入口 | 主要问题 |
|---|---|---|
| 推理范式 | `reasoning-paradigms.md` | direct、ReAct、Plan-and-Execute、Reflection、ORDA-VU 什么时候用？ |
| 推理技术选择 | `reasoning-technique-selection.md` | CoT/ToT/ReAct/PAL/CoD/GoD/MASS/RLVR——给定任务特征选哪种？（从 cognitive-architecture/ 迁入） |
| 记忆范式 | `memory-paradigms.md` | in-context、RAG、Disclosure、分层记忆、图记忆如何取舍？ |
| 工具使用范式 | `tool-paradigms.md` | 静态工具、动态发现、MCP、code-as-tool、原子工具和丰富工具如何组合？ |
| 协作范式 | `collaboration-paradigms.md` | 单 Agent、Coordinator-Worker、Peer、Event-driven、Human-in-loop 如何选择？ |
| 控制范式 | `control-paradigms.md` | rule、LLM judge、hook、sandbox、verification gate 如何互补？ |
| 方法论 | `../design-space/methodology/` | Harness、产品画布、自治等级、执行深度、决策矩阵、MVA 阶梯 |
| 决策树 | `decision-trees.md` | 把范式选择从列表升级为可执行选择过程 |
| 自适应范式 | `adaptive-paradigm.md` | 运行时参数动态调整：模型路由、策略自适应、自改进闭环 |

## 范式选择总流程

```text
1. 定义交付物和外部效果
2. 判定任务深度：D0-D6
3. 判定动作风险：可逆性、影响范围、验证能力
4. 判定复杂度等级：C0-C6
5. 使用 `decision-trees.md` 选择推理、记忆、工具、协作和控制范式
6. 回到 category architecture，把范式落到具体对象、工具、状态和 eval
7. 用 `architecture/reference-topologies.md` 和 `index/design-checklist.md` 做架构评审
```

## ORDA-VU 的定位

ORDA-VU（Observe → Represent → Decide → Act → Verify → Update）是本框架推荐的**运行时闭环外壳**，不是排斥其他范式的唯一答案。

- ReAct 可以作为 ORDA-VU 中 Decide/Act 的细粒度循环。
- Plan-and-Execute 可以作为 Decide 阶段的规划器 + Act 阶段的执行器。
- Reflection 可以作为 Verify/Update 阶段的诊断与修订机制。
- RAG、Disclosure、Layered Memory 是 Represent/Context/Memory 的不同装配方式。
- Rule、Hook、Sandbox、LLM Judge 是 Act/Verify/Governance 的不同控制方式。

因此，范式选择的核心思路是：**用 ORDA-VU 组织闭环，再选择适合任务的局部范式填充每个阶段。**

## 什么时候不要上复杂范式

轻量级 Agent 不应该被生产级框架压垮。若满足以下条件，可以从最小闭环开始：

```text
低风险 + 可逆 + 用户实时在场 + 不需要跨会话状态 + 可人工验证
```

先读 `methodology/minimum-viable-agent.md`，从 MVA-0 / MVA-1 做起，再根据失败证据逐步加入 world state、effect ledger、memory、observability 和 operations。
