# Warp Agent Mode Controller & Permissions

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。

> **Evidence Status** — grounded. `app/src/ai/blocklist/controller.rs`（2870 行）、`permissions.rs`（1197 行）、`orchestration_events.rs`（1394 行）源码。

## 架构总览

Agent Mode 的核心是 `BlocklistAIController`，它编排 AI 模型交互的完整生命周期：输入构造 → 请求发送 → 流式响应 → 工具执行 → 权限检查 → 状态更新。

```text
用户输入
    ↓
BlocklistAIController
    ├── InputModel（输入管理）
    ├── ContextModel（上下文构造）
    ├── HistoryModel（对话历史）
    ├── ActionModel（动作执行）
    ├── Permissions（权限检查）
    └── OrchestrationEventService（多 Agent 事件）
    ↓
ResponseStream → 流式输出 → UI 更新
```

## Controller 核心结构

```rust
// app/src/ai/blocklist/controller.rs

pub struct SessionContext {
    session_type: Option<SessionType>,      // Local / WarpifiedRemote
    shell: Option<ShellLaunchData>,
    current_working_directory: Option<String>,
}

pub enum BlocklistAIControllerEvent {
    SentRequest {
        contains_user_query: bool,
        is_queued_prompt: bool,           // 来自 /queue 的延迟发送
        model_id: LLMId,
        stream_id: ResponseStreamId,
    },
    FinishedReceivingOutput {
        stream_id: ResponseStreamId,
        conversation_id: AIConversationId,
    },
    ExportConversationToFile { filename: Option<String> },
    FreeTierLimitCheckTriggered,
}

// 请求输入：包含多任务支持
pub struct RequestInput {
    pub conversation_id: AIConversationId,
    pub input_messages: HashMap<TaskId, Vec<AIAgentInput>>,  // 多任务输入
    pub working_directory: Option<String>,
    pub model_id: LLMId,
    pub coding_model_id: LLMId,
    pub cli_agent_model_id: LLMId,
    pub computer_use_model_id: LLMId,
    pub shared_session_response_initiator: Option<ParticipantId>,
    pub request_start_ts: DateTime<Local>,
    pub supported_tools_override: Option<Vec<ToolType>>,
}
```

**关键洞察**：
- 支持 **多任务并行**（`HashMap<TaskId, Vec<AIAgentInput>>`）
- 支持 **多模型路由**（主模型、编码模型、CLI agent 模型、Computer Use 模型）
- 支持 **共享会话**（`shared_session_response_initiator`）
- 支持 **工具集覆盖**（`supported_tools_override`）

## 权限系统

```rust
// app/src/ai/blocklist/permissions.rs

// 命令执行权限（三层分类）
pub enum CommandExecutionPermission {
    Allowed(CommandExecutionPermissionAllowedReason),
    Denied(CommandExecutionPermissionDeniedReason),
}

pub enum CommandExecutionPermissionAllowedReason {
    Dispatched,                  // 用户显式调度
    ExplicitlyAllowlisted,       // 在允许列表中
    IsReadOnlyAndSettingEnabled,  // 只读命令 + 设置允许
    AgentDecided,                // Agent 自主决定
    AlwaysAllowed,               // 始终允许
    RunToCompletion,             // 运行到完成模式
}

pub enum CommandExecutionPermissionDeniedReason {
    AutonomyForceDisabled,       // 自治被强制禁用
    AlwaysAskEnabled,            // 始终询问设置
    ExplicitlyDenylisted,        // 在拒绝列表中
    ContainsRedirection,         // 包含重定向
    Inconclusive,                // 无法判断
    AgentDecided,                // Agent 决定拒绝
}

// 文件读取权限
pub enum FileReadPermission {
    Allowed(FileReadPermissionAllowedReason),
    Denied(FileReadPermissionDeniedReason),
}

pub enum FileReadPermissionAllowedReason {
    Dispatched,
    AlreadyReadInConvo,          // 本次对话已读过
    ExplicitlyAllowlisted,
    AutoreadSettingEnabled,
    AgentDecided,
    RunToCompletion,
}

// 文件写入权限
pub enum FileWritePermission {
    Allowed(FileWritePermissionAllowedReason),
    Denied(FileWritePermissionDeniedReason),
}

pub enum FileWritePermissionDeniedReason {
    AutonomyForceDisabled,
    AlwaysAskEnabled,
    Inconclusive,
    AgentDecided,
    ProtectedPath,               // 系统保护文件（如 MCP 配置）
}
```

### 权限 Profile 系统

```rust
pub struct BlocklistAIPermissions {
    temporary_file_permissions: HashMap<AIConversationId, HashSet<PathBuf>>,
}

impl BlocklistAIPermissions {
    /// 返回考虑企业覆盖后的权限 profile
    pub fn permissions_profile_for_id(
        &self,
        ctx: &AppContext,
        profile_id: ClientProfileId,
    ) -> AIExecutionProfile {
        AIExecutionProfile {
            apply_code_diffs: self.get_apply_code_diffs_setting_for_profile(ctx, profile_id),
            read_files: self.get_read_files_setting_for_profile(ctx, profile_id),
            execute_commands: self.get_execute_commands_setting_for_profile(ctx, profile_id),
            mcp_permissions: self.get_mcp_permissions_setting_for_profile(ctx, profile_id),
            write_to_pty: self.get_write_to_pty_setting_for_profile(ctx, profile_id),
            command_allowlist: ...,
            command_denylist: ...,
            directory_allowlist: ...,
            mcp_allowlist: ...,
            mcp_denylist: ...,
            computer_use: ...,
            ask_user_question: ...,
        }
    }
}
```

**设计洞察**：
- 权限是**带原因的枚举**（`Allowed(reason)` / `Denied(reason)`），支持审计和遥测
- `AgentDecided` 出现在 allow 和 deny 两侧 — agent 可以自主决定
- `ProtectedPath` 是不可覆盖的安全硬限制
- `RunToCompletion` 是"快进模式"下的特殊权限
- 临时权限（`temporary_file_permissions`）绑定到对话生命周期
- 企业覆盖（enterprise override）可以覆盖用户设置

## Orchestration Event Service（多 Agent 编排）

```rust
// app/src/ai/blocklist/orchestration_events.rs

pub struct OrchestrationEventService {
    pending_events: HashMap<AIConversationId, Vec<PendingEvent>>,
    awaiting_server_echo_events: HashMap<AIConversationId, Vec<PendingEvent>>,
    lifecycle_subscription_routes: HashMap<AIConversationId, Vec<LifecycleSubscriptionRoute>>,
    conversation_statuses: HashMap<AIConversationId, ConversationStatus>,
}

pub enum PendingEventDetail {
    Message {
        message_id: String,
        addresses: Vec<String>,
        subject: String,
        message_body: String,
    },
    Lifecycle {
        event: api::AgentEvent,
    },
}

pub struct PendingEvent {
    pub event_id: String,
    pub source_agent_id: String,
    pub attempt_count: i32,        // 最多 3 次重试
    pub detail: PendingEventDetail,
}

pub enum OrchestrationEventServiceEvent {
    EventsReady { conversation_id: AIConversationId },
}
```

**设计洞察**：
- Orchestration 服务支持**多 Agent 间的消息传递和生命周期事件**
- 事件有**重试机制**（最多 3 次）和**去重**
- 生命周期事件支持订阅路由（`lifecycle_subscription_routes`）
- 事件分为 Message（Agent 间通信）和 Lifecycle（启动/错误/完成）

## Controller 与其他组件的交互

```text
BlocklistAIController
    │
    ├── subscribe → BlocklistAIHistoryModel（对话历史变更）
    ├── subscribe → BlocklistAIActionModel（动作事件）
    ├── subscribe → OrchestrationEventService（编排事件就绪）
    ├── subscribe → AgentViewController（Agent View 事件）
    │
    ├── read → BlocklistAIContextModel（构造请求上下文）
    ├── read → BlocklistAIPermissions（检查权限）
    ├── read → SkillManager（获取可用 skills）
    │
    ├── write → BlocklistAIHistoryModel（更新对话状态）
    ├── write → BlocklistAIActionModel（触发动作）
    │
    └── call → api::send_request（发送到服务端）
         └── ResponseStream（流式处理响应）
```

## 与知识库的关联

### 印证

- `architecture/planes/control/overview.md`：带原因的权限枚举 = 可审计的控制层
- `architecture/planes/orchestration/overview.md`：OrchestrationEventService = Agent 间通信基础设施
- `design-space/methodology/harness-engineering.md`：Controller 编排了完整的 Harness 组件

### 独特贡献

1. **带原因的权限枚举**：`Allowed(reason)` / `Denied(reason)` 取代 bool，支持审计
2. **Agent 自主决策权限**：`AgentDecided` 同时出现在 allow/deny — agent 有自治权
3. **多模型路由**：一个请求可以指定不同场景使用不同模型
4. **多任务并行**：`HashMap<TaskId, Vec<AIAgentInput>>` 支持并行任务
5. **ProtectedPath 硬限制**：即使用户设置允许，系统文件也不可写
6. **Orchestration 事件系统**：支持多 Agent 间的消息传递和生命周期管理
