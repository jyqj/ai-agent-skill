# Token Budget Controller

> **Evidence Status** — production-validated. 来自 Claude Code 的 tokenBudget.ts 生产实现，在控制 Agent 输出规模与保证任务完成之间取得平衡。

## 问题

LLM 在 Agent 循环中的单轮输出规模不可预测。模型可能在 200 token 时就发出 stop_reason="end_turn"（任务未完成就放弃），也可能输出到 max_tokens 上限仍未停止（输出膨胀浪费预算）。两种情况都破坏 Agent 的可靠性：前者导致任务中途放弃，后者导致上下文被低质量内容填满。

模型自身的停止决策不够可靠——它没有全局视角来判断"还该不该继续"。Harness 层需要一个元控制器来覆写模型的停止行为。

## 核心机制

**Token Budget Controller 是 Harness 覆写模型停止决策的元控制器。** 它不修改模型参数，而是在模型输出结束后决定：是否注入一条 nudge message 让模型继续，还是强制终止。

### 阈值触发 continuation

```
已用 token / 总预算 ≥ 90%  →  不触发 continuation（预算即将耗尽）
已用 token / 总预算 < 90%  →  检查是否应该 continue
```

当模型输出 stop_reason="end_turn" 但预算仍有余量时，Controller 注入一条 nudge message（如"请继续完成剩余步骤"），触发模型继续输出。这本质上是用一条廉价的系统消息换取任务完成度。

### 收益递减检测

连续 continuation 不是无限的。Controller 追踪每次 continuation 后模型输出的增量 token 数：

```
continuation_1: delta = 2000 tokens  → 有效，继续
continuation_2: delta = 800 tokens   → 有效，继续
continuation_3: delta = 300 tokens   → < 500 阈值，计数 +1
continuation_4: delta = 200 tokens   → < 500 阈值，计数 = 2 → 停止
```

**连续 2 次增量 < 500 tokens → 判定收益递减，强制停止。** 这避免了模型在 continuation 中只输出空洞的总结或重复内容。

### Nudge Message 注入

Nudge message 的设计要点：

- **角色**：system 或 user，取决于 API 约束
- **内容**：简短、具体、指向剩余任务（如"上面的修改还未完成，请继续"），避免泛泛的"请继续"导致模型重复已有内容
- **不可见**：nudge message 在任务完成后从对话历史中清除，不污染后续轮次的上下文

### 与 max_tokens 的关系

Controller 不直接设置 max_tokens。它在 max_tokens 之上增加了一层逻辑：

- max_tokens 是 API 级别的硬上限（单次 API 调用的输出上限）
- Token Budget 是 Harness 级别的软上限（跨多次 API 调用的总预算）
- Controller 通过控制 continuation 次数来间接控制总输出量

## 项目对照

| 项目 | 实现方式 |
|---|---|
| Claude Code | `tokenBudget.ts`：90% 阈值触发、收益递减检测（delta < 500 × 2 次）、nudge message 注入 |
| Aider | `max-chat-history-tokens` 配置 + 自动摘要，但缺少 continuation 机制 |
| OpenCode | 上下文预算管理侧重压缩而非 continuation，与本模式互补 |

## 与其他 plane/pattern 的关系

| 相关模式 | 关系 |
|---|---|
| `compaction.md` | Compaction 管理历史上下文的大小，Budget Controller 管理当前轮输出的大小——两者共同控制上下文窗口 |
| `depth-budgeting.md` | Depth Budget 控制"做多少步"，Token Budget 控制"每步说多少话" |
| `streaming-tool-execution.md` | 流式执行期间，Token Budget 需要实时追踪已用 token，而非等到流结束 |
| `behavior-correction-layer.md` | Correction Layer 检测空回复并重试，Token Budget Controller 检测过短回复并 continue——两者在不同层面保证输出质量 |

## 适用条件

**适用：**
- 需要控制 Agent 单轮输出规模的场景（长代码生成、多步计划执行）
- 模型容易过早停止或过度输出的场景
- 预算敏感的部署环境

**不适用：**
- 单轮交互（问答模式）——无需跨轮预算管理
- 模型输出极短且固定（如分类任务）——continuation 无意义
- 无法注入 nudge message 的 API（如某些受限的 API 端点）

## 反模式

| 反模式 | 表现 | 修复 |
|---|---|---|
| 无限 continuation | 不检测收益递减，模型反复输出重复内容 | 收益递减检测 + 最大 continuation 次数 |
| 泛泛 nudge | "请继续"导致模型重复已输出内容 | nudge 指向具体剩余任务 |
| 预算硬切 | 到达预算直接截断，不给模型收尾机会 | 预留 10% 缓冲区用于收尾 |

## 参考实现

- Claude Code: `tokenBudget.ts` — 预算控制与 continuation 逻辑
