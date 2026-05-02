# Context as State

> **Evidence Status** — synthesized. 长任务 Agent 中反复出现“上下文被压缩或截断后任务进度丢失”的失败模式；State / Context 边界见 `../../architecture/module-boundaries.md`。

## 定义

把当前模型上下文当作任务状态库使用。计划、已完成步骤、用户约束、失败原因和外部对象状态只存在 prompt 或聊天历史里，没有 TaskCheckpoint、WorldStateSnapshot 或 TraceEvent。

## 典型表现

- 上下文压缩后忘记已做过的步骤；
- 中断恢复时从头开始；
- 多 Agent 合并时不知道哪个步骤已验证；
- 最终回答无法引用真实 checkpoint。

## 风险

Context 是可丢弃、可压缩、可重建的注意力窗口。把它当 state，会让长任务不可恢复、不可审计、不可评估。

## 修复

- 任务进度写入 `TaskCheckpoint`；
- 外部对象状态写入 `WorldStateSnapshot`；
- 写动作写入 `EffectRecord`；
- 失败写入 `FailureRecord`；
- ContextPack 只引用这些对象，不成为唯一事实来源。

## 评审问题

```text
如果当前 context 被清空，Agent 能否从 checkpoint 恢复？
最终回答中的“已完成”是否能回到 EffectRecord？
哪些信息只是当前注意力，哪些是持久状态？
```
