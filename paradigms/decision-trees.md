# Paradigm Decision Trees

> **Evidence Status** — synthesized. reasoning、memory、tool、collaboration、control 五类范式的选择矩阵综合；用于把“列出范式”升级为可操作的选择过程。

## 0. 总入口

```text
用户要外部效果吗？
  ├─ 否：以 C0/C1 为主，关注 claim/evidence
  └─ 是：进入 effect risk 判断

外部效果是否可逆且可验证？
  ├─ 可逆 + 可验证：C3 Verified Action
  ├─ 可逆但不可直接验证：C3 + human/external ack
  └─ 不可逆或高影响：C4/C5 + approval + compensation/rollback plan

任务是否会跨多轮、跨系统或中断？
  ├─ 否：单任务拓扑
  └─ 是：State + World State + Recovery + Trace
```

## 1. 推理范式

```text
任务只需要解释/总结吗？
  ├─ 是 → Direct Answer
  └─ 否 → 需要外部读取吗？
       ├─ 是，但工具结果不改变计划 → Tool-Augmented Direct
       └─ 是，工具结果会改变下一步 → ReAct / ORDA-VU micro-loop

任务可预先拆成稳定步骤吗？
  ├─ 是 → Plan-and-Execute + step verification
  └─ 否 → ReAct with stop gate and recovery budget

风险高或写动作不可逆吗？
  ├─ 是 → Plan + Approval + Verification Gate
  └─ 否 → 按深度选择 Direct / ReAct / Plan

需要探索多个候选方案吗？
  ├─ 是 → Tree/Graph Search + evaluator + branch budget
  └─ 否 → 不引入搜索复杂度
```

## 2. 记忆范式

```text
信息只在当前任务有效吗？
  ├─ 是 → Context / TaskState，不写长期记忆
  └─ 否 → 是否需要长期复用？
       ├─ 否 → Trace only
       └─ 是 → 进入记忆类型判断

是外部对象当前状态吗？
  ├─ 是 → WorldStateSnapshot + TTL
  └─ 否 → 是用户偏好/项目约定/技能/关系吗？
       ├─ 用户偏好 → Disclosure + user control
       ├─ 项目约定 → Project Memory + validation
       ├─ 成功路径 → Skill candidate + eval gate
       └─ 多实体关系 → Graph Memory + provenance
```

## 3. 工具范式

```text
工具动作是否高风险或外部写入？
  ├─ 是 → Rich/Workflow Tool + policy + effect verification
  └─ 否 → Atomic/Static Tool 可接受

任务形态是否高度变化？
  ├─ 是 → Atomic Tool + Tool Router
  └─ 否 → Rich Domain Tool 或 Workflow Tool

工具来自第三方协议/MCP 吗？
  ├─ 是 → MCP trust boundary + capability grant + output sanitization
  └─ 否 → 常规 Tool Registry

需要生成临时代码处理数据吗？
  ├─ 是 → Code-as-Tool + sandbox + artifact trace
  └─ 否 → typed tool 优先
```

## 4. 协作范式

```text
单 Agent 能在上下文和时间预算内完成吗？
  ├─ 是 → Single Agent + Tools
  └─ 否 → 任务是否可并行拆分？
       ├─ 是 → Coordinator-Worker
       └─ 否 → 是否需要隔离角色/视角？
            ├─ 是 → Subagent / Peer review
            └─ 否 → Stateful single agent + progressive disclosure

多个 Agent 是否共享外部对象？
  ├─ 是 → Shared World Model + arbitration + locks/leases
  └─ 否 → OutputContract + merge strategy

是否持续运行？
  ├─ 是 → Event-driven + heartbeat + idempotency
  └─ 否 → Task-scoped orchestration
```

## 5. 控制范式

```text
规则能确定判定吗？
  ├─ 是 → Rule / Permission Tree
  └─ 否 → 语义判断是否低风险？
       ├─ 是 → LLM Judge + rubric
       └─ 否 → LLM Judge + Rule + Human escalation

动作会改变外部世界吗？
  ├─ 否 → output check / citation check
  └─ 是 → Effect verification gate

动作是否不可逆或高影响？
  ├─ 是 → Approval + sandbox/dry-run + rollback/compensation
  └─ 否 → risk-based gate + trace

上线到生产了吗？
  ├─ 是 → shadow/canary + incident path + kill switch
  └─ 否 → fixture eval + local trace
```

## 6. 最终输出

范式选择的输出不应只是一个名字，而应形成结构化设计：

```yaml
paradigm_selection:
  reasoning: direct | tool_augmented | react | plan_execute | orda_vu | tree_search
  memory: none | context | rag | disclosure | layered | graph | world_state
  tools: static | atomic | rich_domain | workflow | mcp | code_as_tool
  collaboration: single | subagent | coordinator_worker | peer | event_driven | human_in_loop
  control: rule | judge | hook | sandbox | approval | verification | canary
  complexity_level: C0 | C1 | C2 | C3 | C4 | C5 | C6
  required_planes: []
  stop_gates: []
  eval_fixtures: []
```

相关文件：`reasoning-paradigms.md`、`memory-paradigms.md`、`tool-paradigms.md`、`collaboration-paradigms.md`、`control-paradigms.md`、`../architecture/complexity-levels.md`。
