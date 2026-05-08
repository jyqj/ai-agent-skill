# Agent Control

> **Evidence Status** — grounded. 基于 Codex 参考源码观察整理；代码片段仅作架构映射。

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。
// codex-rs/core/src/agent/control.rs
// AgentControl: 多 Agent 协作的控制平面

/// 每个 root session 创建一个 AgentControl，所有子 agent 共享同一实例
pub(crate) struct AgentControl {
    /// Weak 引用避免循环: ThreadManagerState → Session → AgentControl → ThreadManagerState
    manager: Weak<ThreadManagerState>,
    /// 注册表作用域限于当前 root thread 树
    state: Arc<AgentRegistry>,
}

impl AgentControl {
    /// Spawn 新 agent 并提交初始 prompt
    pub async fn spawn_agent(
        &self,
        config: Config,
        initial_operation: Op,
        session_source: Option<SessionSource>,
    ) -> CodexResult<ThreadId> {
        let reservation = self.state.reserve_spawn_slot(config.agent_max_threads)?;

        // 继承父 agent 的 shell snapshot 和 exec policy
        let inherited_shell = self.inherited_shell_snapshot_for_source(&state, source).await;
        let inherited_policy = self.inherited_exec_policy_for_source(&state, source).await;

        // 分配唯一昵称
        let (source, metadata) = self.prepare_thread_spawn(
            &mut reservation,
            &config,
            parent_thread_id,
            depth,
            agent_path,
            agent_role,
            /*preferred_nickname*/ None,
        )?;

        // 创建新 thread，传入同一个 AgentControl
        let new_thread = state.create_thread_with_agent_control(
            config,
            source,
            self.clone(),  // 共享 AgentControl
        ).await?;

        // 提交初始操作
        new_thread.codex.submit(initial_operation).await?;

        Ok(new_thread.thread_id)
    }
}

// AgentRegistry: 追踪活跃 agent
pub(crate) struct AgentRegistry {
    agents: RwLock<HashMap<ThreadId, AgentMetadata>>,
    nickname_pool: RwLock<HashSet<String>>,
    spawn_depth_limit: usize,
}

impl AgentRegistry {
    /// 检查 spawn 深度限制
    pub fn reserve_spawn_slot(&self, max_threads: usize) -> Result<Reservation> {
        let current = self.agents.read().len();
        if current >= max_threads {
            return Err(CodexErr::AgentLimitReached(max_threads));
        }
        // 返回 reservation token
    }
}

// 关键设计点:
// 1. 同一个 AgentControl 共享给所有子 agent（作用域隔离）
// 2. Weak 引用避免内存泄漏
// 3. 昵称从池中分配，保证唯一
// 4. spawn 有深度限制，防止无限递归
// 5. 继承父 agent 的 shell 和 policy 配置

// ===== Multi-Agent v2 消息模型 =====
//
// v1 工具集: spawn_agent / wait_agent / send_input / list_agents / close_agent
// v2 新增:   send_message / followup_task / resume_agent
//
// MessageDeliveryMode:
//   QueueOnly    — 消息入队但不唤醒目标 agent
//   TriggerTurn  — 消息入队并立即唤醒目标 agent 处理
//
// SpawnAgentForkMode（控制子 agent 继承的上下文）:
//   FullHistory      — 继承完整对话历史
//   LastNTurns(n)    — 仅继承最近 n 轮
//
// `keep_forked_rollout_item()`:
//   fork 时过滤工具调用和推理过程，只保留 system/developer/user 消息和 final answer。
//   目的：减少子 agent 的上下文噪声，避免继承无关的中间状态。
//
// followup_task:
//   向已完成（Completed）的 agent 追加新任务并重新激活。
//   避免为同一上下文重复 spawn，复用已有状态。
