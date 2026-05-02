# Decision Log Pattern

> **Evidence Status** — synthesized. 源自长上下文压缩和检查点恢复的实际需求，尚未在生产系统中验证最小 Schema 的效果。

长任务中最容易丢的不是工具输出，而是"为什么这么做"。上下文压缩（Context Compaction）之后，Agent 可能忘记哪些方案已经排除、哪些约束来自用户、为什么选择了当前路径、哪些风险还悬着、哪些失败已经试过。决策日志（Decision Log）就是为了在压缩中幸存下来而设计的结构化记录。

## 记什么

State Engine 维护一个结构化的决策日志，不记录所有细节，只记录影响后续执行的判断。每条记录包含决策本身、理由、被排除的替代方案、支撑证据和风险评估：

```yaml
decision:
  id: dec_001
  timestamp: string
  milestone: patch
  decision: Use minimal token refresh fix instead of rewriting auth flow
  rationale:
    - failure isolated to refresh branch
    - large rewrite would increase regression risk
  alternatives_rejected:
    - rewrite auth middleware
    - disable refresh retry
  evidence:
    - path: src/auth/refresh.ts
    - test: auth-refresh.test.ts
  risk:
    level: check
    note: may affect session renewal edge case
  follow_up:
    - run targeted auth tests
```

## 什么时候写入

写入时机是这个模式的关键。不是事后补录，而是在决策发生的那一刻同步记录：

- 选择计划路径时
- 排除一个方案时
- 遇到用户约束时
- 工具失败并改变策略时
- 执行高风险动作前
- checkpoint 前
- 上下文压缩前
- 最终交付前

## 与上下文压缩的关系

压缩上下文时，原始工具输出可以被摘要或卸载，但决策日志、未解决风险和失败记录必须作为高优先级内容保留或摘要进入新的 Context Pack。这是决策日志存在的根本理由：它是压缩安全的决策记忆。

## 适用场景

所有执行深度达到 D3 及以上的 Agent。如果任务短到不需要上下文压缩，这个模式的价值就不大。
