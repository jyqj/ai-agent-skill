# Agent 退役机制

> **Evidence Status** — theoretical
> 来源：微服务退役实践、技术债管理文献、Skill Governance 中 deprecated/retired 状态的扩展需求；长期运行 Agent 系统的运维经验。

## 1. 什么时候该停止

不是所有 Agent/Skill/Memory 都应该永远存在。识别退役时机是运维成熟度的标志。

### 退役信号

| 信号 | 说明 | 检测方式 |
|---|---|---|
| 持续低效 | 任务完成率长期低于阈值 | 定期 eval |
| 使用率归零 | 长期无人调用 | 调用频率监控 |
| 维护成本超过价值 | 适配成本高于重建成本 | 成本审计 |
| 安全风险 | 依赖的模型/工具有已知漏洞 | 安全扫描 |
| 功能被替代 | 新的 Agent/Skill 完全覆盖其能力 | 能力矩阵对比 |
| 合规失效 | 不再满足新的合规要求 | 合规审查 |
| 环境消失 | 依赖的外部服务/API 已下线 | 依赖健康检查 |

### 决策框架

```text
维护成本 > 价值产出？
├── 是 → 有替代方案？
│        ├── 是 → 启动退役 + 迁移
│        └── 否 → 值得重建？
│                 ├── 是 → 重建后退役旧版
│                 └── 否 → 直接退役
└── 否 → 有安全/合规风险？
         ├── 是 → 修复或退役
         └── 否 → 继续运行
```

## 2. 三种退役：Skill / Agent / Memory

### 2.1 Skill 退役

Skill 退役是最轻量的退役，影响范围最小。

```yaml
skill_retirement:
  trigger: "连续 30 天成功率 < 50% 且无修复计划"
  process:
    - status: active → deprecated
      action: "标记为 deprecated，不再优先召回"
      duration: "14 天观察期"
    - status: deprecated → retired
      action: "从活跃索引中移除，保留在归档索引中"
    - status: retired → archived
      action: "移入冷存储，保留 metadata 用于审计"
  rollback: "如果退役后有任务需要该 skill，可以恢复到 deprecated 状态重新评估"
```

与 Skill Governance 的关系：Governance Schema 中的 `status: retired` 就是退役状态。退役不是删除 -- 保留记录用于：
- 审计追溯
- 防止重复创建类似的失败 skill
- 作为未来改进的参考

### 2.2 Agent 退役

Agent 退役影响范围更大，涉及依赖方迁移。

```yaml
agent_retirement:
  phases:
    - phase: announcement
      duration: "30 天"
      actions:
        - "通知所有依赖方"
        - "发布替代方案或迁移指南"
        - "停止接受新的集成请求"

    - phase: deprecation
      duration: "60 天"
      actions:
        - "响应中附加 deprecation 警告"
        - "减少可用能力（只保留核心功能）"
        - "监控依赖方迁移进度"

    - phase: sunset
      duration: "14 天"
      actions:
        - "只返回错误消息和迁移指引"
        - "不再处理实际请求"

    - phase: shutdown
      actions:
        - "停止服务"
        - "撤销凭证和权限"
        - "归档日志和配置"
        - "从服务发现中移除"
```

### 2.3 Memory 退役

Memory 退役最为复杂，涉及数据生命周期和隐私合规。

```yaml
memory_retirement:
  types:
    - type: episodic_memory
      retirement_trigger: "过期 + 未被召回超过 90 天"
      process: "标记过期 → 从活跃索引移除 → 冷存储 → 定期清理"

    - type: semantic_memory
      retirement_trigger: "关联的 skill/convention 已退役"
      process: "标记关联已断 → 评估独立价值 → 保留或清理"

    - type: user_memory
      retirement_trigger: "用户请求删除 / 隐私合规要求"
      process: "立即从所有索引移除 → 从存储中删除 → 生成删除证明"
      compliance: "GDPR right to erasure / CCPA delete request"

    - type: project_memory
      retirement_trigger: "项目归档或终止"
      process: "冻结写入 → 保持只读 → 按保留策略清理"
```

## 3. 退役流程通用模板

```text
1. 识别 (Identify)
   ├── 触发退役信号
   ├── 评估影响范围
   └── 确认没有更好的替代方案

2. 计划 (Plan)
   ├── 确定退役时间线
   ├── 识别所有依赖方
   ├── 准备迁移方案
   └── 确定数据归档策略

3. 通知 (Announce)
   ├── 通知依赖方
   ├── 发布迁移指南
   └── 设置倒计时

4. 降级 (Deprecate)
   ├── 标记为 deprecated
   ├── 限制新的使用
   ├── 在响应中附加警告
   └── 监控迁移进度

5. 归档 (Archive)
   ├── 备份关键数据
   ├── 导出审计日志
   ├── 保存配置快照
   └── 记录退役原因

6. 关闭 (Shutdown)
   ├── 停止服务
   ├── 撤销权限
   ├── 清理资源
   └── 从注册表移除

7. 验证 (Verify)
   ├── 确认无残留依赖
   ├── 确认数据已归档
   ├── 确认凭证已撤销
   └── 更新文档
```

## 4. 数据归档策略

| 数据类型 | 保留策略 | 存储位置 |
|---|---|---|
| 配置和 prompt | 永久保留（轻量） | 版本控制系统 |
| Eval 结果 | 保留 1 年 | 冷存储 |
| 执行日志 | 保留 90 天 | 日志归档 |
| Skill 定义 | 永久保留（用于审计） | 知识库归档区 |
| 用户数据 | 按合规要求 | 加密冷存储或删除 |
| Memory 内容 | 按类型和合规要求 | 冷存储或删除 |

## 5. 退役后的监控

退役不是结束 -- 需要监控是否有残留影响：

```yaml
post_retirement_monitoring:
  duration: "30 天"
  checks:
    - "是否有请求仍在到达已关闭的端点"
    - "是否有 Agent 仍在引用已退役的 Skill"
    - "是否有用户投诉功能缺失"
    - "归档数据的完整性校验"
  actions:
    on_residual_traffic: "重定向到替代方案或错误页面"
    on_skill_reference: "更新引用方的配置"
    on_user_complaint: "提供迁移帮助"
```

## 6. 与 Skill Governance 的关系

Skill Governance 定义了 Skill 的生命周期状态：

```text
candidate → active → quarantined → deprecated → retired
```

本文档扩展了 `retired` 状态的处理细节：

- Governance 关注"何时进入 retired 状态"
- 本文档关注"进入 retired 状态后的具体操作"
- 本文档还覆盖了 Governance 不涵盖的 Agent 级和 Memory 级退役

## 7. 紧急退役

当发现安全漏洞或严重缺陷时，可能需要跳过常规流程：

```yaml
emergency_retirement:
  trigger: "安全漏洞 / 数据泄露 / 严重合规违规"
  process:
    - "立即停止服务（不等待迁移期）"
    - "撤销所有凭证"
    - "通知依赖方（事后通知）"
    - "进行安全调查"
    - "完成常规退役流程的剩余步骤"
  approval: "需要安全团队 + 运维团队双重确认"
```

## 8. 反模式

| 反模式 | 风险 |
|---|---|
| 不退役 | 僵尸 Agent/Skill 消耗资源、引入安全风险 |
| 直接删除 | 丢失审计信息、破坏依赖方 |
| 不通知 | 依赖方在运行时才发现服务不可用 |
| 不归档 | 无法追溯退役原因、无法复用经验 |
| 退役后不监控 | 残留依赖导致静默失败 |
| 过早退役 | 用户还在使用但被强制迁移 |

## 延伸阅读

- `../learning/skill-governance.md` -- Skill 生命周期状态管理
- `value-drift.md` -- 漂移无法校正时可能触发退役
- `co-evolution.md` -- 版本不兼容可能导致组件退役
- `ecosystem-protocols.md` -- Agent 退出生态的协议层面处理
- `../planes/operations/overview.md` -- 运维流程支撑退役操作
