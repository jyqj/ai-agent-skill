# ExecPolicy Starlark 规则引擎

> **Evidence Status** — grounded. 基于 Codex 参考源码观察整理。

## 概述

ExecPolicy 是 Codex 的确定性命令审批层，在 Guardian LLM 审批之前执行，用 Starlark 语法定义策略规则。

## 规则文件与加载

- `.rules` 文件使用 Starlark 语法，支持前缀匹配（如 `git *` 匹配所有 git 子命令）
- 分层加载：从 config layer stack 按优先级加载，高优先级覆盖低优先级
- 用户可在项目级、全局级分别维护规则文件

## 三级判定

每条规则返回三种判定之一，均附带 `justification` 说明理由：
- **Allow** — 直接放行，不经 Guardian
- **Prompt** — 需要用户/Guardian 确认
- **Forbidden** — 直接拒绝，不可覆盖

## 动态修订（ExecPolicyAmendment）

用户批准某命令后，系统可自动将该前缀写入 `default.rules` 文件。
效果：同类命令后续执行时直接 Allow，实现"越用越顺"的渐进信任。

## 危险命令启发式

当无规则匹配时，fallback 到两个启发式函数：
- `is_known_safe_command()` — 识别只读/无副作用命令（如 `ls`, `cat`）
- `command_might_be_dangerous()` — 标记高危模式（如 `rm -rf`, `chmod 777`）

## Banned Prefix

以下前缀不允许作为 Allow 规则的匹配前缀，防止过度放权：
- `python`, `bash`, `sh`, `git`, `sudo` 等通用解释器/提权命令

## 网络规则持久化

`append_network_rule_and_update` 支持将主机级网络策略（允许/拒绝特定域名）持久化到规则文件中，与命令规则同文件管理。

## 与 Guardian 的关系

确定性规则（ExecPolicy + Hooks）优先于 LLM 审批（Guardian）。只有在 ExecPolicy 返回 Prompt 且无缓存审批时，才触发 Guardian 调用。这减少了不必要的 LLM 开销。
