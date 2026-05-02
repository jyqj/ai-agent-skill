# Autonomy Levels

> **Evidence Status** — synthesized. 核心概念归纳与跨模块一致性整理。

> **完整版**见 `../paradigms/methodology/autonomy-and-depth.md`。本文保留核心概念供快速查阅。

| 等级 | 名称 | Agent 行为 | 人类角色 | 典型产品 |
|---|---|---|---|---|
| L0 | Answer | 只解释、回答、总结 | 提问者 | Chatbot |
| L1 | Recommend | 给方案和建议 | 决策者 | Copilot |
| L2 | Draft | 生成可编辑草稿 | 编辑者 | Writing/Coding Copilot |
| L3 | Execute with Approval | 提出动作，审批后执行 | 审批者 | Coding Agent、Workflow Agent |
| L4 | Bounded Autonomy | 在规则内自动执行 | 监督者 | Research Agent、低风险企业流程 |
| L5 | Delegated Workflow | 长时自主推进，定期汇报 | 委托者 | 高成熟度 Agent Platform |

## 自主性不是越高越好

正确自主性取决于：

```text
动作风险 × 可逆性 × 用户信任 × 验证能力 × 失败成本
```

例如：搜索资料可以 L4，修改本地代码可以 L3/L4，删除生产数据应该 L1/L2。

## 与执行深度的区别

| 维度 | 问题 | 示例 |
|---|---|---|
| 自主性 | Agent 能不能自己做？ | 是否允许自动提交 PR |
| 执行深度 | Agent 要做到哪一步？ | 是否必须跑测试并修复失败 |
