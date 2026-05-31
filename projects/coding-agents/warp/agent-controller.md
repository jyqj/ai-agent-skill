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

**设计要点**：
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

**设计要点**：
- 权限是**带原因的枚举**（`Allowed(reason)` / `Denied(reason)`），支持审计和遥测
- `AgentDecided` 出现在 allow 和 deny 两侧，agent 可以自主决定
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

**设计要点**：
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

## ThirdPartyHarness Adapter Pattern

### 来源
`app/src/ai/agent_harness/`, `crates/ai/src/harness/`

### 架构
```rust
// trait 定义：所有外部 coding agent 的统一接口
pub trait ThirdPartyHarness {
    /// 验证 harness 是否可用（二进制存在、版本兼容等）
    fn validate(&self, ctx: &HarnessContext) -> Result<ValidationResult>;

    /// 准备运行环境（创建临时目录、写入配置、设置环境变量）
    fn prepare(&self, ctx: &HarnessContext, config: &HarnessConfig) -> Result<PreparedHarness>;

    /// 构建 runner（返回可执行的 HarnessRunner）
    fn build_runner(&self, prepared: PreparedHarness) -> Result<Box<dyn HarnessRunner>>;
}

// 生命周期：validate → prepare → build_runner → run → save/resume
```

### HarnessRunner 有状态运行时
```rust
pub trait HarnessRunner: Send {
    /// 启动 agent 进程
    async fn start(&mut self) -> Result<()>;

    /// 发送用户输入
    async fn send_input(&mut self, input: &str) -> Result<()>;

    /// 读取输出流
    fn output_stream(&self) -> Pin<Box<dyn Stream<Item = HarnessOutput>>>;

    /// 保存状态（用于跨 session 恢复）
    async fn save_state(&self) -> Result<HarnessState>;

    /// 停止
    async fn stop(&mut self) -> Result<()>;
}
```

### 注释
- **validate → prepare → build_runner** 三阶段生命周期，每阶段可独立失败和重试。
- 支持 Claude Code、Codex CLI、Gemini CLI 等外部 agent 作为 harness 运行。
- HarnessRunner 是有状态的，持有子进程句柄、PTY 会话和输出缓冲区。
- `save_state()` 返回可序列化的 `HarnessState`，配合 `ResumePayload` 实现跨会话恢复。

---

## ResumePayload 跨 Agent 恢复

### 来源
`app/src/ai/agent_harness/resume.rs`

### 代码
```rust
pub struct ResumePayload {
    pub harness_type: HarnessType,           // Claude / Codex / Gemini 等
    pub conversation_id: AIConversationId,
    pub harness_state: HarnessState,          // 序列化的 runner 状态
    pub working_directory: PathBuf,
    pub environment_snapshot: HashMap<String, String>,
    pub timestamp: DateTime<Utc>,
}

// 恢复流程
pub async fn resume_agent(payload: ResumePayload) -> Result<Box<dyn HarnessRunner>> {
    let harness = get_harness(payload.harness_type);
    let prepared = harness.prepare_for_resume(&payload)?;
    let mut runner = harness.build_runner(prepared)?;
    runner.restore_state(payload.harness_state).await?;
    Ok(runner)
}
```

### 注释
- ResumePayload 包含恢复 agent 所需的全部信息：harness 类型、对话 ID、runner 状态、工作目录和环境变量。
- 跨 Agent 恢复意味着用户可以关闭 Warp、重新打开后继续之前的 agent 会话。
- 环境快照确保恢复后的 agent 运行在与中断时相同的环境中。

---

## RunAgents 批量子 Agent 编排

### 来源
`app/src/ai/blocklist/controller.rs`

### 架构
```rust
// 单个 tool call 启动多个子 agent
pub struct RunAgentsRequest {
    pub agents: Vec<AgentSpec>,
    pub orchestration_mode: OrchestrationMode,
}

pub struct AgentSpec {
    pub harness_type: HarnessType,           // Local 或 Remote
    pub task_description: String,
    pub working_directory: Option<PathBuf>,
    pub model_override: Option<LLMId>,
}

pub enum OrchestrationMode {
    Parallel,      // 全部并行启动
    Sequential,    // 按顺序执行
    Supervised,    // 主 agent 监督，按需启动
}
```

### 注释
- RunAgents 允许单个 tool call 同时启动多个子 agent，每个可以是 Local 或 Remote。
- 三种编排模式：Parallel（全并行）、Sequential（串行）、Supervised（主 agent 按需调度）。
- 每个子 agent 独立的工作目录和模型配置。

---

## OrchestrationConfig 用户审批式编排

### 来源
`app/src/ai/blocklist/orchestration_events.rs`

### 代码
```rust
pub struct OrchestrationConfig {
    pub require_user_approval: bool,          // 关键操作需用户审批
    pub auto_approve_read_only: bool,         // 只读操作自动通过
    pub max_concurrent_agents: usize,         // 最大并发 agent 数
    pub timeout_per_agent: Duration,          // 单个 agent 超时
    pub escalation_policy: EscalationPolicy,  // 升级策略
}

pub enum EscalationPolicy {
    AbortOnFailure,        // 任一失败则全部中止
    ContinueOnFailure,    // 失败的跳过，其余继续
    RetryThenEscalate,    // 重试后升级到用户
}
```

### 注释
- 用户审批式编排：关键操作（文件写入、命令执行）在执行前需用户确认。
- `auto_approve_read_only` 允许只读操作自动通过，减少审批噪音。
- EscalationPolicy 定义了子 agent 失败时的处理策略。

---

## Computer Use 跨平台 GUI 操作

### 来源
`app/src/ai/tools/computer_use.rs`

### 注释
- Warp 内置 Computer Use 工具，支持跨平台（macOS/Windows/Linux）的 GUI 自动化。
- 使用 `computer_use_model_id` 指定专用模型（通常为 vision model）。
- 操作包括：截屏、鼠标点击、键盘输入、窗口管理。
- 权限层独立控制：`computer_use` 在 `AIExecutionProfile` 中有专门开关。

---

## Cloud Environments 容器化运行

### 来源
`app/src/ai/cloud/`

### 注释
- Warp 支持在云端容器中运行 agent，隔离本地环境风险。
- Cloud 环境下所有 project skills 都可见（无 cwd 匹配限制）。
- Agent 的文件操作、命令执行都在容器内完成，结果通过 API 同步回本地。

---

## PTY Write Mode 三种模式

### 来源
`app/src/ai/blocklist/permissions.rs`

### 代码
```rust
pub enum PtyWriteMode {
    Disabled,       // 禁止写入 PTY
    Cautious,       // 只允许安全命令（按 allowlist）
    Autonomous,     // agent 可自由写入 PTY
}
```

### 注释
- PTY（伪终端）写入是 Warp 独有的工具模式：agent 直接向终端会话写入命令。
- 三种模式对应不同的自治级别：Disabled（完全手动）、Cautious（安全子集）、Autonomous（完全自主）。
- 与普通命令执行不同，PTY 写入可以与用户当前的终端会话交互（如发送 Ctrl+C 中断）。

---

## AskUserQuestion 结构化多选交互

### 来源
`app/src/ai/tools/ask_user.rs`

### 代码
```rust
pub struct AskUserQuestion {
    pub question: String,
    pub options: Vec<QuestionOption>,      // 结构化选项
    pub allow_free_text: bool,             // 是否允许自由文本
    pub timeout: Option<Duration>,
}

pub struct QuestionOption {
    pub label: String,
    pub value: String,
    pub description: Option<String>,
}
```

### 注释
- Agent 通过 `AskUserQuestion` 工具向用户提出结构化问题。
- 支持预定义选项（类似多选/单选）和自由文本输入。
- 有超时机制：超时后 agent 可使用默认选项继续。
- 在 `AIExecutionProfile` 中 `ask_user_question` 有独立开关。

---

## 与知识库的关联

### 印证

- `architecture/planes/control/overview.md`：带原因的权限枚举 = 可审计的控制层
- `architecture/planes/orchestration/overview.md`：OrchestrationEventService = Agent 间通信基础设施
- `design-space/methodology/harness-engineering.md`：Controller 编排了完整的 Harness 组件

### 独特贡献

1. **带原因的权限枚举**：`Allowed(reason)` / `Denied(reason)` 取代 bool，支持审计
2. **Agent 自主决策权限**：`AgentDecided` 同时出现在 allow/deny，agent 有自治权
3. **多模型路由**：一个请求可以指定不同场景使用不同模型
4. **多任务并行**：`HashMap<TaskId, Vec<AIAgentInput>>` 支持并行任务
5. **ProtectedPath 硬限制**：即使用户设置允许，系统文件也不可写
6. **Orchestration 事件系统**：支持多 Agent 间的消息传递和生命周期管理
7. **ThirdPartyHarness Adapter**：validate → prepare → build_runner 三阶段外部 agent 集成
8. **ResumePayload 跨 Agent 恢复**：关闭重开后继续之前的 agent 会话
9. **RunAgents 批量编排**：单个 tool call 启动多个 Local/Remote 子 agent
10. **Computer Use**：跨平台 GUI 自动化作为一等工具
11. **PTY Write Mode**：三级自治的终端直写模式
12. **AskUserQuestion**：结构化多选的人机交互
