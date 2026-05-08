# Hooks 系统 (hooks.ts)

> **Evidence Status** — grounded. 基于 Claude Code 参考源码观察整理；代码片段仅作架构映射。

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。

## 来源
src/utils/hooks.ts
src/utils/hooks/*.ts
src/types/hooks.ts

## 关键点
Claude Code 的 hooks 是一等公民，不是事后添加的功能：
- 20+ 种 hook 事件类型
- 同步和异步 hook
- 可以注入消息、修改权限、阻止操作
- 支持 plugin hooks、skill hooks、用户自定义 hooks

## 代码

```typescript
// ========== Hook 事件类型 ==========

type HookEvent =
  // 会话生命周期
  | 'session_start'
  | 'session_end'
  | 'setup'

  // 工具执行
  | 'pre_tool_use'
  | 'post_tool_use'
  | 'post_tool_use_failure'

  // 权限
  | 'permission_request'
  | 'permission_denied'

  // 压缩
  | 'pre_compact'
  | 'post_compact'

  // 子代理
  | 'subagent_start'
  | 'subagent_stop'

  // 任务
  | 'task_created'
  | 'task_completed'

  // 用户输入
  | 'user_prompt_submit'

  // 文件变更
  | 'file_changed'
  | 'cwd_changed'

  // ... 更多事件

// ========== Hook 输入类型（每种事件不同） ==========

type PreToolUseHookInput = {
  tool_name: string
  tool_input: Record<string, unknown>
  tool_use_id: string
  session_id: string
}

type PostToolUseHookInput = PreToolUseHookInput & {
  tool_result: string
  is_error: boolean
}

type StopHookInput = {
  stop_reason: 'end_turn' | 'tool_use' | 'max_tokens'
  assistant_message: string
  session_id: string
}

// ========== Hook 输出（可以影响行为） ==========

type SyncHookJSONOutput = {
  // 阻止操作
  decision?: 'block' | 'approve'
  reason?: string

  // 修改权限
  permission_updates?: PermissionUpdate[]

  // 注入消息
  message?: string
}

type AsyncHookJSONOutput = {
  // 异步 hook 返回附件（如记忆）
  attachments?: { path: string; content: string }[]
}

// ========== Hook 执行 ==========

async function executeHook(
  hookEvent: HookEvent,
  input: HookInput,
  options: HookOptions,
): Promise<HookResult> {
  const hooks = getRegisteredHooks()
  const matchingHooks = hooks.filter(h => matchesEvent(h, hookEvent))

  const results: HookResult[] = []

  for (const hook of matchingHooks) {
    // 构建环境变量
    const env = {
      ...subprocessEnv(),
      CLAUDE_SESSION_ID: input.session_id,
      CLAUDE_HOOK_EVENT: hookEvent,
      CLAUDE_HOOK_INPUT: JSON.stringify(input),
    }

    // 执行 hook 命令
    const { stdout, stderr, exitCode } = await spawn(hook.command, {
      env,
      timeout: hook.timeout ?? DEFAULT_HOOK_TIMEOUT,
    })

    // 解析输出
    const output = parseHookOutput(stdout)

    // 处理 block 决策
    if (output?.decision === 'block') {
      return { blocked: true, reason: output.reason }
    }

    // 收集结果
    results.push({
      hook: hook.name,
      output,
      exitCode,
    })
  }

  return { blocked: false, results }
}

// ========== 特定事件的 Hook 执行器 ==========

// 工具执行前
async function executePreToolUseHooks(
  toolName: string,
  toolInput: Record<string, unknown>,
  toolUseId: string,
): Promise<{ blocked: boolean; reason?: string }> {
  const input: PreToolUseHookInput = {
    tool_name: toolName,
    tool_input: toolInput,
    tool_use_id: toolUseId,
    session_id: getSessionId(),
  }

  return executeHook('pre_tool_use', input, {
    // pre_tool_use 可以阻止工具执行
    allowBlock: true,
  })
}

// 停止时
async function executeStopHooks(
  stopReason: string,
  assistantMessage: AssistantMessage,
): Promise<{ continueLoop: boolean; injectedMessage?: string }> {
  const input: StopHookInput = {
    stop_reason: stopReason,
    assistant_message: extractTextContent(assistantMessage),
    session_id: getSessionId(),
  }

  const result = await executeHook('stop', input, {
    allowBlock: true,
  })

  // stop hook 可以注入消息强制继续
  if (result.output?.message) {
    return { continueLoop: true, injectedMessage: result.output.message }
  }

  return { continueLoop: false }
}

// 压缩前（可以保存重要信息）
async function* executePreCompactHooks(
  messages: Message[],
): AsyncGenerator<HookResultMessage> {
  const input: PreCompactHookInput = {
    messages_to_compact: messages.map(summarizeMessage),
    session_id: getSessionId(),
  }

  const result = await executeHook('pre_compact', input, {})

  // 返回 hook 产生的消息（如保存到记忆）
  for (const hookResult of result.results) {
    if (hookResult.output?.attachments) {
      for (const attachment of hookResult.output.attachments) {
        yield createHookResultMessage(attachment)
      }
    }
  }
}
```

## 注释

### Hook 的核心能力

| 能力 | 实现方式 | 用例 |
|-----|---------|-----|
| 阻止操作 | `decision: 'block'` | 安全审计、权限控制 |
| 注入消息 | `message: string` | 自验证循环、额外上下文 |
| 修改权限 | `permission_updates` | 动态授权 |
| 保存状态 | `attachments` | 压缩前保存重要信息 |

### 关键设计决策

1. **Shell 命令作为 Hook**
   - 用户可以用任何语言实现 hook
   - 输入通过环境变量和 JSON 传递
   - 输出通过 stdout JSON 返回

2. **同步 vs 异步**
   - 同步 hook 可以阻止操作
   - 异步 hook 在后台执行
   - 通过 `allowBlock` 区分

3. **层次化 Hook 来源**
   - 用户定义（settings.json）
   - Plugin 定义
   - Skill 定义
   - 内置 hook

4. **Hook 优先级**
   - 多个 hook 可以匹配同一事件
   - 任一 hook block 就停止
   - 消息按顺序聚合

### 与 Ralph Loop 的关系

stop hook 实现了 Ralph Loop：
```typescript
if (result.output?.message) {
  return { continueLoop: true, injectedMessage: result.output.message }
}
```

hook 返回 message → 注入到上下文 → 强制继续循环
