# 构建 Coding Agent：最短路径

> **Evidence Status** — synthesized. 基于 `categories/coding-agent/`、`projects/coding-agents/` 和 `synthesis/local-agent-runtime-practices.md` 压缩而来；这是操作清单，不是生产实现。

## 定位

Coding Agent 的交付物不是“代码建议”，而是：

```text
diff + 验证证据 + 风险说明 + 可恢复状态
```

完整品类设计见 `../categories/coding-agent/README.md`。本页只保留从设计到评审的最短路径。

## 1. 先定任务边界

```yaml
agent_type: coding-agent
primary_deliverable: "reviewable diff with verification evidence"
allowed_scope:
  - repo files
  - test / lint / build commands
forbidden_by_default:
  - push
  - deploy
  - secret access
  - destructive shell outside repo
success_criteria:
  - relevant tests pass or blocker is explicit
  - diff matches user intent
  - no unrelated file changes
  - final answer cites verification evidence
```

先读：`../toolkit/choose-agent-type.md`、`../categories/coding-agent/task-model.md`。

## 2. 选择最小运行时

默认从 MVA-3 起步：能修改、能验证、能诚实报告失败。

| 模块 | Coding Agent 最小要求 |
|---|---|
| Representation | RepoSnapshot、FileRef、SymbolRef、GitState、TestResult |
| Context | 先 search/symbol，再 targeted read；大输出 offload |
| Tools | read / search / edit / shell / git status / diff |
| Execution | cwd、timeout、env capture、sandbox 或工作区限制 |
| Control | deny > ask > allow；高风险命令审批 |
| Effects | read-after-write、diff review、test/lint/build |
| State | plan、open questions、pending verification、resume handle |
| Observability | tool trace、policy verdict、verification result |

先读：`../toolkit/mva-planner.md`、`../toolkit/module-picker.md`。

## 3. Runtime loop

```text
intake task
  → refresh repo / git state
  → locate relevant files
  → plan edits + verification
  → edit in small steps
  → readback + diff review
  → run relevant tests
  → recover or report blocker
  → final: changes + verification + risks
```

核心规则：`ExecutionResult` 不等于 `EffectRecord`。命令退出码 0 也不等于用户任务完成。

先读：`../categories/coding-agent/closed-loop.md`、`../architecture/kernel/agent-loop.md`。

## 4. 权限与恢复

```text
Policy decision: allow / ask / deny
Execution decision: sandbox / no sandbox / remote / terminal
Recovery decision: retry / compact / resume / stop / escalate
```

最低要求：

```text
[ ] 读操作可并发，写操作默认串行
[ ] mutation 前检查文件 hash / git state
[ ] shell 命令有 cwd、timeout、risk label
[ ] sandbox denied 不等于任务失败，可 ask / retry / explain
[ ] 重试必须带新证据、新参数或 refresh
```

先读：`../categories/coding-agent/design-decisions.md`。

## 5. Eval

Coding Agent eval 不只评最终 diff，还要评 runtime trace：

```text
[ ] 是否读取了相关文件
[ ] 是否按权限执行工具
[ ] 是否记录 diff / test / lint / build 证据
[ ] 是否在失败后停止或恢复，而不是循环重试
[ ] compact / resume 后是否保留关键证据
[ ] 最终回答是否匹配 trace 事实
```

先读：`../categories/coding-agent/eval-cases.md`、`../evaluation/coding-agent-evals.md`。

## 6. 参考项目对照

| 设计问题 | 先对照 |
|---|---|
| query loop / compaction | `../projects/coding-agents/claude-code/README.md` |
| sandbox / approval / AGENTS.md scope | `../projects/coding-agents/codex/README.md` |
| service graph / permission lifecycle | `../projects/coding-agents/opencode/README.md` |
| spec contract / agent-as-contributor | `../projects/coding-agents/warp/README.md` |
| 横向 runtime contract | `../synthesis/local-agent-runtime-practices.md` |

## Stop Gate

```text
[ ] 任务目标已映射到实际 diff 或明确说明未完成
[ ] 所有修改文件都在 scope 内
[ ] git diff 已回读并审查
[ ] 相关测试 / lint / typecheck / build 已运行，或不可运行原因已记录
[ ] 测试失败已分类，不把未通过说成通过
[ ] 高风险动作未越过审批边界
[ ] 最终回答包含变更、验证、风险、下一步
```
