# Warp Terminal + AI Integration Architecture

> **Evidence Status** — grounded. `WARP.md`、`app/src/` 目录结构、`Cargo.toml` workspace 配置。

## 架构总览

Warp 把 AI 能力嵌入终端架构，是一体化设计而非插件式集成。

```text
┌─────────────────────────────────────────────────────────────────┐
│                      Warp Application                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │   Terminal     │  │   AI / Agent  │  │   Drive       │       │
│  │   Emulation    │  │   Mode        │  │   (Cloud Sync)│       │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘       │
│          │                  │                   │               │
│  ┌───────┴──────────────────┴───────────────────┴───────┐      │
│  │                    Workspace Layer                    │      │
│  │  Sessions │ Terminals │ Notebooks │ Settings          │      │
│  └───────────────────────┬───────────────────────────────┘      │
│                          │                                      │
│  ┌───────────────────────┴───────────────────────────────┐      │
│  │                     WarpUI Framework                   │      │
│  │  Entity-Component-Handle │ Elements │ Actions │ Theme  │      │
│  └───────────────────────┬───────────────────────────────┘      │
│                          │                                      │
│  ┌───────────────────────┴───────────────────────────────┐      │
│  │                    Platform Layer                      │      │
│  │  macOS │ Windows │ Linux │ WASM                        │      │
│  └───────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

## 自研 UI 框架：WarpUI

### Entity-Component-Handle 模式

WarpUI 不使用 DOM、React 虚拟 DOM 或传统 MVC，而是采用类似 ECS（Entity-Component-System）的架构：

```text
全局 App 对象
  └── 拥有所有 Views 和 Models（entities）
       ├── View A ──── ViewHandle<B> ──→ View B
       ├── View B ──── ViewHandle<C> ──→ View C
       └── Model M ── ModelHandle<N> ──→ Model N
```

关键设计规则：
- **全局 App 对象拥有所有实体**：Views 和 Models 不直接持有彼此，通过 Handle 引用
- **AppContext 提供临时访问**：render/event 期间通过 AppContext 解引用 Handle
- **Elements 描述视觉布局**：Flutter 启发的声明式元素系统
- **Actions 处理事件**：类似 Elm Architecture 的消息传递
- **MouseStateHandle 必须在构造时创建**：render 中内联 `MouseStateHandle::default()` 会导致鼠标交互失效

### 与 Agent 的关系

WarpUI 的 Entity-Handle 模式对 agent 编程有重要影响：
- Agent 必须理解 Handle 间接性，不能直接操作 View，要通过 Handle
- 终端 Model 的 lock 机制要求 agent 理解死锁风险
- 跨平台条件编译意味着 agent 修改 UI 代码时必须考虑平台差异

## Terminal Model Locking

Warp 对终端模型锁有严格的安全要求：

```text
⚠️ TerminalModel.lock() 规则：
1. 加新 lock 前，验证调用栈中没有已持有的 lock
2. 优先传递已 lock 的引用，而非重新获取 lock
3. 必须 lock 时，保持范围尽可能小
4. 避免在持锁期间调用可能也会 lock 的函数
```

**对 agent 的启示**：这不是一般的"注意线程安全"。Warp 把具体的 lock 安全规则写入了 `WARP.md`，确保 agent（无论是 Oz 还是外部 agent）在修改终端相关代码时遵守。

## Feature Flag 生命周期

Warp 的 feature flag 系统体现了渐进发布的完整设计：

```text
定义 flag        →  dogfood 默认开启  →  preview 推广  →  release 推广  →  移除 flag + 清理死代码
add-feature-flag    DOGFOOD_FLAGS        promote-feature   RELEASE_FLAGS    remove-feature-flag
```

```rust
#[derive(Sequence)]
pub enum FeatureFlag {
    YourNewFeature,
}

pub const DOGFOOD_FLAGS: &[FeatureFlag] = &[
    FeatureFlag::YourNewFeature,
];

if FeatureFlag::YourNewFeature.is_enabled() {
    // 被 flag 保护的行为
}
```

关键设计：
- **优先运行时检查而非编译期指令**：`FeatureFlag::X.is_enabled()` 优于 `#[cfg(...)]`，方便切换和清理
- **`#[cfg(...)]` 仅用于编译必需的场景**：平台特定代码或依赖不存在时
- **Flag 要高层、面向产品**：不是每个调用点一个 flag
- **有专门的 skill 管理生命周期**：add / promote / remove 三个独立 skill

## Cargo Workspace 架构

60+ member crates 的 workspace 结构体现了模块化设计：

| 层级 | Crate | 职责 |
|---|---|---|
| 应用层 | `app/` | 主应用二进制：终端、AI、Drive、认证、设置、工作区 |
| UI 框架 | `crates/warpui/`、`crates/warpui_core/` | 自研 UI 框架（MIT 许可） |
| 核心工具 | `crates/warp_core/` | 平台抽象、核心工具 |
| 编辑器 | `crates/editor/` | 文本编辑功能 |
| 通信 | `crates/ipc/`、`crates/graphql/` | 进程间通信、GraphQL |
| 持久化 | `crates/persistence/` | Diesel ORM + SQLite + migrations |
| 测试 | `crates/integration/` | 自定义集成测试框架 |

## 测试策略

Warp 对测试有明确的分层要求：

```text
单元测试：cargo nextest run
  - 文件命名：${filename}_tests.rs 或 mod_test.rs
  - 通过 #[cfg(test)] #[path = "..."] mod tests; 包含
  - 不在对应模块文件中直接写测试

集成测试：crates/integration/
  - 自定义测试框架
  - 端到端用户流覆盖

预提交检查：./script/presubmit
  - cargo fmt
  - cargo clippy --workspace --all-targets --all-features --tests -- -D warnings
  - 测试套件
```

## 编码风格对 Agent 的约束

Warp 的 `WARP.md` 不只是风格指南，更是 agent 的行为约束：

| 约束 | 说明 | Agent 影响 |
|---|---|---|
| 避免不必要的类型标注 | 尤其是闭包参数 | agent 不应过度标注类型 |
| 用 import 而非路径限定符 | 除 cfg 保护的代码分支外 | agent 要把 import 放文件顶部 |
| context 参数名为 `ctx` 且放最后 | AppContext/ViewContext/ModelContext | agent 改函数签名时必须遵守 |
| 移除未使用参数 | 不用 `_` 前缀，直接删除 + 更新调用方 | agent 要同时修改签名和所有调用点 |
| 内联 format 参数 | `eprintln!("{message}")` | agent 不用 `eprintln!("{}", message)` |
| 不删除无关注释 | 除非注释描述的逻辑已改变 | agent 不应在修改时顺手删注释 |
| 穷尽匹配 | 避免 `_` 通配符 | agent 加 enum variant 时必须处理所有 match |

## 与知识库的关联

### 印证

- `architecture/planes/interface/overview.md`：终端作为 agent 的原生接口，不需要适配层
- `architecture/planes/execution/overview.md`：Cargo workspace + 跨平台编译 = 执行环境隔离
- `design-space/patterns/hook-system.md`：feature flag 生命周期由专门的 skill hook 管理

### 补充

- **Terminal-Native Agent**：不同于 IDE 插件或 CLI wrapper，agent 运行在终端的原生进程中
- **Lock Safety as Agent Constraint**：把线程安全规则写入 agent 可读的文档，是 agent 约束的新方式
- **Style Guide as Agent Behavior**：编码风格是 agent 的硬约束

### 独特贡献

1. **Entity-Component-Handle UI**：自研 UI 框架作为 agent 操作的目标环境
2. **Feature Flag Lifecycle Skills**：三个 skill（add/promote/remove）覆盖完整生命周期
3. **Lock Safety in WARP.md**：通过文档约束 agent 的并发行为
4. **60+ Crate Workspace**：模块化设计让 agent 能精准定位修改范围
