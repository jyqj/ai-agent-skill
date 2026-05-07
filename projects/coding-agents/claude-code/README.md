# Claude Code


> **Evidence Status** — grounded. 基于本目录下的源码分析、layer 文档与 snippet。可信度高。

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

上下文压缩、工具并发执行和 Hook 权限控制三者在 QueryEngine 内形成闭环联动——这让它成为少数真正把 runtime 当工程问题来解决的生产级 harness。

## 关键发现

- QueryEngine 是跨 turn 持久化状态、驱动压缩和工具编排的完整 runtime，而非简单的 API 包装器。
- Hook 机制把控制层从”隐式约定”变成了”可声明、可拦截、可注入”的一等公民——这是大多数 agent 框架缺失的。
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
- 印证了 `paradigms/methodology/harness-engineering.md` 的 11 组件模型
- 补充了 `../../../design-space/patterns/compaction.md` 的实际实现（多层策略）
- 补充了 `../../../architecture/kernel/agent-loop.md` 的生产级实现
- 验证了 `../../../architecture/planes/orchestration/overview.md` 的子代理是上下文防火墙
