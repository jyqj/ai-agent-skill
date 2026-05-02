# Feedback Loops

> **Evidence Status** — synthesized. skill crystallization、failure-driven improvement、eval regression 与用户纠错的共同需求。

## 定义

Learning 应被拆成多条可审计反馈回路：

```text
user correction loop
trace mining loop
eval regression loop
skill crystallization loop
policy hardening loop
```

## 五类反馈回路

| 回路 | 输入 | 输出 | 是否自动激活 |
|---|---|---|---|
| User Correction | 用户纠正、偏好、约束 | state / memory update candidate | 谨慎 |
| Trace Mining | 成功/失败 trace | pattern candidate / anti-pattern | 否 |
| Eval Regression | fixture 失败 | policy / prompt / tool contract update | 否 |
| Skill Crystallization | 多次成功路径 | reusable skill / SOP | 需要验证 |
| Policy Hardening | 安全或越权事件 | deny rule / approval gate / guardrail | 可以半自动 |

## 关键边界

- 不是每次成功都值得写进长期 skill。
- 不是每次用户纠正都值得进入长期 memory。
- 失败回路的目标是减少同类错误，而不是盲目增加规则数量。

## 推荐对象

```yaml
feedback_record:
  feedback_id: string
  source: user | eval | incident | trace_mining
  target_layer: prompt | tool | policy | memory | skill | docs
  proposed_change: string
  evidence_refs: []
  activation_state: candidate | validated | activated | reverted
```

## 与仓库演进的关系

本知识库本身也应遵守类似回路：

```text
批评或使用痛点
→ 找到缺层 / 缺样板 / 缺测试
→ 新增文档 / fixture / starter kit
→ 跑自检
→ 继续观察是否真被复用
```
