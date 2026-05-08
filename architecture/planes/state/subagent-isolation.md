## 子 Agent 状态隔离

> **Evidence Status** — production-validated. 来自 Claude Code Swarm worker、Codex AgentControl + AgentRegistry、OpenCode Session.create({ parentID }) 的生产实现。

多 Agent 场景下，子 Agent 的状态不得污染主循环。这不是设计偏好，而是正确性要求——如果子 Agent 的中间消息混入主循环的上下文，会导致主循环的计划被子 Agent 的局部观察干扰。

### 项目对照

| 项目 | 隔离机制 | 状态交换协议 |
|------|---------|-------------|
| **Claude Code** | Swarm worker 独立消息历史；主循环通过 `inProgressTasks` / `foregroundedTaskId` 追踪子任务，不共享消息 | 子任务完成后，结果作为 tool result 注入主循环 |
| **Codex** | `AgentControl` 独立控制平面；同一 `AgentControl` 实例共享给所有子 Agent，但每个子 Agent 有独立 `ThreadId` 和消息历史 | `AgentRegistry` 追踪活跃 Agent；`spawn_depth_limit` 防止无限递归；`Weak` 引用避免循环 |
| **OpenCode** | `Session.create({ parentID })` 创建独立子会话；`TaskTool` 递归调用 `SessionPrompt.prompt` | 子会话完成后，assistant 消息拼接为 tool output 返回父会话；`task_id` 支持后续恢复 |

### 隔离不变量

```text
1. 子 Agent 的消息历史不进入主循环的上下文窗口
2. 子 Agent 的状态变更不触发主循环的状态观测器
3. 子 Agent 可继承父的配置（权限、模型、shell snapshot），但不能反向修改
4. 子 Agent 的结果通过明确的 tool result 协议返回，不通过共享内存
5. 子 Agent 的 spawn 有深度和数量限制（Codex: agent_max_threads + spawn_depth_limit）
```

Codex 的 `AgentControl` 设计值得注意：它用 `Weak<ThreadManagerState>` 引用避免 Session → AgentControl → ThreadManagerState 的循环引用，同时在 `reserve_spawn_slot` 中检查当前活跃 Agent 数是否超限。这不是防御性编程——Codex 的 BQ 分析发现过 Agent 递归 spawn 导致 OOM 的生产事故。
