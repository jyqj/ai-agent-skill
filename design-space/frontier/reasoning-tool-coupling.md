# Reasoning and Tool Coupling

> **Evidence Status** — theoretical. 基于 tool-native reasoning API、hosted agent runtime 以及 plan-execute / reflection / ReAct 等范式的最新演化趋势。属于 frontier 观察。

## 核心变化

早期 Agent 设计常把推理和工具调用看成简单串联：

```text
think → call tool → think → call tool
```

现在更常见的变化是：

- 推理粒度和 tool schema 一起设计；
- 平台直接把 tool call、trace、handoff、built-in tools 纳入同一运行时；
- “推理摘要”本身也成为可观察对象；
- 结构化输出和 citations / tool results 的关系变得更复杂。

## 三种耦合方式

| 方式 | 特征 | 优点 | 风险 |
|---|---|---|---|
| Loose Coupling | 模型自由输出，再被 parser/tool layer 吃掉 | 实现简单 | 容易漂移，难控制 |
| Contract Coupling | tool schema、output contract、verification gate 一起设计 | 可控、好测 | 需要 upfront design |
| Hosted Coupling | runtime 直接提供 built-in tools、handoff、trace | 集成成本低 | 容易被平台默认假设牵着走 |

## 设计启发

### 1. 把“下一步决策对象”显式化

无论是 ReAct 还是 planner/worker，都应该把下面这些对象暴露出来：

```text
current_goal
current_evidence
open_questions
next_action_candidates
verification_plan
```

### 2. 工具不只是能力，也是 context shaper

一个工具是否返回长文本、结构化对象、artifact ref 或 summary，会直接影响后续推理质量和成本。

### 3. 推理摘要值得进入 observability

不要求暴露所有内部思考，但需要可观察的：

- 为什么改了计划；
- 为什么触发额外检索；
- 为什么宣告 partial completion；
- 为什么阻断高风险动作。

## 对本知识库的影响

- `prompting/`、`tools/`、`observability/` 之间的边界会越来越紧。
- `starter-kit/` 需要预留 planner 和 verifier 的替换点。
- 评估不只看 final answer，还要看 trace 是否解释了计划切换与 verification。
