# Coding Agent Action Model

> **Evidence Status** — synthesized. `architecture/planes/tools/overview.md`、`architecture/planes/execution/overview.md`、`architecture/planes/effects/overview.md` 与 coding agent 项目工具系统。

## 动作分类

| 类别 | 动作 | 典型工具 | 默认风险 |
|---|---|---|---|
| Read | list files、read file、grep、symbol search、git log/status | filesystem/git/search | safe |
| Analyze | parse AST、inspect dependencies、summarize error | code parser/model | safe/check |
| Write | edit、create、delete、rename、format | edit/apply_patch | check/approval |
| Execute | shell、test、lint、typecheck、build | shell/test runner | check/approval |
| Git | diff、stage、commit、branch、push | git tools | check/high |
| Verify | run test、read diff、CI status、snapshot compare | shell/git/CI | safe/check |

## 工具风险策略

| 操作 | 默认策略 | 说明 |
|---|---|---|
| read/search/status/diff | allow | 只读且低风险 |
| edit/create | allow or ask by scope | 工作区本地修改，需 diff 可审查 |
| delete/rename | ask | 易破坏，需意图清楚 |
| shell test/lint/build | allow with timeout | 可配置白名单 |
| arbitrary shell | ask | 命令可能危险 |
| git commit | ask | 影响历史，但可回滚 |
| git push/deploy/prod config | deny/explicit approval | 高风险或外部效果 |
| secret/env access | deny unless scoped | 防泄露 |

## Action Contract

每个写动作都要显式化：

```yaml
action:
  action_id: string
  tool_id: edit_file
  target:
    path: src/example.ts
    range: [120, 150]
  preconditions:
    - file_hash_matches_last_read
    - task_scope_allows_src_changes
  intended_effect: fix null handling in parseUser
  postconditions:
    - file contains new guard
    - no unrelated hunks
  verification_method:
    - read_back_file_range
    - git_diff_review
    - npm test -- parseUser
  rollback:
    - reverse patch
```

## Happy Path 工具链

```text
read/search → form hypothesis → read target files → edit → read back → git diff → test/lint/typecheck → fix failures → final diff summary
```

## Failure Recovery

| 失败 | 立即动作 | 不要做 |
|---|---|---|
| patch apply failed | 重新读取文件，计算新 patch | 盲目重试旧 patch |
| test failed | 分类：目标失败/无关失败/环境失败 | 直接宣称完成 |
| command timeout | 缩小测试范围或询问用户 | 无限延长 |
| permission denied | 解释需要的权限或改用安全路径 | 绕过策略 |
| branch dirty | 展示冲突和当前 diff | 覆盖用户改动 |
| dependency missing | 检查安装策略/项目说明 | 自动全局安装 |

## Effect Ledger for Code Changes

```yaml
effect_record:
  effect_id: string
  target_system: filesystem | git | ci
  world_object_refs:
    - repo://path/to/project
    - file://src/example.ts#L120-L150
  intended_effect: "fix parseUser null handling"
  tool_calls:
    - edit_file:...
  actual_observation:
    diff_ref: git-diff://...
    test_result_ref: test://...
  verification_status: verified | failed | partial | unverified
  remaining_risks:
    - integration tests not available
```

## 并发策略

| 并发类型 | 默认 |
|---|---|
| 多文件只读搜索 | 可并行 |
| 多个测试读取/分析 | 可并行，但资源预算控制 |
| 同一文件写入 | 串行 |
| 多 worker 写不同文件 | 需要 plan-level merge 和 conflict policy |
| shell 命令 | 受 resource/cancellation 控制 |

## 相关通用模块

- Tool Spec：`../../architecture/planes/tools/overview.md`
- Execution Host：`../../architecture/planes/execution/overview.md`
- Control Policy：`../../architecture/planes/control/overview.md`
- Effect Verification：`../../architecture/planes/effects/overview.md`
- Concurrency：`../../architecture/planes/concurrency/overview.md`
