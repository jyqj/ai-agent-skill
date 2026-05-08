# Education Agent Implementation Map

> **Evidence Status** — synthesized. Khanmigo、Duolingo、Carnegie Learning MATHia、ITS 研究传统及本知识库相关 patterns 综合整理。

## 参考实现覆盖矩阵

| 设计问题 | Khanmigo | Duolingo Max | Carnegie MATHia | Squirrel AI | AutoTutor |
|---|---|---|---|---|---|
| 苏格拉底式引导 | ★★★ | ★ | ★★ | ★ | ★★★ |
| 间隔重复 | ★ | ★★★ | ★★ | ★★ | ★ |
| 知识追踪 | ★★ | ★★ | ★★★ | ★★★ | ★★ |
| 自适应难度 | ★★ | ★★★ | ★★★ | ★★★ | ★★ |
| 错误概念诊断 | ★★ | ★ | ★★★ | ★★ | ★★★ |
| 教师仪表盘 | ★★★ | ★ | ★★★ | ★★ | ★ |
| 多模态教学 | ★★ | ★★★ | ★★ | ★ | ★ |
| 动机/游戏化 | ★ | ★★★ | ★ | ★ | ★ |

## 品类模块 → 参考系统映射

| 品类模块 | 参考系统 | 关键学习点 |
|---|---|---|
| LearnerModel | Carnegie MATHia / Squirrel AI | 知识追踪需要细粒度概念级 mastery，而非笼统的"分数" |
| KnowledgeGraph | Squirrel AI | 知识图谱驱动自适应路径——概念间的先修关系是路径规划基础 |
| 教学策略 | Khanmigo / AutoTutor | 苏格拉底式引导需要退出条件——不能无限追问 |
| 难度适应 | Duolingo / Carnegie | IRT + 规则混合方案在实践中最稳——纯 IRT 冷启动差，纯规则精度低 |
| 间隔重复 | Duolingo / Anki | SM-2 及其变体是成熟方案；关键是多样化复习形式 |
| 安全边界 | Khanmigo | 作弊检测和年龄内容过滤是教育场景特有需求 |
| 教师协作 | Khanmigo / Carnegie | 教师仪表盘不是附加功能，而是闭环的一部分 |

## 跨品类模式复用

### 来自 Companion Agent 的模式

| 模式 | 在 Education Agent 中的应用 |
|---|---|
| 长期用户档案 | LearnerModel 作为长期维护的学习者画像 |
| 分层记忆（STM/MTM/LTM） | 会话级交互历史 / 近期学习事件 / 长期知识状态和错误概念 |
| 关系阶段管理 | 学习阶段管理（新手 → 熟悉 → 自主） |
| 参与度监测 | 教育场景的参与度信号更丰富（响应时间、正确率、提问频率） |

参考：`../companion-agent/README.md`、`../companion-agent/representation.md`

### 来自 Research Agent 的模式

| 模式 | 在 Education Agent 中的应用 |
|---|---|
| 知识准确性校验 | 教学内容的事实准确性——教错内容比 Research Agent 的 citation drift 后果更严重 |
| 渐进式展示 | 讲解中的分层展示——先简单再深入，而非一次性倾倒 |
| 结构化知识表示 | KnowledgeGraph 借鉴 Research Agent 的 ClaimRecord 结构——概念需要有支撑和关联 |

参考：`../research-agent/README.md`、`../research-agent/representation.md`

## 关联设计模式

| 模式 | 在 Education Agent 中的用途 | 参考 |
|---|---|---|
| progressive-disclosure | 分层讲解——按学习者水平逐步展开 | `../../design-space/patterns/progressive-disclosure.md` |
| layered-memory | 学习者模型的分层存储——短期交互 / 中期学习事件 / 长期知识状态 | `../../design-space/patterns/layered-memory.md` |
| human-in-the-loop | 教师作为审核者和配置者 | `../../evaluation/human-in-the-loop-evals.md` |
| adaptive-loop | 难度自适应的核心模式 | `../../architecture/planes/control/overview.md` |

## 模块配置配方

| 模块 | Education Agent 特化配置 | 通用参考 |
|---|---|---|
| Representation | LearnerModel、KnowledgeGraph、CurriculumStructure、AssessmentResult、MisconceptionRecord | `../../architecture/planes/representation/overview.md` |
| Context | 学习者状态 + 当前课程位置 + 活跃错误概念 + 近期评估结果 | `../../architecture/planes/context/overview.md` |
| Tools | 练习生成、评估引擎、知识图谱查询、间隔重复调度 | `../../architecture/planes/tools/overview.md` |
| Control | 内容准确性 gate、年龄安全 gate、难度边界 gate、作弊检测 gate | `../../architecture/planes/control/overview.md` |
| State | 学习者知识状态、课程进度、错误概念日志、复习调度 | `../../architecture/planes/state/overview.md` |
| Observability | mastery 变化追踪、难度调整日志、参与度趋势、错误概念矫正率 | `../../architecture/planes/observability/overview.md` |
| Interaction | 学习者：引导式对话；教师：仪表盘 + 预警；家长：进度概览 | `../../architecture/planes/interaction/overview.md` |
| Cost | 评估题目数量预算、讲解深度控制、复习频率上限 | `../../architecture/planes/cost/overview.md` |

## MVA 阶梯

| 级别 | 能力 | 关键增量 |
|---|---|---|
| MVA-0 | 单次概念讲解 + 固定难度练习 | 基础教学能力，无适应性 |
| MVA-1 | 多轮对话教学 + 简单难度调整 | 加入 inner loop |
| MVA-2 | 跨会话学习者模型 + 知识追踪 | 加入 outer loop + 持久化 |
| MVA-3 | 错误概念诊断 + 自适应评估 + 间隔重复 | 加入诊断和记忆管理 |
| MVA-4 | 学习路径规划 + 教师仪表盘 + 安全合规 | 加入 meta loop + 教师协作 |
| MVA-5 | 多模态教学 + 协作学习 + 自我改进 | 完整教育生态 |

## 推荐阅读路径

### 学教学策略与引导

```text
categories/education-agent/action-model.md（苏格拉底式提问模式）
categories/education-agent/closed-loop.md（双循环架构）
categories/education-agent/design-decisions.md（策略选择权衡）
```

### 学学习者建模

```text
categories/education-agent/representation.md（LearnerModel 结构）
categories/companion-agent/representation.md（长期用户档案参考）
architecture/planes/state/overview.md（状态管理通用框架）
```

### 学知识准确性保障

```text
categories/education-agent/eval-cases.md（准确性评估用例）
categories/research-agent/representation.md（知识表示与校验）
categories/research-agent/action-model.md（citation gate 参考）
```

## 结论

| 结论 | 含义 |
|---|---|
| Education Agent 的核心不是"能回答问题"，而是教学策略选择 | 同一个概念对不同学习者需要完全不同的教学方式 |
| 错误概念是教育场景的 first-class object | 不能像普通错误一样简单纠正——需要诊断、矫正、跟踪 |
| 双循环是最小可行架构 | inner loop 管即时反馈，outer loop 管学习路径 |
| 内容准确性比其他品类更关键 | 教错内容的伤害比"回答不够好"严重得多 |
| 教师在回路不是可选项 | 教师是闭环的一部分，不是旁观者 |
