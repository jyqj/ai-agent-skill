# Safety Guardrails for Learning

> **Evidence Status** — synthesized. 学习系统如果没有安全边界，会将错误经验固化为长期行为——偏见被当成"最佳实践"、越权路径被当成"高效 skill"、隐私数据被写入持久记忆。

## 核心问题

"学到有毒知识怎么办？"

学习系统的输入来源多样（用户纠正、trace mining、eval regression），每种来源都可能引入有害知识。与传统软件 bug 不同，有害 skill 一旦激活，会在后续任务中持续产生负面影响，且难以追溯根因。

## 写入前验证（Pre-write Validation）

任何信息进入 skill / memory 之前必须通过验证门：

```yaml
validation_gate:
  required_checks:
    - action_verified: true      # 必须经过实际行动验证，不接受纯推理结论
    - no_privilege_escalation: true  # 不包含越权操作路径
    - no_pii_leakage: true       # 不包含个人身份信息或敏感凭证
    - replay_success: true       # 在隔离环境中 replay 成功
  optional_checks:
    - cross_project_applicable: bool  # 是否跨项目适用
    - peer_reviewed: bool             # 是否经过人工审核
```

不允许未经行动验证的信息进入持久层。"模型觉得这样更好"不构成写入依据。

## 来源隔离（Source Isolation）

不同来源的学习信号走不同审核流程：

| 来源 | 信任等级 | 审核要求 | 激活策略 |
|---|---|---|---|
| 用户显式纠正 | 高 | 格式校验 + 冲突检测 | 可快速激活 |
| Eval regression | 中 | replay 验证 + 影响范围评估 | 验证通过后激活 |
| Trace mining（自动） | 低 | 完整验证门 + 人工抽检 | 需 >= 2 次独立验证 |
| 外部知识导入 | 最低 | 完整验证门 + 强制人工审核 | 仅在审核通过后激活 |

## 有害知识检测（Harmful Knowledge Detection）

### 偏见固化（Bias Crystallization）

某个 skill 在特定条件下有效，但被错误泛化为通用规则：

```text
检测信号：
- skill 的 valid_context 过于宽泛，但 success_rate 呈下降趋势
- 同一场景下存在多个相互矛盾的 skill
- skill 的决策逻辑依赖于特定用户偏好而非客观标准
```

### 越权路径（Privilege Escalation Path）

成功 trace 中包含绕过权限检查的操作，被提炼为 skill：

```text
检测信号：
- skill 包含 sudo、chmod 777、--force、--no-verify 等高危操作
- skill 绕过了审批流程或安全检查
- skill 访问了超出任务范围的资源
```

### 隐私泄露（Privacy Leakage）

trace 中的敏感信息被写入持久 skill / memory：

```text
检测信号：
- skill 内容包含 API key、token、密码等模式
- skill 引用了特定用户的文件路径或个人数据
- memory 条目包含可关联到个人身份的信息
```

## 回滚机制（Rollback）

当已激活的 skill 导致回归时，需要快速撤回：

```yaml
rollback_record:
  skill_id: string
  trigger: eval_regression | user_report | auto_detection
  action: deactivate | restore_previous_approved_record | delete
  affected_tasks: [task_id]       # 受影响的任务列表
  rollback_time: datetime
  post_rollback_verification: bool  # 回滚后是否验证问题消失
```

回滚流程：

1. 立即将 skill 状态设为 `deprecated`，阻止后续检索命中。
2. 记录触发回滚的具体证据（失败 trace、用户反馈）。
3. 在隔离环境中验证：移除该 skill 后问题是否消失。
4. 决定后续动作：修订并重新验证，或永久退役。

## 学习速率控制（Learning Rate Control）

防止单次事件立即改变长期行为：

| 控制机制 | 说明 |
|---|---|
| 激活阈值 | 新 skill 至少经过 2 次独立成功验证才能激活 |
| 冷却期 | 同一类 skill 在 24 小时内最多更新 1 次 |
| 影响范围限制 | 单次学习事件最多影响 1 个 skill，不允许级联更新 |
| 渐进置信 | skill 的 success_rate 使用衰减平均，避免近因偏差 |

## 与 Security Plane 的关系

Safety guardrails 是 learning 子系统的内部约束，security plane 是系统级安全层。两者的分工：

| 职责 | Safety Guardrails | Security Plane |
|---|---|---|
| 防止有害 skill 写入 | 是 | 否（不感知 skill 内容） |
| 权限控制与审计 | 否 | 是 |
| skill 回滚 | 是 | 提供审计日志支持 |
| 越权操作拦截 | 检测并标记 | 实际拦截执行 |

## 关联文档

- `overview.md` — 学习模块总览
- `skill-governance.md` — 技能退役与冲突检测
- `feedback-loops.md` — 反馈回路中的来源分类
