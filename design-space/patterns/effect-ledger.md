# Effect Ledger

> **Evidence Status** — synthesized. 源自 coding、workflow、browser、ops 等多类 Agent 场景中"动作成功 ≠ 效果达成"的反复教训，目前为草案。

一个常见的 Agent 失败模式是：工具返回 success，Agent 就认为任务完成了。但"动作已发出"和"世界已改变"之间往往有巨大的鸿沟：

- API 返回 200 OK，但数据库里没有任何变化；
- 点击了提交按钮，但表单校验失败，页面并未提交；
- 邮件发送接口返回成功，但邮件被退信或进了垃圾箱；
- 部署流水线启动了，但健康检查一直不通过。

这些情况的共同点是：工具层面的成功信号不足以证明业务层面的效果达成。

## 解法

效果账本（Effect Ledger）要求为每个写操作记录五项信息：

| 字段 | 含义 |
|------|------|
| `intended_effect` | 这个动作预期改变什么 |
| `world_object_refs` | 受影响的外部对象（数据库行、页面元素、文件路径等） |
| `verification_method` | 如何验证效果是否达成（重新查询、截图比对、健康检查等） |
| `verification_status` | 当前验证状态：pending / confirmed / failed / skipped |
| `rollback_or_compensation` | 如果效果未达成，回滚或补偿方案是什么 |

这不是事后审计用的日志，而是运行时的决策依据。Agent 在判断"是否继续下一步"时，应该检查 Effect Ledger 中前一步的 `verification_status`，而不是仅凭工具返回值。

## 三重角色

Effect Ledger 同时承担三个功能：

**流程门控**——当 `verification_status` 为 pending 或 failed 时，阻止后续依赖该效果的操作继续执行。

**事故定位**——出了问题后，可以快速找到"哪一步的 intended_effect 没有实际达成"，而不是在一堆 success 日志里猜。

**审计追溯**——对于合规要求高的场景，Effect Ledger 提供了完整的"意图-动作-验证"链条。
