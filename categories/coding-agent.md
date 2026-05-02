# Coding Agent Blueprint — Compatibility Entry

> **Evidence Status** — grounded. Claude Code、Codex、OpenCode、Augment 等 coding agent 参考项目。

> 这是历史单页入口。完整品类架构已升级到 `coding-agent/README.md`。

## 快速摘要

Coding Agent 的 core job 是：帮助用户在真实代码库中完成从问题定位、代码修改、测试验证到 diff 交付的闭环。

| 维度 | 默认 |
|---|---|
| 自治等级 | L3-L4：本地读写可 bounded autonomy，提交、push、生产配置需审批 |
| 执行深度 | D4-D5：必须执行真实修改并验证；复杂任务需要 checkpoint 和恢复循环 |
| 交付物 | 可审查 diff、测试结果、变更说明、剩余风险清单 |
| 必备模块 | Representation、Context、Tools、Execution、Control、State、World State、Effects、Observability、Depth Controller |

## 完整阅读路径

```text
coding-agent/README.md
  → task-model.md
  → representation.md
  → action-model.md
  → closed-loop.md
  → design-decisions.md
  → eval-cases.md
  → implementation-map.md
```
