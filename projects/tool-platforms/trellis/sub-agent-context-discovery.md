# Sub-Agent Context Discovery

> **Evidence Status** — grounded. Trellis Class-2 platform 实现。

## 问题

Class-2 平台（Codex 等）没有 SessionStart hook，无法在会话开始时注入任务上下文。Sub-agent 启动后不知道当前任务是什么。

## Pull-Based 解决方案

在 sub-agent 定义的 developer_instructions 前缀添加自发现步骤：

```
## Required: Load Trellis Context First
1. Check dispatch prompt first line for `Active task: <path>`
2. Run: python3 task.py current --source
3. Read <task-path>/prd.md
4. Read <task-path>/implement.jsonl
5. For each JSONL entry's "file" field, read that spec file
```

## 三种 Context 注入路径对比

| 路径 | 平台 | 机制 | 延迟 |
|------|------|------|------|
| Hook push | Claude Code, Cursor | SessionStart 注入 | 零 |
| Per-turn push | Codex (with hook), Gemini | UserPromptSubmit 注入 | 零 |
| Pull-based | Codex (no hook), OpenCode | Agent 自发现 | 1-3 tool calls |

## 优势与风险

优势：不依赖平台 hook 能力，所有平台都能用
风险：额外 tool call 消耗 token，自发现可能失败
