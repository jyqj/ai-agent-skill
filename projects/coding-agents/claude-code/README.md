# Claude Code

## 证据卡

**证明了什么**：成熟的单 Agent coding assistant 需要精细的上下文管理、多层权限、流式工具执行和 Hook 可编程性。

**核心运行时对象**：

| 对象 | 实现 | 对应 Plane |
|------|------|-----------|
| Agent Loop | Generator/yield + 7 个恢复路径 + State.transition | kernel/agent-loop |
| Context Engine | 五级压缩 + 13K buffer + microCompact | context |
| Permission | 4 层管线（config→classifier→hook→user） | control, security |
| Tool Orchestration | isConcurrencySafe + StreamingToolExecutor | tools |
| Hook System | asyncRewake + interrupt + TaskOutput 管理 | interaction |

**可复用规则**：
1. 恢复策略必须有 circuit breaker（maxOutputTokensRecoveryCount=3）
2. 压缩有安全缓冲（13K），micro 优先于 full
3. 工具并发按 input 动态判定，非静态分类
4. Hook 可中止整个 turn（interrupt），不只是拒绝单个工具
5. Fallback 时清空已队列工具结果，防止跨模型状态泄漏

**不该照搬的**：
- Generator 模式与 Rust/Go 生态不兼容，选型需按语言特性
- 200K 上下文窗口的压缩策略不适用于小窗口模型

**关键数值**：13K buffer, maxRecovery=3, maxConcurrency=10, hookTimeout=600s/1.5s

---

> **Evidence Status** — grounded. 基于本目录下的源码分析、layer 文档与源码观察摘录。可信度高。

## 基本信息

- **类型**：coding-agent
- **项目定位**：生产级 CLI coding agent，重点是 QueryEngine、压缩、工具并发与 hooks。
- **学习来源**：本地源码分析与专题文档。
- **推荐入口**：README → context-layer.md / execution-layer.md / control-layer.md。

## 模块覆盖

| 模块 | 覆盖程度 | 证据文件 | 可复用模式 |
|---|---|---|---|
| context | 深 | context-layer.md | compaction / progressive disclosure |
| tools | 深 | execution-layer.md | tool registry / concurrency control |
| control | 深 | control-layer.md | hook-system / verification gate |
| orchestration | 中 | orchestration-layer.md | subagent |
| state | 中 | state-ui-layer.md | git-based state |
| memory | 中 | context-layer.md | skill loading |

## 独特贡献

上下文压缩、工具并发执行和 Hook 权限控制三者在 QueryEngine 内形成闭环联动。这使其成为少数真正把 runtime 当工程问题来解决的生产级 harness。

## 关键发现

### Runtime 吸收点

| Runtime obligation | 本项目模式 | 关键文件 |
|---|---|---|
| loop | QueryEngine / query loop 管理跨 turn 状态 | `query-loop.md` |
| context | snip、micro、collapse、auto 多层压缩 | `compaction.md`、`context-layer.md` |
| tool lifecycle | 只读并发、写操作受控、工具结果回写状态 | `tool-orchestration.md`、`execution-layer.md` |
| permission | permission mode + hooks 拦截 | `hooks-system.md`、`control-layer.md` |
| state / UI | AppState、tool progress、session 状态投影 | `state-ui-layer.md` |
| verification | diff / test / readback 进入 stop gate | `query-loop.md` |

- QueryEngine 是跨 turn 持久化状态、驱动压缩和工具编排的完整 runtime，而非简单的 API 包装器。
- Hook 机制把控制层从”隐式约定”变成了”可声明、可拦截、可注入”的一等公民，这一点在大多数 agent 框架中是缺失的。
- 上下文压缩是四层按阈值渐进触发的策略链（snip → micro → collapse → auto），每层独立可组合。

## 核心洞察

### 1. QueryEngine 是核心 Harness
- `QueryEngine` 类封装了整个会话生命周期
- 每个会话一个 QueryEngine 实例，状态跨 turns 持久化
- 核心状态：messages、fileStateCache、usage、permissionDenials

### 2. query() 是真正的 Agent Loop
- `query.ts` 中的 `queryLoop()` 是无限循环的 TAO 实现
- 状态用 `State` 对象管理，包含：messages、toolUseContext、autoCompactTracking、turnCount 等
- 每次迭代：压缩 → 调用 API → 解析响应 → 执行工具 → 更新状态

### 3. 多层压缩策略（非常精细）
- **snipCompact**: 历史裁剪
- **microcompact**: 工具输出压缩
- **contextCollapse**: 上下文折叠
- **autoCompact**: 超过阈值时完整摘要
- 按顺序执行，每层独立，可组合

### 4. 工具执行的并发控制
- `toolOrchestration.ts` 实现了智能分批
- 只读工具并发执行，写入工具串行执行
- `isConcurrencySafe` 属性标记工具是否可并发

### 5. Hooks 是一等公民
- 20+ 种 hook 事件类型
- 支持同步和异步 hook
- hook 可以注入消息、修改权限、阻止操作
- 用于 session lifecycle、tool execution、permission、file changes

### 6. 子代理是独立的 query 调用
- `runAgent.ts` 创建隔离的 `ToolUseContext`
- 子代理有自己的 MCP servers、tools、file state cache
- 结果通过摘要返回主上下文

## 架构层深度分析

基于 Harness Engineering 视角的完整架构分析：

| 文档 | 覆盖范围 | 核心洞察 |
|------|---------|---------|
| [context-layer.md](context-layer.md) | memdir/, skills/, context/ | Memory 四类型分类、Skills 渐进披露、Context 通知队列 |
| [execution-layer.md](execution-layer.md) | tools/, services/mcp/ | 60+ 工具架构、权限决策树、MCP 客户端 |
| [control-layer.md](control-layer.md) | services/compact/, hooks/ | 4 阶段压缩、25 种 Hook、熔断机制 |
| [orchestration-layer.md](orchestration-layer.md) | QueryEngine, query, AgentTool/ | 查询循环、Fork vs Spawn、Task 系统 |
| [state-ui-layer.md](state-ui-layer.md) | state/, ink/, components/ | AppState 状态树、Ink 渲染管道、性能优化 |

## 关键代码片段
- `./query-loop.md` - Agent 主循环
- `./compaction.md` - 多层压缩策略
- `./tool-orchestration.md` - 工具执行编排
- `./hooks-system.md` - Hook 机制

## 与知识库的关联
- 印证了 `design-space/methodology/harness-engineering.md` 的 11 组件模型
- 补充了 `../../../design-space/patterns/compaction.md` 的实际实现（多层策略）
- 补充了 `../../../architecture/kernel/agent-loop.md` 的生产级实现
- 验证了 `../../../architecture/planes/orchestration/overview.md` 的子代理是上下文防火墙
