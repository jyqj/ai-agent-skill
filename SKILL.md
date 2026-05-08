---
name: ai-agent-architecture
description: AI Agent 产品架构、哲学基础、认知架构、范式选择、运行时模块、品类设计、工具与权限、上下文与记忆、执行深度、多 Agent 编排、评估回归、真实项目对照和 reference-only starter kit。当用户讨论 Agent 架构、Harness 工程、Agent Runtime、工具设计、记忆系统、上下文压缩、执行深度、效果验证、安全边界、多模型、多 Agent、Agent 评估或 Agent 产品化时使用此 skill。
---

# AI Agent Architecture

Agent 不是“模型 + 工具”。它接收现实的表示，在权限、成本、时间窗口和模型能力约束下做决策，再通过工具、接口和人机协作影响外部世界。设计 Agent，就是设计这条链路的边界、证据、权限、状态和验收。

> **Evidence Status** — mixed. 内容来自参考项目分析、跨项目综合与架构抽象；部分已由本地项目和 fixture 验证，部分仍是理论框架。

> **Skill 定位**：这是 Agent 开发的架构参照和评审工具，不是生产框架。`starter-kit/`、`evaluation/eval-runner/` 和项目分析中的代码只用于解释架构对象、边界和闭环；采用前必须按真实接口、安全、测试和运维要求重写。

任务分流见 [START-HERE.md](START-HERE.md)。本文只作为 AI 加载用速查卡；完整主干见 `index/mainline-map.md`。

## 核心判断

```text
Agent Product = f(User Job, World Representation, Runtime Capability, Evaluation)
Closed Loop   = Observe → Represent → Decide → Act → Verify → Update
```

不可违反的 6 条原则：

| 原则 | 落到运行时 | 验收方式 |
|---|---|---|
| 表示先于推理 | `Observation.raw_refs / transform_chain / confidence / freshness / trust` | 关键结论可回查原始来源 |
| 行动必须经有边界的接口 | `ToolCall / CapabilityGrant / PolicyVerdict` | 写动作经过 schema、权限和审计 |
| 工具成功不等于世界成功 | `ExecutionResult` 与 `EffectRecord` 分离 | readback / test / external ack |
| 状态必须外置且可恢复 | `TaskCheckpoint / DecisionLog / pending_effects` | 中断后能继续，不靠模型记忆 |
| 不确定性是一等对象 | `blocked / pending / partially_verified / unverifiable_by_agent` | 最终交付不伪装已验证 |
| 从最小闭环开始 | MVA、risk、depth、eval 共同决定模块 | 无失败信号不引入重模块 |

## 常见故障入口

| 症状 | 先看哪里 |
|---|---|
| 只给建议不交付 | `toolkit/mva-planner.md`、`architecture/controllers/execution-depth/overview.md` |
| 输入一变就误解 | `architecture/planes/representation/overview.md` |
| 工具 success 但任务没完成 | `architecture/planes/effects/overview.md`、`synthesis/tool-effect-verification.md` |
| 长任务中断后接不上 | `architecture/planes/state/overview.md`、`synthesis/runtime-vs-world-state.md` |
| 上下文满后质量下降 | `architecture/planes/context/overview.md` |
| 记忆越来越不准 | `architecture/planes/memory/overview.md`、`synthesis/context-memory-state-boundaries.md` |
| 外部内容带偏 Agent | `architecture/planes/security/overview.md`、`design-space/patterns/untrusted-context-boundary.md` |
| 权限、审批、沙箱混乱 | `architecture/planes/control/overview.md`、`architecture/planes/identity-capability/overview.md` |
| 多 Agent 协作混乱 | `architecture/planes/orchestration/overview.md` |
| 上线后行为漂移 | `architecture/planes/operations/overview.md`、`evaluation/eval-framework.md` |
| Agent 执行了但不是用户想要的结果 | `architecture/planes/interaction/overview.md`（用户意图歧义） |
| Agent 在该请求帮助时没有请求 | `paradigms/control-paradigms.md`（HITL vs HOTL） |

## 最短路径

| 任务 | 路径 |
|---|---|
| 新建 Agent | `START-HERE.md` → `toolkit/choose-agent-type.md` → `toolkit/mva-planner.md` |
| 设计运行时 | `architecture/README.md` → `architecture/runtime-data-model.md` → `architecture/runtime-data-flow.md` |
| 做设计评审 | `toolkit/review-checklist.md` → `index/design-checklist.md` |
| 对照真实项目 | `projects/README.md` → `synthesis/local-agent-runtime-practices.md` |
| 做评估 | `toolkit/eval-planner.md` → `evaluation/README.md` |
| 查完整主干 | `index/mainline-map.md` |

## Provenance / Trust 规则

阅读任何文件时先看顶部 `Evidence Status`：

| 标记 | 含义 | 使用方式 |
|---|---|---|
| production-validated | 至少 2 个生产系统观察到 | 可作为强设计依据 |
| prototype-validated | 1 个生产或多个原型观察到 | 可采用，但需场景验证 |
| grounded | 来自参考项目代码或文档证据 | 可参考，不要照搬 |
| synthesized | 跨项目抽象 | 先当设计假设 |
| mixed | 实践与抽象混合 | 区分证据和推断 |
| theoretical | 理论或哲学框架 | 用于解释，不直接当实现规范 |
| speculative | 前沿猜想 | 只作灵感 |

不要把 theoretical / speculative 当成现实验证结论。关键 claim 要能回到 raw reference、effect record、World State snapshot、trace 或项目证据。
