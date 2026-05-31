# Observability as a Control Plane

> **Evidence Status** — theoretical. 基于 trace/span/eval/online feedback 工具生态与多个 Agent 运行时的需求观察。属于 frontier 方向。

## 核心判断

Observability 不再只是“事后看日志”，而正在变成：

```text
runtime decision support + eval dataset source + rollback evidence + policy tuning input
```

## 为什么它值得单独讨论

Agent 可观测性的复杂度来自多个维度：

- 多步 trace；
- tool 调用；
- human correction；
- effect verification；
- cost explosion；
- subtle regressions；

这些都要求比传统应用日志更细的对象模型。

## 最小 trace 对象

```yaml
trace_event:
  event_type: intake | represent | decide | tool_call | effect_record | interaction | verify | deliver
  step_id: string
  parent_step_id: string|null
  task_id: string
  tool_name: string|null
  cost: {}
  risk: {}
  evidence_refs: []
```

## 观测体系的四个用途

| 用途 | 说明 |
|---|---|
| Debug | 复现为什么走到这一步 |
| Eval | 从真实失败中沉淀 fixture 和 regression suite |
| Control | 在 trace 中触发 loop detection、budget gate、approval |
| Learning | 从成功/失败轨迹提炼 skill 和 policy update |

## 仍在演进的问题

- 哪些“推理摘要”应该被保留为可观察对象。
- 如何在不暴露敏感内部链路的前提下保留足够诊断信息。
- offline eval 与 online traces 如何共享相同对象模型。
