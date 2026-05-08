# Tool Orchestrator

> **Evidence Status** — grounded. 基于 Codex 参考源码观察整理；代码片段仅作架构映射。

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。
// codex-rs/core/src/tools/orchestrator.rs
// ToolOrchestrator: 工具执行的核心编排器

pub async fn run(&mut self, tool, req, tool_ctx, turn_ctx, approval_policy) {
    // === 阶段 1: 审批检查 ===
    let requirement = tool.exec_approval_requirement(req)
        .unwrap_or_else(|| default_exec_approval_requirement(approval_policy, &policy));

    match requirement {
        ExecApprovalRequirement::Skip => {
            // 自动通过，记录到 telemetry
        }
        ExecApprovalRequirement::Forbidden { reason } => {
            return Err(ToolError::Rejected(reason));
        }
        ExecApprovalRequirement::NeedsApproval { reason } => {
            // 请求用户/Guardian 审批
            let decision = tool.start_approval_async(req, approval_ctx).await;
            match decision {
                ReviewDecision::Denied | ReviewDecision::Abort => {
                    return Err(ToolError::Rejected("rejected"));
                }
                ReviewDecision::Approved => { already_approved = true; }
                ReviewDecision::NetworkPolicyAmendment { amendment } => {
                    // 处理网络策略修改
                }
            }
        }
    }

    // === 阶段 2: 首次执行（带沙箱）===
    let initial_sandbox = self.sandbox.select_initial(
        &turn_ctx.file_system_sandbox_policy,
        turn_ctx.network_sandbox_policy,
        tool.sandbox_preference(),
    );

    let initial_attempt = SandboxAttempt {
        sandbox: initial_sandbox,
        policy: &turn_ctx.sandbox_policy,
        file_system_policy: &turn_ctx.file_system_sandbox_policy,
        network_policy: turn_ctx.network_sandbox_policy,
        // ...
    };

    let (first_result, deferred_network) = Self::run_attempt(
        tool, req, tool_ctx, &initial_attempt
    ).await;

    match first_result {
        Ok(out) => return Ok(out),

        // === 阶段 3: 沙箱拒绝 → 提权重试 ===
        Err(ToolError::Codex(SandboxErr::Denied { output, .. })) => {
            if !tool.escalate_on_failure() {
                return Err(...);  // 不允许重试
            }

            // 请求用户确认后无沙箱重试
            let retry_reason = "command failed; retry without sandbox?";
            let decision = tool.start_approval_async(req, approval_ctx).await;

            if decision == ReviewDecision::Approved {
                let escalated_attempt = SandboxAttempt {
                    sandbox: SandboxType::None,  // 无沙箱
                    // ...
                };
                return Self::run_attempt(tool, req, tool_ctx, &escalated_attempt).await;
            }
        }
        Err(err) => return Err(err),
    }
}

// 关键设计点:
// 1. 审批是第一步，不是最后一步
// 2. 沙箱拒绝有升级路径（用户确认后可提权）
// 3. 网络策略和文件系统策略分离处理
// 4. Guardian 审批和用户审批共用同一决策路径
