# Context Engineering 实现

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

## 来源
`/Users/jin/Desktop/knode/opencode/packages/opencode/src/session/`

## 关键点
OpenCode 实现了完整的三层上下文管理策略，是 Context Engineering 的工业级参考实现。

---

## 1. System Prompt 构建

### 来源
`session/system.ts`

### 代码
```typescript
export namespace SystemPrompt {
  // 按模型动态选择 prompt
  export function provider(model: Provider.Model) {
    if (model.api.id.includes("gpt-4") || model.api.id.includes("o1") || model.api.id.includes("o3"))
      return [PROMPT_BEAST]        // GPT 高阶模型
    if (model.api.id.includes("gpt")) return [PROMPT_GPT]
    if (model.api.id.includes("gemini-")) return [PROMPT_GEMINI]
    if (model.api.id.includes("claude")) return [PROMPT_ANTHROPIC]
    return [PROMPT_DEFAULT]
  }

  // 构建环境信息块
  export async function environment(model: Provider.Model) {
    return [[
      `You are powered by the model named ${model.api.id}...`,
      `Working directory: ${Instance.directory}`,
      `Workspace root folder: ${Instance.worktree}`,
      `Is directory a git repo: ${project.vcs === "git" ? "yes" : "no"}`,
      `Platform: ${process.platform}`,
      `Today's date: ${new Date().toDateString()}`
    ].join("\n")]
  }

  // 动态加载可用 skills 列表
  export async function skills(agent: Agent.Info) {
    const list = await Skill.available(agent)
    return [Skill.fmt(list, { verbose: true })]
  }
}
```

### 注释
- 11 个模型特定的 prompt 模板：anthropic.txt, gpt.txt, beast.txt, gemini.txt 等
- System Prompt 注入点：`provider prompt → session system → user system`

---

## 2. 溢出检测

### 来源
`session/overflow.ts`

### 代码
```typescript
const COMPACTION_BUFFER = 20_000  // 保留 20K tokens 作为缓冲

export function isOverflow(input: {
  cfg: Config.Info
  tokens: MessageV2.Assistant["tokens"]
  model: Provider.Model
}) {
  if (input.cfg.compaction?.auto === false) return false

  const context = input.model.limit.context
  const count = input.tokens.total ||
    input.tokens.input + input.tokens.output +
    input.tokens.cache.read + input.tokens.cache.write

  // 计算保留缓冲
  const reserved = input.cfg.compaction?.reserved ??
    Math.min(COMPACTION_BUFFER, ProviderTransform.maxOutputTokens(input.model))

  // 计算可用预算
  const usable = input.model.limit.input
    ? input.model.limit.input - reserved
    : context - ProviderTransform.maxOutputTokens(input.model)

  return count >= usable  // 触发溢出条件
}
```

### Token 估算
```typescript
// util/token.ts
export namespace Token {
  const CHARS_PER_TOKEN = 4  // 简单线性估算

  export function estimate(input: string) {
    return Math.max(0, Math.round((input || "").length / CHARS_PER_TOKEN))
  }
}
```

### 注释
- Token 预算分配：输入预算 = context - maxOutputTokens - buffer
- 输出预算默认 32,000 tokens（可配置）
- 保留缓冲 20,000 tokens

---

## 3. 修剪策略 (Pruning)

### 来源
`session/compaction.ts` L86-132

### 代码
```typescript
const PRUNE_MINIMUM = 20_000    // 最少释放
const PRUNE_PROTECT = 40_000    // 保护阈值
const PRUNE_PROTECTED_TOOLS = ["skill"]  // 豁免工具

// 倒向遍历消息，保护最近的 2 个用户回合
loop: for (let msgIndex = msgs.length - 1; msgIndex >= 0; msgIndex--) {
  const msg = msgs[msgIndex]
  if (msg.info.role === "user") turns++
  if (turns < 2) continue  // 保护最后 2 个用户回合

  for (let partIndex = msg.parts.length - 1; partIndex >= 0; partIndex--) {
    const part = msg.parts[partIndex]
    if (part.type === "tool" && part.state.status === "completed") {
      if (PRUNE_PROTECTED_TOOLS.includes(part.tool)) continue
      // 标记为已压缩（时间戳）
      part.state.time.compacted = Date.now()
    }
  }
}
```

### 注释
- 保护最近 2 个用户回合的工具输出
- `skill` 工具的输出被豁免（保留上下文知识）
- 使用时间戳标记压缩状态，而非删除

---

## 4. 压缩策略 (Compaction with Replay)

### 来源
`session/compaction.ts` L134-340

### 代码
```typescript
const prompt = `Provide a detailed prompt for continuing our conversation above.
Focus on information that would be helpful for continuing...
---
## Goal
[What goal(s) is the user trying to accomplish?]

## Instructions
- [What important instructions did the user give...]
- [If there is a plan or spec...]

## Discoveries
[What notable things were learned...]

## Accomplished
[What work has been completed...]

## Relevant files / directories
[Construct a structured list...]
---`

// 在压缩失败时，自动回放到最后一个完整用户问题
if (result === "continue" && input.auto) {
  if (replay) {
    // 重新加载之前的用户消息和附件（除去媒体）
  }
}

// 条件化媒体剥离
const modelMessages = yield* Effect.promise(() =>
  MessageV2.toModelMessages(msgs, model, { stripMedia: true })
)
```

### 注释
- 模板驱动的摘要生成：Goal → Instructions → Discoveries → Accomplished → Files
- 压缩失败时自动回放用户消息（除媒体外）
- `stripMedia: true` 在压缩时剥离图片等媒体内容

---

## 5. 截断策略 (Truncation)

### 来源
`tool/truncate.ts`

### 代码
```typescript
export namespace Truncate {
  export const MAX_LINES = 2000
  export const MAX_BYTES = 50 * 1024  // 50KB 阈值
  export const RETENTION = Duration.days(7)  // 保留期

  export type Result =
    | { content: string; truncated: false }
    | { content: string; truncated: true; outputPath: string }

  const output = Effect.fn("Truncate.output")(function* (
    text: string,
    options: Options = {},
    agent?: Agent.Info
  ) {
    // 逐行或逐字节累积，直到超限
    if (direction === "head") {
      for (i = 0; i < lines.length && i < maxLines; i++) {
        const size = Buffer.byteLength(lines[i], "utf-8") + (i > 0 ? 1 : 0)
        if (bytes + size > maxBytes) {
          hitBytes = true
          break
        }
        out.push(lines[i])
        bytes += size
      }
    }

    // 生成提示：可选调用任务工具处理完整文件
    const hint = hasTaskTool(agent)
      ? `Use the Task tool to have explore agent process this file...`
      : `Use Grep to search the full content or Read with offset/limit...`
  })
}
```

### 注释
- 双重限制：50KB 字节 OR 2000 行
- 支持 head/tail 两种方向
- 超限时写入文件，返回文件路径和处理提示
- 保留期 7 天后自动清理

---

## 6. 消息结构与多轮对话

### 来源
`session/message-v2.ts`

### 代码
```typescript
export namespace MessageV2 {
  // 部分类型
  export const TextPart = PartBase.extend({
    type: z.literal("text"),
    text: z.string(),
    synthetic: z.boolean().optional(),
    time: z.object({ start: z.number(), end: z.number().optional() }).optional(),
  })

  export const ToolPart = PartBase.extend({
    type: z.literal("tool"),
    tool: z.string(),
    input: z.string(),
    state: z.object({
      status: z.enum(["pending", "running", "completed", "failed"]),
      output: z.string(),
      error: z.string().optional(),
      time: z.object({
        created: z.number(),
        start: z.number().optional(),
        end: z.number().optional(),
        compacted: z.number().optional(),  // 压缩时间戳
      }),
    }),
  })

  export const CompactionPart = PartBase.extend({
    type: z.literal("compaction"),
    auto: z.boolean(),
    overflow: z.boolean().optional(),
  })

  // 转换为模型消息
  export async function toModelMessages(
    input: WithParts[],
    model: Provider.Model,
    options?: { stripMedia?: boolean },
  ): Promise<ModelMessage[]> {
    // 处理工具结果中的媒体注入
    const supportsMediaInToolResults = (() => {
      if (model.api.npm === "@ai-sdk/anthropic") return true
      if (model.api.npm === "@ai-sdk/openai") return true
      if (model.api.npm === "@ai-sdk/amazon-bedrock") return true
      return false
    })()

    // 条件化媒体处理
    const attachments = part.state.time.compacted || options?.stripMedia
      ? []
      : (part.state.attachments ?? [])
  }
}
```

### 注释
- `compacted` 时间戳用于标记已压缩的工具输出
- 媒体支持按 Provider 区分（Anthropic/OpenAI/Bedrock 支持工具结果中的媒体）
- `stripMedia` 选项用于压缩时剥离媒体

---

## 设计模式总结

| 策略 | 触发条件 | 效果 |
|------|---------|------|
| 修剪 | tokens > usable - 40K | 标记旧工具输出为 compacted |
| 压缩 | tokens > usable | LLM 生成摘要，重放用户消息 |
| 截断 | output > 50KB OR 2000行 | 写入文件，返回路径和提示 |
| 媒体剥离 | 压缩时 | 移除图片等媒体附件 |
