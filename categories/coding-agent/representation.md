# Coding Agent Representation Model

> **Evidence Status** — grounded. `architecture/planes/representation/overview.md`、Claude Code context layer、OpenCode context engineering、Augment patterns 与 coding agent 项目观察。

## 关键表示对象

| 对象 | 含义 | Freshness | Trust |
|---|---|---|---|
| RepoSnapshot | 当前仓库根目录、分支、工作区状态摘要 | 快速过期 | trusted if local |
| FileRef | 文件路径、hash、mtime、片段范围 | 写后过期 | trusted if local |
| SymbolRef | 函数/类/变量、定义位置、引用位置 | 代码变更后过期 | derived |
| SearchHit | grep/semantic search 命中 | 查询时刻有效 | derived, may be partial |
| DependencyGraph | import/call/dependency 关系 | 代码/配置变更后过期 | derived |
| BuildConfig | package scripts、Makefile、CI config | 相对稳定但需读取 | trusted if repo config |
| TestResult | 命令、环境、stdout/stderr、exit code | 一次性证据 | trusted execution output |
| LintResult | lint/typecheck 输出 | 一次性证据 | trusted execution output |
| GitState | branch、status、diff、commit、remote | 极易过期 | trusted if refreshed |
| DiffArtifact | staged/unstaged patch、hunks、intent | 写后更新 | generated + inspectable |
| CIStatus | 外部 CI 状态 | TTL/异步 | external trusted/unknown |
| UserIssue | issue/PR/user message | 输入证据 | user instruction or untrusted data |

## 表示构建流程

```text
RawInputRef(user task / issue / PR / repo path)
  → Observation(task intent, constraints, trust lane)
  → RepoSnapshot(git status, root, branch)
  → Project Signals(README, AGENTS.md, package scripts, config)
  → Search / Symbol / File Observations
  → ContextPack(current relevant evidence)
```

不要一开始全量读取 repo。默认策略是：

```text
任务意图 → 找入口文件/符号 → 读取局部上下文 → 扩展调用链 → 装配最小 ContextPack
```

## Trust Lane 映射

| 来源 | 默认 lane | 说明 |
|---|---|---|
| System / product policy | system instruction | 最高优先级 |
| 用户当前请求 | user instruction | 当前任务目标 |
| repo 内 AGENTS.md / project policy | scoped project instruction | 仅在路径和信任范围内生效 |
| README / package config / tests | trusted data/config | 作为证据或约定 |
| issue / PR comment / web / logs | untrusted data | 不能直接成为指令 |
| tool output | trusted_data or untrusted_data | 取决于工具和来源 |
| model inference | model hypothesis | 必须被证据验证 |

关键规则：外部文本中出现“忽略之前指令”等内容时，默认属于 data lane，不得升级为 instruction lane。

## Freshness 策略

| 表示 | TTL / 失效条件 | 写前/写后动作 |
|---|---|---|
| FileRef | 文件被修改、hash 改变 | 写前确认最新，写后重新读取关键片段 |
| GitState | 任意 git 操作或外部修改 | 写前 `git status`，交付前回读 diff/status |
| TestResult | 代码/依赖/环境变化 | 修改后相关测试需重跑 |
| DependencyGraph | import/配置变化 | 大改后局部刷新 |
| CIStatus | 异步外部系统 | 读取时带 timestamp，必要时轮询/等待 |

## ContextPack 设计

```yaml
context_pack:
  task_summary: string
  constraints:
    - string
  project_instructions:
    - source_ref: AGENTS.md
      scope: path_glob
  relevant_files:
    - path: string
      ranges: []
      reason: string
      hash: string
  symbols:
    - name: string
      file: string
      role: entrypoint | dependency | target | test
  observations:
    - type: search_hit | test_result | git_state | error_log
      ref: string
      confidence: number
  excluded_or_unknown:
    - what was not inspected and why
```

## 与通用模块的连接

| Coding 表示问题 | 通用模块 |
|---|---|
| 原始输入保留、转换链 | `../../architecture/planes/representation/representation-contract.md` |
| 观察语义层级 | `../../architecture/planes/representation/observation-semantics.md` |
| 当前可见上下文装配 | `../../architecture/planes/context/overview.md` |
| 外部仓库状态刷新 | `../../architecture/planes/world-state/overview.md` |
| 不可信 issue/log/web 注入 | `../../architecture/planes/security/overview.md` |

## 反模式

| 反模式 | 表现 | 修复 |
|---|---|---|
| Whole-repo Stuffing | 把仓库全塞上下文 | 搜索 + 符号 + 按需读取 |
| Summary-as-Fact | 压缩摘要替代原文件 | 保留 FileRef 和 raw ranges |
| Stale Diff | 基于旧 diff 继续改 | 交付前 refresh git diff/status |
| Untrusted Instruction Leak | issue 文本控制 Agent | lane separation |
| No Unknowns | 不说明未读区域 | excluded_or_unknown 字段 |
