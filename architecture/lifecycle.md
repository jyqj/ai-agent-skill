# Runtime Lifecycle

> **Evidence Status** — synthesized. 参考项目中 observe/query loop、tool execution、checkpoint、compaction、approval、recovery 的共同结构；本知识库将生产级 Agent 生命周期整理为 ORDA-VU 闭环。

## 1. 主生命周期

```text
0 Configure
1 Intake
2 Represent
3 Select Depth
4 Assemble Prompt & Context
5 Decide
6 Identity / Policy / Budget Gate
7 Act
8 Sense
9 Verify
10 Recover if needed
11 Interact / Collaborate if needed
12 Update
13 Deliver or Continue
```

简化主循环：

```text
Observe → Represent → Decide → Act → Verify → Update
```

## 2. 阶段表

| 阶段 | 输入 | 处理 | 输出 | 失败时 |
|---|---|---|---|---|
| Configure | runtime config、policy、tool schema、eval baseline | 校验并锁定运行约束，计算配置指纹 | ConfigFingerprint | 配置不完整则禁止启动 |
| Intake | user/event/webhook/sensor | 解析来源身份，提取 raw refs | RawInputRef、PerceptionEvent | 来源不明则降级或请求确认 |
| Represent | raw refs | parse、normalize、chunk、标注 trust/freshness | ObservationSet | 低置信度阻断高风险动作 |
| Select Depth | task、risk、intent | 评估风险等级，匹配执行深度与预算 | TaskGraph、DepthBudget | 风险不明则 conservative depth |
| Assemble Prompt & Context | observations、memory、state、world snapshot | 按 trust lane 拼装 PromptContract 与 ContextPack | PromptContract、ContextPack | 上下文不足则读取或刷新 |
| Decide | context pack、goal、budget | 推理并选定下一步动作 | Decision | 决策无 schema 则重试或降级 |
| Identity / Policy / Budget Gate | decision、identity、capability、policy、trust、risk、cost | 逐项核验身份、权限、策略、预算 | CapabilityGrant、PolicyVerdict | 拒绝、请求审批、改为只读 |
| Act | allowed tool call | 路由到 Execution Host 执行工具调用 | ExecutionResult | 按 failure mode 恢复 |
| Sense | execution result、readback | 归一化工具返回值，提取新观察 | Observation / EffectCandidate | 结果缺失则重读或标记 unknown |
| Verify | postconditions、tests、readback | 比对预期后置条件与实际效果 | VerificationResult | 失败则进入 recovery route |
| Recover | failure、partial effect、timeout、budget | 分类失败模式，执行补偿、回滚或升级 | FailureRecord、RecoveryAction | 无可恢复路径则停止并说明 |
| Interact / Collaborate | uncertainty、risk、delegation need | 路由到用户、审批者或协作 Agent | InteractionEvent、AgentMessage | 交互超时则按策略降级 |
| Update | verification、observations、decision | 聚合为 checkpoint，刷新 world state 与 effect ledger | UpdatedState | 状态冲突则暂停或刷新 |
| Deliver / Continue | stop gate | 判定 stop gate，交付结果或继续循环 | Deliverable | 不满足 stop gate 则继续 |

阶段间的时序约束和有效期管理详见 [Time Plane](planes/time/overview.md)。

## 3. 闭环粒度

ORDA-VU 可以嵌套在不同粒度中：

| 粒度 | 范围 | 典型使用 |
|---|---|---|
| Micro-loop | 单个工具调用 | ReAct / tool observation |
| Step-loop | 计划步骤 | Plan-and-Execute |
| Task-loop | 用户任务 | 大多数交付型 Agent |
| Session-loop | 多轮会话 | 用户纠错、持续协作 |
| System-loop | 持续运行 | Ops、平台、长期学习 |

## 4. 子循环

### 4.1 Representation Repair Loop

```text
low confidence / stale / lossy / conflict
  → fetch raw ref or alternative source
  → rebuild observation
  → compare with previous observation
  → continue or surface uncertainty
```

### 4.2 Effect Verification Loop

```text
execute write action
  → record intended_effect
  → read back target object
  → compare postcondition
  → verified / failed / pending / partially_verified
```

### 4.3 Human Interaction Loop

```text
uncertainty / risk / blocked action / teachable moment
  → choose interaction type
  → send minimal sufficient message
  → receive approval / correction / preference / refusal
  → update state or continue
```

### 4.4 Recovery Loop

```text
failure detected
  → classify failure mode
  → inspect new evidence
  → choose retry / repair / rollback / compensate / ask human / stop
  → update decision log
```

## 5. Stop Gate

```text
stop_candidate
  → deliverable check
  → representation check
  → prompt/context disclosure check
  → world-state freshness check
  → effect verification check
  → recovery state check
  → identity / authorization check
  → claim evidence check
  → interaction obligation check
  → cost/risk disclosure check
  → final response
```

| 检查 | 问题 |
|---|---|
| Deliverable Check | 用户要的东西是否真的存在？ |
| Representation Check | 关键输入是否可靠、可回查、足够新鲜？ |
| Prompt/Context Check | 是否有关键约束被压缩或遗漏？ |
| World State Check | 关键外部状态是否已刷新？ |
| Effect Check | 需要产生的现实效果是否已验证？ |
| Recovery Check | 失败、部分效果或不可验证状态是否已被显式处理？ |
| Identity Check | 高影响动作是否有授权来源和能力范围？ |
| Claim Check | 最终结论是否有证据支撑？ |
| Interaction Check | 是否需要告诉用户阻塞、风险、降级或剩余不确定性？ |
| Cost/Risk Check | 是否超出预算或风险等级？ |

## 6. Verify 不可达时

| 状态 | 处理 |
|---|---|
| 无法 readback | 记录 pending / external_ack，并请求后续确认 |
| 无法运行 test | 交付静态检查、未运行原因和建议命令 |
| 传感器/截图冲突 | 暂停高风险动作，重新观察或请用户确认 |
| 权限不足 | 改为 proposal，不声称已执行 |
| 预算耗尽 | partial deliver + checkpoint + 下一步建议 |

## 7. 生命周期反模式

| 反模式 | 表现 | 修复 |
|---|---|---|
| Chat Turn Loop | 每轮只重发上下文，无状态和工具效果 | 引入 checkpoint、effect ledger、stop gate |
| One-shot Tool Call | 调工具后直接回答 | 增加 read-after-write 和 verification |
| Approval-only Interaction | 只在高风险动作问用户 | 增加进度、纠错、教学和拒绝解释 |
| Context-only Recovery | 失败后只让模型“再想想” | 引入 failure classification 和新观察 |
| Summary-as-Fact | 压缩摘要被当成原始事实 | raw ref + transform chain + replay |
| Silent Learning | 任务后自动写入长期记忆/skill | 写入审批、评估、失效策略 |
