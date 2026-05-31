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
  │  > 判定"环境会在执行中变化"：
  │  >   若依赖的外部状态 TTL <任务预估耗时 → 环境会变化。
  │  >   或：原型运行中 ≥20% 的执行出现"步骤前提失效"（如资源被他人修改、
  │  >   API 返回值与预期不一致）→ drift 频率过高，需要 World State 刷新。
  │  >   实用简判：任务涉及 ≥2 个外部系统，且预估耗时 >30 秒 → 按"会变化"处理。
  ├─ 否：单任务拓扑
  └─ 是：State + World State + Recovery + Trace
```

下图展示总入口的三级判定流程:

```mermaid
flowchart TD
    START(["任务进入"]) --> Q1{"用户要外部效果?"}
    Q1 -->|"否"| A1["C0/C1 为主\n关注 claim/evidence"]
    Q1 -->|"是"| Q2{"外部效果是否\n可逆且可验证?"}

    Q2 -->|"可逆 + 可验证"| A2["C3 Verified Action"]
    Q2 -->|"可逆但不可直接验证"| A3["C3 + human/external ack"]
    Q2 -->|"不可逆或高影响"| A4["C4/C5 + approval\n+ compensation/rollback plan"]

    A2 --> Q3{"任务会跨多轮\n跨系统或中断?"}
    A3 --> Q3
    A4 --> Q3

    Q3 -->|"否"| A5["单任务拓扑"]
    Q3 -->|"是"| A6["State + WorldState\n+ Recovery + Trace"]

    style START fill:#f9f,stroke:#333
    style A5 fill:#9f9,stroke:#333
    style A6 fill:#9f9,stroke:#333
```

## 1. 推理范式

```text
任务只需要解释/总结吗？
  ├─ 是 → Direct Answer
  └─ 否 → 需要外部读取吗？
       ├─ 是，但工具结果不改变计划 → Tool-Augmented Direct
       └─ 是，工具结果会改变下一步 → ReAct / ORDA-VU micro-loop
            > 判定"多步"：若完成任务需要 ≥3 次独立工具调用，且后续调用依赖前序结果 → 多步。
            > 1-2 次独立查询 → Tool-Augmented Direct 即可。
            > ≥5 次且有分支 → 考虑 Plan-and-Execute。

任务可预先拆成稳定步骤吗？
  │  > 判定方法：人工拆分为 N 步后做原型运行（≥10 次）。
  │  > 若 ≥80% 步骤的单次成功率 ≥90% → "稳定" → Plan-and-Execute。
  │  > 若任一步骤失败率 >20%，或步骤顺序需运行时决定 → "不稳定" → ReAct。
  ├─ 是 → Plan-and-Execute + step verification
  └─ 否 → ReAct with stop gate and recovery budget

风险高或写动作不可逆吗？
  │  > "可逆"分级：
  │  >   L0 纯读 — 无副作用，始终安全。
  │  >   L1 软可逆 — 可通过 API/undo 在 <5 min 回滚（如撤销 git commit、删除草稿）。
  │  >   L2 硬可逆 — 可回滚但需人工介入或耗时 >5 min（如数据库恢复、工单状态回退）。
  │  >   L3 不可逆 — 无法回滚（如发送邮件、物理动作、资金转账、删除无备份数据）。
  │  > L0-L1 → 按深度选择；L2 → 加 dry-run + 确认；L3 → 必须 Plan + Approval + Verification。
  ├─ 是 → Plan + Approval + Verification Gate
  └─ 否 → 按深度选择 Direct / ReAct / Plan

需要探索多个候选方案吗？
  ├─ 是 → Tree/Graph Search + evaluator + branch budget
  └─ 否 → 不引入搜索复杂度
```

下图展示推理范式的四级选择流程:

```mermaid
flowchart TD
    R0(["推理范式选择"]) --> Q1{"任务只需\n解释/总结?"}
    Q1 -->|"是"| A1["Direct Answer"]
    Q1 -->|"否"| Q2{"需要外部读取?"}

    Q2 -->|"否"| A1
    Q2 -->|"是，工具结果\n不改变计划"| A2["Tool-Augmented Direct"]
    Q2 -->|"是，工具结果\n会改变下一步"| Q3{"≥3 次依赖性\n工具调用?"}

    Q3 -->|"否(1-2 次)"| A2
    Q3 -->|"是"| Q4{"步骤可预先拆分\n且稳定?"}

    Q4 -->|"是(≥80% 步骤\n成功率 ≥90%)"| A3["Plan-and-Execute\n+ step verification"]
    Q4 -->|"否(失败率 >20%\n或顺序需运行时决定)"| A4["ReAct + stop gate\n+ recovery budget"]

    A3 --> Q5{"风险高或\n写动作不可逆?"}
    A4 --> Q5

    Q5 -->|"L0-L1 可逆"| A5["按深度选择\nDirect / ReAct / Plan"]
    Q5 -->|"L2 硬可逆"| A6["加 dry-run + 确认"]
    Q5 -->|"L3 不可逆"| A7["Plan + Approval\n+ Verification Gate"]

    A5 --> Q6{"需要探索\n多个候选方案?"}
    A6 --> Q6
    A7 --> Q6

    Q6 -->|"是"| A8["Tree/Graph Search\n+ evaluator + branch budget"]
    Q6 -->|"否"| A9["不引入搜索复杂度"]

    style R0 fill:#f9f,stroke:#333
    style A8 fill:#9f9,stroke:#333
    style A9 fill:#9f9,stroke:#333
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

下图展示记忆范式的选择流程:

```mermaid
flowchart TD
    M0(["记忆范式选择"]) --> Q1{"信息只在\n当前任务有效?"}
    Q1 -->|"是"| A1["Context / TaskState\n不写长期记忆"]
    Q1 -->|"否"| Q2{"需要长期复用?"}

    Q2 -->|"否"| A2["Trace only"]
    Q2 -->|"是"| Q3{"是外部对象\n当前状态?"}

    Q3 -->|"是"| A3["WorldStateSnapshot\n+ TTL"]
    Q3 -->|"否"| Q4{"信息类型?"}

    Q4 -->|"用户偏好"| A4["Disclosure\n+ user control"]
    Q4 -->|"项目约定"| A5["Project Memory\n+ validation"]
    Q4 -->|"成功路径"| A6["Skill candidate\n+ eval gate"]
    Q4 -->|"多实体关系"| A7["Graph Memory\n+ provenance"]

    style M0 fill:#f9f,stroke:#333
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

下图展示工具范式的四条判定链:

```mermaid
flowchart TD
    T0(["工具范式选择"]) --> Q1{"工具动作是否\n高风险或外部写入?"}
    Q1 -->|"是"| A1["Rich/Workflow Tool\n+ policy + effect verification"]
    Q1 -->|"否"| A2["Atomic/Static Tool"]

    A1 --> Q2{"任务形态\n是否高度变化?"}
    A2 --> Q2

    Q2 -->|"是"| A3["Atomic Tool\n+ Tool Router"]
    Q2 -->|"否"| A4["Rich Domain Tool\n/ Workflow Tool"]

    A3 --> Q3{"工具来自\n第三方/MCP?"}
    A4 --> Q3

    Q3 -->|"是"| A5["MCP trust boundary\n+ capability grant\n+ output sanitization"]
    Q3 -->|"否"| A6["常规 Tool Registry"]

    A5 --> Q4{"需要生成\n临时代码处理数据?"}
    A6 --> Q4

    Q4 -->|"是"| A7["Code-as-Tool\n+ sandbox + artifact trace"]
    Q4 -->|"否"| A8["typed tool 优先"]

    style T0 fill:#f9f,stroke:#333
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

下图展示协作范式的三级判定流程:

```mermaid
flowchart TD
    C0(["协作范式选择"]) --> Q1{"单 Agent 能在\n上下文和时间预算\n内完成?"}
    Q1 -->|"是"| A1["Single Agent + Tools"]
    Q1 -->|"否"| Q2{"任务是否\n可并行拆分?"}

    Q2 -->|"是"| A2["Coordinator-Worker"]
    Q2 -->|"否"| Q3{"是否需要\n隔离角色/视角?"}

    Q3 -->|"是"| A3["Subagent / Peer review"]
    Q3 -->|"否"| A4["Stateful single agent\n+ progressive disclosure"]

    A2 --> Q4{"多个 Agent 是否\n共享外部对象?"}
    A3 --> Q4

    Q4 -->|"是"| A5["Shared World Model\n+ arbitration + locks/leases"]
    Q4 -->|"否"| A6["OutputContract\n+ merge strategy"]

    A5 --> Q5{"是否持续运行?"}
    A6 --> Q5

    Q5 -->|"是"| A7["Event-driven\n+ heartbeat + idempotency"]
    Q5 -->|"否"| A8["Task-scoped orchestration"]

    style C0 fill:#f9f,stroke:#333
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
  │  > 触发人工审批的条件（满足任一即需审批）：
  │  >   1. 可逆性 ≥ L2（硬可逆或不可逆）。
  │  >   2. 影响范围：涉及 >100 条记录、>$100 金额、或影响外部用户可见状态。
  │  >   3. 合规要求：SOX/GDPR/HIPAA 等法规明确要求人工签核的动作。
  │  >   4. 首次执行：该动作模板在生产环境首次运行（无历史成功记录）。
  │  > 不需审批：L0-L1 可逆 + 影响范围小 + 有历史成功记录 → 自动执行 + trace。
  ├─ 是 → Approval + sandbox/dry-run + rollback/compensation
  └─ 否 → risk-based gate + trace

上线到生产了吗？
  ├─ 是 → shadow/canary + incident path + kill switch
  └─ 否 → fixture eval + local trace
```

下图展示控制范式的四级判定流程:

```mermaid
flowchart TD
    K0(["控制范式选择"]) --> Q1{"规则能确定判定?"}
    Q1 -->|"是"| A1["Rule / Permission Tree"]
    Q1 -->|"否"| Q2{"语义判断\n是否低风险?"}

    Q2 -->|"是"| A2["LLM Judge + rubric"]
    Q2 -->|"否"| A3["LLM Judge + Rule\n+ Human escalation"]

    A1 --> Q3{"动作会改变\n外部世界?"}
    A2 --> Q3
    A3 --> Q3

    Q3 -->|"否"| A4["output check\n/ citation check"]
    Q3 -->|"是"| A5["Effect verification gate"]

    A5 --> Q4{"动作不可逆\n或高影响?"}

    Q4 -->|"是(L2+/高影响/\n合规/首次执行)"| A6["Approval + sandbox\n/ dry-run + rollback"]
    Q4 -->|"否(L0-L1 +\n影响小 + 有历史记录)"| A7["risk-based gate\n+ trace"]

    A6 --> Q5{"上线到生产?"}
    A7 --> Q5

    Q5 -->|"是"| A8["shadow/canary\n+ incident path\n+ kill switch"]
    Q5 -->|"否"| A9["fixture eval\n+ local trace"]

    style K0 fill:#f9f,stroke:#333
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
