# Context Layer 架构分析


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> 来源：Claude Code 源码逆向分析
> 路径：`src/memdir/`, `src/skills/`, `src/context/`

## 1. Memory 系统 (memdir/)

### 架构设计

**核心理念：四类型分类法**
- Memory 系统采用闭合的四类型分类：`user`、`feedback`、`project`、`reference`
- 设计原则：只存储**不可从代码派生**的信息。代码模式、架构、git历史等被显式排除
- 两种存储模式：
  - **标准模式**：MEMORY.md 作为索引 + 单独的 .md 文件作为具体记录
  - **助手模式**（KAIROS）：日志追加模式，每日文件 `YYYY-MM-DD.md`，后台梦幻技能定期蒸馏

**关键数据结构**
```typescript
// memoryTypes.ts
type MemoryType = 'user' | 'feedback' | 'project' | 'reference'
type MemoryHeader = {
  filename: string
  filePath: string
  mtimeMs: number
  description: string | null
  type: MemoryType | undefined
}
```

**内容截断策略**（memdir.ts）
- 行限制：200 行（MAX_ENTRYPOINT_LINES）
- 字节限制：25KB（MAX_ENTRYPOINT_BYTES）
- 同时满足两个条件，违反任一则截断并警告
- 目的：防止长行索引导致 token 爆炸（P97 观测 197KB）

### 关键算法

**递归扫描 + 新鲜度感知**（memoryScan.ts）
```typescript
// 单遍扫描：读取 → 排序，避免 stat-sort-read 的双倍 syscall
export async function scanMemoryFiles(
  memoryDir: string,
  signal: AbortSignal,
): Promise<MemoryHeader[]>
  // 每个文件只读前 30 行frontmatter
  // 按 mtime 倒序排列（newest-first）
  // 限制最多 200 个文件（MAX_MEMORY_FILES）
```

**时间感知提醒**（memoryAge.ts）
- `memoryAgeDays()`：计算年龄，floor-round（今天 = 0，昨天 = 1）
- 超过 1 天的记忆自动标记陈旧警告
- 在 FileReadTool 输出中包装 `<system-reminder>` 提醒验证 vs 当前代码

**相关性选择**（findRelevantMemories.ts）
- 用 Sonnet 模型作为记忆选择器，而非基于关键词匹配
- 设计：防止工具 API 文档被算作"使用中工具的记忆"并被错误注入
- 输出限制：最多 5 个相关记忆（已排除 MEMORY.md 索引本身）

### 路径分辨率链（paths.ts）

```
优先级：
1. CLAUDE_COWORK_MEMORY_PATH_OVERRIDE (env var, Cowork 用)
2. autoMemoryDirectory in settings.json (安全：userSettings/localSettings/flagSettings, NOT projectSettings)
3. ~/.claude/projects/<sanitized-git-root>/memory/
```

**安全考量**：设置来源分层，防止恶意 repo 重定向 memory 到 ~/.ssh

**安全戒备（teamMemPaths.ts）**
- 符号链接逃逸防护：`realpathDeepestExisting()` + 两遍验证
  - 第一遍：path.resolve() 消除 .. 段（快速拒绝）
  - 第二遍：realpath() 破解符号链接，验证真实路径在目录内
- 攻击向量防护：
  - null bytes（C-based syscall 截断）
  - URL-encoded traversals（%2e%2e%2f）
  - Unicode normalization 攻击（fullwidth ．．／）
  - 悬挂符号链接（dangling symlinks）

---

## 2. Skills 系统 (skills/)

### 加载机制

**分层加载顺序**（loadSkillsDir.ts）
```typescript
LoadedFrom:
  | 'commands_DEPRECATED' // 向后兼容
  | 'skills'              // 磁盘上的 .md 文件
  | 'plugin'              // 外部插件提供
  | 'managed'             // 托管的默认 skills
  | 'bundled'             // CLI 内置编译
  | 'mcp'                 // MCP 协议
```

**命令类型系统**
```typescript
type Command = {
  type: 'prompt' | 'bash' | 'shell'
  source: 'user' | 'managed' | 'bundled' | 'plugin' | 'mcp'
  loadedFrom: LoadedFrom
  getPromptForCommand?: (args: string, context: ToolUseContext) => Promise<ContentBlockParam[]>
}
```

### 渐进式披露实现

**Bundled Skills：编译时注册**（bundledSkills.ts）
```typescript
export function registerBundledSkill(definition: BundledSkillDefinition): void
  // 1. 定义包含: name, description, whenToUse, getPromptForCommand()
  // 2. 文件提取：可选 files: Record<string, string>
  //    - 首次调用时延迟提取到 /tmp 或 ~/.claude/bundled-skills/<nonce>/
  //    - 闭包-local memoization：避免并发写入竞争
  // 3. getPromptForCommand 包装：prependBaseDir() 添加前缀
```

**安全的文件提取**
- 每进程 nonce 为基础目录，防止 symlink 预创建
- 0o700 权限模式（所有者唯一）
- `open(O_EXCL | O_NOFOLLOW)` 创建文件，防止 TOCTOU

### 与 ToolSearch 的关系

**Token 预估**
```typescript
export function estimateSkillFrontmatterTokens(skill: Command): number
  // 仅估算 name + description + whenToUse（前面板）
  // 完整内容仅在调用时加载
```

**前面板不可知的设计**
- Skills 在列表中通过 frontmatter 选择（token budget 约束）
- 模型看不到完整内容直到调用 `getPromptForCommand()`
- whenToUse 字段驱动选择性加载

---

## 3. Context 管理 (context/)

### 通知系统（notifications.tsx）

**队列 + 优先级模型**
```typescript
type Priority = 'low' | 'medium' | 'high' | 'immediate'
type Notification = {
  key: string
  priority: Priority
  timeoutMs?: number
  invalidates?: string[]      // 使此通知失效其他通知
  fold?: (acc, incoming) => Notification  // 可选折叠
}
```

**核心调度器：processQueue()**
- **当前通知**：同时最多 1 个显示
- **队列**：按优先级排序的待显示列表
- **immediate 通知**：跳过队列，立即显示
- **折叠机制**：相同 key 的通知合并（`Array.reduce()` 风格）

### 模态上下文（modalContext.tsx）

**大小感知**
```typescript
type ModalCtx = {
  rows: number
  columns: number
  scrollRef: RefObject<ScrollBoxHandle | null> | null
}

useModalOrTerminalSize(fallback)
  // 优先 ModalContext，降级到终端大小
```

### 浮动覆盖协调（promptOverlayContext.tsx）

**双通道设计**
```typescript
// 数据通道：slash-command 建议列表
useSetPromptOverlay(data: PromptOverlayData | null)

// 对话通道：任意 React 节点
useSetPromptOverlayDialog(dialog: ReactNode | null)
```

**分离写入器和观察者**
- SetContext 是稳定引用（不因自己的写入而重新渲染）
- DataContext 供消费者观察
- 防止每次建议更新时重新渲染整个 tree

### 统计存储（stats.tsx）

**多层聚合**
```typescript
{
  metrics: Map<string, number>       // 计数器
  histograms: Map<string, Histogram> // 观察值分布
  sets: Map<string, Set<string>>     // 去重值集合
}

Histogram {
  reservoir: number[]  // 蓄水池采样（Algorithm R，N=1024）
  count, sum, min, max
}
```

---

## 4. Harness 设计洞见

### 上下文工程原则

**1. 生命周期完整性**
- **Memory**：跨会话持久化 + 会话内更新 + 后台蒸馏
- **Skills**：编译时注册 + 运行时懒加载
- **Context**：React 提供者链 + 生命周期自动管理

**2. 多源融合架构**
```
用户持久化层（Memory）
    ↓
系统提示注入（loadMemoryPrompt）
    ↓
用户上下文消息（extractMemories 后台）
    ↓
相关记忆检索（findRelevantMemories via Sonnet 选择器）
```

**3. 安全默认**
- **路径**：规范化 → resolve() → realpath()（两遍验证）
- **符号链接**：显式防护
- **访问**：权限模式 0o700 + nonce 隔离

**4. Token 成本意识**
- MEMORY.md 截断（200 行 + 25KB）
- 前面板选择（frontmatter only token 估算）
- 相关记忆选择上限（5 个）
- 懒加载（Skills 内容仅在调用时读取）

### 可复用模式

**模式 1：分层路径分辨率**
```typescript
getPath = memoize(
  (): string => {
    const override = getOverride() ?? getSetting()
    if (override) return override
    return computeDefault()
  },
  () => getProjectRoot()
)
```

**模式 2：优先级队列 + 超时**
```typescript
{
  current: T | null
  queue: T[]
  timeout: NodeJS.Timeout | null
}
processQueue() // 持续迭代直至队列空
```

**模式 3：双上下文拆分（读 vs 写）**
```typescript
const DataContext = createContext<T | null>(null)
const SetContext = createContext<(T|null) => void | null>(null)
// 写入器不订阅 DataContext，避免自触发重渲染
```

**模式 4：闭包-local memoization**
```typescript
let promise: Promise<Result> | undefined
const wrapped = async () => {
  promise ??= perform()
  return await promise
}
// 防止并发 I/O 竞争
```

---

## 5. 关键业务逻辑

### Memory 写入流
```
user → 显式 /save 或隐含保存
  → buildMemoryPrompt() 注入完整说明
  → Write tool 创建 .md + MEMORY.md 索引
  → ensureMemoryDirExists() 保证目录存在
```

### Memory 读取流
```
Turn 开始
  → loadMemoryPrompt() 加载系统提示部分
  → turn 中提及 past 时 → findRelevantMemories()
  → Sonnet 选择器返回 ≤5 文件
  → 检查 mtime → memoryFreshnessNote() 标记 >1 天的
  → 注入系统提醒
```

### Skills 导入路线
```
磁盘扫描：~/.claude/skills/
  → loadMarkdownFilesForSubdir()
  → 解析 frontmatter → Command 对象
  → estimateSkillFrontmatterTokens() 计算成本

Bundled 注册：
  → registerBundledSkill({ name, getPromptForCommand, files? })
  → 首次调用时 extractBundledSkillFiles()
  → prependBaseDir() 给提示加前缀
```
