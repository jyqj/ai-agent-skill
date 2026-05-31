# Education Agent Task Model

> **Evidence Status** — synthesized. ITS 文献、Bloom 分类法、IRT 理论、自适应学习系统实践综合整理，结合 ORDA-VU 闭环与评估维度。

## 任务类型

| 类型 | 用户输入示例 | 默认深度 | 默认自治 | 成功定义 |
|---|---|---|---|---|
| 概念讲解 | "什么是光合作用？" | D2-D3 | L3 | 准确、层次清晰、适配学习者水平 |
| 练习生成 | "给我出几道二次方程的题" | D3 | L3-L4 | 难度适配、题型多样、覆盖目标知识点 |
| 自适应评估 | "测试一下我对概率论的掌握" | D3-D4 | L4 | 准确估计掌握度、识别知识漏洞 |
| 学习路径规划 | "我想三个月学会 Python" | D4 | L3 | 目标可达、先修关系正确、节奏合理 |
| 错误概念诊断 | "我总是搞不清牛顿第三定律" | D4 | L3-L4 | 定位具体错误概念、追溯根因 |
| 进度追踪 | "我这周学了什么？" | D3 | L4 | 准确反映掌握状态、识别趋势 |
| 协作学习促进 | "帮我们小组讨论这个案例" | D3 | L3 | 平衡参与、引导深度思考、避免搭便车 |

## TaskEnvelope

```yaml
task_envelope:
  task_type: concept_explanation | exercise_generation | adaptive_assessment | learning_path_planning | misconception_diagnosis | progress_tracking | collaborative_facilitation
  learning_objective: string
  subject_domain: string
  learner_context:
    current_level: string|null
    known_misconceptions: []
    learning_style_preference: string|null
    age_group: string|null
  success_criteria:
    - content accuracy verified
    - difficulty within ZPD
    - learner engagement maintained
  constraints:
    - no incorrect content
    - age-appropriate
    - no direct answer to assessment questions
  output_contract:
    format: explanation | exercise_set | assessment_report | learning_plan | diagnostic_report
    include_feedback: boolean
    include_next_steps: boolean
```

## 任务深度说明

### D2-D3: 概念讲解

学习者提出一个概念性问题，Agent 需要：

1. 判断学习者当前水平（从历史或显式提问中）
2. 选择适当的抽象层次和类比
3. 构建层次化解释（定义 → 直觉 → 例子 → 边界条件）
4. 检验理解（追问或嵌入式检查题）

难点：同一概念对不同水平的学习者需要完全不同的解释策略。

### D3: 练习生成

练习生成需要有针对性：

- 覆盖目标知识点的关键变体
- 包含常见错误概念对应的干扰项
- 难度在学习者能力附近（不太简单、不太难）
- 提供不同认知层次的题目（记忆 → 理解 → 应用 → 分析）

### D3-D4: 自适应评估

动态调整题目难度以高效估计学习者能力：

- 基于 IRT 或类似模型选择最优信息量的题目
- 根据回答实时更新能力估计
- 在精度和题量之间平衡（不让学习者做太多题）
- 识别错误模式而非仅统计对错

### D4: 学习路径规划

最复杂的任务，需要：

- 理解目标技能的知识图谱和先修关系
- 评估学习者当前状态（已掌握/部分掌握/未接触）
- 规划从当前到目标的最优路径
- 考虑学习者可用时间、学习节奏、遗忘曲线
- 在路径中插入复习节点（间隔重复）

### D4: 错误概念诊断

错误概念诊断要深入到根因层面：

- 通过诊断性问题序列定位具体错误概念
- 区分"不知道"和"错误理解"
- 追溯错误概念的先修知识链（哪个前置概念出了问题）
- 评估错误概念的根深程度（偶然错误 vs 系统性错误理解）

## 成功维度

| 维度 | 问题 | 证据 |
|---|---|---|
| Content Accuracy | 教学内容是否准确无误 | 学科知识校验、与权威来源对比 |
| Difficulty Calibration | 难度是否在学习者 ZPD 内 | 正确率在 60-85% 区间、学习者未表现挫败或无聊 |
| Pedagogical Effectiveness | 教学策略是否促进理解而非死记 | 迁移测试表现、错误概念消除率 |
| Engagement | 学习者是否持续参与 | 响应时间稳定、主动提问、完成率 |
| Misconception Handling | 错误概念是否被有效诊断和矫正 | 诊断准确率、矫正后稳定性 |
| Learning Outcome | 学习者是否真的学会了 | 延迟后测、迁移应用 |

## 失败分类

| 失败 | 严重度 | 表现 | 恢复策略 |
|---|---|---|---|
| 教学内容错误 | **Critical** | 传授了错误知识 | 立即修正 + 追溯影响范围 + 通知学习者 |
| 年龄不适当内容 | **Critical** | 向未成年人展示不当内容 | 内容过滤 + 年龄分级校验 |
| 难度严重偏高 | High | 学习者连续失败、挫败感 | 回退难度 + 检查先修知识 + 切换策略 |
| 难度严重偏低 | Medium | 学习者无聊、不投入 | 提升难度 + 增加挑战性变体 |
| 错误概念强化 | **Critical** | Agent 的解释无意中加固了错误理解 | 重新诊断 + 使用认知冲突法矫正 |
| 动机伤害 | High | 过度批评、不恰当比较、制造焦虑 | 切换到鼓励性反馈 + 调整目标 |
| 评估偏差 | High | 能力估计系统性偏高或偏低 | 多维度交叉验证 + 重新校准 |
| 作弊协助 | High | 直接给出考试/作业答案 | 检测 + 引导学习过程 |
| 脱离教学目标 | Medium | 对话偏离学习主题 | 温和引导回主题 |
| 学习者模型过时 | Medium | 基于过期数据做决策 | 触发诊断性评估刷新 |

## 与 Bloom 认知层次的映射

| Bloom 层次 | 典型任务 | Agent 动作 |
|---|---|---|
| 记忆 | 术语定义、事实回忆 | 间隔重复、闪卡生成 |
| 理解 | 概念解释、举例 | 类比构建、多角度解释 |
| 应用 | 解题、实践操作 | 练习生成、步骤引导 |
| 分析 | 比较、分类、因果推理 | 开放式问题、案例分析 |
| 评价 | 判断、论证 | 苏格拉底式提问、辩论引导 |
| 创造 | 设计、综合、项目 | 项目引导、创意支架 |

## 最终交付契约

```text
1. 内容：准确、分层、适配学习者水平
2. 评估：嵌入理解检查，不只是单向输出
3. 反馈：具体、建设性、指向改进方向
4. 下一步：明确学习者应做什么
5. 元数据：难度标注、知识点覆盖、与学习目标的关联
```
