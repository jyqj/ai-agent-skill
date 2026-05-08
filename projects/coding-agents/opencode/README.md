# OpenCode


> **Evidence Status** — grounded. 本目录下的专题文件与架构总结。

## 基本信息

- **类型**：coding-agent
- **项目定位**：多形态 AI agent 框架，强调函数式 runtime、权限模型和多代理编排。
- **学习来源**：本地源码分析。
- **推荐入口**：README → context-engineering.md / tool-system.md / orchestration.md。

## 模块覆盖

| 模块 | 覆盖程度 | 证据文件 | 可复用模式 |
|---|---|---|---|
| context | 深 | context-engineering.md | prune / compact / truncate |
| tools | 深 | tool-system.md | schema validation / registry |
| control | 深 | control-memory.md | deny > ask > allow |
| orchestration | 中 | orchestration.md | task subagent |
| operations | 中 | README.md | framework-style rollout readiness |

## 独特贡献

OpenCode 是一个**可组合的 agent runtime 框架**。它用 Effect.js 的 Service + Layer 把依赖注入、错误处理和资源生命周期统一到类型系统中，harness 的每一层都可以独立测试和替换——从"做一个 agent"到"做一个 agent 框架"的关键跨越。

## 关键发现

### Runtime 吸收点

| Runtime obligation | 本项目模式 | 关键文件 |
|---|---|---|
| loop | session processor + Effect Service graph | `orchestration.md` |
| context | prune → compact → truncate 分级降级 | `context-engineering.md` |
| tool lifecycle | Zod schema、registry、permission 共同设计 | `tool-system.md` |
| permission | deny > ask > allow，异步 permission lifecycle | `control-memory.md` |
| state / resume | DB messages、continue/session/fork | `orchestration.md` |
| event stream | reducer / SSE 把 runtime events 落成 UI | `README.md` |

- 权限模型（deny > ask > allow）必须和工具系统共同设计，否则后补的权限层总是有缝隙。
- 上下文溢出不应是单一策略，OpenCode 的三层渐进处理（修剪 → 压缩 → 截断）证明了分层降级比单一阈值更鲁棒。
- Doom Loop 检测属于 runtime 基础设施，而不应该依赖 prompt 提示来"请不要重复"。

## 项目概述
多形态 AI Agent 框架（CLI/Web/Desktop），采用 Effect.js + Drizzle + Hono 技术栈，支持 27+ AI 供应商。

## 学习来源
- **日期**: 2026-04-15

## 核心洞察

### 1. Effect.js 函数式 Harness 架构
- 所有服务使用 `Service + Layer` 模式
- 依赖注入、资源管理、错误处理统一
- 可组合、可测试、自动生命周期管理

### 2. 三层上下文溢出管理
- **修剪 (Pruning)**: 倒向遍历，保护最近 2 个用户回合，删除旧工具输出
- **压缩 (Compaction)**: 模板驱动的摘要生成，失败时自动重放
- **截断 (Truncation)**: 50KB/2000行限制，超限写文件并提示

### 3. 9 种 Edit 匹配策略
从精确匹配到上下文感知，逐级降级：
SimpleReplacer → LineTrimmedReplacer → BlockAnchorReplacer → WhitespaceNormalizedReplacer → IndentationFlexibleReplacer → EscapeNormalizedReplacer → TrimmedBoundaryReplacer → ContextAwareReplacer → MultiOccurrenceReplacer

### 4. 三层权限模型 (deny > ask > allow)
- 规则支持通配符模式匹配
- 使用 Deferred 实现异步权限请求
- last-match-wins 评估策略

### 5. 多代理编排
- 7 个内置代理：build, plan, general, explore, compaction, title, summary
- 三种模式：primary, subagent, all
- Task 工具创建独立子会话运行子代理

### 6. Doom Loop 检测
- 工具名+参数 JSON 全等匹配，连续 3 次触发权限检查
- 匹配范围：单条 assistant message 内的 tool_calls 集合
- 步骤限制：`maxSteps = agent.steps ?? Infinity`

### 8. Effect.js 三段式桥接
- Interface（Zod Schema）→ Layer（Effect Service + 依赖注入）→ 静态门面（namespace Effect.fn）
- 每层可独立测试和替换

### 9. LSP 三级感知
- Level 1：edit 后自动触发 diagnostics 诊断
- Level 2：9 种主动操作工具（definitions, references, hover, symbols 等）
- Level 3：基于 symbol 信息自动修正 edit 影响范围
- 28 种语言自动 LSP server 管理（TypeScript, Rust, Go, Python, Java 等）

### 10. Snapshot 独立 Git
- 每个会话在 `.opencode/snapshots/` 下维护独立 git repo
- 不污染用户工作区 git 历史，支持会话级 revert

### 11. Batch Tool（用户态并行）
- 单次调用并行执行最多 25 个工具
- 每个子工具独立权限检查、独立截断、独立错误处理

### 12. Plan Mode
- 只读权限规则集，禁止所有写操作
- 与 build 模式共享会话上下文，无缝切换

### 7. 分级重试策略
- 检测 Overloaded/Rate Limited/exhausted 等错误
- 优先级：响应头 retry-after-ms > 指数退避（2^n 秒，最多 30s）

## 关键代码
- `./context-engineering.md` - System Prompt 构建、溢出检测、压缩策略
- `./tool-system.md` - 工具定义、注册、执行、权限控制
- `./orchestration.md` - Agent 循环、多代理、状态机
- `./control-memory.md` - 权限系统、会话状态、持久化存储

## 与知识库的关联
- 印证了 `design-space/methodology/harness-engineering.md` 的 Harness = Context + Execution + Control + Orchestration 分层
- 补充了 `../../../design-space/patterns/compaction.md` 的三层策略实现（修剪→压缩→截断）
- 补充了 `../../../design-space/patterns/subagent.md` 的 Task 工具子代理模式
- 印证了 `../../../architecture/planes/control/overview.md` 的权限模型设计（deny > ask > allow）
- 补充了 `../../../architecture/kernel/agent-loop.md` 的 Doom Loop 检测机制
- 印证了 `../../../architecture/planes/execution/overview.md` 的工具系统设计（Zod 验证、权限上下文）

## 技术栈
| 层级 | 技术 | 用途 |
|------|------|------|
| Runtime | Bun 1.3.11 | 快速执行、内置 SQLite、TS 原生 |
| FX | Effect.js 4.0.0-beta | 函数式错误处理、异步编排 |
| Validation | Zod 4.1.8 | Schema 定义与验证 |
| HTTP | Hono 4.10.7 | 轻量 Web 框架 |
| Database | Drizzle ORM 1.0.0-beta | 类型安全 SQL |
| AI SDK | ai (Vercel) 6.0.138 | LLM 适配器、流式处理 |
| TUI | @opentui 0.1.92 | 终端 UI 渲染 |
| Frontend | SolidJS 1.9.10 | 响应式 Web UI |

## 架构图
```
opencode (monorepo)
├── packages/
│   ├── opencode/              # 核心引擎（286 个 TS 文件）
│   │   ├── src/agent/         # 代理定义与配置
│   │   ├── src/session/       # 会话、消息、压缩、重试
│   │   ├── src/tool/          # 工具系统
│   │   ├── src/permission/    # 权限控制
│   │   ├── src/mcp/           # MCP 集成
│   │   ├── src/provider/      # 27+ AI 供应商适配
│   │   ├── src/bus/           # 事件总线
│   │   ├── src/plugin/        # 插件系统
│   │   └── src/server/        # HTTP/WebSocket 服务
│   ├── app/                   # Web UI (SolidJS)
│   ├── console/               # TUI 控制台
│   └── ...                    # desktop, sdk, plugin 等
```
