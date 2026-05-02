# Agent 主循环 (query.ts)

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。

## 来源
src/query.ts:241-500+

## 关键点
Claude Code 的核心 agent loop，展示了生产系统 TAO 循环的复杂性（参考观察）：
- 状态管理
- 多层压缩
- 错误恢复
- 工具执行

## 代码

```typescript
// 可变状态，跨循环迭代携带
type State = {
  messages: Message[]
  toolUseContext: ToolUseContext
  autoCompactTracking: AutoCompactTrackingState | undefined
  maxOutputTokensRecoveryCount: number
  hasAttemptedReactiveCompact: boolean
  maxOutputTokensOverride: number | undefined
  pendingToolUseSummary: Promise<ToolUseSummaryMessage | null> | undefined
  stopHookActive: boolean | undefined
  turnCount: number
  transition: Continue | undefined  // 为什么上一次迭代继续
}

async function* queryLoop(params: QueryParams) {
  let state: State = { /* 初始化 */ }

  // 无限循环
  while (true) {
    // 1. 解构当前状态
    let { toolUseContext } = state
    const { messages, autoCompactTracking, turnCount } = state

    // 2. 多层压缩（按顺序）
    let messagesForQuery = [...getMessagesAfterCompactBoundary(messages)]

    // 2.1 Tool result 预算限制
    messagesForQuery = await applyToolResultBudget(messagesForQuery, ...)

    // 2.2 Snip 压缩（历史裁剪）
    if (feature('HISTORY_SNIP')) {
      const snipResult = snipModule.snipCompactIfNeeded(messagesForQuery)
      messagesForQuery = snipResult.messages
    }

    // 2.3 Microcompact（工具输出压缩）
    const microcompactResult = await deps.microcompact(messagesForQuery, ...)
    messagesForQuery = microcompactResult.messages

    // 2.4 Context Collapse（上下文折叠）
    if (feature('CONTEXT_COLLAPSE')) {
      const collapseResult = await contextCollapse.applyCollapsesIfNeeded(...)
      messagesForQuery = collapseResult.messages
    }

    // 2.5 AutoCompact（完整摘要）
    const { compactionResult } = await deps.autocompact(messagesForQuery, ...)
    if (compactionResult) {
      // 替换为摘要消息
      messagesForQuery = buildPostCompactMessages(compactionResult)
    }

    // 3. 调用 API
    const response = await api.createMessage({
      messages: normalizeMessagesForAPI(messagesForQuery),
      systemPrompt: fullSystemPrompt,
      ...
    })

    // 4. 处理响应
    for await (const event of response) {
      yield event
      // 处理流式事件...
    }

    // 5. 执行工具
    if (hasToolUse) {
      for await (const update of runTools(toolUseBlocks, ...)) {
        // 处理工具执行结果
        // 更新状态
      }
    }

    // 6. 决定是否继续
    if (shouldTerminate) {
      return { type: 'terminal', ... }
    }

    // 7. 更新状态，继续下一轮
    state = {
      ...state,
      messages: updatedMessages,
      turnCount: turnCount + 1,
      transition: continueReason,
    }
  }
}
```

## 注释

### 关键设计决策

1. **Generator 函数 (`async function*`)**
   - 允许流式输出事件
   - 调用方可以提前终止
   - 符合 JavaScript 的惰性执行模型

2. **状态封装在单一对象**
   - 每次迭代解构 state
   - continue 站点更新整个 state 对象
   - 避免散落的状态变量

3. **多层压缩是正交的**
   - 每层独立运行
   - 按顺序：snip → microcompact → collapse → autocompact
   - 可以单独开关（feature flags）

4. **transition 字段记录"为什么继续"**
   - 调试时可以追踪循环原因
   - 测试时可以断言恢复路径

### 与知识库概念的关联

- **Agent Loop**: 这是 TAO 循环的生产系统观察点
- **Compaction**: 多层策略，不是单一压缩
- **State Management**: 显式状态对象，不依赖闭包
