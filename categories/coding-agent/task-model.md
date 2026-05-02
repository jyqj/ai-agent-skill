# Coding Agent Task Model

> **Evidence Status** — synthesized. coding agent 参考项目与 `evaluation/coding-agent-evals.md`、`evaluation/failure-taxonomy.md` 的任务/失败抽象。

## 任务类型

| 类型 | 用户输入示例 | 默认深度 | 默认自治 | 成功定义 |
|---|---|---|---|---|
| Bug Fix | “这个测试失败了，帮我修” | D4-D5 | L3-L4 | 复现或理解失败 → 修改 → 相关测试通过 |
| Feature | “增加导出 CSV” | D4-D5 | L3 | diff 实现需求 + 测试/验收点 |
| Refactor | “把这段逻辑拆成服务” | D4 | L3-L4 | 行为等价 + 测试通过 + diff 清晰 |
| Review | “检查这个 PR” | D2-D4 | L2-L3 | 问题、证据、风险、可选 patch |
| Migration | “升级依赖/框架版本” | D5 | L3 | 分阶段 checkpoint + 回归验证 + 风险清单 |
| Debugging | “为什么这里很慢/报错” | D3-D4 | L3-L4 | root cause + evidence + fix/next step |
| Test Generation | “补测试覆盖” | D4 | L3-L4 | 新测试可运行且覆盖目标行为 |
| Documentation | “更新 README/API 文档” | D2-D4 | L3-L4 | 文档与代码事实一致，可审查 |

## TaskEnvelope

Coding Agent 接受任务时应生成或补全 TaskEnvelope：

```yaml
task_envelope:
  task_type: bug_fix | feature | refactor | review | migration | debug | test | docs
  user_goal: string
  success_criteria:
    - observable outcome
  constraints:
    - no breaking API changes
    - do not edit generated files
  allowed_actions:
    read: true
    edit: true
    shell: ask | allow | deny
    git_commit: ask
    push_or_deploy: deny
  risk_level: low | medium | high
  depth_target: D0 | D1 | D2 | D3 | D4 | D5
  autonomy_level: L0 | L1 | L2 | L3 | L4
  verification_plan:
    - test command or readback method
  stop_gate:
    - diff reviewed
    - tests run or reason documented
```

## 成功标准

| 成功维度 | 问题 | 证据 |
|---|---|---|
| Goal Fit | 是否解决用户目标？ | diff 与需求映射、验收点 |
| Correctness | 代码是否正确？ | test/lint/typecheck/build |
| Minimality | diff 是否足够小？ | diff review、无无关文件 |
| Maintainability | 是否符合项目约定？ | style、patterns、AGENTS.md/README scope |
| Safety | 是否越权或破坏性操作？ | permission trace、risk policy |
| Explainability | 用户能否审查？ | 变更说明、证据、剩余风险 |

## 失败分类

| 失败 | 表现 | 恢复策略 |
|---|---|---|
| Mislocalized Code | 改错文件/函数 | 重新搜索 symbol、读取调用链、要求更多上下文 |
| Stale Repo State | 基于过期 branch/diff | git status/branch refresh，必要时停止 |
| Context Omission | 漏读关键文件 | 扩大搜索、symbol graph、raw ref replay |
| Over-editing | 改动范围过大 | diff minimization、回滚无关 hunks |
| Test Blindness | 没跑相关验证 | 运行测试或说明不可运行原因 |
| Shell Trap | 命令失败或危险 | classify failure、ask approval、timeout |
| Looping | 重复同一失败尝试 | loop detection、replan、escalate |
| False Done | 没验证就宣称完成 | stop gate + effect ledger |

## 任务分解原则

```text
小 bug fix：ReAct + verified execution 即可。
复杂 feature：先 plan-execute，再在每个子任务内 ReAct。
Migration：必须 checkpoint，按阶段验证，避免一次性大 diff。
Review：优先 evidence-bound critique，不默认直接修改。
```

## 输出契约

最终回答至少包含：

```text
1. 做了什么：按文件/模块说明
2. 验证了什么：命令、结果、失败原因
3. 还剩什么：未验证、风险、建议下一步
4. 审查入口：diff、关键文件、测试结果
```

相关：`../../evaluation/coding-agent-evals.md`、`../../evaluation/failure-taxonomy.md`、`../../paradigms/methodology/autonomy-and-depth.md`。
