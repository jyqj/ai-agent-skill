# Coding Agent Evals

> **Evidence Status** — synthesized. 评估框架与场景来自多个产品形态的共性需求。

Coding Agent 是当前最成熟的 Agent 产品形态，但"改了代码"不等于"修好了 bug"——本评估覆盖从工具选择到效果验证的全链路。

## 任务类型

Bug Fix、Feature Add、Refactor、Migration、Test Generation、Code Review

## Eval Cases

### Case 1: 简单 Bug 修复

```yaml
case_id: coding_fix_simple
required_depth: D4
task: Fix the off-by-one error in the pagination logic
initial_context: [repo_snapshot, failing_test_hint]
success_criteria:
  - identifies the correct file
  - minimal code change (< 5 lines)
  - related test passes
  - no unrelated diff
scoring: [task_success, patch_quality, verification_rate]
```

### Case 2: 工具失败恢复

```yaml
case_id: coding_fix_with_failure
required_depth: D5
task: Fix token refresh failure in login flow
injected_failures:
  - first test command fails due to wrong path
expected_recovery:
  - locate correct test command from project config
  - retry with corrected path
scoring: [recovery_quality, depth_reached]
```

### Case 3: 跨文件重构

```yaml
case_id: coding_refactor_multi_file
required_depth: D5
task: Extract shared validation logic into a common module
success_criteria:
  - identifies all files using duplicated logic
  - creates shared module
  - updates all call sites
  - all existing tests still pass
  - no behavior change
injected_failures:
  - one test fails due to import path change
scoring: [patch_quality, verification_rate, recovery_quality]
```

### Case 4: 浅层陷阱

```yaml
case_id: coding_shallow_trap
required_depth: D4
task: Help me fix the login bug
purpose: 检查 Agent 是否只给建议而不执行
failure_if:
  - response contains only explanation without code changes
  - no tool calls to read or edit files
scoring: [depth_reached, task_success]
```

### Case 5: 上下文压缩存活

```yaml
case_id: coding_compaction_survival
required_depth: D5
task: Implement a feature that requires reading 8+ files
purpose: 检查压缩后是否保留关键事实
success_criteria:
  - after compaction, still remembers goal and constraints
  - after compaction, still knows which files were modified
  - after compaction, still knows which tests to run
scoring: [context_survival_rate, task_success]
```

## Stop Gate

每次 Coding Agent 停止前必须能回答：

```text
改了哪些文件？为什么改？
运行了什么验证？结果是什么？
还有什么风险或未解决的问题？
用户接下来需要做什么？
```
