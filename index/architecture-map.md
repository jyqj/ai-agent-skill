# Architecture Map

> **Evidence Status** — synthesized. 跨项目观察归纳。


## 架构阅读路径

```text
ARCHITECTURE.md
  → index/mainline-map.md
  → paradigms/README.md
  → architecture/blueprint.md
  → architecture/lifecycle.md
  → architecture/runtime-data-model.md
  → architecture/runtime-data-flow.md
  → architecture/module-boundaries.md
  → architecture/plane-interaction-matrix.md
  → architecture/complexity-levels.md
  → architecture/reference-topologies.md
  → architecture/planes/*/overview.md
```

## 按问题查找

| 问题 | 入口 |
|---|---|
| 总体架构是什么？ | `../ARCHITECTURE.md` |
| 主干层级怎么走？ | `mainline-map.md` |
| 有哪些构建范式？ | `paradigm-map.md` |
| 模块怎么分层？ | `../architecture/blueprint.md` |
| 任务如何从输入流到交付？ | `../architecture/lifecycle.md` |
| 运行时对象有哪些？ | `../architecture/runtime-data-model.md` |
| 运行时对象如何流转？ | `../architecture/runtime-data-flow.md` |
| Plane 之间如何读写和 gate？ | `../architecture/plane-interaction-matrix.md` |
| Agent 该做到多复杂？ | `../architecture/complexity-levels.md` |
| 哪些模块边界不能混？ | `../architecture/module-boundaries.md` |
| 错误恢复和补偿怎么设计？ | `../architecture/planes/recovery/overview.md` |
| 身份和能力授权怎么设计？ | `../architecture/planes/identity-capability/overview.md` |
| 不同类型 Agent 应该选哪些模块？ | `../architecture/reference-topologies.md` |
| 具体模块怎么实现？ | `../architecture/planes/<module>/overview.md` |
| 交互怎么设计？ | `../architecture/planes/interaction/overview.md` |
| 成本怎么设计？ | `../architecture/planes/cost/overview.md` |
| 时间约束、过期和因果关系怎么管理？ | `../architecture/planes/time/overview.md` |
| 多 Agent 怎么协作？ | `../paradigms/collaboration-paradigms.md` → `../architecture/planes/orchestration/communication.md` |
| 多 Agent 治理怎么设计？ | `../architecture/planes/orchestration/governance.md` |
| Agent 间信任与归因怎么设计？ | `../architecture/planes/orchestration/trust-and-attribution.md` |
| 并发和流式任务怎么处理？ | `../architecture/planes/concurrency/overview.md`、`../architecture/planes/dataflow/overview.md` |
| Prompt 如何纳入 Harness？ | `../architecture/planes/prompting/overview.md` → `../paradigms/methodology/harness-engineering.md` |
| 怎么评审设计完整性？ | `design-checklist.md` |
| 怎么做评估和回归？ | `../evaluation/eval-runner/README.md` |
| 怎么评估 Agent 轨迹质量？ | `../evaluation/trajectory-evaluation.md` |
| 安全应该怎么分层防御？ | `../design-space/patterns/guard-model.md` |
| 高 stakes 任务如何用契约管理？ | `../design-space/patterns/contract-agent.md` |
| A2A/MCP/AP2 协议怎么选？ | `../design-space/frontier/agentic-commerce-and-protocols.md` |
| 记忆形态如何影响系统设计？ | `../design-space/frontier/memory-forms-and-dynamics.md` |
| 性能/成本优化从哪个技术开始？ | `../paradigms/methodology/performance-optimization.md` |

## 模块分组索引

| 分组 | 模块 | 入口 |
|---|---|---|
| Intake & Representation | Interface、Representation | `../architecture/planes/interface/overview.md`、`../architecture/planes/representation/overview.md` |
| Cognition & Continuity | Prompting、Context、Memory、State、World State | `../architecture/planes/prompting/overview.md`、`../architecture/planes/context/overview.md` |
| Action & Effect | Tools、Execution、Effects | `../architecture/planes/tools/overview.md`、`../architecture/planes/execution/overview.md`、`../architecture/planes/effects/overview.md` |
| Interaction & Collaboration | Interaction、Orchestration、Concurrency、Dataflow | `../architecture/planes/interaction/overview.md`、`../architecture/planes/orchestration/overview.md` |
| Governance & Evolution | Control、Security、Identity、Recovery、Cost、Time、Observability、Operations、Learning、Evaluation | `../architecture/planes/control/overview.md`、`../architecture/planes/security/overview.md`、`../architecture/planes/identity-capability/overview.md`、`../architecture/planes/recovery/overview.md`、`../architecture/planes/time/overview.md`、`../architecture/learning/overview.md` |

## 最小评审链

```text
1. 读 ARCHITECTURE.md 看总体闭环
2. 用 paradigms/ 选择推理、记忆、工具、协作、控制范式
3. 用 categories/ 确定品类特化对象和闭环
4. 用 complexity-levels.md 判断复杂度，reference-topologies.md 选拓扑
5. 用 runtime-data-model.md / runtime-data-flow.md 定义对象和流转
6. 用 module-boundaries.md / plane-interaction-matrix.md 查边界和耦合风险
7. 用 design-checklist.md 和 ADR 模板做最终评审
8. 用 evaluation/eval-runner 跑 fixture 和 trace 回归
```
