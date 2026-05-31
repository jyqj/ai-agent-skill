# Hermes Agent

## 证据卡

**证明了什么**：大规模多平台 Agent 需要 Gateway 边界隔离、结构化错误分类、多维预算和自主学习循环。

**核心运行时对象**：

| 对象 | 实现 | 对应 Plane |
|------|------|-----------|
| Gateway | 35+ 平台适配器 + 会话隔离 + Cron 调度 | sensing-representation |
| ToolRegistry | AST 动态发现 + check_fn TTL 30s | tools |
| ErrorClassifier | 8 阶段管线 + 17 种 FailoverReason | recovery |
| IterationBudget | 4 维（iteration/token/time/cost） + consume/refund | context, cost |
| SQLite FTS5 | trigram tokenizer + WAL + Jitter 重试 | memory |
| Skill Curator | 间隔 7 天 + idle 2h 才运行 | learning |

**可复用规则**：
1. 错误分类用管线而非 switch-case，每阶段可独立演进
2. 工具可用性探测缓存 30s（check_fn TTL），避免高频重复检测
3. 记忆用 FTS5 而非向量 DB（零运营成本），trigram tokenizer 支持模糊匹配
4. Curator 间隔 7 天 + idle 2h 才运行，避免打断实时任务
5. 冻快照模式同时解决前缀缓存热度和跨会话记忆生效

**不该照搬的**：
- 35+ 平台适配的复杂度对单平台 Agent 是过度设计
- Kanban Worker 隔离模式仅在多 Worker 分布式场景有价值

**关键数值**：IterationBudget 默认 90(父)/50(子), check_fn TTL=30s, curator 间隔=7 天, FTS5 trigram tokenizer

---

> **Evidence Status** — grounded. 本目录下的 gateway、memory、execution、tool registry 等分析。

## 基本信息

- **类型**：general-agent
- **项目定位**：生产级通用 agent，重点是内置学习循环、多平台 gateway 和多 backend 执行。
- **学习来源**：仓库分析与源码观察文件。
- **推荐入口**：README → gateway.md / memory-skills.md / execution-env.md。

## 模块覆盖

| 模块 | 覆盖程度 | 证据文件 | 可复用模式 |
|---|---|---|---|
| interface | 深 | gateway.md | platform adapter |
| tools | 深 | tool-registry.md | tool registry / toolset / MCP / Kanban |
| execution | 深 | execution-env.md | 7 后端执行 + Checkpoints v2 |
| memory | 中 | memory-skills.md | frozen snapshot / skills |
| learning | 中 | memory-skills.md | self-improvement loop |
| control | 中 | README.md | three-layer approval |
| browser | 中 | tool-registry.md | Lightpanda + Chrome 双引擎 |
| kanban | 中 | tool-registry.md | 任务分派 + Worker 隔离 |

## 独特贡献

Hermes 把学习循环内置到 runtime 中：从经验中创建技能、技能在使用中迭代优化、主动触发记忆持久化。结合多平台 gateway 和 7 种执行后端，它展示了一个**能跨会话成长、跨平台部署**的长期运行系统的完整形态。最新版本新增了 Kanban 工作流分派系统、Checkpoints v2 单一共享存储、Lightpanda 高速浏览器引擎，以及深度 MCP/ACP 集成。

## 关键发现

- Gateway 不只是”接入层”，它定义了 agent runtime 的真实边界：会话隔离、平台适配、Cron 调度都在这里发生。
- 冻结快照模式（系统提示冻结 + 运行时写磁盘）同时解决了前缀缓存热度和跨会话记忆生效两个问题。
- 工具注册表作为单一真实源（schema / handler / check_fn 统一查询），消除了工具信息在 prompt、代码、配置之间的漂移。
- Checkpoints v2 单一共享 store（`~/.hermes/checkpoints/store/`）实现全局对象去重，磁盘占用从 ~847MB（47 shadow repos）降至 <200MB。
- Kanban 分派模式通过环境变量握手（`HERMES_KANBAN_TASK` / `HERMES_KANBAN_RUN_ID`）实现 Worker 隔离，兼顾分布式协作与安全。
- Lightpanda（Zig 实现）导航速度 1.3-5.8x 快于 Chrome，内存占用更低，失败时自动回退到 Chrome。

> **Self-improving AI Agent by Nous Research**

## 项目概述

Hermes Agent 是一个生产级 AI Agent 系统，核心特点是**内置学习循环**：
- 从经验中创建技能
- 技能在使用中迭代优化
- 主动触发记忆持久化
- 跨会话搜索过去对话
- 跨会话构建用户模型

## 架构亮点

```
Agent = AIAgent (run_agent.py) + Harness (everything else)

核心循环：同步单线程，ThreadPoolExecutor 并发工具执行
上下文策略：冻快照 + 实时持久化 + 延迟压缩
工具系统：中心化注册表 + Toolset 组合 + MCP / managed gateway 动态发现
记忆系统：FTS5 全文搜索 + 冻快照注入
执行环境：7 后端（local/docker/ssh/modal/daytona/vercel/singularity）+ Checkpoints v2
多平台网关：适配器模式 + 会话隔离 + Cron 调度
浏览器引擎：Lightpanda + Chrome 双引擎（自动降级）
任务分派：Kanban 工作流 + Worker 隔离 + Diagnostics
协议集成：MCP（Model Context Protocol）+ ACP（Agent Control Plane）
```

## 关键设计决策

| 决策 | 选择 | 原因 |
|-----|------|------|
| Agent Loop | 同步 | 简化调试，线程安全通过锁实现 |
| 工具执行 | 可选并发 | 仅在安全时并行（无路径冲突、无交互） |
| 上下文压缩 | 延迟触发 | 50% 阈值，两阶段（轻量剪枝 + LLM 总结） |
| 记忆注入 | 冻快照 | 保持前缀缓存热度，mid-session 写不改提示 |
| 子代理 | 完全隔离 | 独立 toolset/prompt/session，防权限提升 |
| 审批 | 三层 | 正则检测 → 智能评估 → 用户确认 |
| Checkpoints | v2 共享 store | 全局对象去重，auto_prune + size_cap 自动维护 |
| 浏览器 | 双引擎 | Lightpanda 快速路径 + Chrome 完整功能回退 |
| 任务分派 | Kanban + Worker | 环境变量握手隔离，diagnostics engine 检测异常 |
| 协议 | MCP + ACP | schema_sanitizer 标准化 + OAuth 认证流 |

## 文件索引

| 文件 | 内容 |
|------|------|
| `./agent-loop.md` | 核心循环、迭代预算、压缩触发 |
| `./tool-registry.md` | 工具注册、dispatch、MCP/Kanban/Lightpanda |
| `./memory-skills.md` | 记忆持久化、技能系统、学习循环 |
| `./execution-env.md` | 7 后端执行环境、Checkpoints v2、沙箱策略 |
| `./gateway.md` | 多平台网关、会话管理、Cron |
| `./credential-pool.md` | 多凭证故障转移引擎、选择策略、租约管理 |
| `./error-recovery.md` | 结构化错误分类管道、17 种 FailoverReason |
| `./transport-layer.md` | Provider 格式转换层、多 provider 适配 |

## 可复用洞察

1. **冻快照模式** - 系统提示冻结保持缓存，运行时写磁盘跨会话生效
2. **迭代预算** - 线程安全计数器，consume/refund 模型，压力警告注入
3. **注册表单一真实源** - 所有 schema/handler/check_fn 从一处查询
4. **Toolset 组合** - includes 递归展平，enable/disable 过滤
5. **子代理隔离** - 工具交集、独立 prompt、跨度限制
6. **威胁扫描** - 记忆写入前检测注入/泄露模式
7. **WAL + Jitter 重试** - SQLite 多进程安全，随机退避破坏 convoy
8. **渐进式信息披露** - 技能元数据列表 → 完整内容 → 支持文件
9. **Checkpoints v2 共享存储** - 单一 store 全局对象去重，auto_prune + enforce_size_cap 自动维护
10. **双引擎浏览器** - Lightpanda 快速路径 + Chrome 完整功能自动降级，screenshot 预路由
11. **Kanban Worker 隔离** - 环境变量握手（HERMES_KANBAN_TASK）+ 工具交集 + skip_memory
12. **MCP Schema 标准化** - schema_sanitizer 处理 Pydantic/MCP 不规范输出，OAuth 流集成
