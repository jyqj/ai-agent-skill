# Harness Engineering

> **Evidence Status** — synthesized. coding、tool platform、general agent、memory system 参考项目中对 context、tool、execution、control、state、trace 的共同实践。


## 定义

**Harness 是 Agent 系统中除了 Model 之外的一切。**

```text
Model   = 推理、生成、语义泛化
Harness = 输入表示、上下文装配、工具执行、状态持久化、权限控制、效果验证、评估回归
```

模型能力决定 Agent 的下限；Harness 设计决定 Agent 的上限。

## 三层工程关系

```text
Harness Engineering（最广）
└── Agent 运行环境、接口、工具、状态、验证、运维
    ├── Context Engineering
    │   └── 管理模型当前看见什么
    │       └── Prompt Engineering
    │           └── 优化单次交互的指令表达
    └── Execution / Control / Memory / Evaluation / Operations
```

| 层次 | 优化目标 | 时间范围 | 典型问题 |
|---|---|---|---|
| Prompt | 单次输出质量 | 一轮交互 | 指令是否清楚？格式是否稳定？ |
| Context | 当前注意力质量 | 一个窗口 | 模型看见的是不是正确证据？ |
| Harness | 任务完成率和可控性 | 多轮、多会话、上线后 | 能否行动、验证、恢复、回归？ |

## Harness 的核心组件

| 组件 | 回答的问题 | 对应目录 |
|---|---|---|
| Interface | 输入从哪里来？ | `../../architecture/planes/interface/overview.md` |
| Representation | 原始现实如何编码？ | `../../architecture/planes/representation/overview.md` |
| Prompt / Context | 模型看到什么、按什么契约输出？ | `../../architecture/planes/prompting/overview.md`、`../../architecture/planes/context/overview.md` |
| Memory / State / World State | 什么能跨轮保留，外部对象状态如何刷新？ | `../../architecture/planes/memory/overview.md`、`../../architecture/planes/state/overview.md`、`../../architecture/planes/world-state/overview.md` |
| Tools / Execution | 如何把意图变成动作？ | `../../architecture/planes/tools/overview.md`、`../../architecture/planes/execution/overview.md` |
| Control / Security | 哪些动作允许，哪些输出可信？ | `../../architecture/planes/control/overview.md`、`../../architecture/planes/security/overview.md` |
| Effects | 如何证明现实发生了变化？ | `../../architecture/planes/effects/overview.md` |
| Observability / Operations | 如何追踪、回归、上线、回滚？ | `../../architecture/planes/observability/overview.md`、`../../architecture/planes/operations/overview.md` |

## 从失败反推 Harness

| 失败 | 说明 | Harness 补强 |
|---|---|---|
| 误解输入 | 原始输入转换有损或无来源 | Representation Contract + raw refs |
| 找不到上下文 | context pack 装配错误 | Context retrieval + compaction |
| 工具调用成功但任务没完成 | 把 execution success 当 effect success | Effect Ledger + verification gate |
| 重复失败 | 没有 failure mode 和 retry budget | structured failure + loop detection |
| 用户不信任 | 权限和进度不可见 | Interaction + trust escalation |
| 上线退化 | 行为配置不可追踪 | ConfigFingerprint + regression |

## 设计原则

1. 从交付物和外部效果反推工具，不从工具清单反推产品。
2. 所有模型可见输入都要标注来源、信任和时效。
3. 所有写动作都要声明 intended effect、postcondition 和 verification method。
4. 所有长任务都要有 checkpoint、stop gate 和恢复策略。
5. 所有生产行为变化都要有 trace、配置指纹和回归评估。

## 与范式层的关系

Harness 不是一种推理范式，而是承载各种范式的工程外壳：

- ReAct 需要工具 observation 和 loop detection。
- Plan-and-Execute 需要 TaskState、checkpoint 和 step verification。
- RAG / Disclosure 需要 Representation、Context、Memory 和 trust boundary。
- Multi-agent 需要 AgentMessage、OutputContract 和 merge strategy。
- LLM-as-Judge 需要 rubric、校准 eval 和 trace。

相关文件：`../../paradigms/reasoning-paradigms.md`、`../../paradigms/memory-paradigms.md`、`../../paradigms/tool-paradigms.md`、`../../paradigms/control-paradigms.md`。
