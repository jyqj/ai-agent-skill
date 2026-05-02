# Architecture Blueprint

> **Evidence Status** — synthesized. 参考项目中 runtime、tooling、memory、context、state、security、evaluation 的共同结构；本知识库对 Agent 系统的五层职责拓扑。

## 1. Canonical Topology

```text
External Reality
  ├─ users / teams
  ├─ files / repos / browsers / databases / APIs
  ├─ logs / metrics / sensors / devices
  └─ other agents
        ↓
[1] Intake & Representation
        ↓
[2] Cognition & Continuity
        ↓
[3] Action & Effect
        ↓
[4] Interaction & Collaboration
        ↓
[5] Recovery / Update / Evaluation
        ↕
[Cross-cutting] Governance & Evolution
```

治理不是最后一步，而是横切层：Control、Security、Identity & Capability、Recovery、Cost、Observability、Operations、Learning、Evaluation 会覆盖所有关键边界。

## 2. 各层职责

| 层 | 负责 | 不负责 | 关键产物 |
|---|---|---|---|
| Intake & Representation | 采集输入、保留原始引用、构建表示、标注信任和时效 | 做最终决策 | RawInputRef、Observation |
| Cognition & Continuity | Prompt、Context、Kernel、Memory、Task State、World State | 绕过工具直接行动 | ContextPack、Decision、Checkpoint、WorldStateSnapshot |
| Action & Effect | 工具调用、执行宿主、外部效果、验证 | 决定是否越权执行 | ToolCall、ExecutionResult、EffectRecord |
| Interaction & Collaboration | 人机交互、多 Agent 通信、并发、数据流 | 替代安全和业务策略 | InteractionEvent、AgentMessage、FlowRun |
| Recovery / Update / Evaluation | 失败分类、补偿、状态更新、验收判断 | 伪造业务成功 | FailureRecord、TaskCheckpoint、EvalResult |
| Cross-cutting Governance | 权限、身份、安全、成本、观测、运维、学习 | 作为事后装饰 | CapabilityGrant、PolicyVerdict、TraceEvent、CandidateRecord |

## 3. 依赖方向

```text
Interface → Representation → Context → Kernel
Kernel → Control → Tools → Execution → Effects → Verification
Verification → Effects / State / World State / Memory / Trace
Failure → Recovery → State / World State / Effects / Interaction
Interaction ↔ Kernel / Control / State
Orchestration ↔ Kernel / World State / Effects
Identity / Control / Security / Cost / Observability / Operations 横切所有关键调用
```

## 4. 禁止依赖

| 禁止 | 为什么 | 正确做法 |
|---|---|---|
| Kernel 直接执行系统命令 | 无权限、无 trace、无 effect | 通过 Tool Runtime + Execution Host |
| Context 当作状态库 | 上下文可丢失、可压缩 | 用 TaskCheckpoint / MemoryRecord |
| Memory 当作当前现实 | 记忆可能过期 | 用 WorldStateSnapshot 刷新 |
| Tool result 直接当完成 | success 不等于 effect verified | 写 EffectRecord 并验证 |
| Tool output 当系统指令 | 外部内容可注入攻击 | 放入 untrusted lane |
| 人类审批当作全部交互 | 用户还需要教学、纠错、进度、拒绝解释 | 建 Interaction Plane |
| 多 Agent 只靠自然语言委派 | 无协议、无边界、难仲裁 | 使用 AgentMessage / OutputContract |
| 成本只在账单里看 | 设计期不控制会失控 | 建 ResourcePlan / cost gate |
| 失败只靠重试 | 会放大风险和成本 | FailureRecord + retry budget + recovery gate |
| 第三方能力当本地授权 | confused deputy / 越权 | CapabilityGrant + trust lane + policy gate |

## 5. 单一事实来源

| 问题 | 单一事实来源 |
|---|---|
| 原始输入是什么？ | RawInputRef |
| 当前模型看见了什么？ | ContextPack |
| 当前指令结构是什么？ | PromptContract |
| 当前任务进展到哪里？ | TaskCheckpoint |
| 外部对象最后一次被观察到是什么状态？ | WorldStateSnapshot |
| 工具是否执行？ | ExecutionResult |
| 现实效果是否发生？ | EffectRecord + VerificationResult |
| 用户是否批准、纠错或教学？ | InteractionEvent |
| 多 Agent 冲突如何处理？ | ConflictRecord / ArbitrationDecision |
| 成本预算如何使用？ | ResourcePlan + CostTrace |
| 某个结论凭什么成立？ | Claim Evidence / Observation provenance |
| 当前行为由什么配置产生？ | ConfigFingerprint / TraceEvent |
| 谁授权 Agent 做这个动作？ | CapabilityGrant / AuditContext |
| 失败如何恢复或停止？ | FailureRecord / RecoveryPlan |

## 6. 成熟度阶梯

完整复杂度分级见 `complexity-levels.md`。本表是运行时成熟度的快速读法：

| 等级 | 特征 | 适用 |
|---|---|---|
| A0 Chat Wrapper | 无状态、无工具、无验证 | 低风险问答 |
| A1 Tool Assistant | 有工具 schema，但弱状态弱验证 | 简单自动化 |
| A2 Stateful Agent | 有 checkpoint、context、memory | 长任务、代码任务 |
| A3 Effect-aware Agent | 有 world state、effect ledger、read-after-write | 企业工作流、写外部系统 |
| A4 Governed Agent | 有 trust boundary、eval、canary、incident response | 生产环境、多租户、高风险任务 |
| A5 Adaptive Agent | 有受控学习、skill 治理、回归门禁 | 长期演进型平台 |

## 7. 和目录的对应关系

```text
ARCHITECTURE.md                         # 顶层入口
architecture/blueprint.md               # 本文件：分层拓扑
architecture/lifecycle.md               # 任务生命周期
architecture/runtime-data-model.md      # 数据资产和 schema
architecture/runtime-data-flow.md       # 数据流、触发关系和生命周期
architecture/module-boundaries.md       # 模块边界和反模式
architecture/plane-interaction-matrix.md # plane 读写/gate/耦合矩阵
architecture/complexity-levels.md       # C0-C6 复杂度等级
architecture/reference-topologies.md    # 不同复杂度的 Agent 拓扑
architecture/planes/*/overview.md       # 各模块细节
```
