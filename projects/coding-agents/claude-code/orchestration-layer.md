# Orchestration Layer 架构分析


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> 来源：Claude Code 源码逆向分析
> 路径：`src/QueryEngine.ts`, `src/query.ts`, `src/tools/AgentTool/`, `src/tasks/`

## 1. 查询引擎 (QueryEngine.ts)

### 核心职责
- **单一实例化**：一个 QueryEngine 对应一个完整的对话周期
- **会话状态持久化**：维护消息数组、权限否认记录、使用量等跨轮状态

### 初始化流程
```
QueryEngine 构造器
├─ 初始化：mutableMessages、abortController、permissionDenials
├─ 读文件缓存克隆（用于隔离）
└─ 使用量基线设置
```

### 系统提示组装
- **多层嵌套**：
  - 基础系统提示（通过 `fetchSystemPromptParts`）
  - 内存机制提示（当设置自定义提示且启用自动内存路径）
  - 追加系统提示（用户指定）
  - 所有部分通过 `asSystemPrompt()` 合并为单一对象

### submitMessage 核心步骤
1. **输入处理**：调用 `processUserInput()` 处理提示
2. **会话持久化**：在进入查询循环前写入消息到会话文件
3. **上下文重建**：斜杠命令处理后重建 `ProcessUserInputContext`

---

## 2. 核心查询循环 (query.ts)

### 查询状态机
```typescript
type State = {
  messages: Message[]
  toolUseContext: ToolUseContext
  autoCompactTracking?: AutoCompactTrackingState
  maxOutputTokensRecoveryCount: number
  hasAttemptedReactiveCompact: boolean
  pendingToolUseSummary?: Promise<ToolUseSummaryMessage | null>
  stopHookActive?: boolean
  turnCount: number
  transition?: { reason: Continue | undefined }
}
```

### 消息处理流程

**1. 上下文压缩**
- 应用工具结果预算（内容替换、大小限制）
- 历史 Snip 压缩（可选，feature 门控）
- 微型压缩（缓存编辑，deferred 边界消息）
- 上下文折叠投影（不修改消息，只读时投影）
- 自动压缩（如果超过阈值，递归查询压缩模型）

**2. API 调用循环**
- 创建模型流适配器（StreamingToolExecutor 或 legacy runTools）
- 流式接收助手消息块
- 流式工具执行（如果启用）
- 处理流式故障回退

### 工具执行编排

**分区策略**（toolOrchestration.ts）：
```typescript
partitionToolCalls() →
├─ 并发安全批次：多个连续的只读工具（并发运行，最多 10 并发）
└─ 非并发安全批次：单一写入工具（串行运行）
```

### 终止条件

| 原因 | 触发场景 |
|------|---------|
| `blocking_limit` | 上下文超限（无自动压缩） |
| `aborted_streaming` | 用户中断（流式阶段） |
| `prompt_too_long` | API 错误恢复失败 |
| `completed` | 正常完成或 API 错误（不重试） |
| `aborted_tools` | 工具执行时中止 |
| `hook_stopped` | 钩子阻止继续 |
| `max_turns` | 达到最大轮数 |

### 错误恢复层级
```
413 (prompt-too-long) 错误：
├─ 阶段 1：上下文折叠排放（如果启用）
├─ 阶段 2：反应性压缩（整体总结）
└─ 如果两者都失败：表面错误，跳过 stop 钩子

max_output_tokens 错误：
├─ 升级重试：8k → 64k（一次，feature 门控）
└─ 多轮恢复：3 次重试，带有恢复消息
```

---

## 3. 子代理系统 (AgentTool/)

### Agent 定义结构
```typescript
BaseAgentDefinition
├─ BuiltInAgentDefinition
│  ├─ getSystemPrompt(toolUseContext) → string
│  └─ 源：'built-in'
└─ CustomAgentDefinition
   ├─ getSystemPrompt() → string（来自 closure）
   └─ 源：'userSettings' | 'projectSettings' | 'policySettings' | 'pluginSettings'
```

### Frontmatter 支持的字段
- `description`, `tools`, `disallowedTools`, `prompt`, `model`
- `effort`, `permissionMode`, `mcpServers`, `hooks`
- `maxTurns`, `skills`, `initialPrompt`
- `memory` ('user' | 'project' | 'local')
- `background`, `isolation` ('worktree' | 'remote')

### Fork vs Spawn：两种编排模式

**Fork 子代理**（forkSubagent.ts）：
- **触发条件**：`!subagent_type` 且启用 FORK_SUBAGENT feature
- **继承模式**：完整对话历史 + 父系统提示（字节相同，缓存共享）
- **缓存共享**：所有 fork 子代理产生相同前缀，最大化 prompt cache 命中

**Spawn 子代理**（runAgent.ts）：
- 独立代理定义，新会话 ID，隔离消息历史
- 支持自定义 MCP 服务器

### 隔离模式

| 模式 | 说明 |
|------|------|
| **Worktree** | 在隔离的 git worktree 中运行，父会话不受影响 |
| **Remote** | 在远程 CCR 计算中运行（企业部署） |

### 并行编排

**后台执行**（background: true）：
- 代理任务注册为 `local_agent` 任务类型
- 主线程立即返回，任务在后台运行
- 完成时通过 task-notification 向主线程发送消息

---

## 4. Task 系统

### Task 类型与生命周期
```typescript
TaskType: 'local_bash' | 'local_agent' | 'remote_agent' |
          'in_process_teammate' | 'local_workflow' | 'monitor_mcp' | 'dream'

TaskStatus: 'pending' | 'running' | 'completed' | 'failed' | 'killed'
```

### 任务标识
- 前缀：'b' (bash) | 'a' (agent) | 'r' (remote) | 't' (teammate) | 'w' (workflow) | 'm' (mcp) | 'd' (dream)
- 后缀：8 个随机字符（36^8 ≈ 2.8 万亿，防暴力符号链接）

### LocalMainSessionTask
- Ctrl+B 两次背景化主会话查询
- 查询在后台继续，UI 恢复到新提示
- 完成时通知用户

---

## 5. Harness 设计洞见

### 多窗口协调

**Coordinator Mode**（feature gate: COORDINATOR_MODE）：
- 禁用 Fork 子代理（fork + coordinator 互斥）
- 用户上下文注入
- MCP 工具注入用于 scratch pad 访问

### Agent Teams

**权限冒泡**（permissionMode: 'bubble'）：
- 子代理权限提示呈现到父终端
- 父会话用户批准/拒绝

### Streaming Tool Execution

**StreamingToolExecutor**：
- 在 API 流式时并行执行工具
- 流消息 → 检测 tool_use → 入队 → 异步执行
- 故障回退：模型切换时丢弃孤立消息

### 上下文管理与缓存共享

**Prompt Cache Byte-Exact**：
- Fork 占位符相同（FORK_PLACEHOLDER_RESULT）
- 只有最终文本块变化（指令）
- 所有 fork 子代理的 API 请求前缀相同

---

## 6. 核心编排模式总结

| 模式 | 触发 | 父-子通信 | 隔离 | 缓存 |
|------|------|---------|------|------|
| **Fork** | `!subagent_type` | 消息 + 指令文本 | 逻辑（同进程） | 高（字节相同前缀） |
| **Spawn** | 显式 agentType | 消息传递 | 进程/worktree | 低（独立历史） |
| **Main Session** | Ctrl+B | 主线程管理 | N/A | N/A |
| **MCP 代理** | mcpServers spec | 工具调用 | 配置作用域 | 工具缓存 |

### 终止条件的层级

1. **模型层**：未产生 tool_use block（`!needsFollowUp`）
2. **恢复层**：错误重试（413、max_output_tokens）
3. **策略层**：max_turns、token_budget、stop_hooks、权限
4. **信号层**：用户中止（abortController.signal）

### 关键的状态持久化

| 组件 | 持久化方式 | 作用域 |
|------|----------|--------|
| 消息历史 | 会话文件（recordTranscript） | 跨会话恢复 |
| 工具权限 | AppState.toolPermissionContext | 当前会话 |
| 代理内存 | MEMORY.md（per scope） | user/project/local |
| MCP 配置 | 全局 MCP 连接池 | 进程生命周期 |
| Task 状态 | AppState.tasks | 进程生命周期 |

---

## 7. 关键的性能优化

**Prefetch 设计**：
- MemoryPrefetch：并行加载相关内存
- SkillDiscoveryPrefetch：并行发现技能

**并发工具执行**：
- 分区：read-only 批（并发） vs 写入批（串行）
- 最大 10 并发
- 上下文修饰符队列化，批处理完成后应用

**流式早期返回**：
- StreamingToolExecutor 在流式时执行工具
- 避免等待 API 完成所有流才启动工具执行

**压缩多阶段**：
- Snip（便宜）→ Microcompact（缓存编辑）→ Autocompact（完整总结）
- 每个阶段都是可选的，独立启用
