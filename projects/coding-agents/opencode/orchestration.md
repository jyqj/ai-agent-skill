# Orchestration 实现

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

## 来源
`/Users/jin/Desktop/knode/opencode/packages/opencode/src/`

## 关键点
OpenCode 实现了完整的多代理编排系统，包括 Agent 循环、子代理、状态机和长时运行任务处理。

---

## 1. Agent 定义与模式

### 来源
`agent/agent.ts`

### 代码
```typescript
export namespace Agent {
  // Agent 三种模式
  export const Mode = z.enum(["primary", "subagent", "all"])

  // Agent 信息结构
  export const Info = z.object({
    id: AgentID.zod,
    name: z.string(),
    mode: Mode,
    model: z.object({
      providerID: ProviderID.zod,
      modelID: ModelID.zod,
    }).optional(),
    prompt: z.string().optional(),           // 自定义 system prompt
    permission: Permission.Ruleset.optional(), // 权限覆盖
    steps: z.number().optional(),             // 最大步骤数
    hidden: z.boolean().optional(),           // 隐藏代理
  })

  // 7 个内置代理
  const BUILTIN_AGENTS = {
    build: {
      name: "build",
      mode: "primary",
      prompt: "You are a coding agent...",
      permission: { "*": "ask", "read": "allow" },
    },
    plan: {
      name: "plan",
      mode: "primary",
      prompt: "You are a planning agent...",
      permission: { "*": "deny", "read": "allow", "glob": "allow", "grep": "allow" },
    },
    general: {
      name: "general",
      mode: "subagent",
      prompt: "You are a general-purpose agent...",
    },
    explore: {
      name: "explore",
      mode: "subagent",
      prompt: "You are a code exploration expert...",
      permission: { "*": "deny", "read": "allow", "glob": "allow", "grep": "allow" },
    },
    compaction: { mode: "all", hidden: true, ... },
    title: { mode: "all", hidden: true, ... },
    summary: { mode: "all", hidden: true, ... },
  }
}
```

### 注释
- **primary**: 可由用户直接启动（build, plan）
- **subagent**: 只能通过 Task 工具调用（general, explore）
- **all**: 灵活模式，两者皆可
- 隐藏代理用于系统任务（compaction, title, summary）

---

## 2. Agent 主循环

### 来源
`session/prompt.ts` L278-L762

### 代码
```typescript
export namespace SessionPrompt {
  export const loop = Effect.fn("SessionPrompt.loop")(function* (input: LoopInput) {
    const { sessionID, agent, model } = input
    let step = 0
    const maxSteps = agent.steps ?? Infinity

    while (true) {
      step++

      // 1. 检查退出条件
      const lastMsg = yield* MessageV2.latest(sessionID)
      if (lastMsg?.finish && !["tool_calls", "unknown"].includes(lastMsg.finish)) {
        break  // stop, max_tokens, error 等都退出
      }

      // 2. 检查待处理任务
      const subtask = yield* getSubtask(sessionID)
      if (subtask?.type === "subtask") {
        yield* executeSubtask(subtask)
        continue
      }
      if (subtask?.type === "compaction") {
        yield* SessionCompaction.run(subtask)
        continue
      }

      // 3. 检查上下文溢出
      if (isOverflow({ tokens: lastMsg.tokens, model })) {
        yield* SessionCompaction.create(sessionID, { auto: true })
        continue
      }

      // 4. 创建并运行 processor
      const processor = yield* SessionProcessor.create(input)
      const result = yield* processor.process()

      // 5. 循环决策
      switch (result) {
        case "stop":
          return  // 退出循环
        case "compact":
          yield* SessionCompaction.create(sessionID, { auto: true })
          continue
        case "continue":
          if (step >= maxSteps) {
            // 最后一步注入提示
            yield* MessageV2.appendSynthetic(sessionID, {
              role: "assistant",
              content: "You have reached the maximum number of steps...",
            })
            return
          }
          continue
      }
    }
  })
}
```

### 注释
- 无限循环 + 多种退出条件
- 子任务优先处理（subtask > compaction > normal）
- 步骤限制 `maxSteps` 防止无限执行

---

## 3. 子代理执行 (Task Tool)

### 来源
`tool/task.ts`

### 代码
```typescript
export const TaskTool = Tool.define("task", async (ctx) => ({
  description: "Launch a subagent to handle a specific task...",
  parameters: z.object({
    description: z.string().describe("Clear description of the task"),
    agent: z.string().optional().describe("Subagent name (default: general)"),
    task_id: z.string().optional().describe("Resume existing task"),
  }),

  async execute(params, ctx) {
    // 1. 解析目标代理
    const targetAgent = params.agent ?? "general"
    const agentInfo = await Agent.get(targetAgent)

    // 2. 创建或恢复会话
    const session = params.task_id
      ? await Session.get(params.task_id)
      : await Session.create({
          parentID: ctx.sessionID,  // 关联父会话
          title: `${params.description} (@${agentInfo.name} subagent)`,
          permission: agentInfo.permission,  // 继承代理权限
        })

    // 3. 创建用户消息
    await MessageV2.create({
      sessionID: session.id,
      role: "user",
      parts: [{ type: "text", text: params.description }],
    })

    // 4. 递归调用 SessionPrompt.prompt
    const result = await SessionPrompt.prompt({
      sessionID: session.id,
      agent: agentInfo,
      model: ctx.model,  // 继承模型
    })

    // 5. 收集结果
    const messages = await MessageV2.list(session.id)
    const output = messages
      .filter(m => m.role === "assistant")
      .map(m => m.parts.filter(p => p.type === "text").map(p => p.text).join(""))
      .join("\n")

    return {
      title: `Completed task: ${params.description}`,
      output,
      metadata: { task_id: session.id },
    }
  },
}))
```

### 注释
- 创建独立子会话，`parentID` 关联父会话
- 支持 `task_id` 恢复已有任务
- 递归调用 `SessionPrompt.prompt`
- 返回 `task_id` 供后续恢复

---

## 4. 会话状态机

### 来源
`session/status.ts`

### 代码
```typescript
export namespace SessionStatus {
  // 状态定义
  export type Status =
    | { type: "idle" }
    | { type: "busy" }
    | { type: "retry"; attempt: number; message: string; next: number }

  // 状态存储
  const state = Instance.state(() => ({
    status: new Map<SessionID, Status>(),
  }))

  // 状态转换
  export function set(sessionID: SessionID, status: Status) {
    state.get().status.set(sessionID, status)
    Bus.publish(SessionStatus.Event.Updated, { sessionID, status })
  }

  export function get(sessionID: SessionID): Status {
    return state.get().status.get(sessionID) ?? { type: "idle" }
  }
}

// 状态转换流程
/*
idle
  ↓ (开始处理)
busy
  ├→ (失败可重试) retry { attempt: N, message, next: timestamp }
  │    ↓ (等待后)
  │  busy (重试)
  └→ (完成/失败) idle
*/
```

### 注释
- 三状态：idle → busy → retry → idle
- `retry.next` 存储下次重试时间戳
- 通过 Bus 发布状态变更事件

---

## 5. 消息部分状态

### 来源
`session/message-v2.ts`

### 代码
```typescript
export namespace MessageV2 {
  // 工具部分状态
  export const ToolPartState = z.object({
    status: z.enum(["pending", "running", "completed", "failed"]),
    output: z.string(),
    error: z.string().optional(),
    time: z.object({
      created: z.number(),
      start: z.number().optional(),
      end: z.number().optional(),
      compacted: z.number().optional(),
    }),
    attachments: z.array(FilePart).optional(),
  })

  // 状态转换
  /*
  pending (创建时)
    ↓ (开始执行)
  running
    ├→ completed { output, time.end }
    └→ failed { error, time.end }
  */
}
```

### 注释
- 四状态：pending → running → completed/failed
- `compacted` 时间戳标记已压缩的输出
- `attachments` 存储工具产生的附件（图片等）

---

## 6. Doom Loop 检测

### 来源
`session/processor.ts` L186-L210

### 代码
```typescript
export namespace SessionProcessor {
  const DOOM_LOOP_THRESHOLD = 3

  const detectDoomLoop = (toolCalls: ToolCall[], history: ToolCall[][]) => {
    if (history.length < DOOM_LOOP_THRESHOLD) return false

    // 检查最近 N 次是否调用了相同的工具
    const recent = history.slice(-DOOM_LOOP_THRESHOLD)
    const currentTools = new Set(toolCalls.map(t => t.toolName))

    return recent.every(calls => {
      const tools = new Set(calls.map(t => t.toolName))
      return [...currentTools].every(t => tools.has(t))
    })
  }

  // 在主循环中使用
  if (detectDoomLoop(toolCalls, toolCallHistory)) {
    // 触发权限检查，强制用户干预
    yield* ctx.ask({
      permission: "doom_loop",
      patterns: toolCalls.map(t => t.toolName),
      metadata: { reason: "Detected potential infinite loop" },
    })
  }
}
```

### 注释
- 连续 3 次相同工具调用触发检测
- 强制权限检查，让用户决定是否继续
- 防止 Agent 陷入无限循环

---

## 7. 智能重试策略

### 来源
`session/retry.ts`

### 代码
```typescript
export namespace SessionRetry {
  export function retryable(error: unknown): boolean {
    // 不重试的情况
    if (MessageV2.ContextOverflowError.isInstance(error)) return false
    if (!error.isRetryable) return false

    // 可重试的错误
    const message = String(error)
    return (
      message.includes("Overloaded") ||
      message.includes("Rate Limited") ||
      message.includes("too_many_requests") ||
      message.includes("exhausted") ||
      message.includes("unavailable")
    )
  }

  export function delay(attempt: number, error?: unknown): number {
    // 优先级：响应头 > 指数退避
    if (error?.headers?.["retry-after-ms"]) {
      const parsed = parseInt(error.headers["retry-after-ms"], 10)
      return Math.min(parsed, 2_147_483_647)  // 防止溢出
    }

    // 指数退避：2^attempt 秒，最多 30 秒
    return Math.min(2000 * Math.pow(2, attempt - 1), 30_000)
  }

  export function policy(options: PolicyOptions) {
    return Schedule.exponential(Duration.seconds(2)).pipe(
      Schedule.whileInput((error) => retryable(error)),
      Schedule.tapInput((error) => {
        const info = {
          attempt: Schedule.currentAttempt(),
          message: options.parse(error).message,
          next: Date.now() + delay(Schedule.currentAttempt(), error),
        }
        options.set(info)
      }),
    )
  }
}
```

### 注释
- 区分可重试和不可重试错误
- 响应头 `retry-after-ms` 优先
- 指数退避：2s → 4s → 8s → 16s → 30s (cap)

---

## 8. Processor 流事件处理

### 来源
`session/processor.ts`

### 代码
```typescript
export namespace SessionProcessor {
  export type Result = "compact" | "stop" | "continue"

  interface ProcessorContext {
    toolcalls: Record<string, MessageV2.ToolPart>
    shouldBreak: boolean
    snapshot: string | undefined
    blocked: boolean
    needsCompaction: boolean
    currentText: MessageV2.TextPart | undefined
    reasoningMap: Record<string, MessageV2.ReasoningPart>
  }

  const handleEvent = Effect.fn("handleEvent")(function* (event: StreamEvent, ctx: ProcessorContext) {
    switch (event.type) {
      case "start":
        yield* SessionStatus.set(ctx.sessionID, { type: "busy" })
        return

      case "reasoning-start":
        ctx.reasoningMap[event.id] = {
          type: "reasoning",
          text: "",
          time: { start: Date.now() },
          metadata: event.providerMetadata,
        }
        return

      case "reasoning-delta":
        ctx.reasoningMap[event.id].text += event.text
        return

      case "text-delta":
        if (!ctx.currentText) {
          ctx.currentText = { type: "text", text: "", time: { start: Date.now() } }
        }
        ctx.currentText.text += event.text
        return

      case "tool-call":
        ctx.toolcalls[event.callId] = {
          type: "tool",
          tool: event.toolName,
          input: JSON.stringify(event.args),
          state: { status: "pending", time: { created: Date.now() } },
        }
        return

      case "finish":
        // 检查是否触发压缩
        if (isOverflow({ tokens: event.usage, model: ctx.model })) {
          ctx.needsCompaction = true
          return "compact"
        }
        return "continue"

      case "error":
        ctx.blocked = true
        return "stop"
    }
  })
}
```

### 注释
- 流事件类型：start, reasoning-*, text-delta, tool-call, finish, error
- reasoning 单独追踪（支持 o1/o3 等 reasoning 模型）
- 返回值驱动主循环决策

---

## 9. Effect.js 三段式桥接架构

### 来源
`tool/*.ts`, `session/prompt.ts`, `provider/index.ts`

### 架构
```text
Interface 层 (Zod Schema + 类型定义)
    ↓
Layer 层 (Effect Service + 依赖注入)
    ↓
静态门面 (namespace 导出的 Effect.fn)
```

### 注释
- **Interface 层**：每个模块用 `z.object()` 定义数据结构和 `namespace` 暴露类型，不含副作用。
- **Layer 层**：用 `Effect.Service` + `Layer.effect` 包装实际实现，声明依赖（DB、Bus、Config 等），由 Effect Runtime 自动注入。
- **静态门面**：用 `Effect.fn("Module.method")` 封装，调用方不感知 Effect 内部，直接 `yield*` 即可。
- 这种三段式让每一层可独立测试和替换——Interface 做 mock、Layer 做 stub、门面做集成。

---

## 10. Doom Loop 实际匹配逻辑

### 来源
`session/processor.ts`

### 补充
上文第 6 节的 Doom Loop 检测，实际匹配逻辑更严格：

```typescript
// 比较的是「工具名 + 参数 JSON」全等，而非仅工具名
const serialize = (call: ToolCall) => `${call.toolName}:${JSON.stringify(call.args)}`
const currentKey = toolCalls.map(serialize).sort().join("|")

// 范围：单条 assistant message 内的全部 tool_calls
// 如果最近 DOOM_LOOP_THRESHOLD 条 assistant message 的 serialized key 完全相同，触发
```

### 注释
- 仅按工具名检测会误报（同一工具不同参数是正常行为）。
- 全等匹配 + 参数序列化确保只在 agent 真正"原地打转"时触发。
- 作用域是单条 assistant message 内的 tool_calls 集合，跨 message 的相同调用不触发。

---

## 11. Snapshot 独立 Git

### 来源
`session/snapshot.ts`

### 代码
```typescript
export namespace Snapshot {
  // 每个会话维护独立的 git snapshot
  export const create = Effect.fn("Snapshot.create")(function* (sessionID) {
    const dir = yield* Instance.directory
    // 在 .opencode/snapshots/{sessionID}/ 下初始化独立 git repo
    // 记录当前工作区状态
    yield* Git.init(snapshotDir)
    yield* Git.addAll(snapshotDir)
    yield* Git.commit(snapshotDir, `snapshot at ${Date.now()}`)
  })

  // FileDiff 结构
  export const FileDiff = z.object({
    path: z.string(),
    type: z.enum(["added", "modified", "deleted", "renamed"]),
    additions: z.number(),
    deletions: z.number(),
  })
}
```

### 注释
- Snapshot 使用独立 git repo，不污染用户工作区的 git 历史。
- 每次会话可生成文件级 diff 摘要（additions/deletions/type）。
- 支持会话级的 revert 操作：回退到 snapshot 记录的工作区状态。

---

## 12. Batch Tool（用户态并行）

### 来源
`tool/batch.ts`

### 注释
- OpenCode 支持 Batch Tool：单次调用可并行执行最多 25 个工具。
- 与 Provider 级的 `parallel_tool_calls` 不同，Batch Tool 是**用户态编排**——由 agent 显式发起一组工具调用，框架侧并行执行。
- 内部使用 `Effect.all(..., { concurrency: 25 })` 控制并发上限。
- 每个子工具独立权限检查、独立截断、独立错误处理，单个失败不阻塞其他。

---

## 13. Plan Mode

### 来源
`agent/agent.ts`

### 注释
- Plan Agent 是内置的 primary agent，system prompt 强调"只分析不执行"。
- 权限规则集：`{ "*": "deny", "read": "allow", "glob": "allow", "grep": "allow" }` —— 禁止所有写操作。
- 用户可随时切换 build ↔ plan 模式，切换时保持会话上下文不变。
- Plan Mode 生成的计划可被后续 build agent 直接消费——计划结果作为上下文注入。

---

## 设计模式总结

| 模式 | 实现 | 效果 |
|------|------|------|
| 无限循环 + 多出口 | `while(true)` + 条件 break | 灵活的循环控制 |
| 子任务优先 | subtask > compaction > normal | 确保子任务及时处理 |
| 递归子代理 | Task Tool → SessionPrompt.prompt | 独立上下文执行 |
| 三状态机 | idle → busy → retry → idle | 清晰的状态管理 |
| Doom Loop 检测 | 工具名+参数 JSON 全等，3 次连续匹配 | 精准防止无限循环 |
| 智能重试 | 响应头 > 指数退避 | 优雅处理临时错误 |
| Effect 三段式 | Interface → Layer → 静态门面 | 可测试可替换的依赖注入 |
| Snapshot Git | 独立 git repo 记录工作区 | 不污染用户 git 历史 |
| Batch Tool | 用户态 25 并发 | 显式并行工具编排 |
| Plan Mode | 只读权限 + 分析 prompt | 安全的规划阶段 |
