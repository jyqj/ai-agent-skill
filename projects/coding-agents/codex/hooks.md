# Hooks 系统

> **Evidence Status** — grounded. 基于 Codex 参考源码观察整理。

## 概述

Hooks 是 Codex 的确定性拦截层，在 LLM 审批之前执行，可对工具调用和会话事件做即时判定。

## Hook 类型

| Hook | 触发时机 | 典型用途 |
|---|---|---|
| SessionStart | 会话启动 | 初始化检查、环境校验 |
| UserPromptSubmit | 用户提交输入 | 输入过滤、预处理 |
| PreToolUse | 工具调用前 | 权限拦截、参数校验 |
| PostToolUse | 工具调用后 | 结果审计、日志 |
| PermissionRequest | 权限请求触发 | 直接 Allow/Deny，跳过 Guardian |
| PreCompact | 上下文压缩前 | 保留关键信息 |
| PostCompact | 上下文压缩后 | 压缩后校验 |

## 关键能力

- **直接裁定**：PermissionRequest Hook 可直接返回 Allow/Deny，完全跳过 Guardian LLM 调用
- **上下文注入**：Hook 可通过 `additional_contexts` 向对话中注入额外信息
- **输入阻断**：`PendingInputHookDisposition::Blocked` 可完全阻止用户输入进入处理流程

## 执行优先级

```
Hooks (确定性) → ExecPolicy (确定性) → Guardian (LLM)
```

确定性规则优先于 LLM 审批。只有当 Hooks 和 ExecPolicy 都未做出明确判定时，才回退到 Guardian LLM。这一分层设计减少了不必要的 LLM 调用，同时保证关键策略的确定性执行。
