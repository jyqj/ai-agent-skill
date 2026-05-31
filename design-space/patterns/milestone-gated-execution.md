# Milestone-Gated Execution Pattern

> **Evidence Status** — synthesized. 源自带检查点的多步编码和研究工作流，里程碑粒度和合并策略尚需更多实际系统的验证数据。

长任务如果只有一个大目标，Agent 很容易出现三类问题：计划看起来完整但执行时跑偏；做了很多动作但无法证明阶段完成；工具失败后不知道应该重试、换路还是停止。里程碑门控（Milestone-Gated Execution）的核心思路是：**把任务拆成可验证的阶段，每个阶段必须通过门控检查才能进入下一个**。

## 执行流

```text
Task → Milestone 1 → verify → checkpoint
                                  ↓
       Milestone 2 → verify → checkpoint
                                  ↓
       Milestone 3 → verify → checkpoint
                                  ↓
       Final verification → delivery
```

每个里程碑（Milestone）不只是一个标题，而是一个完整的规格：有输入上下文、允许的工具范围、禁止的动作、退出条件和验证方法。

## Milestone Spec

```yaml
milestone:
  id: understand_codebase
  objective: Locate auth flow and relevant tests
  input_context:
    - user_goal
    - repository_snapshot
  allowed_tools:
    - read_file
    - grep
    - list_dir
  forbidden_actions:
    - edit_file
    - shell_write
  exit_criteria:
    - relevant_files_identified
    - suspected_failure_points_listed
  verification:
    type: evidence_check
    required_evidence:
      - file_paths
      - code_snippets
      - reasoning_summary
  checkpoint: true
```

注意 `forbidden_actions`：在"理解代码库"阶段禁止编辑文件，这种约束看似多余，但正是防止 Agent 跑偏的关键机制。

## Gate Types

里程碑之间通过不同类型的门控（Gate）连接：

- **Entry Gate**：检查是否有足够上下文进入下一里程碑。缺少关键信息时阻止进入，避免在信息不足时盲目执行。
- **Action Gate**：运行时检查工具调用是否在允许范围内。这是最直接的防跑偏机制。
- **Verification Gate**：检查阶段产物是否满足退出条件，验证的是"做对了"而非"做完了"。
- **Risk Gate**：高风险动作（如生产环境操作）需要人工审批才能通过。
- **Merge Gate**：多 Worker 并行时，合并输出前检查冲突。
- **Final Gate**：最终交付前检查证据完整性。

## 适用场景

这个模式在以下场景中价值最大：复杂 bug 修复、多源研究报告、企业流程自动化、代码迁移、长期项目助理。共同点是任务跨度大、中间可能出错、出错后需要可恢复。

## 反模式

- 只有自然语言计划，没有结构化里程碑。
- 只按时间切阶段，不按可验证产物切阶段。
- 每阶段都允许所有工具（失去了门控的意义）。
- 验证失败后直接重跑同一动作（应该换策略或上报）。

## Per-Turn Breadcrumb Gate (Trellis)

> **Evidence**: Trellis — 3 Phase / 13 Step 工作流

传统 milestone gate 在阶段边界做一次性检查。Trellis 的 breadcrumb 模式在每一轮都强化当前阶段的约束：

**3 Phase × 13 Step**：
- Phase 1 Plan (5 steps)：create → brainstorm → research → configure context → activate
- Phase 2 Execute (3 steps)：implement → quality check → rollback
- Phase 3 Finish (5 steps)：verify → debug retrospective → spec update → commit → wrap-up

**Per-Turn 强化**：每轮 AI 交互，Hook 读取 task.json status，注入对应 workflow-state 块。这意味着：
- AI 不会"忘记"当前阶段（即使经过 context compaction）
- 跳步行为被阻止（每轮都有阶段约束）
- 状态恢复是自动的（重启会话后，hook 重新读取 status）

**Spec Curation Gate (Phase 1.3)**：特殊门控 —— 主 agent 必须人工策展 implement.jsonl / check.jsonl 才能进入 Phase 2。这是一个人机协作的关卡，确保 sub-agent 接收到正确的 spec 上下文。

**与传统 Milestone Gate 的互补**：breadcrumb 不替代 milestone gate，而是在 gate 之间的每一步都提供持续的方向约束。两者可以组合使用。
