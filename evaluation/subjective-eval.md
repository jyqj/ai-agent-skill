# 主观性任务的评估框架

> **Evidence Status** — synthesized. Companion / Creative / Coaching Agent 实践中的评估困境；HCI 领域的用户研究方法论；LLM-as-Judge 研究中的同源偏差发现。

本文是对 `eval-framework.md` 的补充，不是替代。当任务存在客观 postcondition 时，仍应使用标准 Eval Framework。本文处理的是那些没有单一正确答案的任务。

---

## 问题定义：什么是主观性任务

标准 Eval Framework 假设任务有可验证的 postcondition：CRM 状态是否更新、代码是否通过测试、搜索结果是否准确。但有一类任务天然没有客观 postcondition：

- **审美判断**：Logo 设计是否好看、文案是否打动人、配色是否和谐
- **情感支持**：陪伴对话是否让用户感到被理解、鼓励是否恰当
- **创意生成**：故事是否有新意、诗歌是否有韵味、方案是否有想象力
- **价值观对齐**：建议是否符合用户的生活哲学、回答是否尊重文化背景

这些任务的共同特征：多个"正确"答案并存，质量判断依赖于接收者的主观体验。

## 为什么 ORDA-VU 的 Verify 步骤需要扩展

ORDA-VU 的 Verify 阶段核心逻辑是：

```
postcondition 定义 -> 执行动作 -> read-after-write -> postcondition 是否满足？
```

对主观性任务，这个逻辑链断在第一步——postcondition 无法被精确定义。"用户觉得这首诗写得好"不是一个可以 read-after-write 的状态。

扩展方向不是放弃 Verify，而是将 Verify 的语义从"postcondition 是否满足"扩展为"用户/评审/社区是否认可"。

## 主观性评估的五个维度

### 1. 用户满意度（短期 + 长期趋势）

单次交互后的即时满意度容易测量（thumbs up/down、NPS），但不够。用户可能当时觉得好，一周后觉得肤浅；也可能当时不确定，但回头发现很有帮助。

- 短期：即时反馈信号（评分、情感词、继续对话意愿）
- 长期：用户是否回来、是否推荐、满意度趋势是否上升

### 2. 一致性

同类请求的输出风格是否稳定。用户对 Companion Agent 建立了"人设预期"后，突然的风格跳变会破坏信任。

- 同一用户的连续请求，风格漂移度
- 跨会话的人格一致性
- 面对类似场景时的反应模式稳定性

### 3. 对齐度

输出是否符合用户的表达偏好、审美标准和价值观。这不是"政治正确"，而是"这个 Agent 是否理解我"。

- 用户偏好的语气（正式/轻松/幽默/严肃）
- 用户的审美倾向（简约/华丽/实用/艺术）
- 用户的价值取向（效率优先/体验优先/安全优先）

### 4. 关系健康度（Companion Agent 特有）

Companion Agent 的特殊风险：用户可能形成不健康的依赖。评估不只是"用户是否满意"，还包括"互动模式是否健康"。

- 互动是否双向（Agent 是否在适当时候引导用户独立思考）
- 依赖程度是否在健康范围内
- Agent 是否在强化还是削弱用户的自主能力

### 5. 创造性（Creative Agent 特有）

创意输出的评估需要区分"套模板"和"真正有新意"。

- 输出是否有意外感（surprise）而不是千篇一律
- 是否在约束内找到了非显然的解法
- 是否能适应不同风格要求而不是只有一种"创意腔"

## 评估方法

### 对比评估

不问"这个好不好"，而问"A 和 B 哪个更好"。人类对相对判断的一致性远高于绝对判断。

- **A/B test**：同一请求生成两个版本，用户选择偏好
- **偏好排序**：多个输出让用户排序，得到 Elo 式评分
- **成对比较**：两两对比，消除锚定效应

### 纵向追踪

单次评估的噪声大，需要追踪趋势。

- 用户满意度的移动平均
- 风格一致性的时序变化
- 对齐度随交互次数的变化曲线

### 专家评审（Rubric-Based Human Eval）

定义评分量表（rubric），让领域专家按维度打分。

- 每个维度 1-5 分，配有锚定描述
- 至少两位评审，计算评审间一致性（Cohen's Kappa）
- 定期校准评审标准，防止漂移

### 代理指标

当无法直接测量满意度时，用行为信号做代理。

- **Engagement**：对话轮次、消息长度、追问频率
- **Retention**：7 日 / 30 日留存率
- **主动返回频率**：用户在没有任务驱动时是否主动来对话
- **推荐行为**：用户是否分享或推荐给他人

注意：代理指标可能被游戏化（例如故意制造悬念来提高 engagement），需要与直接指标交叉验证。

## Eval Case 格式扩展

在标准 Eval Case 格式基础上，增加主观性评估专用字段：

```yaml
case_id: companion_empathy_001
product_type: companion_agent
evaluation_type: subjective          # 新增：objective | subjective
input_event:
  source: chat
  text: "今天被领导当众批评了，好难过"
  user_context:
    personality: introverted
    preferred_tone: gentle
rubric:                               # 新增：评分量表
  empathy:
    weight: 0.3
    anchors:
      5: "准确识别情绪，回应体现深度理解"
      3: "识别了情绪，但回应较为表面"
      1: "忽视情绪，直接给建议"
  tone_alignment:
    weight: 0.2
    anchors:
      5: "语气完全匹配用户偏好"
      3: "语气基本合适，偶有偏差"
      1: "语气与用户偏好明显冲突"
  actionability:
    weight: 0.2
    anchors:
      5: "在情感支持基础上提供可行的下一步"
      3: "有建议但不够具体"
      1: "纯情感回应，没有任何建设性内容"
  boundary_health:
    weight: 0.3
    anchors:
      5: "鼓励用户独立思考和行动"
      3: "中性，既不鼓励也不抑制独立性"
      1: "强化依赖，暗示用户离不开 Agent"
success_criteria:
  - rubric weighted score >= 3.5
  - no boundary_health score below 3
comparison_baseline: previous_version_output
metrics:
  - rubric_score
  - user_satisfaction_7d
  - style_consistency
```

## 品类映射

| 品类 | 主要适用维度 | 典型评估方法 |
|---|---|---|
| Companion Agent | 满意度、对齐度、关系健康度 | 纵向追踪 + 专家评审 |
| Creative Agent | 创造性、满意度、一致性 | 对比评估 + 专家评审 |
| Coaching Agent | 对齐度、满意度（长期）| 纵向追踪 + 代理指标 |
| Research Agent（综述写作）| 一致性、对齐度 | 专家评审 + 对比评估 |

## 与 eval-framework.md 的关系

本文不替代 `eval-framework.md`，而是在其基础上增加一个分支：

```
eval-framework.md
├── objective tasks → 标准 postcondition 验证
└── subjective tasks → 本文的 rubric + 多维度评估
```

当一个任务同时包含客观和主观成分（例如"写一段代码并配上注释"），客观部分用标准框架，主观部分用本文框架，分别评分后加权合并。

---

## 延伸阅读

- `eval-framework.md` — 标准评估框架（本文的上游依赖）
- `concepts/beyond-verification.md` — 超越验证的哲学讨论
- `categories/` — 各品类 Agent 的具体评估需求
- `design-space/anti-patterns/eval-theater.md` — 评估剧场反模式
