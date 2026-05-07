# 工具执行编排 (toolOrchestration.ts)

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。

## 来源
src/services/tools/toolOrchestration.ts

## 关键点
Claude Code 的工具执行不是简单的串行，而是智能分批：
- 只读工具可以并发执行
- 写入工具必须串行执行
- 通过 `isConcurrencySafe` 属性判断

这最大化了吞吐量，同时保证了正确性。

## 代码

```typescript
// 最大并发数（可配置）
function getMaxToolUseConcurrency(): number {
  return parseInt(process.env.CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY || '', 10) || 10
}

// 分批策略
type Batch = { isConcurrencySafe: boolean; blocks: ToolUseBlock[] }

/**
 * 将工具调用分成批次：
 * 1. 单个非只读工具（串行）
 * 2. 连续的多个只读工具（并发）
 */
function partitionToolCalls(
  toolUseMessages: ToolUseBlock[],
  toolUseContext: ToolUseContext,
): Batch[] {
  return toolUseMessages.reduce((acc: Batch[], toolUse) => {
    const tool = findToolByName(toolUseContext.options.tools, toolUse.name)
    const parsedInput = tool?.inputSchema.safeParse(toolUse.input)

    // 判断是否可并发
    const isConcurrencySafe = parsedInput?.success
      ? (() => {
          try {
            return Boolean(tool?.isConcurrencySafe(parsedInput.data))
          } catch {
            // 如果判断函数抛错，保守地视为不可并发
            return false
          }
        })()
      : false

    // 如果当前工具可并发，且上一批也可并发，合并到同一批
    if (isConcurrencySafe && acc[acc.length - 1]?.isConcurrencySafe) {
      acc[acc.length - 1]!.blocks.push(toolUse)
    } else {
      // 否则创建新批次
      acc.push({ isConcurrencySafe, blocks: [toolUse] })
    }
    return acc
  }, [])
}

// 主执行函数
async function* runTools(
  toolUseMessages: ToolUseBlock[],
  assistantMessages: AssistantMessage[],
  canUseTool: CanUseToolFn,
  toolUseContext: ToolUseContext,
): AsyncGenerator<MessageUpdate, void> {
  let currentContext = toolUseContext

  // 遍历每个批次
  for (const { isConcurrencySafe, blocks } of partitionToolCalls(toolUseMessages, currentContext)) {
    if (isConcurrencySafe) {
      // 并发批次
      const queuedContextModifiers: Record<string, ((ctx: ToolUseContext) => ToolUseContext)[]> = {}

      // 并发执行所有工具
      for await (const update of runToolsConcurrently(blocks, assistantMessages, canUseTool, currentContext)) {
        // 收集上下文修改器（稍后统一应用）
        if (update.contextModifier) {
          const { toolUseID, modifyContext } = update.contextModifier
          queuedContextModifiers[toolUseID] ??= []
          queuedContextModifiers[toolUseID].push(modifyContext)
        }
        yield { message: update.message, newContext: currentContext }
      }

      // 按原始顺序应用上下文修改
      for (const block of blocks) {
        const modifiers = queuedContextModifiers[block.id]
        if (modifiers) {
          for (const modifier of modifiers) {
            currentContext = modifier(currentContext)
          }
        }
      }
      yield { newContext: currentContext }

    } else {
      // 串行批次
      for await (const update of runToolsSerially(blocks, assistantMessages, canUseTool, currentContext)) {
        if (update.newContext) {
          currentContext = update.newContext
        }
        yield { message: update.message, newContext: currentContext }
      }
    }
  }
}

// 串行执行
async function* runToolsSerially(
  toolUseMessages: ToolUseBlock[],
  assistantMessages: AssistantMessage[],
  canUseTool: CanUseToolFn,
  toolUseContext: ToolUseContext,
): AsyncGenerator<MessageUpdate, void> {
  let currentContext = toolUseContext

  for (const toolUse of toolUseMessages) {
    // 标记工具开始执行
    toolUseContext.setInProgressToolUseIDs(prev => new Set(prev).add(toolUse.id))

    // 执行单个工具
    for await (const update of runToolUse(toolUse, ...)) {
      if (update.contextModifier) {
        currentContext = update.contextModifier.modifyContext(currentContext)
      }
      yield { message: update.message, newContext: currentContext }
    }

    // 标记工具完成
    markToolUseAsComplete(toolUseContext, toolUse.id)
  }
}
```

## 注释

### 设计要点

1. **isConcurrencySafe 是工具属性**
   - 每个工具定义自己是否可并发
   - 基于输入参数动态判断（如读取操作 vs 写入操作）
   - 判断失败时保守处理（视为不可并发）

2. **批次合并**
   - 连续的只读工具合并到一个批次
   - 单个写入工具独占一个批次
   - 保持原始调用顺序

3. **上下文修改的顺序**
   - 并发执行时，收集所有修改器
   - 按原始工具顺序应用修改
   - 保证确定性结果

4. **Generator 流式输出**
   - 每个工具结果立即 yield
   - 调用方可以实时显示进度
   - 支持提前中断

### 典型工具的并发安全性

| 工具 | isConcurrencySafe | 原因 |
|-----|-------------------|------|
| Read | true | 只读操作 |
| Glob | true | 只读操作 |
| Grep | true | 只读操作 |
| Write | false | 修改文件 |
| Edit | false | 修改文件 |
| Bash | 取决于命令 | ls 可以，rm 不行 |
