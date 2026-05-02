# User Teaching

> **Evidence Status** — synthesized. MemoryRecord、Skill Crystallization、user feedback 等机制。

## 1. 教学类型

| 类型 | 例子 | 写入对象 |
|---|---|---|
| Preference | “以后报告先给结论” | MemoryRecord.preference |
| Correction | “这里客户 A 指的是 Acme，不是 Alpha” | TaskCheckpoint + optional MemoryRecord |
| Boundary | “不要自动发外部邮件” | Policy / UserControl |
| Procedure | “这个项目发布前先跑这三个检查” | SkillRecord.procedure |
| Vocabulary | “ARR 在我们这里指 annual recurring revenue” | MemoryRecord.fact |

## 2. 写入规则

```text
一次性纠错 → 只更新当前 task state
稳定偏好 → 请求用户是否记住
组织级规则 → 需要更高权限审批
程序性技能 → 需要成功 trace 和 eval 后才能激活
```

## 3. 教学确认格式

```yaml
proposed_learning:
  type: preference | fact | procedure | boundary
  scope: task | user | project | workspace | organization
  evidence: []
  applies_when: []
  do_not_apply_when: []
  requires_confirmation: true
```
