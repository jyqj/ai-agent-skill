# Warp Feature Flag System

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。

> **Evidence Status** — grounded. `crates/warp_features/src/lib.rs` 完整源码（1188 行）。

## 架构概述

Warp 的 feature flag 系统是一个**编译期 + 运行时混合**的三层设计，支持 150+ 个 feature flags 和四阶段渐进发布。

## 核心数据结构

```rust
// crates/warp_features/src/lib.rs

#[derive(Copy, Clone, Hash, PartialEq, Eq, Debug, Sequence)]
pub enum FeatureFlag {
    // --- 基础设施 ---
    Changelog,
    CrashReporting,
    DebugMode,
    Autoupdate,
    RuntimeFeatureFlags,
    
    // --- AI / Agent Mode (核心) ---
    AgentMode,
    AgentModeAnalytics,
    AgentModeWorkflows,
    AIRules,
    AgentPredict,
    AgentModePrimaryXML,      // XML 输出 system prompt
    AgentModePrePlanXML,
    AgentOnboarding,
    AgentDecidesCommandExecution,  // agent 自主决定是否执行命令
    PredictAMQueries,
    AIMemories,                // 自动生成 AI 记忆
    AIResumeButton,
    AskUserQuestion,           // agent 可主动提问
    
    // --- MCP ---
    McpServer,
    McpOauth,
    FileBasedMcp,              // .mcp.json 文件支持
    MCPGroupedServerContext,
    
    // --- Skills ---
    OzPlatformSkills,          // 从 .agents/skills/ 等目录加载 skills
    BundledSkills,             // Warp 内置 skills
    SkillArguments,            // skill 参数传递
    ListSkills,                // 发送 skills 列表给服务端
    
    // --- Orchestration (多 Agent) ---
    Orchestration,             // 多 agent 并行执行
    OrchestrationV2,           // 服务端持久消息
    OrchestrationPillBar,      // UI: agent 切换条
    
    // --- Code / Editor ---
    ContextChips,
    GrepTool,
    FileRetrievalTools,
    ImageAsContext,
    CrossRepoContext,
    CodebaseIndexPersistence,
    FullSourceCodeEmbedding,
    
    // ... 150+ flags total
    
    // --- 最新: Cloud Mode, HOA, Oz ---
    CloudMode,
    CloudModeFromLocalSession,
    AgentHarness,              // 外部 agent CLI 支持
    OzHandoff,                 // 工作区快照交接
    HOANotifications,
    CloudModeInputV2,
    HandoffCloudCloud,
}
```

**设计要点**：150+ flags 中约 40% 与 AI/Agent 直接相关，体现了 Warp 向 Agentic Development Environment 的转型深度。

## 三层状态优先级

```rust
// 优先级：override > user_preference > global_state

static FLAG_STATES: [AtomicBool; cardinality::<FeatureFlag>()] =
    [const { AtomicBool::new(false) }; { cardinality::<FeatureFlag>() }];

static USER_PREFERENCE_MAP: [AtomicTriState; cardinality::<FeatureFlag>()] =
    [const { AtomicTriState::new() }; { cardinality::<FeatureFlag>() }];

impl FeatureFlag {
    pub fn is_enabled(&self) -> bool {
        // 三层查询：test override → user preference → global state
        overrides::get_override(*self)
            .or(USER_PREFERENCE_MAP[*self as usize].get())
            .or(Some(FLAG_STATES[*self as usize].load(Ordering::Relaxed)))
            .unwrap_or(false)
    }

    pub fn set_user_preference(self, enabled: bool) {
        USER_PREFERENCE_MAP[self as usize].set(enabled);
    }

    // 测试专用：RAII guard，drop 时自动清除
    #[cfg(feature = "test-util")]
    pub fn override_enabled(self, enabled: bool) -> overrides::OverrideGuard {
        overrides::override_flag(self, enabled)
    }
}
```

**设计洞察**：
- `AtomicTriState` 自定义了三态原子类型（Unset/False/True），避免 `Option<AtomicBool>` 的开销
- User preference 允许用户显式 opt-in/opt-out，覆盖全局状态
- Test override 用 RAII guard + thread-local，确保测试隔离
- Debug 模式下断言 flags 已初始化，防止过早访问

## 四阶段渐进发布

```rust
// 阶段 1: Dogfood — 开发团队
pub const DOGFOOD_FLAGS: &[FeatureFlag] = &[
    FeatureFlag::AgentModeAnalytics,
    FeatureFlag::AgentModeWorkflows,
    FeatureFlag::OzPlatformSkills,
    FeatureFlag::OrchestrationV2,
    FeatureFlag::AgentHarness,
    FeatureFlag::OzHandoff,
    FeatureFlag::HOANotifications,
    // ... 60+ flags
];

// 阶段 2: Preview — Friends of Warp
pub const PREVIEW_FLAGS: &[FeatureFlag] = &[
    FeatureFlag::Orchestration,
    FeatureFlag::BlocklistMarkdownTableRendering,
    FeatureFlag::MarkdownTables,
    FeatureFlag::GitOperationsInCodeReview,
    // ... smaller set
];

// 阶段 3: Release — 所有正式版用户
pub const RELEASE_FLAGS: &[FeatureFlag] = &[
    FeatureFlag::Autoupdate,
    FeatureFlag::Changelog,
    FeatureFlag::CrashReporting,
    // 注意：大部分功能通过 app/Cargo.toml default features 而非此列表启用
];

// 阶段 4: 移除 — remove-feature-flag skill 清理
```

## 测试 Override 隔离

```rust
#[cfg(feature = "test-util")]
mod overrides {
    thread_local! {
        static FLAG_OVERRIDES: RefCell<HashMap<FeatureFlag, bool>> = RefCell::new(HashMap::new());
    }

    #[must_use = "if unused the override will be immediately cleared"]
    pub struct OverrideGuard { flag: FeatureFlag }

    pub fn override_flag(flag: FeatureFlag, enabled: bool) -> OverrideGuard {
        set_override(flag, enabled);
        OverrideGuard { flag }
    }

    impl Drop for OverrideGuard {
        fn drop(&mut self) {
            clear_override(self.flag);  // RAII: 自动清除
        }
    }
}
```

**关键规则**：
- `#[must_use]` 防止 override guard 被忽略
- 不支持嵌套 override（panic on duplicate）
- Thread-local 意味着多线程测试需要每个线程设置 override

## 运行时菜单集成

```rust
// crates/warp_core/src/features.rs
pub fn runtime_flags_menu_items() -> Vec<MenuItem> {
    if !FeatureFlag::RuntimeFeatureFlags.is_enabled() {
        return Vec::new();
    }
    RUNTIME_FEATURE_FLAGS
        .iter()
        .map(|flag| feature_flag_menu_item(*flag))
        .collect()
}
```

RuntimeFeatureFlags 本身也是一个 flag — 只有 debug/dogfood 版本才能在运行时切换 flags。

## 与知识库的关联

### 印证

- `architecture/planes/control/overview.md`：Feature flag 是运行时控制的一种实现
- `design-space/patterns/`：渐进发布（dogfood → preview → release → remove）是经典的 canary 模式

### 独特贡献

1. **三层状态优先级**：override > user preference > global，比简单的 on/off 更灵活
2. **AtomicTriState**：自定义原子类型处理"未设置"状态
3. **RAII Override Guard**：测试隔离的优雅实现
4. **Flag 本身也是 Flag**：RuntimeFeatureFlags 控制运行时切换能力
5. **150+ Flags 中 40% 是 AI 相关**：量化了 Warp 的 agent 转型深度
