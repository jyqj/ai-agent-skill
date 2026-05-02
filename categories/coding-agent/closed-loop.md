# Coding Agent Closed Loop

> **Evidence Status** — synthesized. `architecture/lifecycle.md`、`architecture/kernel/agent-loop.md`、coding agent 参考项目中的工具循环、状态更新、验证和恢复。

## ORDA-VU for Coding Agent

```text
Observe
  用户任务、repo 路径、issue/PR、当前 git 状态、错误日志
Represent
  TaskEnvelope、RepoSnapshot、FileRef、SymbolRef、TestResult、constraints
Decide
  task type、plan、risk、target files、verification plan、approval points
Act
  read/search/edit/shell/git/test/subagent
Verify
  read-after-write、git diff、test/lint/typecheck/build、CI readback
Update
  TaskState、EffectRecord、ContextPack、memory candidates、final response
```

## Happy Path

```text
1. Intake
   - 解析用户目标、约束、风险、期望交付物
2. Repo refresh
   - git status / branch / root / project signals
3. Localization
   - search / symbol / dependency / test mapping
4. Plan
   - 定义变更策略、验证策略、审批点
5. Edit
   - 小步修改，写后读取关键片段
6. Verify
   - diff review + 相关测试 + lint/typecheck/build
7. Recover if needed
   - 分类失败，刷新表示，修复或升级
8. Deliver
   - 变更说明、验证结果、剩余风险、下一步
```

## Failure Loops

### Patch Failure Loop

```text
patch failed
  → refresh FileRef
  → compare expected context
  → generate narrower patch
  → retry once
  → if still failed, escalate with exact conflict
```

### Test Failure Loop

```text
test failed
  → classify failure:
      target regression | unrelated existing failure | environment failure | flaky | unknown
  → if target regression: inspect failure + edit
  → if unrelated: document evidence, avoid masking
  → if environment: explain blocker and suggested command
  → stop after budget or no new evidence
```

### Context Failure Loop

```text
uncertain / conflicting evidence
  → expand search or raw ref replay
  → identify unknowns
  → ask only if ambiguity blocks high-impact action
```

### Verification Failure Loop

```text
verification missing or impossible
  → try narrower verification
  → use equivalent evidence if available
  → report partial verification explicitly
  → do not claim done as fully verified
```

## Stop Gate

Coding Agent 只有满足 stop gate，才能进入最终交付：

```text
[ ] 任务目标已映射到实际 diff 或明确说明未完成
[ ] 所有修改文件都在任务 scope 内
[ ] git diff 已回读并审查
[ ] 相关测试 / lint / typecheck / build 已运行，或不可运行原因已记录
[ ] 测试失败已分类，不把未通过说成通过
[ ] 高风险动作未越过审批边界
[ ] 最终回答包含变更、验证、风险、下一步
```

## Verification Strategy

| 验证 | 适合 | 证据 |
|---|---|---|
| Unit test | bug fix、small feature | command + exit code + relevant output |
| Integration test | cross-module behavior | command + environment notes |
| Typecheck | TS/Python typed code | command + output |
| Lint/format | style and static rules | command + output |
| Build | compile/package | command + output |
| Manual diff review | all code changes | diff hunks + intent mapping |
| CI readback | PR/remote changes | status + timestamp |
| Static reasoning | tests unavailable | limited, must label as unverified/partial |

## Final Response Contract

```text
Summary
- concise statement of what changed

Changes
- file/path: what and why

Verification
- command: result
- unavailable verification: reason

Risks / Follow-ups
- remaining risks
- suggested next steps
```

## 与范式层的关系

- 外层：ORDA-VU。
- 定位和修复：ReAct。
- 大任务：Plan-and-Execute。
- 失败诊断：Reflection bounded by test/diff evidence。
- 高风险动作：Control + Approval + Verification。

相关：`../../paradigms/reasoning-paradigms.md`、`../../paradigms/control-paradigms.md`、`../../architecture/lifecycle.md`。
