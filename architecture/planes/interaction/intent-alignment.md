# Intent Alignment and Cognitive Load

> **Evidence Status** — synthesized. 从 Interaction Plane（overview.md）的交互原则扩展，结合长任务中意图漂移和用户认知过载的常见失败模式。

## 1. 问题

`overview.md` 定义了交互事件类型和原则，但缺少以下关键维度：

- **意图漂移检测**：Agent 在长任务中如何持续确认自己理解的意图与用户实际意图一致？
- **认知负载管理**：当 Agent 需要用户输入时，如何平衡信息完整性和用户认知负载？
- **多利益方冲突**：当 Agent 同时服务多个利益方时，如何处理目标冲突？

## 2. 意图漂移检测

### 2.1 什么是意图漂移

```text
意图漂移 = 用户实际意图随时间变化，但 Agent 仍按初始理解执行

常见场景：
- 用户在任务进行中改变了需求但没有明确告知
- 外部环境变化导致原始目标不再合理
- 用户看到中间结果后调整了期望
- 多轮对话中，隐含前提逐渐偏移
```

### 2.2 漂移检测信号

| 信号 | 检测方式 | 置信度 |
|---|---|---|
| 用户纠正频率上升 | correction 事件在最近 N 轮的频率 | high |
| 用户反馈与预期不一致 | 用户对"正确"结果表示不满 | high |
| 目标表述变化 | 用户重新描述目标时用词显著不同 | medium |
| 上下文隐含前提变化 | 用户提到了初始任务未包含的约束 | medium |
| 长时间无确认 | 长任务中用户长时间未回应进度报告 | low |

### 2.3 对齐机制

| 机制 | 时机 | 形式 |
|---|---|---|
| 任务启动确认 | 接到任务后 | "我理解你需要 X，通过 Y 方式实现，对吗？" |
| 里程碑对齐 | 每完成一个主要阶段 | "已完成 A，接下来计划做 B，是否调整？" |
| 漂移检测主动对齐 | 检测到漂移信号时 | "注意到 X 信号，你的目标是否有变化？" |
| 结果交付确认 | 任务完成时 | "完成了 X，这是否符合你的期望？" |
| 最小问题原则 | 任何时候 | 每次只问一个最关键的对齐问题 |

### 2.4 对齐频率控制

```text
对齐频率 = f(任务风险, 任务时长, 漂移信号强度)

低风险短任务：启动 + 交付 = 2 次
中风险中任务：启动 + 每个里程碑 + 交付
高风险长任务：启动 + 每个里程碑 + 漂移检测 + 交付
```

**过度对齐**也是问题——如果每一步都问用户"对不对"，用户会感到厌烦和不信任 Agent 的能力。

## 3. 认知负载管理

### 3.1 认知负载类型

| 类型 | 定义 | 示例 |
|---|---|---|
| 信息过载 | 一次给用户太多信息 | 一次展示 50 个文件的 diff |
| 选择过载 | 给用户太多选项 | "请从以下 8 个方案中选择" |
| 上下文切换 | 要求用户在不同上下文间跳转 | "先看代码，再看日志，再看配置" |
| 技术壁垒 | 使用用户不理解的技术概念 | 对非开发者说"需要 rebase" |

### 3.2 负载控制策略

| 策略 | 适用场景 | 实现 |
|---|---|---|
| 渐进式披露 | 信息过载 | 默认摘要，用户可展开详情 |
| 推荐 + 回退 | 选择过载 | 给出推荐方案 + 理由，用户可选择其他 |
| 上下文打包 | 上下文切换 | 把相关信息组织在一起呈现 |
| 术语适配 | 技术壁垒 | 根据用户角色选择表达方式 |
| 批量 vs 逐个 | 多项确认 | 低风险批量确认，高风险逐个确认 |

### 3.3 用户状态感知

```yaml
UserState:
  role: developer | manager | end_user
  expertise_level: expert | intermediate | novice
  current_engagement: active | passive | away
  recent_correction_rate: float  # 最近 N 轮的纠正比例
  interaction_preference: minimal | balanced | verbose
```

- `expertise_level` 决定术语使用级别
- `current_engagement` 决定是否发送非阻塞更新
- `recent_correction_rate` 高时增加对齐频率
- `interaction_preference` 调整信息详细度

## 4. 多利益方冲突处理

### 4.1 冲突场景

| 场景 | 冲突方 | 示例 |
|---|---|---|
| 代码审查 | 开发者 vs Reviewer | 开发者想快速合并，reviewer 要求重构 |
| 企业工作流 | 业务方 vs 合规方 | 业务要求加速，合规要求额外审查 |
| 多人协作 | 团队成员 A vs B | 对实现方案的不同偏好 |
| 系统安全 | 用户 vs 安全策略 | 用户要求绕过安全检查 |

### 4.2 冲突处理策略

```text
1. 识别冲突
   - 检测目标之间的矛盾
   - 标记冲突点和冲突方

2. 分类冲突
   - 硬约束冲突（如安全 vs 便利）→ 硬约束优先
   - 偏好冲突（如方案 A vs 方案 B）→ 呈现权衡，请求决策
   - 优先级冲突（如速度 vs 质量）→ 明确当前上下文的优先级

3. 透明呈现
   - 不静默选择一方
   - 展示每个选项的利弊
   - 标记不可调和的约束

4. 请求决策
   - 将决策权交给有权限的人
   - 提供足够信息但不过载
```

### 4.3 优先级链

```text
安全/合规 > 数据完整性 > 用户明确指令 > 效率 > 偏好
```

当冲突涉及安全或合规时，Agent 不应将决策权交给用户，而应执行安全约束并解释原因。

## 5. IntentAlignmentRecord Schema

```yaml
alignment_id: string
type: initial | milestone | drift_detected | delivery | conflict
trigger: scheduled | signal_detected | user_initiated
question: string
user_response: string | null
alignment_result: confirmed | adjusted | cancelled
adjustments_made:
  - field: string
    old_value: any
    new_value: any
timestamp: datetime
```

## 6. 常见失败

| 失败 | 表现 | 修复 |
|---|---|---|
| 意图漂移失明 | 长任务结束才发现做错了 | 里程碑对齐 + 漂移信号检测 |
| 过度确认 | 每一步都问用户 | 按风险和时长控制对齐频率 |
| 信息倾泻 | 一次给用户 50 行 diff | 渐进式披露 + 摘要优先 |
| 虚假选择 | 给用户选项但每个选项效果相同 | 只在选项有实质差异时请求选择 |
| 静默偏袒 | 多方冲突时不透明地选择一方 | 冲突透明呈现 + 权衡说明 |
| 技术黑话墙 | 非开发者无法理解 Agent 的提问 | 用户状态感知 + 术语适配 |

## 7. 与其他模块的关系

| 模块 | 关系 |
|---|---|
| `interaction/overview.md` | 本文档深化 overview 中 clarification 和 correction 的语义 |
| `interaction/ux-patterns.md` | 提供 UX 层面的具体实现模式 |
| `../explainability/overview.md` | 对齐失败时需要 Decision Explanation |
| `../memory/overview.md` | 意图调整记录可以进入长期记忆 |
| `../control/overview.md` | 安全/合规冲突由 Control 策略裁决 |
| `../../../design-space/methodology/autonomy-and-depth.md` | 自治等级决定对齐的频率和深度 |
| `../../../concepts/agent-epistemics.md` | 意图对齐的目标是减少 Agent 关于用户意图的 Unknown |

## Evidence Status

混合来源。意图漂移检测和认知负载管理的概念在 HCI 领域成熟，但在 Agent 交互设计中缺少系统化实践。多利益方冲突处理基于企业 Agent 的常见痛点归纳。
