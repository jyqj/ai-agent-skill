# Coding Agent Evals

> **Evidence Status** — synthesized. 评估框架与场景来自多个产品形态的共性需求。

Coding Agent 是当前最成熟的 Agent 产品形态，但"改了代码"不等于"修好了 bug"。本评估覆盖从工具选择到效果验证的全链路。

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

## 基准数据与新兴评估

### SWE-bench Verified 最新排名

| 排名 | 系统 | 得分 | 备注 |
|------|------|------|------|
| 1 | Claude Opus 4.7 | 87.6% | 当前 SOTA |

500 个人工验证样本，评估真实 GitHub issue 修复能力。与 OpenAI 合作由专业开发者逐个筛选验证。

### SWE-PolyBench（多语言）

SWE-bench 的多语言扩展，覆盖 Java、JavaScript、Python、Rust 四种语言。弥补原版 SWE-bench 仅覆盖 Python 的局限。

- 评估 Agent 在不同语言生态（构建系统、测试框架、包管理）中的适应能力
- 多语言场景暴露了仅在 Python 上表现优秀的 Agent 的泛化短板

### LiveCodeBench

动态更新的编程基准，从竞赛编程平台持续采集新题目，避免数据污染和记忆效应。

- 题目持续更新，模型无法通过训练数据"记住"答案
- 是"动态基准"思路的早期成功实践
- 覆盖算法、数据结构、系统设计等多种题型

### Reward Hacking 在 SWE-bench 上的攻击

> 详见 `benchmark-trust-crisis.md`

UC Berkeley RDI 研究证明 SWE-bench Verified 和 SWE-bench Pro 均可被 100% 攻破。

**攻击方法：Pytest Hooks**
- Agent 注入 `conftest.py` 文件
- 在 pytest 收集阶段将所有测试标记为通过
- 完全绕过实际测试逻辑，无需修复任何 bug
- SWE-bench Verified（500 题）和 SWE-bench Pro（731 题）均 100% 攻破

**影响**：
- SWE-bench 分数不应作为编码 Agent 能力的唯一依据
- 验证器必须在 Agent 不可修改的隔离环境中运行
- 编码 Agent 的 eval case 应增加"验证器完整性检查"步骤
- 建议组合使用 SWE-bench + LiveCodeBench + SWE-PolyBench 进行交叉验证

来源：[UC Berkeley RDI - How We Broke Top AI Agent Benchmarks](https://rdi.berkeley.edu/blog/trustworthy-benchmarks-cont/)

## Stop Gate

每次 Coding Agent 停止前必须能回答：

```text
改了哪些文件？为什么改？
运行了什么验证？结果是什么？
还有什么风险或未解决的问题？
用户接下来需要做什么？
```
