# Augment Agent Architecture


> **Evidence Status** — grounded. 本目录下的逆向分析、架构图与专题文件。

## 基本信息

- **类型**：coding-agent
- **项目定位**：企业级 coding agent，重点是四层工具主机、Worker 编排与 checkpoint。
- **学习来源**：本地逆向分析：Augment VSCode Extension 编译包与 source map。
- **推荐入口**：README → patterns.md → 相关 snippet / layer 文件。

## 模块覆盖

| 模块 | 覆盖程度 | 证据文件 | 可复用模式 |
|---|---|---|---|
| tools | 深 | README.md / patterns.md | layered-tool-host |
| orchestration | 深 | README.md / patterns.md | worker-orchestration |
| state | 深 | patterns.md | checkpoint-hydration |
| control | 中 | README.md | hook-system |
| context | 中 | README.md | rules-driven context |
| execution | 中 | README.md | sidecar isolation |

## 独特贡献

Augment 同时把”工具宿主分层”（Remote/Local/Sidecar/MCP）和”Worker 编排”（8 个管理工具 + 主从协议）做成一等架构模块。大多数 agent 只在其中一个方向深入，Augment 的组合证明了这两个维度可以正交设计、独立演进。

## 关键发现

- 工具按执行位置分层（云端 / 本地 / 边车 / 协议）本身就同时解决了安全隔离和可扩展性问题，比逐工具配权限更结构化。
- Worker 不只是”并发执行的子任务”，而是拥有独立状态、可暂停/恢复、可中途追加指令的长生命周期实体。
- Checkpoint + Sharding 使”长任务中断后恢复”成为默认能力，而非需要额外设计的异常路径。

> 逆向分析自 Augment VSCode Extension v0.801.0 (9.6MB 编译包 + 33MB Source Map)

## 核心定位

Augment 是一个**企业级 AI 编码助手**，特点：
- 四层工具主机架构（Remote/Local/Sidecar/MCP）
- Worker Agent 编排（主从模式，支持暂停/恢复）
- 完整的 Hook 生命周期系统
- Checkpoint + Sharding 持久化
- 规则驱动的上下文工程

---

## 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                      Augment Harness                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Tool Host Layer                       │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │    │
│  │  │  Remote  │ │  Local   │ │ Sidecar  │ │   MCP    │    │    │
│  │  │ (Cloud)  │ │(VSCode)  │ │(Process) │ │(Protocol)│    │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   Hook System                            │    │
│  │  SessionStart → PreToolUse → PostToolUse → Stop          │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Context & Memory Layer                      │    │
│  │  Blobs | Guidelines | Rules | Skills | Checkpoint        │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │               Worker Agent Orchestration                 │    │
│  │  Start → Send Instruction → Read State → Apply Edits     │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Augment Backend (gRPC)                       │
│  107 RPC Methods | 30 Services | 1587 Message Types             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 核心模式

### 1. 四层工具主机 (Tool Host)

Augment 将工具按执行位置分为四层：

| 层级 | 枚举值 | 位置 | 典型工具 |
|-----|-------|------|---------|
| Remote | 1 | 云端 | WEB_SEARCH, GITHUB_API, LINEAR, JIRA, CONFLUENCE, NOTION |
| Local | 2 | VSCode 进程 | READ_FILE, SAVE_FILE, EDIT_FILE, WORKER_AGENT_* |
| Sidecar | 3 | 独立边车进程 | SHELL, VIEW, GREP_SEARCH, SUB_AGENT, APPLY_PATCH |
| MCP | 4 | MCP 协议 | 用户配置的 MCP 服务器工具 |

**设计要点**：
- Remote 工具需要 OAuth，状态有 AVAILABLE / USER_CONFIG_REQUIRED
- Sidecar 独立进程隔离了风险操作（Shell 执行）
- MCP 层支持 stdio/http/sse 三种传输

### 2. Worker Agent 编排

主 Agent 通过 7 个 Local 工具管理 Worker：

| 工具 | 功能 |
|-----|------|
| `START_WORKER_AGENT` (21) | 启动 Worker |
| `READ_WORKER_STATE` (22) | 读取状态 |
| `WAIT_FOR_WORKER_AGENT` (23) | 等待完成 |
| `SEND_INSTRUCTION_TO_WORKER_AGENT` (24) | 发送指令 |
| `STOP_WORKER_AGENT` (25) | 停止 |
| `DELETE_WORKER_AGENT` (26) | 删除 |
| `READ_WORKER_AGENT_EDITS` (27) | 读取编辑 |
| `APPLY_WORKER_AGENT_EDITS` (28) | 应用编辑 |

**关键流程**：
```
Main Agent                          Worker Agent
    │                                    │
    │── START_WORKER_AGENT ─────────────▶│
    │                                    │ (执行任务)
    │◀─── READ_WORKER_STATE ─────────────│
    │                                    │
    │── SEND_INSTRUCTION ───────────────▶│ (中途指令)
    │                                    │
    │── WAIT_FOR_WORKER_AGENT ──────────▶│ (阻塞等待)
    │                                    │
    │◀─── READ_WORKER_AGENT_EDITS ───────│
    │── APPLY_WORKER_AGENT_EDITS ───────▶│
    │                                    │
    │── STOP_WORKER_AGENT ──────────────▶│ (优雅停止)
```

### 3. Hook 系统

完整的生命周期钩子，支持消息展示和工具拦截：

```typescript
// Hook 类型
type HookEventType =
  | 'SessionStart'    // 会话开始
  | 'PreToolUse'      // 工具调用前（支持 blockTool）
  | 'PostToolUse'     // 工具调用后
  | 'Stop';           // 会话停止

// Hook 输出
interface HookOutput {
  displayMessages?: string[];  // 展示给用户
  blockTool?: boolean;         // 拦截工具调用
  stopAgent?: boolean;         // 停止 Agent
}
```

**PreToolUse 缓存**：
- 使用 `createPreToolUseCache()` 缓存 Hook 结果
- dryRun 模式预检工具安全性
- 避免同一工具调用重复执行 Hook

### 4. Checkpoint + Sharding

```typescript
// 检查点管理
AggregateCheckpointManager
  ├── notifyWebviewOfAgentEditListHasUpdates()
  └── checkpointToEditEventsNode()

// 分片存储
AgentShardStorage
  ├── checkpoint-hydration.ts  // 恢复
  ├── checkpoint-types.ts      // 类型
  └── shard-manager.ts         // 管理器
```

**设计要点**：
- 支持跨会话恢复 Agent 状态
- 编辑事件可转换为检查点
- Shard 机制分散大状态存储

### 5. 工具安全等级

三级安全模型：

| 等级 | 值 | 行为 |
|-----|---|------|
| UNSAFE | 0 | 总是需要审批 |
| SAFE | 1 | 自动执行 |
| CHECK | 2 | 运行时检查 `CheckToolSafety` RPC |

### 6. 并行工具调用

```typescript
// ChatStreamOptions
{
  feature_detection_flags: {
    support_tool_use_start: true,
    support_parallel_tool_use: true  // 启用并行
  }
}

// 始终启用
enableParallelTools: true  // chat-model.ts:1209
```

---

## 上下文工程

### Blobs 机制

文件内容通过 Blob 上传到云端，实现：
- 增量同步（只上传变更）
- 跨请求复用
- 按需检索

```typescript
// API 流程
checkpointBlobs(blobs)  → 注册 blob 名
batchUpload(blobs)      → 上传内容
findMissing(names)      → 查缺补漏
```

### 三层上下文截断

```typescript
// chat-truncation.ts
limitChatHistoryTruncate()  // 截断模式
limitChatHistoryWindow()    // 窗口模式
```

### Guidelines 层级

```typescript
// 三层指南
userGuidelines       // 用户个人偏好
workspaceGuidelines  // 工作区规则
rules[]              // 规则文件
skills[]             // 技能定义
```

---

## 对 Harness 设计的启示

1. **工具分层是正确的**：将工具按执行风险/位置分层，可以独立控制权限和安全策略

2. **Worker Agent 模式强大**：主从编排支持复杂任务分解，但需要设计好状态同步机制

3. **Hook 系统必不可少**：PreToolUse 拦截是安全护栏的关键点

4. **Checkpoint 是长任务基础**：支持暂停/恢复的 Agent 必须有持久化机制

5. **并行工具调用是标配**：现代 Agent 应默认支持并行工具调用以提升效率

6. **上下文工程需要多层**：用户/工作区/规则三层分离是合理的

---

## 关键文件参考

| 文件 | 行数 | 作用 |
|-----|------|-----|
| `chat-model.ts` | 2044 | 核心聊天/Agent 模型 |
| `augment-api.ts` | 1168 | REST API 客户端 |
| `extension.ts` | 1400+ | VSCode 扩展入口 |
| `public_api_pb.js` | 3651 | 公共 API protobuf |
| `remote_agents_pb.js` | 737 | 远程 Agent protobuf |

详见本 README 与 `./patterns.md` 获取架构与模式总结。
