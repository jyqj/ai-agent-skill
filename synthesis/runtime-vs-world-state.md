# Runtime State vs World State

> **Evidence Status** — synthesized. coding、workflow、ops、browser 等品类的项目都同时存在"任务进度"和"外部对象状态"两类状态，且混淆时频繁引发生产问题。

## 为什么经常混淆

很多 Agent 系统只有一个 `state` 对象，任务做到哪一步和外部世界长什么样全部混在一起。这会导致两个经典错误：

1. 任务状态显示"已完成"，但外部世界并没有达标——Ghost Success。
2. 外部世界已经变化（别人改了代码、ticket 被关闭），但 Agent 恢复执行时仍按旧计划继续。

分开建模不是为了架构美感，而是因为它们的**更新来源和刷新策略完全不同**。

## 两类状态的差别

| 维度 | 任务状态（Task State） | 世界状态（World State） |
|---|---|---|
| 关注点 | 任务推进到哪里 | 外部对象当前是什么样 |
| 更新来源 | Agent 自身的计划、步骤、决策、审批 | 回读、传感器、API、DOM、日志 |
| 新鲜度 | 相对稳定，Agent 自己控制 | 可能被外部随时改变 |
| 失败后作用 | 恢复执行到断点 | 验证写动作的前提是否仍然成立 |
| 典型字段 | `current_milestone`, `failed_attempts`, `decision_log` | `observed_at`, `ttl`, `consistency_model` |

## 各品类的具体差异

| 品类 | Task State 示例 | World State 示例 | 典型混淆场景 |
|---|---|---|---|
| Coding Agent | 读到哪里、改了什么、测了什么 | repo、branch、CI、test result 的当前实际状态 | Agent 以为自己在 main 分支，实际已被切走 |
| Workflow Agent | 流程执行到第几步 | CRM、ticket、审批、日历的当前值 | ticket 已被他人关闭，Agent 仍推进后续步骤 |
| Browser Agent | 已导航、已点击、已填写 | 页面 URL、DOM、截图、后端提交状态 | Agent 记录"已点击提交"，页面实际弹出了错误提示 |
| Ops Agent | 已定位、已缓解、已回滚 | 告警是否 resolved、实例是否 healthy、版本是否已切换 | Agent 标记"已回滚"，但旧版本实例未通过 health check |

## 设计建议

- Task State 与 World State 用不同的 schema 和存储，不要放在同一个字典里。
- Checkpoint 恢复时，先装回 Task State（我做到哪了），再刷新 World State（外面现在什么样）。
- 停止条件（Stop Gate）同时绑定两者：任务完成 **并且** 世界达标。

> "能恢复任务"不等于"能恢复对世界的正确理解"。成熟 Agent 必须把两者分开建模。
