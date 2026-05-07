# Module Picker

> **Evidence Status** — synthesized. 把 25 plane 压缩成开发者可用的 5 域选择器；25 plane 只作为审计底盘按需展开。

## 30 秒判断

先选 5 域，再展开 plane。

| 5 域 | 解决什么 | 典型 plane |
|---|---|---|
| 输入与理解 | 外部输入如何变成可信表示 | Interface, Representation, Context, Prompting |
| 记忆与状态 | 如何跨步骤、跨会话保持连续性 | Memory, State, World State, Time |
| 行动与验证 | 如何执行、回读、证明完成 | Tools, Execution, Effects |
| 控制与协作 | 如何授权、交互、多 Agent 协作 | Control, Security, Identity-Capability, Interaction, Orchestration, Concurrency, Dataflow |
| 运维与演化 | 如何控成本、恢复、观测、学习 | Cost, Recovery, Observability, Operations, Learning-Adaptation, Economics, Explainability |

## 按 MVA 选择最小 plane set

| MVA | 必选 | 常见可选 | 默认暂缓 |
|---|---|---|---|
| MVA-0/1 | Prompting, Context | Representation | Tools, Effects, Operations |
| MVA-2 | Representation, Tools, Execution | Control, Cost | Memory, Orchestration |
| MVA-3 | Representation, Tools, Execution, Effects, Control | State, Security | Learning, Economics |
| MVA-4 | Context, State, World State, Recovery | Memory, Time | Dataflow, Economics |
| MVA-5 | Observability, Evaluation, Operations, Cost | Security, Identity | Learning 自动激活 |
| MVA-6 | Dataflow, Concurrency, Recovery, Operations | Learning, Economics | 无 |

## 最小产出

```yaml
selected_domains:
  - action_and_effect
  - control_and_collaboration
required_planes:
  - tools
  - execution
  - effects
  - control
excluded_for_now:
  - learning-adaptation
  - economics
reason: "single-user MVA-3; no platform or continuous learning yet"
```

## 可选增强模块

以下模块不在 5 域基础 plane 内，但在特定场景下应主动引入。

### Reasoning Model Integration

| 何时需要 | 典型配置 |
|---|---|
| 复杂规划（>5 步、有条件分支） | 规划阶段调用推理模型，执行阶段用标准模型 |
| 多步推理（证据链、因果分析） | 推理模型做深度分析，再交由 agent 执行 |
| 高价值决策（金融、安全、不可逆操作） | 推理模型做 pre-flight check，标准模型做日常循环 |

注意：推理模型调用成本显著高于标准模型，需配合 Cost plane 做预算控制。

### Cross-cutting 模块

跨 plane 边界问题需要专门的交叉模块处理，详见 `../architecture/cross-cutting/README.md`。

| 交叉模块 | 解决什么 | 何时需要 |
|---|---|---|
| memory-x-security | 记忆被外部内容投毒、篡改 | Agent 接收不可信输入并写入长期记忆时 |
| protocol-x-security | 工具协议层的信任边界 | Agent 通过 MCP 等协议调用外部工具时 |
| tool-x-effects | 工具调用成功 ≠ 效果达成 | Agent 写外部系统且需要验证时 |
| cost-x-orchestration | 多 Agent 编排的成本爆炸 | 多 Agent 循环调用、递归子任务时 |

## 常见减负规则

- 不改外部世界：先不要 Effects / Recovery 的完整实现，但 Research 仍需要 claim verification。
- 不跨会话：先不要 Memory / State 的复杂持久化。
- 不多 Agent：先不要 Orchestration / Concurrency。
- 不上线：先不要 Operations / Economics，但保留最小 trace。

## 下一步

1. `eval-planner.md`
2. `../index/category-pattern-matrix.md`
3. `../architecture/README.md`
