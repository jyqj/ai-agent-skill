# Hermes Agent


> **Evidence Status** — grounded. 本目录下的 gateway、memory、execution、tool registry 等分析。

## 基本信息

- **类型**：general-agent
- **项目定位**：生产级通用 agent，重点是内置学习循环、多平台 gateway 和多 backend 执行。
- **学习来源**：仓库分析与 snippet 文件。
- **推荐入口**：README → gateway.snippet.md / memory-skills.snippet.md / execution-env.snippet.md。

## 模块覆盖

| 模块 | 覆盖程度 | 证据文件 | 可复用模式 |
|---|---|---|---|
| interface | 深 | gateway.snippet.md | platform adapter |
| tools | 深 | tool-registry.snippet.md | tool registry / toolset composition |
| execution | 深 | execution-env.snippet.md | multi-backend execution |
| memory | 中 | memory-skills.snippet.md | frozen snapshot / skills |
| learning | 中 | memory-skills.snippet.md | self-improvement loop |
| control | 中 | README.md | three-layer approval |

## 独特贡献

Hermes 把学习循环内置到 runtime 中——从经验中创建技能、技能在使用中迭代优化、主动触发记忆持久化。结合多平台 gateway 和 5 种执行后端，它展示了一个**能跨会话成长、跨平台部署**的长期运行系统的完整形态。

## 关键发现

- Gateway 不只是”接入层”，它定义了 agent runtime 的真实边界：会话隔离、平台适配、Cron 调度都在这里发生。
- 冻结快照模式（系统提示冻结 + 运行时写磁盘）同时解决了前缀缓存热度和跨会话记忆生效两个问题。
- 工具注册表作为单一真实源（schema / handler / check_fn 统一查询），消除了工具信息在 prompt、代码、配置之间的漂移。

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
工具系统：中心化注册表 + Toolset 组合 + 动态可用性检查
记忆系统：FTS5 全文搜索 + 冻快照注入
执行环境：5 后端（local/docker/ssh/modal/daytona）统一抽象
多平台网关：适配器模式 + 会话隔离 + Cron 调度
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

## 文件索引

| 文件 | 内容 |
|------|------|
| `./agent-loop.snippet.md` | 核心循环、迭代预算、压缩触发 |
| `./tool-registry.snippet.md` | 工具注册、dispatch、可用性检查 |
| `./memory-skills.snippet.md` | 记忆持久化、技能系统、学习循环 |
| `./execution-env.snippet.md` | 执行环境抽象、沙箱策略 |
| `./gateway.snippet.md` | 多平台网关、会话管理、Cron |

## 可复用洞察

1. **冻快照模式** - 系统提示冻结保持缓存，运行时写磁盘跨会话生效
2. **迭代预算** - 线程安全计数器，consume/refund 模型，压力警告注入
3. **注册表单一真实源** - 所有 schema/handler/check_fn 从一处查询
4. **Toolset 组合** - includes 递归展平，enable/disable 过滤
5. **子代理隔离** - 工具交集、独立 prompt、跨度限制
6. **威胁扫描** - 记忆写入前检测注入/泄露模式
7. **WAL + Jitter 重试** - SQLite 多进程安全，随机退避破坏 convoy
8. **渐进式信息披露** - 技能元数据列表 → 完整内容 → 支持文件
