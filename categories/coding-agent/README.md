# Coding Agent Architecture

> **Evidence Status** — grounded. 基于 Claude Code、Codex、OpenCode、Augment 四个参考项目，结合通用 architecture planes 归纳。作为品类架构样板。

## Core Job

Coding Agent 的工作不是“回答代码问题”，而是在真实代码库中完成可验证的软件工程任务：

```text
定位问题 → 理解代码库 → 设计修改 → 执行 edit → 运行验证 → 修复失败 → 交付 diff + 证据 + 风险
```

## 用户模型

| 用户 | 心智模型 | 信任建立方式 | 默认交互 |
|---|---|---|---|
| Solo developer | 下属开发者 / pair programmer | 小 diff、可解释、测试通过 | 允许本地修改，提交前确认 |
| Team developer | PR 助手 / reviewer assistant | 遵守项目约定、低噪音 diff | 关键选择同步，输出 reviewable patch |
| Maintainer / reviewer | 分析员 + 变更建议者 | 准确引用代码和风险 | 默认不直接 push |
| Platform team | 自动化 worker | trace、policy、回归稳定 | 高度受控、可审计 |

信任不是二元开关。Coding Agent 应通过成功的小任务、稳定的验证、可回滚的 diff 和明确的风险说明逐步升级权限。

## 任务模型

详见 `task-model.md`。核心分类：

| 任务 | 默认深度 | 完成定义 |
|---|---|---|
| Bug fix | D4-D5 | diff + 相关测试通过 + bug 复现/修复证据 |
| Feature | D4-D5 | diff + 新/改测试 + 用户验收点 |
| Refactor | D4 | 行为等价证明 + 测试通过 + diff 可审查 |
| Code review | D2-D4 | 问题清单 + 证据引用 + 可选 patch |
| Migration | D5 | checkpoint + 分阶段 diff + 回滚/恢复策略 |
| Test generation | D4 | 测试覆盖目标 + 测试可运行 + 失败原因解释 |

## 表示模型

详见 `representation.md`。Coding Agent 的关键表示对象包括：

```text
RepoSnapshot、FileRef、SymbolRef、DependencyGraph、SearchHit、BuildConfig、TestResult、LintResult、GitState、DiffArtifact、CIStatus
```

设计原则：

- 代码文件和命令输出是 representation，不是现实本身。
- repo / branch / diff / test result 都有 freshness；写前需要刷新。
- 外部 issue、PR comment、日志、网页默认是 untrusted data lane。
- AGENTS.md / README / build config 等项目约定只有在信任边界内才可作为 instruction/config lane。

## 行动模型

详见 `action-model.md`。

| 动作 | 示例 | 默认风险 |
|---|---|---|
| Read | list、read、search、git status、test dry-run | safe |
| Write | edit、create、delete、rename、format、commit | check/approval |
| Verify | test、lint、typecheck、build、diff review、CI readback | safe/check |

所有写动作都应有：precondition、intended effect、postcondition、verification method、rollback/compensation。

## 闭环模型

详见 `closed-loop.md`。

```text
Observe task + repo
  → Represent codebase / git / tests / constraints
  → Decide plan + risk + verification strategy
  → Act via read/edit/shell/git tools
  → Verify diff + tests + world state
  → Update task state / memory candidates / final answer
```

Stop gate：

```text
[ ] diff 与任务目标一致
[ ] 相关测试 / lint / typecheck 已运行，或明确说明为何无法运行
[ ] git status / diff 已回读
[ ] 未完成风险和用户需知事项已列出
[ ] 高风险动作未越过审批边界
```

## 品类特有设计决策

详见 `design-decisions.md`。

| 决策 | 默认建议 |
|---|---|
| 沙箱 | shell/code_run 默认在可控工作区；危险命令 require approval |
| 并发 | 只读可并行，写操作串行；共享文件写入需要锁或计划合并 |
| 上下文 | 先索引/搜索，再按需读取；大输出 offload；关键证据 raw ref 可回放 |
| 记忆 | 项目约定和成功命令可进入 Project/Skill Memory；当前 git/test 状态不进长期记忆 |
| 控制 | deny > ask > allow；delete、push、deploy、secret 操作必须显式控制 |
| 运维 | 记录 tool trace、config fingerprint、评估失败样例 |

## 模块配置配方

| 模块 | Coding Agent 特化配置 | 通用参考 |
|---|---|---|
| Representation | RepoSnapshot、FileRef、SymbolRef、TestResult、GitState | `../../architecture/planes/representation/overview.md` |
| Context | file/symbol/test/error 的按需装配与 compaction | `../../architecture/planes/context/overview.md` |
| Tools | read/edit/search/shell/test/git，含 risk + postcondition | `../../architecture/planes/tools/overview.md` |
| Execution | shell sandbox、workspace isolation、timeout、env capture | `../../architecture/planes/execution/overview.md` |
| Control | permission tree、hooks、approval、verification gate | `../../architecture/planes/control/overview.md` |
| State | task plan、checkpoint、progress、open questions | `../../architecture/planes/state/overview.md` |
| World State | branch、working tree、CI、dependency 状态刷新 | `../../architecture/planes/world-state/overview.md` |
| Effects | diff、test result、build status 的 effect ledger | `../../architecture/planes/effects/overview.md` |
| Observability | trace、tool call、失败原因、成本、eval replay | `../../architecture/planes/observability/overview.md` |

## 参考实现映射

详见 `implementation-map.md`。

| 参考项目 | 重点学习 |
|---|---|
| Claude Code | context 压缩、工具并发控制、hook、子代理、UI/state |
| Codex | sandbox、guardian policy、orchestrator、agent control |
| OpenCode | tool schema、permission、doom loop、agent registry |
| Augment | worker orchestration、checkpoint、remote/local/sidecar/MCP host |

## 阅读路径

```text
README.md
  → task-model.md
  → representation.md
  → action-model.md
  → closed-loop.md
  → design-decisions.md
  → eval-cases.md
  → implementation-map.md
```

设计新 Coding Agent 时，再回到：

```text
../../paradigms/reasoning-paradigms.md
../../paradigms/tool-paradigms.md
../../paradigms/control-paradigms.md
../../index/design-checklist.md
```

- 主观性任务的验证扩展：`../../concepts/beyond-verification.md`
