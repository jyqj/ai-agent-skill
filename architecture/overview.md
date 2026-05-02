# Agent Runtime Overview

> **Evidence Status** — grounded. 基于 Claude Code、Codex、OpenCode、Augment、Hermes、Nocturne、MemPalace 等项目的 runtime 实现归纳。

## 1. 汇总运行时图

```text
External Reality
  User · File · Browser · API · DB · Log · Sensor · Device · Other Agent
       │
       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Intake & Representation                                                     │
│ Interface Gateway → Perception Adapter → Representation Builder              │
│ produces: RawInputRef · PerceptionEvent · Observation                        │
└──────┬──────────────────────────────────────────────────────────────────────┘
       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Cognition & Continuity                                                       │
│ Prompting · Context · Kernel · Memory · Task State · World State             │
│ produces: PromptContract · ContextPack · Decision · Checkpoint · Snapshot    │
└──────┬──────────────────────────────────────────────────────────────────────┘
       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Governance Gate                                                              │
│ Identity · Control · Security · Cost · Approval · Budget · Trust Lane        │
│ produces: CapabilityGrant · PolicyVerdict · SecurityVerdict · ResourceDecision│
└──────┬──────────────────────────────────────────────────────────────────────┘
       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Action & Effect                                                              │
│ Tool Runtime → Execution Host → Effect Ledger → Verification                 │
│ produces: ToolCall · ExecutionResult · EffectRecord · VerificationResult     │
└──────┬──────────────────────────────────────────────────────────────────────┘
       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Interaction & Collaboration                                                  │
│ Human Interaction · Orchestration · Concurrency · Dataflow                   │
│ produces: InteractionEvent · AgentMessage · FlowRun · CancellationEvent      │
└──────┬──────────────────────────────────────────────────────────────────────┘
       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Recovery / Update / Evolution                                                │
│ FailureRecord · State Update · World Refresh · Trace · Eval · Learning · Ops │
└──────┬──────────────────────────────────────────────────────────────────────┘
       ├── continue loop
       └── deliver: User Response / Artifact / Verified External Effect
```

## 2. 运行时主流程

```text
1. Interface 接收用户请求或外部事件，生成 RawInputRef。
2. Representation Builder 解析原始输入，生成 Observation。
3. Depth Controller 根据任务、风险和交付物选择 required_depth。
4. Prompting 生成 PromptContract，Context 生成 ContextPack。
5. Kernel 基于 ContextPack 生成 Decision。
6. Identity / Control / Security / Cost 做身份、权限、安全、预算、信任边界和审批检查。
7. Tool Runtime 将允许的 Decision 转成 ToolCall，并交给 Execution Host。
8. Execution Result 进入 Observation Normalizer 和 Effect Ledger。
9. Verification Gate 检查结构、执行、现实效果和最终 claim。
10. Recovery Plane 对失败、部分效果、超时、过期状态和预算耗尽做分类与处理。
11. Interaction / Orchestration / Concurrency / Dataflow 处理用户、Agent 和流式协作。
12. State / World State / Memory / Trace / Eval 更新。
13. Stop Gate 判断交付、继续、恢复、补偿、请求人工或部分完成。
```

## 3. 关键分离原则

| 分离 | 原因 | 入口 |
|---|---|---|
| Interface 与 Representation | 入口适配不同于输入解释 | `module-boundaries.md` |
| Prompting 与 Context | 指令结构不同于当前事实窗口 | `planes/prompting/overview.md` |
| Task State 与 World State | 任务进度不等于外部对象状态 | `planes/state/overview.md`、`planes/world-state/overview.md` |
| Execution Success 与 Effect Success | 命令成功不代表现实已改变 | `planes/effects/overview.md` |
| Approval 与 Interaction | 审批不是人机交互全部 | `planes/interaction/overview.md` |
| Orchestration 与 Concurrency | 分工协议不同于并发控制 | `planes/orchestration/overview.md`、`planes/concurrency/overview.md` |
| Eval 与 Testability | 评分维度不同于可执行测试 | `../evaluation/testability-design.md` |
| Cost Trace 与 Cost Control | 事后统计不同于运行时预算策略 | `planes/cost/overview.md` |
| Identity 与 Capability | 谁发起不同于能做什么 | `planes/identity-capability/overview.md` |
| Failure 与 Recovery | 失败事实不同于恢复策略 | `planes/recovery/overview.md` |

## 4. Stop Gate

成熟 Agent 的停止条件：

```text
required_depth reached
+ deliverables present
+ key observations trustworthy enough
+ prompt/context did not omit critical constraints
+ key world state fresh enough
+ required effects verified or explicitly blocked
+ high-risk actions approved or not executed
+ unresolved uncertainty surfaced
+ cost/risk/identity/recovery/interaction obligations satisfied
```

## 5. 各模块入口

见 `../index/architecture-map.md`。


## 6. 复杂度与交互矩阵

不要默认启用所有模块。先用 `complexity-levels.md` 判断 C0-C6 等级，再用 `reference-topologies.md` 选择拓扑。需要检查模块耦合时，用 `plane-interaction-matrix.md`；需要检查数据对象流转时，用 `runtime-data-flow.md`。
