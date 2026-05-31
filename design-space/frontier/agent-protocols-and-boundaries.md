# Agent Protocols and Boundaries

> **Evidence Status** — theoretical. 基于 MCP 官方文档、A2A 协议文档、hosted agent runtime 说明以及多框架的协议抽象。属于 frontier 方向。

## 核心判断

当前 Agent 生态里经常被混在一起的，其实是四种不同边界：

```text
Repo-to-Agent        代码仓库如何告诉 agent 工作约束
Agent-to-Tool        agent 如何访问工具和外部能力
Agent-to-Agent       agent 如何把任务交给另一个 agent
Hosted Agent Runtime 平台如何提供 tracing、memory、built-in tools 和 handoff
```

把这四层拆开，比纠结某个单独协议更重要。

## 四类边界

| 边界 | 默认对象 | 主要问题 |
|---|---|---|
| Repo-to-Agent | `AGENTS.md`、项目指令、脚本 | 本仓库内的工作方式、检查命令、风格与守卫 |
| Agent-to-Tool | MCP、tool schema、local adapters | 能力暴露、权限、参数、数据与指令分离 |
| Agent-to-Agent | handoff contract、task/result schema、A2A 风格协议 | 任务分发、结果归并、冲突处理 |
| Hosted Runtime | built-in tools、session、trace、guardrail | 平台提供哪些默认能力与可观察性 |

## 设计启发

### 1. MCP 不是多 Agent 编排本身

MCP 更像“agent 访问工具和资源的能力边界”；它解决的是：

- 工具能力如何声明；
- 调用需要什么参数；
- 返回的是数据还是可执行约束；
- 用户 consent、capability segmentation、最小权限如何落地。

### 2. A2A 风格协议也不替代内部 runtime

Agent-to-agent 协议适合描述：

- 任务交给谁；
- 返回什么结果；
- 能否流式；
- 中断、取消、状态同步如何表示。

但它不自动回答：

- 内部 state 怎么存；
- effect 怎么验证；
- 安全边界怎么执行；
- 成本怎么控。

### 3. Repo instructions 是另一种控制面

`AGENTS.md` 一类文件解决的是仓库内部的工作约束：

```text
进入一个仓库后，哪些检查必须跑？
哪些目录不要乱改？
哪些脚本替代口头说明？
```

它属于 repo-to-agent 边界，应和系统 prompt、用户请求、tool output 分开管理。

## 选择矩阵

| 需求 | 优先选择 |
|---|---|
| 把本地工具统一暴露给 agent | Agent-to-Tool capability layer |
| 把一个子任务交给另一个 agent | Agent-to-Agent contract |
| 让 repo 自描述其工作方式 | Repo-to-Agent instructions |
| 需要 tracing / session / hosted built-in tools | Hosted runtime integration |

## 对本知识库的影响

- `tools/` 和 `security/` 不应只讨论函数调用，也要覆盖 capability boundary。
- `orchestration/` 讨论的是任务协议和共享状态，而不是单纯“能否连上工具”。
- `AGENTS.md` 让 repo 维护策略成为一等文档，而不是散落在聊天里。
- `starter-kit/` 应把协议边界显式留出可替换接口。

## 仍未收敛的问题

- agent-to-agent 结果 schema 该如何同时支持证据、冲突和成本回传。
- 一个 runtime 内的 handoff 与跨平台 A2A 互通应该共享多少对象模型。
- capability discovery 与安全 allowlist 如何在大型企业环境里统一。
