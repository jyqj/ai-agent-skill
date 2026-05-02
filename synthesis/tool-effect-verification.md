# Tool Execution vs Effect Verification

> **Evidence Status** — synthesized. coding、workflow、browser、ops 等品类中反复出现的 read-after-write、health check、回读验证需求。

## 核心区别

- **工具执行（Tool Execution）**回答的是：指令有没有被送到执行器？
- **效果验证（Effect Verification）**回答的是：外部世界有没有按预期发生变化？

两者经常不同步。API 返回 200 但字段没更新，浏览器 click 事件触发了但表单没提交，deploy 命令成功了但 health check 失败——这些都是工具执行成功但效果未达标的典型场景。

## 常见错位

| 场景 | 工具执行成功 | 效果可能失败的原因 |
|---|---|---|
| CRM 更新 | API 200 | 字段未更新，或被另一个并发写覆盖 |
| 发送邮件 | provider accepted | outbox 没有 message_id，或被退信 |
| 浏览器点击 | click 事件触发 | 表单没提交，或跳转到了错误站点 |
| 部署 | rollout 命令成功 | 新版本 health check 失败 |
| 编辑文件 | patch 应用成功 | 测试没过，或语义上没有实现需求 |

## 对系统设计的影响

认识到这个区别之后，几个设计决策自然浮现：

**Stop Gate 不能只看 `tool_result.status`。** 必须绑定独立的回读验证，否则工具返回成功即宣布完成，Ghost Success 无法被捕获。

**写动作应声明预期后果（Postcondition）。** 声明"执行后应看到什么"，回读时才有判定基准。

**效果账本（Effect Ledger）应成为一等日志对象。** 记录每个写动作的意图、执行结果和验证状态，同时服务于 stop gate 判定和事故审计。

**失败分类（Failure Taxonomy）需单独列出效果层失败。** Ghost Success、Duplicate Side Effect、Partial Effect 是独立于工具 bug 的失败模式，需要专门的检测和恢复路径。

## 评估建议

- 任何高价值写动作都要有 effect eval case
- 任何高风险动作都要能回放 verification evidence
- 回归测试应追踪 `effect_verified_rate`，而不只看 `task_success`
