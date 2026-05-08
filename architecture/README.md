# 通用运行时架构

> **Evidence Status** — synthesized. 多个参考项目对 runtime、tooling、memory、control、state、trace、execution 的实现；本知识库对 Agent 闭环、分层拓扑、数据资产和模块边界的整理。

## 架构入口

```text
../ARCHITECTURE.md                 # 顶层架构入口：主干 + 五层 + 闭环 + 数据资产
../paradigms/README.md             # 进入模块装配前先做范式选择
blueprint.md                       # 分层拓扑：各层职责、依赖方向、禁止依赖
lifecycle.md                       # 生命周期：intake → represent → decide → act → verify → update
runtime-data-model.md              # 运行时对象：Observation / PromptContract / ToolCall / EffectRecord 等
runtime-data-flow.md               # 对象流转、触发关系、生命周期和归档
module-boundaries.md               # 模块边界：职责、反模式、边界策略
plane-interaction-matrix.md        # plane 之间的读写、gate、强耦合和禁止耦合
complexity-levels.md               # C0-C6 复杂度等级与升级触发器
reference-topologies.md            # T0-T7 参考拓扑：按风险和执行深度选择模块组合
overview.md                        # 汇总运行时图：把上述内容落到 Agent Runtime
adrs/                              # 架构决策记录模板和示例
../starter-kit/README.md           # 从抽象映射到参考代码骨架（可选阅读）
```

## 核心架构

```text
External Reality
  → Intake & Representation
  → Cognition & Continuity
  → Action & Effect
  → Interaction & Collaboration
  → Governance & Evolution
```

## 模块分组

| 分组 | 包含模块 | 主要问题 |
|---|---|---|
| Intake & Representation | Interface、Representation | 现实如何被编码？表示是否可靠？ |
| Cognition & Continuity | Prompting、Context、Memory、State、World State | 如何决策、维持长任务、处理状态？ |
| Action & Effect | Tools、Execution、Effects | 动作如何执行？现实效果如何验证？ |
| Interaction & Collaboration | Interaction、Orchestration、Concurrency、Dataflow | 人、Agent、并发和数据流如何协同？ |
| Governance & Evolution | Control、Security、Identity & Capability、Recovery、Cost、Observability、Operations、Learning、Evaluation | 如何授权、防注入、控成本、恢复、回归、上线和学习？ |

### 为什么这样分组

五层分组对应 Agent 从"理解世界"到"改变世界"再到"约束自身"的递进关系，也决定了模块投入的优先级。

**认知前端（Intake & Representation + Cognition & Continuity）** 是 Agent 对现实的理解能力。Intake 把原始信号编码为带信任度和时效的表示，Cognition 在这些表示上组装上下文、维持任务状态、做出决策。如果表示不可靠或上下文组装有缺陷，后续所有动作都建立在错误基础上——这两层是系统正确性的地基。

**效果实现（Action & Effect）** 是 Agent 对外部世界的实际改变。工具调用、受控执行、效果验证构成从意图到现实的桥梁。这一层的质量直接决定 Agent 是否真正完成了任务，而不仅仅是"输出了看起来正确的文本"。

**约束与学习（Governance & Evolution + Interaction & Collaboration）** 是 Agent 的可信性和演化能力。权限控制、安全边界、成本预算、故障恢复保证 Agent 在约束内运行；审计、回归、经验提炼保证 Agent 能从错误中改进。

模块选择时应按这个顺序投入：先保证认知前端（表示和决策）的正确性，再建设效果实现层（工具和验证），最后补齐约束和学习。跳过前两层直接堆叠治理模块，等于在不稳定的地基上装护栏——护栏本身并不能让 Agent 做出正确决策。

## 与范式层的关系

`architecture/` 回答“模块如何设计”，`paradigms/` 回答“为什么选择这种做法”。例如：

| 架构模块 | 相关范式 |
|---|---|
| Prompting / Kernel | `../paradigms/reasoning-paradigms.md` |
| Memory / Context / World State | `../paradigms/memory-paradigms.md` |
| Tools / Execution / Effects | `../paradigms/tool-paradigms.md` |
| Orchestration / Concurrency | `../paradigms/collaboration-paradigms.md` |
| Control / Security / Identity / Recovery / Operations | `../paradigms/control-paradigms.md` |

## 与品类层的关系

通用模块是品类无关的。具体品类应在 `categories/<type>/` 中说明这些模块如何特化。例如 Coding Agent 的 Representation 不只是“表示层”，而是 RepoSnapshot、FileRef、SymbolRef、GitState、TestResult 等对象；详见 `../categories/coding-agent/representation.md`。


## 推荐补充入口

| 问题 | 文件 |
|---|---|
| 不确定一个 Agent 该做到多复杂 | `complexity-levels.md` |
| 不清楚模块之间该如何交互 | `plane-interaction-matrix.md` |
| 不清楚数据对象如何流转 | `runtime-data-flow.md` |
| 需要记录重大架构选择 | `adrs/adr-template.md` |
| 工具失败、部分效果和补偿事务 | `planes/recovery/overview.md` |
| 身份、租户、MCP capability 和 confused deputy | `planes/identity-capability/overview.md` |
| 时间约束、过期策略和因果关系 | `planes/time/overview.md` |

## 9 域 25 Plane 目录速查

| 域 | Plane | 目录 |
|---|---|---|
| 1. Sensing & Repr | Interface | `planes/interface/` |
| 1. Sensing & Repr | Representation | `planes/representation/` |
| 2. Cognition | Prompting | `planes/prompting/` |
| 2. Cognition | Context | `planes/context/` |
| 2. Cognition | Memory | `planes/memory/` |
| 2. Cognition | State | `planes/state/` |
| 3. World Modeling | World State | `planes/world-state/` |
| 3. World Modeling | Time | `planes/time/` |
| 4. Action & Effect | Tools | `planes/tools/` |
| 4. Action & Effect | Execution | `planes/execution/` |
| 4. Action & Effect | Effects | `planes/effects/` |
| 5. Trust & Identity | Identity & Capability | `planes/identity-capability/` |
| 5. Trust & Identity | Security | `planes/security/` |
| 6. Coordination | Interaction | `planes/interaction/` |
| 6. Coordination | Orchestration | `planes/orchestration/` |
| 6. Coordination | Concurrency | `planes/concurrency/` |
| 6. Coordination | Dataflow | `planes/dataflow/` |
| 7. Lifecycle | Cost | `planes/cost/` |
| 7. Lifecycle | Economics | `planes/economics/` |
| 7. Lifecycle | Operations | `planes/operations/` |
| 7. Lifecycle | Recovery | `planes/recovery/` |
| 8. Reflection | Observability | `planes/observability/` |
| 8. Reflection | Explainability | `planes/explainability/` |
| 8. Reflection | Learning & Adaptation | `planes/learning-adaptation/` |
| 9. Governance | Control | `planes/control/` |
