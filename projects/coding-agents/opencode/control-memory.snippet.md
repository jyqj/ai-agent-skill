# Control & Memory 实现

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

## 来源
`/Users/jin/Desktop/knode/opencode/packages/opencode/src/`

## 关键点
OpenCode 实现了完整的权限控制系统和持久化存储，是 Control Layer 和 Memory 的工业级参考。

---

## 1. 三层权限模型

### 来源
`permission/index.ts`

### 代码
```typescript
export namespace Permission {
  // 权限动作
  export const Action = z.enum(["allow", "deny", "ask"])

  // 权限规则
  export const Rule = z.object({
    permission: z.string(),  // 工具 ID 或类别
    pattern: z.string(),     // glob pattern
    action: Action,
  })

  // 权限规则集
  export type Ruleset = z.infer<typeof Rule>[]

  // 示例规则集
  const DEFAULT_RULESET: Ruleset = [
    { permission: "*", pattern: "*", action: "ask" },           // 默认询问
    { permission: "read", pattern: "*.env", action: "ask" },    // 敏感文件
    { permission: "read", pattern: "*.env.example", action: "allow" },
    { permission: "bash", pattern: "rm *", action: "ask" },     // 危险命令
    { permission: "external_directory", pattern: "*", action: "ask" },
  ]
}
```

### 注释
- 三级权限：`deny > ask > allow`
- 规则支持通配符：`*` 匹配任意，`?` 匹配单字符
- 规则集可叠加（默认 → 用户 → 代理）

---

## 2. 权限评估逻辑

### 来源
`permission/evaluate.ts`

### 代码
```typescript
export namespace Permission {
  // Last-match-wins 评估策略
  export function evaluate(
    permission: string,
    pattern: string,
    ...rulesets: Ruleset[]
  ): Rule {
    const rules = rulesets.flat()

    // 从后向前找最后匹配的规则
    const match = rules.findLast((rule) =>
      Wildcard.match(permission, rule.permission) &&
      Wildcard.match(pattern, rule.pattern)
    )

    // 默认返回 ask
    return match ?? { action: "ask", permission, pattern: "*" }
  }

  // 检查是否禁用
  export function disabled(permission: string, ruleset?: Ruleset): boolean {
    if (!ruleset) return false
    const result = evaluate(permission, "*", ruleset)
    return result.action === "deny"
  }
}

// 通配符匹配
export namespace Wildcard {
  export function match(input: string, pattern: string): boolean {
    if (pattern === "*") return true

    // 转换为正则表达式
    const regex = pattern
      .replace(/[.+^${}()|[\]\\]/g, "\\$&")  // 转义特殊字符
      .replace(/\*/g, ".*")                   // * → .*
      .replace(/\?/g, ".")                    // ? → .

    return new RegExp(`^${regex}$`).test(input)
  }
}
```

### 注释
- `findLast` 实现 last-match-wins
- 通配符转正则表达式匹配
- 无匹配时默认 `ask`

---

## 3. 异步权限请求

### 来源
`permission/index.ts`

### 代码
```typescript
export namespace Permission {
  // 权限请求结构
  export const Request = z.object({
    id: PermissionID.zod,
    sessionID: SessionID.zod,
    tool: z.string(),
    permission: z.string(),
    patterns: z.array(z.string()),   // 实际匹配的模式
    always: z.array(z.string()),     // 永久记住的模式
    metadata: z.record(z.unknown()).optional(),
  })

  // 权限回复
  export const Reply = z.discriminatedUnion("action", [
    z.object({ action: z.literal("once") }),     // 仅本次
    z.object({ action: z.literal("always") }),   // 永久允许
    z.object({ action: z.literal("reject") }),   // 拒绝
  ])

  // 内部状态
  interface PendingEntry {
    info: Request
    deferred: Deferred.Deferred<void, RejectedError | CorrectedError>
  }

  interface State {
    pending: Map<PermissionID, PendingEntry>
    approved: Ruleset  // 运行时批准的规则
  }

  // 请求权限
  export const ask = Effect.fn("Permission.ask")(function* (request: Request) {
    const state = yield* getState()

    // 先检查已批准的规则
    for (const pattern of request.patterns) {
      const result = evaluate(request.permission, pattern, state.approved)
      if (result.action === "allow") continue
      if (result.action === "deny") {
        return yield* Effect.fail(new RejectedError(request))
      }
      // action === "ask"，继续下面的流程
    }

    // 创建 Deferred 等待用户回复
    const deferred = yield* Deferred.make<void, RejectedError | CorrectedError>()
    state.pending.set(request.id, { info: request, deferred })

    // 发布事件通知 UI
    yield* Bus.publish(Permission.Event.Asked, request)

    // 等待回复
    return yield* Deferred.await(deferred)
  })

  // 回复权限请求
  export const reply = Effect.fn("Permission.reply")(function* (
    id: PermissionID,
    response: Reply
  ) {
    const state = yield* getState()
    const entry = state.pending.get(id)
    if (!entry) return

    state.pending.delete(id)

    switch (response.action) {
      case "once":
        // 仅本次允许，不修改规则集
        yield* Deferred.succeed(entry.deferred, undefined)
        break

      case "always":
        // 永久允许，添加到 approved 规则集
        for (const pattern of entry.info.always) {
          state.approved.push({
            permission: entry.info.permission,
            pattern,
            action: "allow",
          })
        }
        yield* Deferred.succeed(entry.deferred, undefined)
        break

      case "reject":
        yield* Deferred.fail(entry.deferred, new RejectedError(entry.info))
        break
    }

    // 发布事件通知 UI
    yield* Bus.publish(Permission.Event.Replied, { id, response })
  })
}
```

### 注释
- `Deferred` 实现异步等待
- `once` vs `always`：临时批准 vs 永久规则
- `pending` Map 跟踪所有进行中的请求

---

## 4. 会话状态管理

### 来源
`session/index.ts`

### 代码
```typescript
export namespace Session {
  // 会话信息结构
  export const Info = z.object({
    id: SessionID.zod,
    slug: z.string(),
    projectID: ProjectID.zod,
    workspaceID: WorkspaceID.zod.optional(),
    parentID: SessionID.zod.optional(),       // 父会话（子代理）
    directory: z.string(),
    title: z.string(),
    version: z.string(),
    time: z.object({
      created: z.number(),
      updated: z.number(),
      compacting: z.number().optional(),      // 压缩中
      archived: z.number().optional(),        // 已归档
    }),
    summary: z.object({
      additions: z.number().optional(),
      deletions: z.number().optional(),
      files: z.number().optional(),
      diffs: Snapshot.FileDiff.array().optional(),
    }).optional(),
    share: z.object({ url: z.string() }).optional(),
    permission: Permission.Ruleset.optional(), // 会话级权限覆盖
    revert: z.object({
      messageID: MessageID.zod,
      time: z.number(),
    }).optional(),
  })

  // 创建会话
  export const create = Effect.fn("Session.create")(function* (input: CreateInput) {
    const id = SessionID.create()
    const slug = generateSlug()
    const now = Date.now()

    const session: Info = {
      id,
      slug,
      projectID: input.projectID,
      workspaceID: input.workspaceID,
      parentID: input.parentID,
      directory: input.directory ?? Instance.directory,
      title: input.title ?? "New Session",
      version: Version.current,
      time: { created: now, updated: now },
      permission: input.permission,
    }

    yield* db.insert(SessionTable).values(session)
    yield* Bus.publish(Session.Event.Created, { info: session })

    return session
  })

  // 分支会话
  export const fork = Effect.fn("Session.fork")(function* (
    sessionID: SessionID,
    messageID: MessageID
  ) {
    const original = yield* Session.get(sessionID)
    const messages = yield* MessageV2.listUntil(sessionID, messageID)

    // 创建新会话
    const forked = yield* Session.create({
      projectID: original.projectID,
      directory: original.directory,
      title: `Fork of ${original.title}`,
    })

    // 复制消息
    for (const msg of messages) {
      yield* MessageV2.copy(msg.id, forked.id)
    }

    return forked
  })
}
```

### 注释
- `parentID` 关联子代理会话
- `revert` 支持回退到特定消息
- `fork` 实现会话分支

---

## 5. 持久化存储 (SQLite + Drizzle)

### 来源
`storage/db.ts`, `session/session.sql.ts`

### 代码
```typescript
// 数据库配置
export function createDatabase(path: string) {
  const db = new Database(path)

  // WAL 模式用于并发写入
  db.run("PRAGMA journal_mode = WAL")
  db.run("PRAGMA synchronous = NORMAL")
  db.run("PRAGMA foreign_keys = ON")
  db.run("PRAGMA busy_timeout = 5000")
  db.run("PRAGMA wal_checkpoint(PASSIVE)")

  return db
}

// 核心表结构
export const SessionTable = sqliteTable("session", {
  id: text("id").primaryKey(),
  project_id: text("project_id").references(() => ProjectTable.id),
  workspace_id: text("workspace_id"),
  parent_id: text("parent_id"),
  slug: text("slug").notNull(),
  directory: text("directory").notNull(),
  title: text("title").notNull(),
  version: text("version").notNull(),
  share_url: text("share_url"),
  summary_additions: integer("summary_additions"),
  summary_deletions: integer("summary_deletions"),
  summary_files: integer("summary_files"),
  permission: text("permission", { mode: "json" }),  // JSON 存储规则集
  time_created: integer("time_created").notNull(),
  time_updated: integer("time_updated").notNull(),
  time_compacting: integer("time_compacting"),
  time_archived: integer("time_archived"),
  revert_message_id: text("revert_message_id"),
  revert_time: integer("revert_time"),
})

export const MessageTable = sqliteTable("message", {
  id: text("id").primaryKey(),
  session_id: text("session_id").references(() => SessionTable.id),
  time_created: integer("time_created").notNull(),
  data: text("data", { mode: "json" }).notNull(),  // JSON 存储消息内容
})

export const PartTable = sqliteTable("part", {
  id: text("id").primaryKey(),
  message_id: text("message_id").references(() => MessageTable.id),
  session_id: text("session_id"),
  time_created: integer("time_created").notNull(),
  data: text("data", { mode: "json" }).notNull(),  // JSON 存储部分内容
})

export const PermissionTable = sqliteTable("permission", {
  project_id: text("project_id").primaryKey(),
  data: text("data", { mode: "json" }).notNull(),  // JSON 存储规则集
})

export const TodoTable = sqliteTable("todo", {
  session_id: text("session_id").notNull(),
  position: integer("position").notNull(),
  content: text("content").notNull(),
  status: text("status").notNull(),  // pending, in_progress, completed
  priority: text("priority"),
}, (table) => ({
  pk: primaryKey({ columns: [table.session_id, table.position] }),
}))
```

### 注释
- WAL 模式支持并发读写
- JSON 列存储复杂对象（permission, message data）
- 外键约束保证数据完整性

---

## 6. 客户端缓存 (LRU)

### 来源
`packages/app/src/context/global-sync/session-cache.ts`

### 代码
```typescript
const SESSION_CACHE_LIMIT = 40  // 最多缓存 40 个会话

type SessionCache = {
  session_status: Record<string, SessionStatus | undefined>
  session_diff: Record<string, FileDiff[] | undefined>
  todo: Record<string, Todo[] | undefined>
  message: Record<string, Message[] | undefined>
  part: Record<string, Part[] | undefined>
  permission: Record<string, PermissionRequest[] | undefined>
  question: Record<string, QuestionRequest[] | undefined>
}

// LRU 驱逐策略
export function pickSessionCacheEvictions(
  sessions: Session[],
  limit: number
): SessionID[] {
  if (sessions.length <= limit) return []

  // 按最后更新时间排序
  const sorted = [...sessions].sort((a, b) =>
    b.time.updated - a.time.updated
  )

  // 保留最近的 limit 个，驱逐其余
  return sorted.slice(limit).map(s => s.id)
}

// 驱逐缓存
export function dropSessionCaches(
  store: Store,
  setStore: SetStore,
  sessionIDs: SessionID[]
) {
  const ids = new Set(sessionIDs)

  for (const key of Object.keys(store.sessionCache)) {
    const cache = store.sessionCache[key as keyof SessionCache]
    for (const id of Object.keys(cache)) {
      if (ids.has(id)) {
        setStore("sessionCache", key, id, undefined)
      }
    }
  }
}
```

### 注释
- 限制 40 个会话缓存
- 按 `time.updated` 排序实现 LRU
- 驱逐时清理所有相关缓存（status, diff, todo, message, part 等）

---

## 7. 事件总线 (Bus)

### 来源
`bus/index.ts`

### 代码
```typescript
export namespace Bus {
  export interface Interface {
    readonly publish: <D extends BusEvent.Definition>(
      def: D,
      properties: z.output<D["properties"]>
    ) => Effect.Effect<void>

    readonly subscribe: <D extends BusEvent.Definition>(
      def: D
    ) => Stream.Stream<Payload<D>>

    readonly subscribeAll: () => Stream.Stream<Payload>
  }

  // 事件定义
  export namespace BusEvent {
    export interface Definition {
      name: string
      properties: z.ZodType
    }
  }

  // 内置事件
  export namespace Session {
    export const Created = BusEvent.define("session.created", z.object({
      info: Session.Info,
    }))
    export const Updated = BusEvent.define("session.updated", z.object({
      info: Session.Info,
    }))
    export const Deleted = BusEvent.define("session.deleted", z.object({
      id: SessionID.zod,
    }))
  }

  export namespace Permission {
    export const Asked = BusEvent.define("permission.asked", Permission.Request)
    export const Replied = BusEvent.define("permission.replied", z.object({
      id: PermissionID.zod,
      response: Permission.Reply,
    }))
  }

  // Effect 实现
  export const layer = Layer.effect(Service, Effect.gen(function* () {
    const pubsub = yield* PubSub.unbounded<Payload>()

    return {
      publish: (def, properties) => PubSub.publish(pubsub, {
        name: def.name,
        properties,
        time: Date.now(),
      }),

      subscribe: (def) => Stream.fromPubSub(pubsub).pipe(
        Stream.filter(event => event.name === def.name)
      ),

      subscribeAll: () => Stream.fromPubSub(pubsub),
    }
  }))
}
```

### 注释
- 基于 Effect PubSub 实现
- 类型安全的事件定义
- 支持单事件订阅和全局订阅

---

## 8. 配置系统

### 来源
`config/config.ts`

### 代码
```typescript
export namespace Config {
  // 配置优先级（高→低）
  // 1. 系统管理配置：/Library/Application Support/opencode (macOS) 或 /etc/opencode (Linux)
  // 2. 项目配置：.opencode/ 目录
  // 3. 用户配置：~/.opencode/ 目录

  export async function load(): Promise<Info> {
    const configs: Info[] = []

    // 1. 用户配置
    const userDir = path.join(os.homedir(), ".opencode")
    if (await exists(path.join(userDir, "config.json"))) {
      configs.push(await readJson(path.join(userDir, "config.json")))
    }

    // 2. 项目配置
    const projectDir = path.join(Instance.directory, ".opencode")
    if (await exists(path.join(projectDir, "config.json"))) {
      configs.push(await readJson(path.join(projectDir, "config.json")))
    }

    // 3. 系统配置
    const systemDir = process.platform === "darwin"
      ? "/Library/Application Support/opencode"
      : "/etc/opencode"
    if (await exists(path.join(systemDir, "config.json"))) {
      configs.push(await readJson(path.join(systemDir, "config.json")))
    }

    // 合并配置（后者覆盖前者，数组拼接）
    return configs.reduce(mergeConfigConcatArrays, DEFAULT_CONFIG)
  }

  function mergeConfigConcatArrays(target: Info, source: Info): Info {
    const merged = mergeDeep(target, source)

    // 数组字段拼接而非覆盖
    if (target.plugin && source.plugin) {
      merged.plugin = Array.from(new Set([...target.plugin, ...source.plugin]))
    }
    if (target.instructions && source.instructions) {
      merged.instructions = Array.from(new Set([...target.instructions, ...source.instructions]))
    }

    return merged
  }
}
```

### 注释
- 三层配置：用户 → 项目 → 系统
- 对象深合并，数组拼接去重
- 支持 `plugin` 和 `instructions` 数组扩展

---

## 设计模式总结

| 模式 | 实现 | 效果 |
|------|------|------|
| 三层权限 | deny > ask > allow | 灵活的权限控制 |
| Last-match-wins | `findLast` 评估 | 规则可叠加覆盖 |
| 异步等待 | `Deferred` | 非阻塞权限请求 |
| LRU 缓存 | 40 会话限制 | 内存控制 |
| 事件驱动 | Bus PubSub | 解耦前后端 |
| 配置合并 | 深合并 + 数组拼接 | 灵活扩展 |
