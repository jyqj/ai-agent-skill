# Education Agent Representation Model

> **Evidence Status** — synthesized. 知识追踪（Knowledge Tracing）文献、IRT、贝叶斯知识追踪（BKT）、Deep Knowledge Tracing（DKT）、自适应学习系统表示层综合整理。

## 关键表示对象

| 对象 | 含义 | Freshness | Trust |
|---|---|---|---|
| LearnerModel | 学习者的综合画像（知识状态、风格、动机） | 每次交互后更新 | medium — 基于推断 |
| KnowledgeGraph | 学科知识结构（概念、先修、难度） | 课程配置时设定 | high — 专家或课标定义 |
| CurriculumStructure | 教学大纲（单元、课时、目标、评估） | 课程配置时设定 | high — 教师/设计者定义 |
| AssessmentResult | 单次评估的详细记录 | 评估完成时写入 | high — 直接观测 |
| LearningSession | 单次学习会话的交互记录 | 会话进行中实时 | high — 直接观测 |
| MisconceptionRecord | 已检测到的错误概念及其状态 | 诊断/矫正时更新 | medium — 推断 + 观测混合 |

## LearnerModel

```yaml
learner_id: string
profile:
  age_group: child | teen | adult
  language: string
  accessibility_needs: []
knowledge_state:
  - concept_id: string
    mastery_level: float  # [0, 1]
    confidence: float     # 估计的确定性
    last_assessed: datetime
    evidence_count: integer  # 基于多少次观测
learning_style:
  preferred_modality: visual | textual | interactive | mixed
  pace: slow | moderate | fast
  response_to_challenge: persists | needs_encouragement | avoids
misconceptions:
  - misconception_id: string
    concept_id: string
    description: string
    severity: surface | moderate | deep
    status: active | partially_corrected | corrected | regressed
    first_detected: datetime
    correction_attempts: integer
motivation:
  engagement_trend: rising | stable | declining
  streak_days: integer
  recent_frustration_signals: integer
  recent_success_signals: integer
goals:
  - goal_id: string
    description: string
    target_date: datetime|null
    progress: float  # [0, 1]
```

### 学习者模型漂移

学习者模型会随时间失效——人会遗忘：

| 场景 | 漂移方向 | 应对 |
|---|---|---|
| 长时间未学习 | mastery_level 可能过高（遗忘） | 基于遗忘曲线衰减 + 复习前先做诊断 |
| 密集学习后 | mastery_level 可能虚高（短期记忆） | 延迟后测验证长期记忆 |
| 外部学习 | mastery_level 可能过低（未捕获的进步） | 允许学习者自报 + 诊断性测试校准 |
| 错误概念矫正后 | 可能回归（corrected → regressed） | 间隔复查错误概念状态 |

## KnowledgeGraph

```yaml
domain: string  # 如 "高中物理"
concepts:
  - concept_id: string
    name: string
    description: string
    difficulty: float  # [0, 1] 领域内相对难度
    bloom_level: remember | understand | apply | analyze | evaluate | create
    prerequisites: []  # concept_id 列表
    mastery_threshold: float  # 达到此水平视为掌握
    common_misconceptions:
      - misconception_id: string
        description: string
        frequency: float  # 学习者群体中的出现频率
        diagnostic_questions: []
        correction_strategies: []
    related_concepts: []  # 非先修但相关的概念
```

### 知识图谱质量

知识图谱的质量直接决定教学质量：

- **先修关系错误**：导致学习路径规划失败——跳过必要前置知识
- **难度标定偏差**：导致自适应算法失准——题目选择不当
- **错误概念库缺失**：导致诊断盲区——无法识别常见错误
- **概念粒度不当**：太粗则无法精确定位，太细则维护成本过高

## CurriculumStructure

```yaml
curriculum_id: string
title: string
target_audience: string
units:
  - unit_id: string
    title: string
    learning_objectives:
      - objective_id: string
        description: string
        mapped_concepts: []  # 关联到 KnowledgeGraph
        bloom_level: string
    lessons:
      - lesson_id: string
        title: string
        content_type: explanation | practice | lab | discussion | review
        estimated_duration: duration
        resources: []
    assessments:
      - assessment_id: string
        type: formative | summative | diagnostic
        mapped_objectives: []
        passing_threshold: float
```

## AssessmentResult

```yaml
assessment_id: string
learner_id: string
timestamp: datetime
assessment_type: formative | summative | diagnostic
items:
  - item_id: string
    concept_id: string
    difficulty: float
    learner_response: string
    is_correct: boolean
    time_on_item: duration
    confidence_self_report: float|null  # 学习者自报置信度
    error_pattern: string|null  # 错误类型标注
summary:
  total_items: integer
  correct_count: integer
  estimated_ability: float  # IRT theta
  ability_confidence_interval: [float, float]
  identified_gaps: []  # concept_id 列表
  identified_misconceptions: []  # misconception_id 列表
  recommended_next: string  # 建议下一步
```

## LearningSession

```yaml
session_id: string
learner_id: string
start_time: datetime
end_time: datetime|null
session_type: tutoring | practice | assessment | review | exploration
interactions:
  - turn_id: integer
    role: agent | learner
    content_summary: string  # 不存储完整对话（隐私）
    pedagogical_intent: explain | question | hint | feedback | encourage | assess
    timestamp: datetime
engagement_signals:
  avg_response_time: duration
  response_time_trend: accelerating | stable | decelerating
  off_topic_count: integer
  help_request_count: integer
  voluntary_continuation: boolean  # 学习者是否主动要求继续
outcomes:
  concepts_covered: []
  mastery_changes: []  # { concept_id, before, after }
  misconceptions_addressed: []
  breakthrough_moments: []  # 突然理解的关键时刻
```

## MisconceptionRecord

```yaml
misconception_id: string
concept_id: string
learner_id: string
description: string
category: factual_error | procedural_error | conceptual_confusion | overgeneralization | undergeneralization
severity: surface | moderate | deep
evidence:
  - session_id: string
    turn_id: integer
    learner_statement: string  # 触发诊断的具体回答
status: active | partially_corrected | corrected | regressed
correction_history:
  - attempt_date: datetime
    strategy_used: cognitive_conflict | bridging_analogy | counterexample | direct_correction
    outcome: no_change | partial | full_correction
    notes: string|null
```

## ContextPack 组装策略

Education Agent 的上下文不应把全部学习历史塞进去，而应按需组装：

```text
1. 当前学习目标和会话类型
2. 学习者当前知识状态（相关概念的 mastery）
3. 活跃的错误概念记录
4. 最近的评估结果（相关知识点）
5. 当前课程位置和进度
6. 近期参与度信号
```

## Trust Lane

| 来源 | 默认 lane |
|---|---|
| 课程标准 / 教师配置 | system instruction |
| 知识图谱 / 学科内容 | trusted_data |
| 学习者回答 | untrusted_data（可能包含错误） |
| 学习者自报（"我已经会了"） | low_trust — 需验证 |
| Agent 对学习者状态的推断 | inference — 有不确定性 |
| 历史学习数据 | memory — 可能过时 |

## 关联模式

- `../../architecture/planes/state/overview.md`（学习者状态管理）
- `../../architecture/planes/representation/overview.md`（表示层通用抽象）
- `../../design-space/patterns/layered-memory.md`（分层记忆 — 短期会话 + 长期学习者模型）
- `../companion-agent/representation.md`（长期用户档案参考）
