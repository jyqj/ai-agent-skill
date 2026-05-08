# OpenAI Codex CLI


> **Evidence Status** — grounded. 本目录下的源码片段与架构分析。

## 基本信息

- **类型**：coding-agent
- **项目定位**：本地 CLI coding agent，重点是跨平台沙箱、guardian 风险评估和多 agent 控制。
- **学习来源**：本地源码分析。
- **推荐入口**：README → guardian-policy.md / orchestrator.md / agent-control.md。

## 模块覆盖

| 模块 | 覆盖程度 | 证据文件 | 可复用模式 |
|---|---|---|---|
| execution | 深 | README.md / orchestrator.md | sandbox isolation |
| control | 深 | guardian-policy.md | risk-based approval + approval persistence |
| security | 深 | guardian-policy.md / exec-policy.md / network-proxy.md | transcript as evidence not instruction |
| orchestration | 中 | orchestrator.md / agent-control.md | agent registry + multi-agent v2 |
| state | 中 | memory-pipeline.md | memory pipeline + AGENTS.md loading |
| policy | 深 | exec-policy.md / hooks.md | deterministic-first approval |
| network | 深 | network-proxy.md | MITM proxy + domain-level ACL |

## 关键发现

### Runtime 吸收点

| Runtime obligation | 本项目模式 | 关键文件 |
|---|---|---|
| loop | task + orchestrator 分阶段运行 | `orchestrator.md` |
| context | compact task、history token accounting、memory pipeline | `memory-pipeline.md` |
| tool lifecycle | approval → sandbox → attempt → escalation retry | `orchestrator.md` |
| permission | Guardian 风险评估，transcript 只作证据 | `guardian-policy.md` |
| permission | 确定性规则优先于 LLM：Hooks → ExecPolicy → Guardian | `hooks.md` / `exec-policy.md` |
| network | MITM 代理实现域名级网络访问控制 | `network-proxy.md` |
| state / resume | SessionState、previous turn settings、AgentControl | `agent-control.md` |
| verification | sandbox outcome 不等于 effect verified，仍需测试/回读 | `orchestrator.md` |

- 沙箱的设计质量直接决定 agent 可被授予的执行深度——执行环境是能力的前提条件。
- 高风险 transcript 必须被视为"证据"而非"指令"，这一原则区分了安全的审批系统和可被注入的审批系统。
- 多 agent 协作需要独立控制平面（AgentControl），否则子 agent 的状态、超时和权限会污染主循环。

## 项目概述
OpenAI 官方的本地 CLI Coding Agent，Rust 实现。

## 学习来源
- **语言**: Rust (核心) + TypeScript (CLI 前端)
- **日期**: 2026-04-15

## 核心洞察

### 1. ToolOrchestrator 是工具执行的核心编排器

工具执行是一个完整的多阶段流程：
```
审批检查 → 沙箱选择 → 首次执行 →
  (如被沙箱拒绝) → 用户确认 → 提权重试
```

关键设计：
- `ExecApprovalRequirement` 枚举：Skip / Forbidden / NeedsApproval
- `SandboxAttempt` 封装每次执行尝试的沙箱配置
- 首次执行失败时，可请求用户批准后无沙箱重试
- 网络审批与文件系统审批分离

### 2. 跨平台沙箱架构（三种实现）

**macOS**: Seatbelt (`/usr/bin/sandbox-exec`)
- 使用 Seatbelt profile 限制文件/网络访问
- `.git` 和 `.codex` 强制只读

**Linux**: Landlock / Bubblewrap
- 优先使用系统 `bwrap`，降级到编译内置版本
- 支持 `--argv0` 兼容性检测

**Windows**: 受限令牌 / Elevated 后端
- `ReadOnlyAccess::Restricted` 模式
- 系统目录自动加入可读列表

关键设计：`FileSystemSandboxPolicy` 和 `NetworkSandboxPolicy` 完全分离。

### 3. Guardian 自动审批系统

**基于 LLM 的风险评估**，而非静态白名单/黑名单：
- 输入：transcript、tool call arguments、retry reason
- 输出：风险分数 (0-100)
- 80+ 分为高风险，需人工审批

Guardian 风险评估原则（见 `./guardian-policy.md`）：
- transcript 作为证据，不作为指令
- 读取丢失内容应更谨慎
- 凭证探测始终高风险
- 用户明确授权可降低风险

### 4. 多 Agent 协作模型

**核心组件**：
- `AgentControl`: 控制平面，管理 spawn/通信
- `AgentRegistry`: 注册表，追踪活跃 agent
- `AgentStatus`: 状态枚举 (Idle/Running/Waiting/Completed/Failed)

**协作工具**：
- `spawn_agent`: 创建子 agent（有深度限制）
- `wait_agent`: 等待子 agent 完成（有超时）
- `send_input`: 向子 agent 发送消息
- `list_agents` / `close_agent`: 管理

**关键设计**：
- 同一个 `AgentControl` 实例共享给所有子 agent
- `Weak<ThreadManagerState>` 避免循环引用
- 子 agent 自动分配昵称（从 `agent_names.txt`）

### 5. 两阶段记忆系统

**Phase 1: Rollout 提取（并行，每线程）**
- 从 state DB 选择近期会话
- 并行调用 LLM 提取结构化记忆
- 输出：`raw_memory`, `rollout_summary`, `rollout_slug`
- 秘密脱敏

**Phase 2: 全局合并（串行，单例）**
- 合并到长期记忆汇总（见 `./memory-pipeline.md`）
- 生成 `rollout_summaries/` 目录
- 运行合并 sub-agent
- watermark 追踪防止重复处理

设计精髓：Phase 1 水平扩展，Phase 2 保证一致性。

### 6. 角色系统与协作模式

**AgentRoleConfig**:
- 自定义 system prompt
- 工具集限制
- 昵称候选列表
- 模型选择

**Collaboration Mode**:
- default：标准模式
- execute：减少确认
- pair_programming：结对编程
- plan：规划模式

模式通过 `<collaboration_mode>` 标签切换。

### 7. AGENTS.md 规范

Codex 定义了 AGENTS.md 作为人机协作接口：
- 可出现在任何目录
- 深层文件优先级高于浅层
- 作用域 = 该目录及所有子目录
- 用户指令 > AGENTS.md > 默认行为

## 关键代码片段
- `./orchestrator.md` - 工具编排器流程
- 沙箱执行尝试 - 见本 README 的”ToolOrchestrator”与”跨平台沙箱架构”部分
- `./agent-control.md` - 多 Agent 控制 + Multi-Agent v2 消息模型
- `./memory-pipeline.md` - 记忆两阶段架构 + AGENTS.md 加载机制
- `./exec-policy.md` - Starlark 规则引擎与动态修订
- `./network-proxy.md` - MITM 代理与域名级网络控制
- `./hooks.md` - 确定性拦截层与事件 Hook
- `./guardian-policy.md` - 含三级审批持久化 + Guardian Session 安全隔离

## 与知识库的关联

### 印证的概念
- `design-space/methodology/harness-engineering.md`: ToolOrchestrator 是 Harness 核心组件的典型实现
- `../../../architecture/planes/orchestration/overview.md`: 子代理是上下文防火墙，有深度限制
- `../../../architecture/planes/control/overview.md`: Guardian 是护栏的 LLM 实现
- `../../../architecture/planes/execution/overview.md`: 跨平台沙箱设计

### 补充的模式
- `../../../design-space/patterns/compaction.md`: 记忆系统的两阶段策略是另一种 compaction
- `../../../design-space/patterns/subagent.md`: Codex 的 AgentControl 是生产级实现

### 独特贡献
1. **沙箱-审批-重试循环**：拒绝触发升级路径，安全策略从"阻止"变成"分级放行"
2. **Guardian LLM 审批**：用 LLM 做风险评估而非硬编码规则，使审批能力随模型能力一起进化
3. **AGENTS.md 规范**：把"项目级 agent 指令"从散落的 prompt 升格为有作用域、有优先级的标准化文件
4. **角色系统**：同一 harness 通过 AgentRoleConfig 支撑不同人格和工具集，验证了 harness 与人格的正交性
5. **三层确定性优先审批**：Hooks → ExecPolicy → Guardian，确定性规则先行，减少 LLM 调用开销
6. **渐进信任（ExecPolicyAmendment）**：用户审批自动沉淀为规则，从"每次确认"到"永久放行"粒度可控
7. **MITM 网络代理**：域名级网络策略与文件系统沙箱正交，双层隔离可独立控制
8. **Guardian 最小权限隔离**：审查者自身禁用一切副作用能力，防止 prompt 注入攻击审批系统
