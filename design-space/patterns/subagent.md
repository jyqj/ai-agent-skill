# Subagent

> **Evidence Status** — grounded. Claude Code 和 Codex 都实现了生产级子代理机制，OpenCode 通过 Task 工具提供了类似能力。三个项目路径不同但核心模式一致。

复杂任务的中间过程——搜索结果、编译错误、调试输出、大文件内容——会不断膨胀主上下文，最终导致上下文腐化（Context Rot）。子代理（Subagent）充当上下文防火墙：把会产生大量中间输出的子任务交给独立的上下文执行，只把最终结果返回主上下文。

## 做法

```
function spawn_subagent(task, return_format):
    sub_context = new_context(
        system_prompt=subagent_prompt,
        task=task
    )

    while not sub_context.done:
        sub_context.step()
        # 所有中间过程留在子上下文中

    # 只返回摘要结果
    return sub_context.summarize(return_format)

# 主 Agent 使用
result = spawn_subagent(
    task="搜索并分析竞品的定价策略",
    return_format="3-5 个关键发现，每个不超过 2 句话"
)
# 主上下文只收到简洁的结果
```

## 什么时候用、什么时候不用

子代理的收益在于主上下文保持清洁、子任务可以深入探索而不怕污染全局、多个子代理还可以并行执行。代价是额外的 LLM 调用带来延迟，以及子代理天然缺少主上下文的完整信息——交接设计（给什么、收什么）直接决定了效果好坏。

适合用子代理的场景：研究/搜索任务、代码实现（隔离调试过程）、大文件处理、独立的验证任务。

**反模式**：不要按技术角色划分子代理（Frontend Agent / Backend Agent / Database Agent）。任务很少按这种方式自然分割。正确的划分依据是上下文隔离需求——哪些子任务会产生大量中间输出，就把它们隔离出去：

- Research Subagent（产生大量搜索结果）
- Implementation Subagent（产生编译错误和调试输出）
- Verification Subagent（产生测试输出）

## 交接设计

给子代理的信息应当包括：明确的任务目标、必要的上下文（不是全部历史）、期望的输出格式。从子代理返回的信息应当包括：任务结果摘要、关键发现、文件路径（如果产生了文件变更）。

## 生产级实现：AgentControl（Codex）

Codex 的实现展示了一个完整的多 Agent 协作架构。核心由两部分组成：

```
AgentControl (控制平面)
+-- manager: Weak<ThreadManagerState>  # 避免循环引用
+-- state: Arc<AgentRegistry>          # 作用域隔离

AgentRegistry (注册表)
+-- agents: HashMap<ThreadId, AgentMetadata>
+-- nickname_pool: HashSet<String>     # 唯一昵称
+-- spawn_depth_limit: usize           # 深度限制
```

几个关键设计决策：每个 root session 拥有一个 AgentControl 实例，所有子 agent 共享同一个注册表，实现作用域隔离（Scoped Isolation）；AgentControl 对 ThreadManager 使用 Weak 引用，避免 Session -> AgentControl -> ThreadManager 的循环引用导致内存泄漏；spawn 深度有硬限制，防止无限递归；子 agent 继承父 agent 的 shell snapshot 和执行策略（Exec Policy）。

协作工具包括 `spawn_agent`（创建）、`wait_agent`（等待完成）、`send_input`（发送消息）、`list_agents`（列出活跃 agent）和 `close_agent`（关闭）。Agent 状态按 Idle -> Running -> Waiting -> Completed/Failed 流转。

## 生产级实现：Task 工具子代理（OpenCode）

OpenCode 走了一条更简洁的路。它定义了三种 Agent 模式（Mode）：`primary`（用户直接启动）、`subagent`（只能通过 Task 工具调用）和 `all`（系统代理，如 compaction）。7 个内置代理分布在这三种模式中。

Task 工具的实现核心是递归调用 `SessionPrompt.prompt`——子代理就是一个新的会话，通过 `parentID` 字段关联回父会话。`task_id` 参数支持恢复已有任务，子代理继承父代理的权限设置，每个子代理有独立的消息历史。

### Codex 与 OpenCode 对比

两者最大的差异在于架构重量级。Codex 用独立的 ThreadManager + AgentRegistry + 状态机实现了完整的进程级管理，有明确的深度限制和生命周期控制；OpenCode 通过递归 SessionPrompt + parentID 关联实现了同样的逻辑隔离，但更轻量，深度限制依赖 maxSteps 而非显式控制。选择哪种取决于你需要多精细的控制粒度——如果只是隔离上下文，OpenCode 的方式够用；如果需要管理大量并发 Worker 并精确控制资源，Codex 的方式更稳健。

## 参考实现

- `../../projects/coding-agents/claude-code/orchestration-layer.md`
- `../../projects/coding-agents/codex/agent-control.md`
