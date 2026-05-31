# Breadcrumb State Machine

> **Evidence Status** — grounded. Trellis workflow.md 源码分析。

## 核心机制

每轮 AI 交互，Hook 读取 task.json 的 status 字段，从 workflow.md 中提取对应的 `[workflow-state:STATUS]` tag 块内容，注入到 user prompt。

## 状态转移

```
[no_task] ──create──> [planning] ──start──> [in_progress] ──archive──> [completed]
                                                    │
                                          (codex inline opt-in)
                                                    ↓
                                         [in_progress-inline]
```

6 个状态：no_task / planning / planning-inline / in_progress / in_progress-inline / completed

## 注入路径

| 路径 | 平台 | 触发 |
|------|------|------|
| SessionStart hook | Claude Code, Cursor | 会话开始 |
| UserPromptSubmit hook | Codex, Gemini, Copilot | 每轮 |
| Plugin entry | OpenCode | 插件加载 |

## 每个状态的 AI 行为指导

| 状态 | AI 被告知做什么 |
|------|--------------|
| no_task | A) 直接回答 B) 创建任务 C) 跳过 Trellis inline 改 |
| planning | 加载 brainstorm skill，策展 JSONL，准备 start |
| in_progress | dispatch implement → check → update-spec → commit |
| in_progress-inline | 直接编码（无 sub-agent dispatch） |
| completed | 目前死代码（archive 移动了目录） |

## Task Resolution Contract

Hook 从以下来源按优先级解析活跃任务：
1. TRELLIS_CONTEXT_ID 环境变量
2. 平台原生会话标识
3. .trellis/.runtime/sessions/<dev>/<session-key>.txt

## 对知识库的贡献

- 补充了 `patterns/hook-system.md`：per-turn 注入超越传统 session-start
- 补充了 `patterns/milestone-gated-execution.md`：breadcrumb 在 gate 之间提供持续约束
- 新范式：状态机驱动的工作流控制（vs 传统的 prompt-based）
