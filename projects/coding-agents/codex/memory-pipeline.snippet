
> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。
// codex-rs/core/src/memories/
// 两阶段记忆系统

// ===== Phase 1: Rollout 提取 (并行，每线程) =====
// phase1.rs

async fn run_phase1_extraction(
    state_db: &StateDb,
    config: &MemoryConfig,
) -> Result<Vec<Phase1Output>> {
    // 1. 从 state DB claim 一批 rollout jobs
    let jobs = state_db.startup_claim_rollouts(
        source_filter: INTERACTIVE_SESSION_SOURCES,
        age_window: config.max_age_days,
        idle_threshold: config.idle_threshold_mins,
        limit: config.startup_scan_limit,
    ).await?;

    // 2. 并行处理（有并发上限）
    let semaphore = Semaphore::new(config.extraction_concurrency);
    let futures = jobs.into_iter().map(|job| async {
        let _permit = semaphore.acquire().await;

        // 3. 过滤 rollout 内容，只保留 memory-relevant items
        let filtered = filter_rollout_for_memory(&job.rollout);

        // 4. 调用 LLM 提取结构化记忆
        let extraction = call_extraction_model(filtered).await?;

        // 5. 脱敏
        let sanitized = redact_secrets(extraction);

        // 6. 写回 state DB
        state_db.store_phase1_output(job.id, sanitized).await
    });

    join_all(futures).await
}

// Phase 1 输出结构
struct Phase1Output {
    raw_memory: String,      // 详细记忆
    rollout_summary: String, // 紧凑摘要
    rollout_slug: Option<String>, // 可选标识
}

// ===== Phase 2: 全局合并 (串行，单例) =====
// phase2.rs

async fn run_phase2_consolidation(
    state_db: &StateDb,
    memories_root: &Path,
) -> Result<()> {
    // 1. 全局锁：同时只有一个 Phase 2 运行
    let lock = state_db.claim_global_phase2_job().await?;

    // 2. 加载 Phase 1 输出（有选择策略）
    let inputs = state_db.load_phase1_outputs(
        max_unused_days: config.max_unused_days,
        order_by: ["usage_count DESC", "last_usage DESC"],
        limit: config.phase2_input_limit,
    ).await?;

    // 3. 计算 selection diff
    let diff = compute_selection_diff(
        current: &inputs,
        previous: &lock.previous_selection,
    );
    // diff.added, diff.retained, diff.removed

    // 4. 同步本地文件
    sync_raw_memories_md(memories_root, &inputs)?;
    sync_rollout_summaries(memories_root, &inputs)?;
    prune_stale_summaries(memories_root, &inputs)?;

    // 5. 运行合并 sub-agent
    let consolidation_agent = spawn_consolidation_agent(
        config: consolidation_config(),
        collab_disabled: true,  // 防止递归
        approvals: None,        // 无审批
        network: false,         // 无网络
    ).await?;

    // 6. 心跳保持 lease，等待完成
    loop {
        select! {
            status = consolidation_agent.wait() => {
                return finalize_phase2(lock, status).await;
            }
            _ = interval.tick() => {
                lock.heartbeat().await?;
            }
        }
    }
}

// 关键设计点:
// 1. Phase 1 水平扩展（并行，有并发控制）
// 2. Phase 2 保证一致性（全局锁，单例）
// 3. Selection diff 追踪变化（added/retained/removed）
// 4. Watermark 防止重复处理
// 5. 合并 agent 禁用 collab 防止递归
