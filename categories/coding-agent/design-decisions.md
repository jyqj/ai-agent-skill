# Coding Agent Design Decisions

> **Evidence Status** — grounded. Claude Code、Codex、OpenCode、Augment 的上下文、工具、控制、执行和编排设计观察。

## 沙箱策略

| 策略 | 适合 | 风险 | 默认建议 |
|---|---|---|---|
| Local workspace | 用户本地 CLI/IDE | 可能影响用户文件 | 只允许 scoped edit，危险命令审批 |
| Container sandbox | 自动化 coding worker | 环境差异 | 适合 CI-like 任务 |
| Remote sandbox | 云端 agent | 权限和数据边界 | 需要 repo clone、secret policy |
| Sidecar execution | 企业/平台 | 集成复杂 | 适合受控工具和审计 |

默认：读操作可本地执行；写操作限制在 repo scope；shell 命令需要 timeout、cwd、env capture 和 risk classifier；push/deploy 默认禁止或强审批。

## 并发策略

```text
只读并行，写入串行。
多 worker 可以并行分析，但合并 diff 必须集中处理。
```

| 场景 | 策略 |
|---|---|
| 多目录搜索 | 并行 |
| 多个测试命令 | 视资源预算并行 |
| 多文件修改 | 计划层串行或分支后合并 |
| 同文件修改 | 严格串行 |
| 子代理审查 | 输出 contract + conflict review |

## 上下文策略

| 问题 | 策略 |
|---|---|
| 大仓库无法全读 | search → symbol → targeted read |
| 工具输出过长 | offload artifact + summary + raw ref |
| 长任务 context rot | checkpoint + compaction + phase summary |
| 关键证据被摘要丢失 | raw ref replay |
| 项目约定很多 | scoped project instructions |

默认 ContextPack 分层：

```text
1. 当前任务目标和约束
2. 项目级指令和约定
3. 相关文件/符号
4. 最近工具观察和测试结果
5. 计划、checkpoint、open questions
6. 压缩历史和 raw refs
```

## 记忆策略

| 信息 | 放哪 | 写入条件 |
|---|---|---|
| 当前 git status / test result | World State / EffectRecord | 不进长期记忆 |
| 项目构建命令 | Project Memory | 执行验证后 |
| 用户偏好，如“少改动” | Long-term/User Memory | 明确、稳定、可撤回 |
| 成功修复流程 | Skill Memory | 多次成功或 eval 通过 |
| 失败样例 | Eval/Trace | 用于回归 |

## 控制策略

默认 policy：

```text
deny > ask > allow
```

| Action | Policy |
|---|---|
| read/search/status/diff | allow |
| edit within repo | allow/check depending scope |
| delete/rename | ask |
| arbitrary shell | ask unless whitelisted |
| install dependencies | ask |
| commit | ask |
| push/deploy | deny or explicit approval |
| access secrets | deny unless scoped and logged |

Hook 建议：

```text
pre_tool_call: risk classification
post_tool_call: standard observation normalization
before_edit: file hash / scope check
after_edit: readback + diff intent check
before_final_answer: stop gate verification
before_memory_write: project/user/skill classification
```

## Operations 策略

Coding Agent 进入生产或团队环境后，至少需要：

```text
[ ] ConfigFingerprint: model / prompt / tool schema / policy / memory policy / eval suite
[ ] TraceEvent: tool calls, edit actions, test results, policy decisions
[ ] Regression suite: representative tasks + failure cases
[ ] Shadow mode: 先建议不执行，比较人类/agent 输出
[ ] Canary: 小范围启用写权限
[ ] Incident response: 误改、泄露、无限循环、成本异常处理
```

## 升级触发器

| 观察 | 升级 |
|---|---|
| 多次误读项目约定 | 引入 Project Memory / Convention Discovery |
| 上下文经常爆 | Compaction + Tool Output Offloading |
| 误改或越权 | Control Policy + approval + scope rules |
| 测试经常无法运行 | Execution Env abstraction + fixture eval |
| 长任务断裂 | Checkpoint + TaskState |
| 多人/多 agent 协作 | OutputContract + SharedWorldModel |
| 上线退化 | Observability + Operations + Eval Runner |

相关：`../../paradigms/tool-paradigms.md`、`../../paradigms/control-paradigms.md`、`../../architecture/planes/operations/overview.md`。
