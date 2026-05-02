# Tool System 实现

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

## 来源
`/Users/jin/Desktop/knode/opencode/packages/opencode/src/tool/`

## 关键点
OpenCode 的工具系统展示了工业级的工具定义、注册、执行和权限控制。

---

## 1. 工具定义接口

### 来源
`tool/tool.ts`

### 代码
```typescript
export namespace Tool {
  export interface Info<Parameters extends z.ZodType = z.ZodType> {
    id: string
    init(ctx?: InitContext): Promise<{
      description: string
      parameters: Parameters
      execute(args: z.infer<Parameters>, ctx: Context): Promise<{
        title: string
        metadata: Metadata
        output: string
        attachments?: FilePart[]
      }>
      formatValidationError?(error: z.ZodError): string
    }>
  }

  export type Context<M extends Metadata = Metadata> = {
    sessionID: SessionID
    messageID: MessageID
    agent: string
    abort: AbortSignal  // 用于取消
    callID?: string
    extra?: { [key: string]: any }
    messages: MessageV2.WithParts[]
    metadata(input: { title?: string; metadata?: Partial<M> }): void  // 流式更新元数据
    ask(input: Omit<Permission.Request, "id" | "sessionID" | "tool">): Promise<void>  // 权限请求
  }

  // 工具定义辅助函数
  export function define<T extends z.ZodType>(
    id: string,
    init: (ctx?: InitContext) => Promise<{ description: string; parameters: T; execute: ... }>
  ): Info<T>
}
```

### 注释
- 异步初始化上下文（支持动态加载）
- Zod 进行参数 schema 验证
- 统一的工具执行管道：验证 → 执行 → 截断

---

## 2. 工具注册系统

### 来源
`tool/registry.ts`

### 代码
```typescript
export namespace ToolRegistry {
  // 三层注册机制
  const state = Instance.state(async () => {
    const dir = Instance.directory

    // 1. 扫描本地工具 {tool,tools}/*.{js,ts}
    const matches = Glob.scanSync("{tool,tools}/*.{js,ts}", { cwd: dir })
    for (const match of matches) {
      const full = path.resolve(dir, match)
      const mod = await import(full)
      // 导出为 default 或 named export
      const tool = mod.default ?? mod[Object.keys(mod)[0]]
      if (tool?.id) tools.set(tool.id, tool)
    }

    // 2. 内置工具
    const builtins = [
      BashTool, ReadTool, GlobTool, GrepTool, EditTool, WriteTool,
      WebFetchTool, WebSearchTool, CodeSearchTool, SkillTool, TaskTool,
      TodoWriteTool, ApplyPatchTool, LSPTool, ...
    ]

    // 3. 插件托管工具
    const plugins = yield* Plugin.getTools()

    return { tools, local: matches }
  })

  // 基于模型/权限过滤工具
  export function tools(model: Provider.Model, agent: Agent.Info) {
    const all = state.get().tools
    return Array.from(all.values()).filter(tool => {
      // codesearch/websearch 仅限 opencode 提供商
      if (["codesearch", "websearch"].includes(tool.id)) {
        return model.api.providerID === "opencode"
      }
      // apply_patch vs edit/write 基于模型
      if (tool.id === "apply_patch") {
        return !["edit", "write"].some(t => all.has(t))
      }
      // 基于 agent.permission 过滤
      if (Permission.disabled(tool.id, agent.permission)) return false
      return true
    })
  }
}
```

### 注释
- 三层工具来源：内置 → 本地插件 → 插件托管
- 运行时过滤：按 Provider、Model、Agent Permission
- `plugin.trigger("tool.definition")` 钩子可修改工具定义

---

## 3. Bash 工具执行

### 来源
`tool/bash.ts`

### 代码
```typescript
export const BashTool = Tool.define("bash", async (ctx) => ({
  description: "Execute shell commands...",
  parameters: z.object({
    command: z.string(),
    timeout: z.number().optional(),
  }),

  async execute(params, ctx) {
    // 1. 使用 tree-sitter 解析命令（Bash/PowerShell）
    const parsed = parseCommand(params.command)

    // 2. 检测文件操作（rm/cp/mv/mkdir）并请求权限
    const fileOps = detectFileOperations(parsed)
    if (fileOps.length > 0) {
      await ctx.ask({
        permission: "bash",
        patterns: fileOps,
        always: ["..."],
      })
    }

    // 3. 执行命令
    const proc = launch(shell, name, params.command, cwd, env)

    // 4. 实时流式输出
    for await (const chunk of proc.stdout) {
      output += chunk
      ctx.metadata({ output: Truncate.output(output) })
    }

    // 5. 超时控制（默认 120s）
    const timeout = params.timeout ?? 120_000
    const result = await Promise.race([
      proc.exited,
      sleep(timeout).then(() => "timeout"),
    ])

    if (result === "timeout") {
      processTree.killTree(proc.pid)
      throw new Error("Command timed out")
    }

    return { title: "Executed command", output }
  },
}))

// 进程管理
function launch(shell, name, command, cwd, env) {
  const proc = spawn(shell, ["-c", command], {
    cwd,
    env: { ...process.env, ...env },
    stdio: ["ignore", "pipe", "pipe"],
  })

  // 取消支持
  ctx.abort.addEventListener("abort", () => {
    processTree.killTree(proc.pid, "SIGTERM")
  })

  return proc
}
```

### 注释
- tree-sitter 解析命令，检测文件操作
- 双阶段超时：SIGTERM + 5s 后 SIGKILL
- 进程树杀死（不只是父进程）

---

## 4. Edit 工具 - 9 种匹配策略

### 来源
`tool/edit.ts`

### 代码
```typescript
// 9 种匹配策略，逐级降级
const replacers = [
  SimpleReplacer,              // 1. 精确匹配
  LineTrimmedReplacer,         // 2. 行级 trim
  BlockAnchorReplacer,         // 3. 上下文锚点（Levenshtein 相似度）
  WhitespaceNormalizedReplacer,// 4. 空白标准化
  IndentationFlexibleReplacer, // 5. 缩进忽略
  EscapeNormalizedReplacer,    // 6. 转义序列标准化
  TrimmedBoundaryReplacer,     // 7. 边界 trim
  ContextAwareReplacer,        // 8. 多行上下文感知
  MultiOccurrenceReplacer,     // 9. 全局替换
]

export const EditTool = Tool.define("edit", async (ctx) => ({
  description: "Edit file content by replacing text...",
  parameters: z.object({
    file_path: z.string(),
    old_string: z.string(),
    new_string: z.string(),
    replace_all: z.boolean().optional(),
  }),

  async execute(params, ctx) {
    const content = await Filesystem.read(params.file_path)

    // 逐级尝试匹配策略
    for (const Replacer of replacers) {
      const result = Replacer.replace(content, params.old_string, params.new_string)
      if (result.success) {
        await Filesystem.write(params.file_path, result.content)

        // 生成 diff
        const diff = createTwoFilesPatch(
          params.file_path, params.file_path,
          content, result.content,
        )

        return {
          title: `Edited ${params.file_path}`,
          output: diff,
          metadata: { strategy: Replacer.name },
        }
      }
    }

    throw new Error("No matching strategy found")
  },
}))

// BlockAnchorReplacer 示例
class BlockAnchorReplacer {
  static replace(content, old, new_) {
    // 使用 Levenshtein 相似度找到最佳匹配位置
    const lines = content.split("\n")
    const oldLines = old.split("\n")

    let bestMatch = { index: -1, score: 0 }
    for (let i = 0; i <= lines.length - oldLines.length; i++) {
      const candidate = lines.slice(i, i + oldLines.length).join("\n")
      const score = levenshteinSimilarity(candidate, old)
      if (score > bestMatch.score && score > 0.8) {
        bestMatch = { index: i, score }
      }
    }

    if (bestMatch.index >= 0) {
      lines.splice(bestMatch.index, oldLines.length, ...new_.split("\n"))
      return { success: true, content: lines.join("\n") }
    }
    return { success: false }
  }
}
```

### 注释
- 从严格到宽松，9 种策略逐级降级
- BlockAnchorReplacer 使用 Levenshtein 相似度 > 0.8
- 生成 unified diff 作为输出

---

## 5. MCP 工具集成

### 来源
`mcp/index.ts`

### 代码
```typescript
export namespace MCP {
  const DEFAULT_TIMEOUT = 30_000

  // MCP 工具转换为 AI SDK Tool
  function convertMcpTool(mcpTool: MCPToolDef, client: MCPClient, timeout?: number): Tool {
    const inputSchema = mcpTool.inputSchema
    const schema: JSONSchema7 = {
      ...(inputSchema as JSONSchema7),
      type: "object",
      properties: (inputSchema.properties ?? {}) as JSONSchema7["properties"],
      additionalProperties: false,
    }

    return dynamicTool({
      description: mcpTool.description ?? "",
      inputSchema: jsonSchema(schema),
      execute: async (args: unknown) => {
        return client.callTool({
          name: mcpTool.name,
          arguments: args as Record<string, unknown>,
        }).pipe(withTimeout(timeout ?? DEFAULT_TIMEOUT))
      },
    })
  }

  // MCP 状态管理
  export const Status = z.discriminatedUnion("status", [
    z.object({ status: z.literal("connected") }),
    z.object({ status: z.literal("disabled") }),
    z.object({ status: z.literal("failed"), error: z.string() }),
    z.object({ status: z.literal("needs_auth") }),
  ])

  // OAuth 流程
  export async function authenticate(mcpName: string) {
    const { authorizationUrl, oauthState } = await startAuth()
    open(authorizationUrl)  // 打开浏览器
    const code = await waitForCallback(oauthState)  // HTTP 服务器捕获重定向
    await finishAuth(code)
    await reconnect(mcpName)
  }
}
```

### 注释
- JSON Schema 转换为 AI SDK Tool
- 超时保护（默认 30s）
- OAuth 流程：启动 HTTP 服务器捕获回调

---

## 6. 工具执行流程

### 来源
`session/prompt.ts`

### 代码
```typescript
// 工具调用完整流程
for (const toolCall of toolCalls) {
  // 1. 查找工具定义
  const tool = registry.get(toolCall.toolName)
  if (!tool) {
    results.push({ error: `Tool not found: ${toolCall.toolName}` })
    continue
  }

  // 2. 初始化工具
  const toolInfo = await tool.init(ctx)

  // 3. 参数验证
  let args: unknown
  try {
    args = toolInfo.parameters.parse(toolCall.arguments)
  } catch (error) {
    if (error instanceof z.ZodError && toolInfo.formatValidationError) {
      results.push({ error: toolInfo.formatValidationError(error) })
    } else {
      results.push({ error: `Invalid arguments: ${error.message}` })
    }
    continue
  }

  // 4. 构建执行上下文
  const execCtx: Tool.Context = {
    sessionID: ctx.sessionID,
    messageID: ctx.messageID,
    agent: ctx.agent.name,
    abort: ctx.abort,
    callID: toolCall.id,
    messages: ctx.messages,
    metadata: (input) => updateMetadata(toolCall.id, input),
    ask: (input) => Permission.ask({ ...input, tool: toolCall.toolName }),
  }

  // 5. 执行工具
  try {
    const result = await toolInfo.execute(args, execCtx)

    // 6. 截断输出
    const truncated = await Truncate.output(result.output, {
      maxBytes: 50 * 1024,
      maxLines: 2000,
    }, ctx.agent)

    results.push({
      title: result.title,
      output: truncated.content,
      truncated: truncated.truncated,
      outputPath: truncated.outputPath,
    })
  } catch (error) {
    results.push({ error: error.message })
  }
}
```

### 注释
- 完整管道：查找 → 初始化 → 验证 → 构建上下文 → 执行 → 截断
- 每个工具调用有独立的 `callID`
- `ask` 方法用于权限请求

---

## 设计模式总结

| 模式 | 实现 | 效果 |
|------|------|------|
| 动态初始化 | `tool.init(ctx)` | 运行时参数注入 |
| Zod 验证 | `parameters.parse(args)` | 类型安全、友好错误 |
| 策略模式 | 9 种 Edit 匹配器 | 优雅降级 |
| 权限上下文 | `ctx.ask()` | 细粒度权限控制 |
| 流式更新 | `ctx.metadata()` | 实时进度反馈 |
| 自动截断 | `Truncate.output()` | 防止 token 溢出 |
