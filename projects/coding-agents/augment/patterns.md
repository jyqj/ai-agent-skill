# Augment 设计模式


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

从 Augment 架构中提取的可复用设计模式。

---

## 1. 四层工具主机 (Layered Tool Host)

### 问题
工具执行风险各异：有的在云端安全执行，有的需要本地权限，有的可能破坏系统。如何统一管理？

### 解法
按执行位置和风险等级分层，每层独立的安全策略和生命周期：

```typescript
enum ToolHostName {
  REMOTE = 1,   // 云端执行，API 调用
  LOCAL = 2,    // 本地 IDE 进程
  SIDECAR = 3,  // 独立沙箱进程
  MCP = 4       // 外部协议
}

interface ToolHost {
  name: ToolHostName;
  listTools(): ToolDefinition[];
  runTool(name: string, input: object): Promise<ToolResult>;
  checkSafety(name: string, input: object): Promise<SafetyLevel>;
}
```

### 权衡
- 优点：职责分离、独立扩展、风险隔离
- 缺点：跨层通信开销、状态同步复杂度

### Augment 实现
- Remote: WEB_SEARCH, GITHUB_API（需要 OAuth）
- Local: READ_FILE, WORKER_AGENT_*（直接访问 VSCode API）
- Sidecar: SHELL, GREP_SEARCH（独立进程执行危险操作）
- MCP: stdio/http/sse 三种传输

---

## 2. Worker Agent 主从编排 (Worker Agent Orchestration)

### 问题
复杂任务需要分解给多个 Agent 并行/串行执行，主 Agent 如何协调？

### 解法
提供一组 Worker 生命周期管理工具：

```typescript
// 主 Agent 的 Worker 管理工具
const workerTools = {
  startWorker: (config: WorkerConfig) => WorkerId,
  sendInstruction: (id: WorkerId, instruction: string) => void,
  readState: (id: WorkerId) => WorkerState,
  waitForWorker: (id: WorkerId) => WorkerResult,
  readEdits: (id: WorkerId) => Edit[],
  applyEdits: (id: WorkerId, edits: Edit[]) => void,
  stopWorker: (id: WorkerId) => void,
  deleteWorker: (id: WorkerId) => void,
};

// 编排流程
async function orchestrate(task: Task) {
  const workers = task.subtasks.map(sub => startWorker(sub));

  for (const worker of workers) {
    const result = await waitForWorker(worker);
    const edits = await readEdits(worker);
    await applyEdits(worker, edits);  // 主 Agent 控制是否应用
  }
}
```

### 权衡
- 优点：任务并行化、失败隔离、可中断恢复
- 缺点：Worker 间无直接通信、状态同步延迟

### Augment 实现
7 个 LOCAL_TOOL_TYPE（21-28）实现完整生命周期，支持 pause/resume。

---

## 3. Hook 缓存 (PreToolUse Cache)

### 问题
PreToolUse Hook 可能被同一工具调用多次触发（dryRun 预检 + 实际执行），如何避免重复执行？

### 解法
基于工具调用签名缓存 Hook 结果：

```typescript
function createPreToolUseCache() {
  const cache = new Map<string, PreToolUseResult>();

  return {
    getOrExecute: async (
      toolName: string,
      toolInput: object,
      executor: () => Promise<PreToolUseResult>
    ) => {
      const key = hash(toolName, toolInput);
      if (cache.has(key)) {
        return cache.get(key);
      }
      const result = await executor();
      cache.set(key, result);
      return result;
    },

    invalidate: (toolName: string, toolInput: object) => {
      cache.delete(hash(toolName, toolInput));
    }
  };
}
```

### 权衡
- 优点：避免重复执行、提升响应速度
- 缺点：缓存失效策略需要仔细设计

### Augment 实现
`pre-tool-use-helpers.ts` 中的 `createPreToolUseCache()`，与 IntelliJ sidecar 共享实现。

---

## 4. Checkpoint Hydration (检查点恢复)

### 问题
长时间运行的 Agent 可能被中断（用户关闭、崩溃），如何恢复状态？

### 解法
定期保存检查点，启动时 hydrate（恢复）：

```typescript
interface Checkpoint {
  id: string;
  timestamp: number;
  conversationId: string;
  edits: EditEvent[];
  taskState: TaskState;
  memorySnapshot: Memory;
}

class CheckpointManager {
  async save(state: AgentState): Promise<void> {
    const checkpoint = this.serialize(state);
    await this.storage.save(checkpoint);
    this.notifyWebview('checkpoint-saved', checkpoint.id);
  }

  async hydrate(checkpointId: string): Promise<AgentState> {
    const checkpoint = await this.storage.load(checkpointId);
    return this.deserialize(checkpoint);
  }
}
```

### 权衡
- 优点：可恢复、可审计、支持分支
- 缺点：存储开销、序列化复杂度

### Augment 实现
- `AggregateCheckpointManager` 管理检查点
- `checkpointToEditEventsNode()` 转换编辑事件
- `notify-webview-on-update.ts` 通知 UI 更新

---

## 5. 三层上下文截断 (Context Truncation Strategy)

### 问题
对话历史可能超出上下文窗口，如何优雅降级？

### 解法
分层截断策略：

```typescript
// 策略 1: 窗口模式 - 保留最近 N 轮
function limitChatHistoryWindow(history: Exchange[], maxRounds: number): Exchange[] {
  return history.slice(-maxRounds);
}

// 策略 2: 截断模式 - 按 token 计数截断
function limitChatHistoryTruncate(
  history: Exchange[],
  maxTokens: number,
  tokenCounter: (text: string) => number
): Exchange[] {
  let total = 0;
  const result = [];
  for (let i = history.length - 1; i >= 0; i--) {
    const tokens = tokenCounter(serialize(history[i]));
    if (total + tokens > maxTokens) break;
    result.unshift(history[i]);
    total += tokens;
  }
  return result;
}

// 组合使用
function truncateContext(history: Exchange[], budget: TokenBudget): Exchange[] {
  // 1. 窗口截断
  let result = limitChatHistoryWindow(history, budget.maxRounds);
  // 2. Token 截断
  result = limitChatHistoryTruncate(result, budget.maxTokens, countTokens);
  return result;
}
```

### 权衡
- 优点：灵活配置、保留最新上下文
- 缺点：可能丢失重要历史信息

### Augment 实现
`chat-truncation.ts` 提供两种策略，`MAX_ATTACHMENT_TEXT_CHARS = 10_000` 限制附件。

---

## 6. 工具安全检查 (Tool Safety Check)

### 问题
同一工具在不同输入下风险不同（如 Shell 执行 `ls` vs `rm -rf`），如何动态判断？

### 解法
三级安全模型 + 运行时检查：

```typescript
enum ToolSafety {
  UNSAFE = 0,  // 总是需要审批
  SAFE = 1,    // 自动执行
  CHECK = 2    // 运行时检查
}

interface ToolDefinition {
  name: string;
  safety: ToolSafety;
}

async function shouldExecute(tool: ToolDefinition, input: object): Promise<boolean> {
  switch (tool.safety) {
    case ToolSafety.SAFE:
      return true;
    case ToolSafety.UNSAFE:
      return await requestUserApproval(tool, input);
    case ToolSafety.CHECK:
      // 调用后端检查（可能有更复杂的规则）
      const result = await api.checkToolSafety(tool.name, input);
      return result.isSafe ? true : await requestUserApproval(tool, input);
  }
}
```

### 权衡
- 优点：灵活、支持复杂规则、可后端更新
- 缺点：CHECK 模式增加延迟

### Augment 实现
- `ToolSafety` 枚举
- `CheckToolSafety` RPC 方法
- Shell 工具有 allowlist 机制

---

## 7. Hook 消息路由 (Hook Message Routing)

### 问题
Hook 可能在工具调用前/后/会话结束时产生消息，如何正确路由到 UI？

### 解法
消息类型分类 + 时间戳防竞态：

```typescript
interface HookMessageContext {
  conversationId: string;
  requestId: string;
  toolUseId?: string;  // PostToolUse 有
  messageType: 'hook' | 'stop';
  accumulatedAt: number;  // 防止旧 stream 消费新消息
}

class HookMessageRouter {
  private pending = new Map<string, { messages: string[]; accumulatedAt: number }>();
  private streamStartTimes = new Map<string, number>();
  private consumedBy = new Map<string, string>();

  accumulate(conversationId: string, messages: string[]): void {
    this.pending.set(conversationId, {
      messages: [...(this.pending.get(conversationId)?.messages ?? []), ...messages],
      accumulatedAt: Date.now()
    });
  }

  consume(conversationId: string, requestId: string): string[] {
    const pending = this.pending.get(conversationId);
    if (!pending || pending.messages.length === 0) return [];

    // 检查是否已被消费
    if (this.consumedBy.has(conversationId)) return [];

    // 检查 stream 启动时间，只有更新的 stream 可以消费
    const streamStart = this.streamStartTimes.get(requestId);
    if (streamStart !== undefined && streamStart < pending.accumulatedAt) {
      return [];  // 旧 stream 不应消费新消息
    }

    this.consumedBy.set(conversationId, requestId);
    this.pending.delete(conversationId);
    return pending.messages;
  }
}
```

### 权衡
- 优点：防止消息丢失/重复、处理并发
- 缺点：复杂度高

### Augment 实现
`ChatModel` 类中有完整的 Hook 消息路由实现，包括：
- `_pendingHookMessagesByConversation`
- `_streamStartTimes`
- `_hookMessagesConsumedBy`

---

## 8. SubAgent 配置加载 (SubAgent Config Loader)

### 问题
用户可能自定义 SubAgent 配置（类似 Claude 的 agents/），如何统一加载？

### 解法
支持多来源 + 内置默认：

```typescript
interface SubAgentConfig {
  name: string;
  description: string;
  model?: string;
  systemPrompt?: string;
  tools?: string[];
}

class SubAgentConfigLoader {
  static loadSubAgentConfigs(options: {
    workspaceRoot: string;
    configPaths: string[];  // ['.augment/agents/', '.claude/agents/']
    includeBuiltinDefaults: boolean;
  }): SubAgentConfig[] {
    const configs: SubAgentConfig[] = [];

    // 1. 加载用户配置
    for (const path of options.configPaths) {
      configs.push(...this.loadFromDir(join(options.workspaceRoot, path)));
    }

    // 2. 可选加载内置默认
    if (options.includeBuiltinDefaults) {
      configs.push(...this.getBuiltinDefaults());
    }

    return configs;
  }
}
```

### 权衡
- 优点：灵活扩展、用户自定义
- 缺点：配置冲突处理

### Augment 实现
`SubAgentConfigLoader` 支持 `.augment/agents/` 和 `.claude/agents/` 目录。

---

## 9. Trigger 事件驱动 (Event-Driven Triggers)

### 问题
如何让 Agent 响应外部事件（PR 创建、Issue 更新）自动执行？

### 解法
Trigger 系统：

```typescript
interface Trigger {
  id: string;
  name: string;
  eventType: 'pr_created' | 'issue_updated' | 'commit_pushed';
  filter: TriggerFilter;  // 匹配条件
  action: TriggerAction;  // 执行动作
}

// API
CreateTrigger(trigger: Trigger)
ListTriggers()
UpdateTrigger(id, updates)
DeleteTrigger(id)
GetTriggerExecutions(id)  // 执行历史
ExecuteTriggerManually(id)  // 手动触发

// 事件处理
ProcessWebhook(event)  // 接收外部 webhook
GetMatchingEntities(trigger)  // 获取匹配实体
```

### 权衡
- 优点：自动化、可审计
- 缺点：调试复杂、权限管理

### Augment 实现
`public_api.proto` 中有完整的 Trigger 服务定义。

---

## 10. 并行工具声明 (Parallel Tool Use Declaration)

### 问题
如何让模型知道可以并行调用工具？

### 解法
在请求中声明特性标志：

```typescript
// ChatStreamOptions
{
  feature_detection_flags: {
    support_tool_use_start: true,      // 支持流式工具开始事件
    support_parallel_tool_use: true    // 支持并行工具调用
  }
}
```

### 权衡
- 优点：向后兼容、渐进启用
- 缺点：需要模型和 Harness 都支持

### Augment 实现
始终启用 `enableParallelTools: true`。
