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
