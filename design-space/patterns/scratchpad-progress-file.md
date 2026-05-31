# Scratchpad & Progress File

> **Evidence Status** — synthesized. 多个长任务 Agent 系统的通用实践，模式简单但效果显著。

## 问题

Agent 的中间推理、尝试路径、失败原因如果只留在上下文窗口里，一旦上下文被压缩或会话中断，这些信息就丢失了。Agent 会重复已经失败的路径，或者忘记已经取得的进展。

## 解法

把中间状态写到文件里，分两种用途：

**Scratchpad** 是临时草稿——思路、假设、实验记录。可以随时清理，不作为事实依据。它的价值在于帮助 Agent "想清楚"，而不是"记住"。

**Progress File** 是长任务的持久状态——已完成的步骤、收集到的证据、阻塞点、下一步计划。它在会话中断后依然有效，是 Agent 恢复执行的依据。

## Progress File 模板

```markdown
# Progress
## Goal
## Current Phase
## Completed
## Evidence
## Open Issues
## Next Step
## Do Not Repeat
```

其中 `Do Not Repeat` 是最容易被忽略但最有价值的部分，它记录已经证明无效的路径，防止 Agent 反复踩同一个坑。
