# Agent Product Model

> **Evidence Status** — synthesized. coding、research、workflow、memory、platform 类参考项目对 runtime 和 product blueprint 的共同结构。


## 核心公式

```text
Agent Product = User Job + World Representation + Required Depth + Runtime Assembly + Verification + Operations + Evaluation
```

一个 Agent 产品是在特定边界内完成用户 job、对外部世界产生可验证效果、并可被评估和运营的系统。

## 产品画布

| 字段 | 要回答的问题 | 失败信号 |
|---|---|---|
| Target User | 谁用？solo user、team、operator、end customer？ | 用户角色混乱 |
| User Job | 用户雇它完成什么工作？ | 只给建议不交付 |
| Entry Point | 从哪里触发：Chat / CLI / IDE / API / Event / Sensor？ | 入口与任务不匹配 |
| Deliverable | 最终交付物是什么？ | 没有可验收结果 |
| World Objects | Agent 操作哪些外部对象？ | 不知道现实被改变了什么 |
| Observable Inputs | 能观察到哪些原始输入？ | 现实输入断层 |
| Representation Contract | 如何解析、摘要、结构化和保留 raw refs？ | 表示失真 |
| Intended Effects | 希望外部世界发生什么变化？ | 工具 success 被当 done |
| Autonomy Level | Agent 能自己做多少？ | 过度自治或过度询问 |
| Execution Depth | 要做到解释、计划、执行、验证还是持续运营？ | 深度不足 |
| Runtime Assembly | 需要哪些 module / topology / paradigm？ | 模块堆叠但无闭环 |
| Approval Points | 哪些动作必须确认？ | 风险不透明 |
| Verification | 怎么证明完成？ | 无证据交付 |
| Recovery | 失败后如何恢复、回滚、交接？ | 卡死或重复失败 |
| Operations | 如何上线、回归、配置追踪、事故响应？ | 时好时坏 |
| Metrics | 用什么指标判断有效？ | 只看 demo |

## 从画布到架构

```text
User Job
  → Deliverable
  → World Objects + Intended Effects
  → Observable Inputs + Representation Contract
  → Autonomy Level + Execution Depth
  → Paradigm Selection
  → Runtime Assembly
  → Verification + Evaluation
```

## 例：Coding Agent

| 字段 | 默认答案 |
|---|---|
| Deliverable | 可审查 diff、测试结果、变更说明、剩余风险 |
| World Objects | repo、branch、file、test suite、CI、PR |
| Intended Effects | 修改代码并让相关验证通过 |
| Depth | D4-D5 |
| Autonomy | L3-L4 |
| Required Paradigms | ORDA-VU + ReAct + Plan-and-Execute + Effect Verification |
| Required Modules | Representation、Context、Tools、Execution、Control、State、World State、Effects、Observability |

详见 `../../categories/coding-agent/README.md`。

## 设计原则

1. 先定义交付物，再定义 Agent。
2. 先定义外部对象和 intended effect，再定义工具。
3. 先定义表示契约，再把输入喂给模型。
4. 先定义验证和回滚，再放开高风险动作。
5. 先设计评估和上线回归，再扩大自主范围。
