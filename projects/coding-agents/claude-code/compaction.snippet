# 多层压缩策略 (autoCompact.ts + compact.ts)

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。

## 来源
src/services/compact/autoCompact.ts
src/services/compact/compact.ts
src/query.ts (压缩调用链)

## 关键点
Claude Code 不是单一压缩，而是多层策略：
1. Tool Result Budget - 限制单个工具输出大小
2. Snip Compact - 历史裁剪
3. Microcompact - 工具输出智能压缩
4. Context Collapse - 上下文折叠
5. Auto Compact - 完整摘要

每层解决不同问题，按顺序执行。

## 代码

```typescript
// ========== 1. 阈值计算 ==========

// 保留给摘要输出的 tokens
const MAX_OUTPUT_TOKENS_FOR_SUMMARY = 20_000

// 有效上下文窗口 = 总窗口 - 摘要输出预留
function getEffectiveContextWindowSize(model: string): number {
  const reservedTokensForSummary = Math.min(
    getMaxOutputTokensForModel(model),
    MAX_OUTPUT_TOKENS_FOR_SUMMARY,
  )
  return contextWindow - reservedTokensForSummary
}

// 触发阈值 = 有效窗口 - 缓冲区
const AUTOCOMPACT_BUFFER_TOKENS = 13_000
function getAutoCompactThreshold(model: string): number {
  return getEffectiveContextWindowSize(model) - AUTOCOMPACT_BUFFER_TOKENS
}

// ========== 2. 警告状态计算 ==========

function calculateTokenWarningState(tokenUsage: number, model: string) {
  const effectiveWindow = getEffectiveContextWindowSize(model)
  const percentLeft = 1 - tokenUsage / effectiveWindow

  return {
    percentLeft,
    isAboveWarningThreshold: tokenUsage > effectiveWindow - WARNING_THRESHOLD_BUFFER_TOKENS,
    isAboveErrorThreshold: tokenUsage > effectiveWindow - ERROR_THRESHOLD_BUFFER_TOKENS,
    isAboveAutoCompactThreshold: tokenUsage > getAutoCompactThreshold(model),
  }
}

// ========== 3. 压缩执行 ==========

// 熔断器：连续失败后停止重试
const MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3

async function autocompact(
  messages: Message[],
  toolUseContext: ToolUseContext,
  cacheSafeParams: CacheSafeParams,
  querySource: QuerySource,
  tracking: AutoCompactTrackingState | undefined,
  snipTokensFreed: number,  // snip 已释放的 tokens
): Promise<{
  compactionResult: CompactionResult | undefined
  consecutiveFailures: number
}> {
  // 检查是否应该压缩
  const tokenCount = tokenCountWithEstimation(messages) - snipTokensFreed
  const threshold = getAutoCompactThreshold(model)

  if (tokenCount < threshold) {
    return { compactionResult: undefined, consecutiveFailures: 0 }
  }

  // 检查熔断器
  if ((tracking?.consecutiveFailures ?? 0) >= MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES) {
    return { compactionResult: undefined, consecutiveFailures: tracking.consecutiveFailures }
  }

  // 执行压缩
  try {
    const result = await compactConversation(messages, cacheSafeParams)
    return { compactionResult: result, consecutiveFailures: 0 }
  } catch (error) {
    // 累计失败次数
    return {
      compactionResult: undefined,
      consecutiveFailures: (tracking?.consecutiveFailures ?? 0) + 1,
    }
  }
}
```

## 注释

### 多层策略的设计理由

| 层 | 问题 | 解法 | 成本 |
|---|------|------|-----|
| Tool Result Budget | 单个工具输出太大 | 限制每个结果的最大大小 | 无（裁剪） |
| Snip Compact | 早期历史不再需要 | 裁剪到最近 N 轮 | 无（裁剪） |
| Microcompact | 工具输出冗余 | 智能压缩工具输出 | 低（规则） |
| Context Collapse | 相关消息可合并 | 折叠相关上下文 | 中（LLM） |
| Auto Compact | 整体超限 | 全历史摘要 | 高（LLM） |

### 关键设计决策

1. **层次独立**
   - 每层有自己的触发条件
   - 一层失败不影响其他层
   - 可以通过 feature flag 单独开关

2. **熔断器模式**
   - 连续失败 3 次后停止重试
   - 避免在不可恢复的情况下浪费 API 调用
   - BQ 分析：之前有会话连续失败 3000+ 次

3. **snipTokensFreed 传递**
   - snip 释放的 tokens 传给 autocompact
   - 让 autocompact 的阈值判断更准确
   - 避免重复压缩

4. **缓冲区思维**
   - 不是等到满了才压缩
   - 预留缓冲区（13K tokens）
   - 给摘要输出预留空间（20K tokens）
