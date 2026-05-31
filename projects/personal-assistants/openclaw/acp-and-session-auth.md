# ACP & Session Auth

> **Evidence Status** — grounded. OpenClaw src/acp/ + src/agents/auth-profiles/ 源码分析。

## ACP (Agent Control Plane)

OpenClaw 自有的本地执行权限管理系统（与 Anthropic 的 ACP 无关）。

核心：
- Persistent bindings（持久化权限绑定）
- Session-level execution approval
- Policy enforcement at tool-call time

## Session-Scoped Auth Overrides

层级：Global defaults → Agent defaults → Session overrides

每个 session 可独立选择：
- Provider（anthropic / openai / ...）
- Model（具体模型 ID）
- Auth profile（API key / OAuth token）

## Auth Profiles

- OAuth + API-key 管理
- Round-robin fallback（轮询多个 profile）
- Refresh queue + cooldown logic
- Per-session override capability

## Sandbox 集成

- Main session：Local execution（默认）
- Non-main session：Docker sandbox（可配置）
- 四种后端：Local / Docker / SSH / OpenShell
