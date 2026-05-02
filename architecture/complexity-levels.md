# Agent Complexity Levels

> **Evidence Status** — synthesized. reference-topologies、minimum-viable-agent、coding/research/workflow/browser 等品类架构的模块组合归纳；用于避免“所有 Agent 都启用全部 plane”的过度工程化。

## 设计原则

复杂度应该由外部效果、任务深度、验证难度和组织风险驱动，而不是由框架目录驱动。

```text
low risk + no external write + human can verify quickly → small topology
external write + stale world state + recovery need → verified/stateful topology
continuous operation + multi-tenant + irreversible action → production topology
```

## 分级

| 等级 | 描述 | 必备 plane | 典型场景 | 不应省略 |
|---|---|---|---|---|
| C0 Advisory | 只解释、总结或给建议 | Interface、Prompting、Context | 普通知识问答、文案建议 | 不确定性声明 |
| C1 Grounded Answer | 需要外部读取或证据 | + Representation、Tools(light)、Security(light) | 研究摘要、只读查询 | provenance、trust lane |
| C2 Tool-Assisted | 工具结果影响下一步 | + Tools、Execution、Observability | 查询、搜索、短链自动化 | standardized observation |
| C3 Verified Action | 有写动作或可验证交付 | + Effects、Control、Recovery | coding patch、CRM 更新、表单填写 | postcondition、readback/test |
| C4 Stateful Long Task | 长任务、会中断或状态会过期 | + State、World State、Interaction | migration、deep research、workflow | checkpoint、freshness refresh |
| C5 Collaborative / Production | 多 Agent、组织风险、持续运行 | + Orchestration、Concurrency、Dataflow、Cost、Operations、Identity | enterprise agent、agent platform、SRE | policy、trace replay、incident path |
| C6 Adaptive System | 长期学习和自适应 | + Memory、Learning & Adaptation、Eval regression | personal memory、team coding platform | candidate validation、invalidation |

## 升级触发器

| 触发器 | 从 | 升级到 | 增加能力 |
|---|---|---|---|
| 用户要求“帮我查/打开/读取” | C0 | C1 | representation + provenance |
| 工具输出会改变下一步 | C1 | C2 | observation normalization + trace |
| 需要写文件、更新系统、提交表单 | C2 | C3 | effect ledger + verification gate |
| 任务跨多轮或中断后要继续 | C3 | C4 | task state + checkpoint |
| 外部对象在执行中会变化 | C3 | C4 | world state snapshot + refresh TTL |
| 多人/多 Agent/多租户协作 | C4 | C5 | identity + orchestration + arbitration |
| 进入生产持续运营 | C4 | C5 | cost、observability、operations、incident |
| 需要从经验中复用 SOP | C5 | C6 | learning candidate + eval regression |

## 降级策略

当验证不可达、权限不足、预算耗尽或风险过高时，不要假装完成；应降级为更低复杂度交付：

```text
C3 Verified Action blocked → C1 Grounded Answer with proposal
C4 Stateful Long Task budget exhausted → partial delivery + checkpoint
C5 Production action denied → dry-run plan + required approval list
C6 Learning candidate unsafe → quarantine + eval fixture
```

## 评审问题

```text
[ ] 当前等级由什么证据触发？
[ ] 用户最终要的是建议、交付物还是外部效果？
[ ] 写动作是否需要从 C2 升到 C3？
[ ] 长任务是否真的需要 C4，还是只是一次性工具链？
[ ] 生产风险是否要求 C5 的 trace、policy 和 incident path？
[ ] 学习机制是否已有 C6 所需的验证和失效条件？
```

相关文件：`reference-topologies.md`、`../paradigms/methodology/minimum-viable-agent.md`、`planes/effects/overview.md`、`planes/recovery/overview.md`。
