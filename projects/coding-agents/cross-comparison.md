# Coding Agent 横向对比

> **Evidence Status** — synthesized. 基于本目录下 5 个 coding agent 项目分析的横向综合。

## 对比范围

| 编号 | Agent | 定位 | 语言 |
|------|-------|------|------|
| CC | Claude Code | 生产级 CLI coding agent | TypeScript |
| CX | Codex CLI | 本地沙箱 coding agent | Rust + TypeScript |
| OC | OpenCode | 多形态 agent 框架 | TypeScript (Effect.js) |
| GA | GenericAgent-as-coding (Augment) | 企业级 IDE agent | TypeScript (VSCode Extension) |
| WP | Warp | Agentic 开发平台 | Rust |

---

## 1. Compaction / Context 策略

| 维度 | CC | CX | OC | GA | WP |
|------|----|----|----|----|-----|
| 压缩层级 | 5 层：Tool Budget → Snip → Micro → Collapse → Auto | 2 阶段：Rollout 提取 → 全局合并 | 3 层：Prune → Compact → Truncate | 2 层：Truncate → Window | Skill-driven 注入，无显式压缩 |
| 触发方式 | 按 token 阈值渐进触发 | 后台异步提取 + 串行合并 | 溢出检测 (context - maxOutput - buffer) | 聊天历史截断/窗口 | Context Model 按需构造 |
| 摘要方法 | LLM 递归摘要 | LLM 提取 + sub-agent 合并 | 模板驱动摘要 (Goal/Instructions/Discoveries) | Cloud Blob 增量同步 | 无全局摘要 |
| 熔断机制 | 连续 3 次失败停止重试 | Watermark 防重复处理 | 无（重放降级） | 无 | 无 |
| 媒体处理 | 按 Provider 条件保留 | 不涉及 | 压缩时 stripMedia | Blob 上传 | 不涉及 |

---

## 2. Permission / Safety 模型

| 维度 | CC | CX | OC | GA | WP |
|------|----|----|----|----|-----|
| 核心模型 | permissionMode + Hooks 拦截 | Guardian LLM 风险评估 (0-100 分) | deny > ask > allow 三层规则 | 三级安全 (UNSAFE/SAFE/CHECK) | 带原因枚举 + Profile 系统 |
| 自动审批 | 只读工具自动通过 | 80 分以下自动通过 | last-match-wins 规则评估 | CHECK → RPC 检查 | AgentDecided + RunToCompletion |
| 沙箱 | 无原生沙箱 | 跨平台沙箱 (Seatbelt/Landlock/Restricted Token) | 无 | Sidecar 进程隔离 | Cloud 容器 + PTY 三模式 |
| 升级路径 | Hook 可阻止/注入 | 沙箱拒绝 → 用户确认 → 提权重试 | 权限请求 → Deferred 等待 | PreToolUse Hook 拦截 | 失败 → EscalationPolicy |
| 持久化 | 会话级 toolPermissionContext | 无 (每次评估) | always 规则写入 approved | dryRun 缓存 | 临时权限绑定对话生命周期 |
| 企业覆盖 | 无 | 无 | 系统管理配置 (/etc/opencode) | 无 | 企业 override 覆盖用户设置 |

---

## 3. Tool Orchestration

| 维度 | CC | CX | OC | GA | WP |
|------|----|----|----|----|-----|
| 并行策略 | 只读并发 (max 10) + 写入串行 | 无原生并行 | Batch Tool 用户态 25 并发 | 始终启用 parallel_tool_use | 多任务 HashMap + 多模型路由 |
| 流式执行 | StreamingToolExecutor (流中即执行) | 无 | Effect Stream 事件驱动 | 流式 + 并行 | ResponseStream 流式处理 |
| 延迟加载 | tool init 异步初始化 | 无 | tool.init(ctx) 运行时注入 | MCP 按需连接 | SkillManager 实时文件监控 |
| 工具来源 | 内置 60+ / MCP / 自定义 | 内置 + AGENTS.md | 内置 + 本地插件 + MCP | 四层主机 (Remote/Local/Sidecar/MCP) | 10 种 Provider 兼容 skill |
| 结果截断 | Tool Result Budget | 无 | 50KB / 2000 行双限制 | Cloud Blob | 无 |

---

## 4. Sub-agent 设计

| 维度 | CC | CX | OC | GA | WP |
|------|----|----|----|----|-----|
| 模式 | Fork (缓存共享) + Spawn (隔离) + In-process Teammate | spawn_agent (进程隔离) + 深度限制 | Task Tool → 递归 SessionPrompt | Worker Agent (主从编排, 8 管理工具) | RunAgents (Local/Remote 批量) + ThirdPartyHarness |
| 隔离级别 | 逻辑隔离 / Worktree / Remote | 独立进程 + 共享 AgentControl | 独立子会话 (parentID) | Sidecar 进程 | 容器 / PTY |
| 通信 | 消息 + 指令文本 / Mailbox | send_input / wait_agent | 摘要返回主上下文 | READ_STATE / SEND_INSTRUCTION | Orchestration 事件 + 生命周期订阅 |
| 恢复 | 后台任务 + Ctrl+B 背景化 | 无 | task_id 恢复已有任务 | Checkpoint + Shard | ResumePayload 跨会话恢复 |
| 深度限制 | 无显式限制 | spawn_depth_limit | maxSteps | 无显式限制 | max_concurrent_agents |

---

## 5. Error Recovery

| 维度 | CC | CX | OC | GA | WP |
|------|----|----|----|----|-----|
| Doom Loop | 无原生检测 (依赖 prompt) | 无 | 工具名+参数 JSON 全等, 3 次触发 | 无 | 无 |
| API 错误 | 413 → Collapse → Compact; max_output → 升级重试 (8k→64k) | 无 | 指数退避 (2^n, max 30s) + retry-after-ms | 无 | 事件重试 (max 3) |
| 熔断器 | autocompact 连续 3 次失败停止 | 无 | 无 | 无 | 无 |
| 分级恢复 | 4 层：Snip → Micro → Collapse → Auto | 2 层：沙箱 → 提权 | 3 层：Prune → Compact → 重放 | Hook 拦截 + blockTool | EscalationPolicy (Abort/Continue/RetryThenEscalate) |
| 用户干预 | Hook stop / abort | 用户确认提权 | 权限检查强制暂停 | stopAgent Hook | AskUserQuestion 结构化交互 |

---

## 6. Memory 管理

| 维度 | CC | CX | OC | GA | WP |
|------|----|----|----|----|-----|
| 会话持久化 | MEMORY.md (user/project/local 3 scope) | StateDb + rollout_summaries | SQLite (Drizzle ORM, WAL) | Checkpoint + Shard | Diesel + SQLite + Drive sync |
| Checkpoint | 会话文件 (recordTranscript) | 无 | DB messages + snapshot git | AggregateCheckpointManager | ResumePayload |
| 滑动窗口 | snipCompact 历史裁剪 | Phase 1 age_window + idle_threshold | Prune 保护最近 2 回合 | limitChatHistoryWindow | 无显式窗口 |
| 跨会话 | Session fork + 会话文件恢复 | 两阶段记忆管道 (Phase 1 并行 + Phase 2 合并) | Session fork + task_id 恢复 | Blob 增量同步 | ResumePayload 跨 agent 恢复 |
| 缓存策略 | 工具权限缓存 (当前会话) | 无 | LRU 40 会话 + 7 天截断文件保留 | PreToolUse 缓存 | skill 去重 (provider 优先级) |

---

## 7. 设计哲学

| 维度 | CC | CX | OC | GA | WP |
|------|----|----|----|----|-----|
| 复杂度 | 中重型 (60+ 工具, 4 层压缩, Hook 系统) | 中型 (沙箱为核心, Guardian 审批) | 中型 (Effect.js 函数式, 可组合框架) | 重型 (四层主机, Worker 编排, gRPC 后端) | 重型 (平台级, 多 agent 协作) |
| 交互范式 | Terminal-first CLI | Terminal-first CLI | Terminal + Web + Desktop 多形态 | IDE-first (VSCode) | Terminal-native 平台 |
| 核心理念 | Runtime 即工程：压缩/并发/Hook 闭环 | 安全即能力：沙箱深度决定执行深度 | 可组合 Runtime：Effect Service + Layer 正交设计 | 工具分层 + Worker 编排正交 | Agent 即贡献者：开发全流程一等参与 |
| 扩展机制 | Hooks + MCP + Custom Agents | AGENTS.md + AgentRoleConfig | 插件 + MCP + 本地工具 | MCP + Guidelines + Rules | Skills + ThirdPartyHarness |
| 开源程度 | 开源 (Anthropic) | 开源 (OpenAI) | 开源 (社区) | 闭源 (逆向分析) | 部分开源 (warpdotdev/warp) |

---

## 关键差异总结

1. **压缩策略最精细的是 Claude Code**：5 层渐进 + 熔断器，其他项目多为 2-3 层。
2. **安全模型最独特的是 Codex**：LLM Guardian 风险评估取代硬编码规则，沙箱覆盖三平台。
3. **框架可组合性最强的是 OpenCode**：Effect.js 三段式让每层可独立测试替换。
4. **Sub-agent 最重型的是 Augment**：Worker 是有完整生命周期的长生命周期实体。
5. **平台化程度最高的是 Warp**：ThirdPartyHarness 让外部 agent 成为可托管可恢复的 runtime 进程。

## 与知识库的关联

- 5 个项目共同验证了 `design-space/methodology/harness-engineering.md` 的 Harness = Context + Execution + Control + Orchestration 分层。
- 压缩策略对比补充了 `design-space/patterns/compaction.md` 的实现光谱：从无压缩到 5 层渐进。
- 安全模型对比补充了 `architecture/planes/control/overview.md`：从 deny/ask/allow 规则到 LLM Guardian 到带原因枚举。
- Sub-agent 对比补充了 `design-space/patterns/subagent.md`：从进程内 fork 到跨平台容器隔离。
