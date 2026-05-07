---
name: ai-agent-architecture
description: AI Agent 产品架构、哲学基础（有界理性/意向立场/BDI/元认知/价值对齐/具身认知）、认知架构（工作记忆/目标层级/推理模式/心智理论/元认知控制）、范式选择、运行时模块（9域25plane）、多模型异构架构、品类架构、表示层、现实接口、外部效果闭环、Research Agent、Coding Agent、多模态与 Computer Use、协议边界、引用链、交互设计、成本工程、多 Agent 协议、并发数据流、Prompt 与 Harness 集成、设计模式、反模式、经验教训、前沿专题、跨框架对照、演化机制（协同演化/价值漂移/退役）、主观性评估、starter kit、参考项目与评估知识库。当用户讨论 Agent 架构、Agent 哲学、认知架构、Agent 范式、Harness 工程、Agent Runtime、Research/Coding/Workflow/Browser/Companion/Creative Agent、工具设计、记忆系统、上下文压缩、执行深度、多 Agent 编排、多模型架构、MCP/A2A/AGENTS.md 边界、现实接口、效果验证、安全边界、交互体验、成本优化、并发调度、价值对齐、Agent 演化、评估回归时使用此 skill。
---

# AI Agent Architecture

一个 Agent 看上去能跑起来，不代表它能交付。模型选对了、工具接上了、Prompt 写得漂亮——但到了生产环境，输入稍有变化就误解任务，做了操作但现实没变，长任务中断后无法恢复，成本飙升，用户觉得既不可控也不可信。根源不在模型能力，而在于缺少系统化的架构视角：如何把表示、决策、行动、验证、交互和演化组织成完整闭环。

这个知识库为此而建。它不教你调 API，而是帮你回答：这类 Agent 该怎么设计、哪些模块不可省、哪些范式适合你的场景、生产级 Agent 需要哪些工程保障。

> **Evidence Status** — mixed. 内容来自参考项目分析、跨项目综合与架构抽象，部分经过实践验证，部分为理论框架。

> **Skill 定位**：这是 Agent 开发过程中的工具包与参照物，不是需要从头读完的教材，也不是框架仓库。`toolkit/` 和 `index/ai-routing-pack.md` 是低认知负荷入口；`starter-kit/`、`evaluation/eval-runner/` 和项目分析文件中的代码都只作为架构对象、边界和闭环的参考映射；不要求直接运行，也不代表生产实现。

## 默认入口

先读 `START-HERE.md`——按场景（构建、诊断、评审、AI 使用）分流到最短路径。

## 经典设计路径

1. **明确用户任务** → `categories/README.md`（选择品类）
2. **确定运行时深度** → `design-space/methodology/autonomy-and-depth.md`（自治等级）+ `design-space/methodology/minimum-viable-agent.md`（MVA 阶梯）
3. **选择品类蓝图** → `categories/<品类>/README.md`（完整架构模板）
4. **设计运行时域** → `architecture/README.md`（25 plane 总览）→ 相关 plane overview
5. **实现效果验证** → `architecture/planes/effects/overview.md` + `design-space/lessons-learned/tool-success-as-completion.md`
6. **接入评估** → `evaluation/README.md` → `evaluation/eval-runner/README.md`

## 经典诊断路径

1. **描述症状** → `design-space/anti-patterns/README.md`（匹配反模式）
2. **定位违反的边界** → `architecture/module-boundaries.md`（常见混淆）
3. **追溯到 Plane** → `architecture/plane-interaction-matrix.md`（交互矩阵定位耦合点）
4. **匹配哲学原则** → `concepts/foundations/PRINCIPLE-INDEX.md`（找到被违反的原则）
5. **查找修复模式** → `design-space/patterns/README.md`
6. **验证修复** → `evaluation/fixtures/README.md`（选择或创建 fixture）

---

> 以上两条路径覆盖最常见场景。哲学基础（`concepts/foundations/`）、认知架构（`cognitive-architecture/`）、范式理论（`paradigms/`）作为解释层，帮助理解"为什么这样设计"，不作为新手主入口。

## 核心公式

```text
Agent Product = f(User Job, World Representation, Runtime Capability, Evaluation)
Closed Loop   = Observe → Represent → Decide → Act → Verify → Update
```

公式的完整展开详见 [ARCHITECTURE.md](ARCHITECTURE.md#agent-产品公式)。

## 按层次导航

按角色推荐入口：

- **架构师**：`ARCHITECTURE.md` → `paradigms/README.md` → `architecture/plane-interaction-matrix.md` → `index/design-checklist.md`
- **实现者**：`categories/<type>/README.md` → `architecture/planes/<module>/overview.md` → `design-space/patterns/` → `starter-kit/README.md`
- **学习者**：`concepts/what-is-agent.md` → `concepts/foundations/README.md` → `cognitive-architecture/README.md` → `design-space/methodology/agent-product-model.md` → `categories/coding-agent/README.md`

知识树按七层纵深组织：

| 层次 | 问题 | 入口 |
|---|---|---|
| 哲学基础 | 为什么 Agent 架构必须是这样？ | `concepts/foundations/README.md` |
| 本体论 | Agent 是什么、边界是什么？ | `concepts/README.md` → `concepts/what-is-agent.md` |
| 认知架构 | Agent 的认知应该如何组织？ | `cognitive-architecture/README.md` |
| 范式论 | 有哪些根本不同的做法？ | `paradigms/README.md` → `index/paradigm-map.md` |
| 品类架构 | 某类 Agent 的完整设计是什么？ | `categories/README.md` → `categories/coding-agent/README.md` |
| 运行时 | 模块如何设计、交互、流转？ | `architecture/README.md` → `architecture/plane-interaction-matrix.md` |
| 证据与评估 | 真实项目、设计模式、评估验收 | `projects/README.md` → `evaluation/eval-framework.md` |
| 根目录项目反思 | 对照本地真实参考项目修正架构规则 | `synthesis/local-reference-systems-reflection.md` → `index/project-module-map.md` |
| 工具包 facade | 降低开发者和 AI 使用时的认知负荷 | `START-HERE.md` → `toolkit/README.md` |

## 按意图导航

完整意图导航（80+ 条）见 `index/intent-navigation.md`。AI 使用的最小路由见 `index/ai-routing-pack.md`。

## 问题诊断

导航表告诉你"往哪读"，但如果你是带着一个具体的 Agent 故障来的，下面这张速查表可能更直接。左列是你观察到的症状，右列指向应该深入的模块：

| 症状 | 可能原因 | 看哪里 |
|---|---|---|
| 只给建议不交付 | 执行深度不足 | `design-space/methodology/autonomy-and-depth.md` + `architecture/controllers/execution-depth/overview.md` |
| 不知道该用 ReAct 还是 Plan-and-Execute | 范式选择缺失 | `paradigms/reasoning-paradigms.md` |
| 输入一变就误解 | 表示层缺失、转换有损、来源不清 | `architecture/planes/representation/overview.md` |
| 做了工具调用但现实没变 | 缺少 postcondition、read-after-write 或 Effect Ledger（效果账本） | `architecture/planes/effects/overview.md` |
| 用户觉得不可控 | 缺交互层、中断策略或渐进授权 | `architecture/planes/interaction/overview.md` |
| 成本失控 | 缺模型路由、缓存、预算分配 | `architecture/planes/cost/overview.md` |
| 多 Agent 协作混乱 | 缺通信协议、共享状态、冲突仲裁 | `paradigms/collaboration-paradigms.md` + `architecture/planes/orchestration/communication.md` |
| 长任务中断后接不上 | 无 checkpoint 或 World State（世界状态快照）过期 | `architecture/planes/state/overview.md` + `architecture/planes/world-state/overview.md` |
| 工具失败后卡住 | 无恢复策略、超时/取消语义不清 | `architecture/planes/recovery/overview.md` + `architecture/planes/concurrency/overview.md` + `evaluation/failure-taxonomy.md` |
| 做了但没验证 | 缺 Verification Gate（验证关卡）或 effect verification | `design-space/patterns/self-verification.md` |
| 上下文满后质量下降 | Context Rot（上下文腐化），缺 Prompt/Context 分层 | `architecture/planes/prompting/overview.md` + `architecture/planes/context/overview.md` |
| 研究报告有来源但说不清哪句对应哪条证据 | Citation Chain（引用链）缺失 | `design-space/patterns/citation-chain.md` + `categories/research-agent/representation.md` |
| 网页/桌面自动化点击成功但用户任务没成功 | GUI 验证只看单通道 | `design-space/patterns/dual-channel-gui-verification.md` + `architecture/planes/effects/gui-verification.md` |
| 记忆不准确 | 写入策略、失效策略或 provenance 缺失 | `paradigms/memory-paradigms.md` + `architecture/planes/memory/overview.md` |
| 外部内容带偏 Agent | 工具输出注入、RAG 污染、信任边界不清 | `architecture/planes/security/overview.md` |
| Agent 越权删除生产数据 | 权限过粗、无破坏性操作确认门 | `design-space/lessons-learned/runaway-deletion.md` |
| 多 Agent 成本失控 | 循环检测缺失、成本上限为软告警 | `design-space/lessons-learned/agent-cost-explosion.md` |
| 记忆被外部注入篡改 | 记忆写入无来源验证 | `design-space/lessons-learned/memory-injection-attack.md` |
| Companion 人格漂移 | 人格只靠 system prompt，无独立锚定 | `design-space/lessons-learned/persona-drift-in-companions.md` |
| 第三方工具诱导 Agent 越权 | 身份、能力边界或委托链缺失 | `architecture/planes/identity-capability/overview.md` |
| 执行越深但失败越难收敛 | 缺 FailureRecord、retry budget 和 compensation | `architecture/planes/recovery/overview.md` |
| 评估停留在概念层 | 缺 mock world、trace replay、shadow mode | `evaluation/testability-design.md` + `evaluation/eval-runner/README.md` |
| 评估体系自身可信度不清 | 缺覆盖率分析、漂移检测、有效性回测 | `evaluation/eval-meta/README.md` |
| 用户不理解 Agent 为什么这样做 | 缺决策解释、置信度自然语言表达 | `architecture/planes/explainability/overview.md` |
| 长任务中意图偏移 | 缺意图漂移检测、对齐频率控制 | `architecture/planes/interaction/intent-alignment.md` |
| 不知道值不值得用 Agent | 缺 ROI 判断、任务适用性评估 | `design-space/methodology/agent-economics.md` |
| 运行中应该换策略但卡在原范式 | 缺动态范式切换触发条件 | `paradigms/paradigm-routing.md` |
| 上线后时好时坏 | 缺配置指纹、回归评估、canary | `architecture/planes/operations/overview.md` |
| Agent 自主删除生产数据 | 无硬性不可逆操作阻断、权限过大 | `design-space/lessons-learned/pocketos-9-second-deletion.md` |
| 评估分数高但生产表现差 | 基准被 Reward Hacking 攻破 | `evaluation/benchmark-trust-crisis.md` |
| 推理模型成本失控 | 缺 budget 管理、推理深度无上限 | `paradigms/reasoning-model-integration.md` + `architecture/planes/cost/paradigm-cost-benchmarks.md` |

## 结构概览

```text
ARCHITECTURE.md          ← 顶层架构入口：主干、闭环、域分组、数据资产
concepts/                ← 稳定概念：Agent、表示与效果、认识论、术语
  foundations/           ← [NEW] 哲学基础：有界理性、意向立场、BDI、元认知、价值对齐、具身认知
cognitive-architecture/  ← [NEW] 认知架构层：工作记忆、目标层级、推理模式、心智理论、元认知控制
paradigms/               ← 范式层：推理、记忆、工具、协作、控制、方法论
categories/              ← 各品类 Agent 的完整设计（12 个品类，含 Creative Agent）
architecture/            ← 通用运行时架构
  planes/                ← 24 个运行时 plane（按 9 个域分组，见 ARCHITECTURE.md）
  cross-cutting/       ← [NEW] 交叉地带：Memory×Security、Paradigm×Cost、Reasoning×ToolUse 等 6 篇
  multi-model/           ← [NEW] 多模型架构：角色分配、置信度聚合、世界模型、神经-符号混合
  evolution/             ← [NEW] 演化期：协同演化、价值漂移、生态协议、退役机制
  learning/              ← 经验固化与技能治理
design-space/            ← 设计原则、模式、反模式、前沿观察
  lessons-learned/       ← [NEW] 已知失败的设计——经验教训档案
guides/                  ← 端到端实践指南：从知识库到完整 Agent 构建
starter-kit/             ← 参考代码骨架（概念映射，非生产代码）
projects/                ← 真实项目的学习笔记和分析
synthesis/               ← 跨项目横向比较、趋势判断
evaluation/              ← 评估框架、runner、失败分类、主观性评估
index/                   ← 主干地图、范式地图、成熟度阶梯、意图导航、checklist
meta/                    ← skill 使用规则、模板、审计
```

## Provenance / Trust 规则

阅读知识库中的任何文件时，先留意文件顶部的 `Evidence Status` 标记。它告诉你这份内容的可信程度：

| 标记 | 含义 | 引用建议 |
|---|---|---|
| production-validated | 在至少 2 个生产系统观察到，可直接采用 | 可作为设计依据 |
| prototype-validated | 在 1 个生产或多个原型观察到 | 可采用，但需在自己的场景验证 |
| grounded | 已从参考项目提炼，有代码或文档证据 | 可作为参考，注意上下文差异 |
| synthesized | 跨项目抽象，未直接观察到完整组合 | 需要实践验证后再确认 |
| mixed | 部分来自实践，部分统一抽象 | 区分哪些部分有证据、哪些是推断 |
| theoretical | 理论框架，有学术或逻辑支撑但未在 Agent 生产中验证 | 作为思考工具，不作为实现规范 |
| speculative | 前沿猜测或探索性设计 | 仅作为灵感，不作为决策依据 |

不要把 theoretical/speculative 内容当作已被现实验证的事实。关键 claim 要回到 observation、effect record、World State snapshot 或项目证据。

> 注：历史文件中的 `draft` 标记等价于 `theoretical`，会逐步迁移。
