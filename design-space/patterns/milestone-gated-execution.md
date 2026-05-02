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
- **Verification Gate**：检查阶段产物是否满足退出条件。不是"做完了"，而是"做对了"。
- **Risk Gate**：高风险动作（如生产环境操作）需要人工审批才能通过。
- **Merge Gate**：多 Worker 并行时，合并输出前检查冲突。
- **Final Gate**：最终交付前检查证据完整性。

## 适用场景

这个模式在以下场景中价值最大：复杂 bug 修复、多源研究报告、企业流程自动化、代码迁移、长期项目助理——共同点是任务跨度大、中间可能出错、出错后需要可恢复。

## 反模式

- 只有自然语言计划，没有结构化里程碑。
- 只按时间切阶段，不按可验证产物切阶段。
- 每阶段都允许所有工具（失去了门控的意义）。
- 验证失败后直接重跑同一动作（应该换策略或上报）。
