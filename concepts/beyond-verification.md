# 超越验证——当 postcondition 不是终极标准

> **Evidence Status** — synthesized. ORDA-VU 框架在主观性任务上的局限性分析；Companion / Creative Agent 的产品实践；HCI 和美学理论中的评价方法论。

> **本文是"验证与完成"话题的主文件。** 元认知控制中的验证关卡见 [元认知控制](../cognitive-architecture/metacognitive-control.md)，效果验证的数据模型见 [表示与效果](representation-and-effects.md)。

本知识库的核心骨架是验证主义的：定义 postcondition、执行动作、read-after-write、确认效果。这对工程型 Agent 是健康的，但对全谱 Agent 不够。下文讨论何时、为何、以及如何超越纯粹的验证。

---

## ORDA-VU 的验证主义根基

ORDA-VU 的 Verify 阶段建立在一个隐含假设上：

> 效果可以被客观测量。如果 postcondition 满足，任务就完成了。

这个假设在以下场景完全成立：

- "代码是否通过测试" —— 运行测试，pass 或 fail
- "CRM 状态是否更新" —— read-after-write，值匹配或不匹配
- "邮件是否已发送" —— 查发件箱，存在或不存在
- "文件是否已创建" —— 检查文件系统，有或没有

这些场景的共同特征：存在一个明确的、二值的、可自动化检测的 postcondition。Verify 阶段可以用程序完成，不需要人类判断。

知识库目前的大部分架构设计——Effect Plane、Effect Ledger、read-after-write 策略——都服务于这个范式。

## 三类不完全可验证的任务

但 Agent 的版图远不止工程任务。以下三类任务无法被标准 postcondition 覆盖：

### 1. 审美与创造性任务

> "帮我设计一个 Logo"、"写一首关于秋天的诗"、"给这段代码写一段优雅的注释"

什么是"好的设计"？没有 postcondition 可以定义它。你可以检查"Logo 是否是 PNG 格式、尺寸是否正确"，但这只是格式验证，不是质量验证。真正的质量——是否打动人、是否传达了品牌气质、是否有辨识度——需要人类的审美判断。

### 2. 情感与陪伴任务

> "我今天心情不好"、"我刚和朋友吵架了"、"陪我聊聊天"

用户情绪变化无法 read-after-write。你不能在对话结束后调用 `user.mood.get()` 来验证情绪是否好转。即使用户说"我好多了"，这也是主观报告，不是客观状态。

更深层的问题：Companion Agent 的目标不是"解决问题"，而是"让用户感到被理解"。"被理解"是一种主观体验，不是一个可测量的状态。

### 3. 价值对齐任务

> "帮我做一个人生规划"、"这个工作机会值不值得接"、"我该不该和 TA 表白"

这类任务的"正确答案"取决于用户的价值观、人生阶段、风险偏好。Agent 给出的建议是否好，不是当下可以判断的——可能三个月后才知道，可能永远无法确定因果关系。

长期的用户满意不是单次可测的 postcondition。

## 扩展验证的语义

不是"放弃验证"，而是扩展 Verify 的含义。从单一的 postcondition 检查，扩展为四种验证模式：

### 从 postcondition 到 resonance（用户对结果的主观满意度反馈）

传统 Verify 问的是："postcondition 是否满足？"

对主观性任务，更恰当的问题是："输出是否与用户的审美、价值观、期望产生共振？"共振不是精确匹配，而是"大方向对了，细节触动了人"。

例如 Creative Agent 为用户生成一个 Logo，格式和尺寸可以用 postcondition 检查，但"是否传达了品牌气质"只能通过用户反馈判断。检测方式包括：用户的即时反应（继续对话 vs 沉默）、后续行为（是否采纳建议）、长期反馈（是否回来）。

### 从 single-point verification 到 longitudinal alignment（纵向一致性——多次交互中趋势是否正确）

传统 Verify 是一次性检查：执行完就验证，验证完就结束。

对价值相关的任务，验证是一个持续过程：每次交互都是一个数据点，趋势比单点更重要。用户满意度的移动平均、偏好预测的准确率、建议采纳率的变化——这些纵向指标比任何单次检查都更有意义。例如 Companion Agent 的情感陪伴效果无法在单次对话中衡量，需要观察用户是否在几周内持续回来、对话深度是否增加。

### 从 objective measurement 到 intersubjective agreement（多方共识——多个判断主体的意见是否一致）

传统 Verify 依赖客观测量：状态值是否正确、测试是否通过。

对审美和创造性任务，替代标准是多方共识：不是"客观上好"，而是"多个有判断力的人都认为好"。这正是专家评审、A/B 测试和偏好排序的理论基础。例如 Creative Agent 生成的设计方案，可以让 3 位设计师独立评分，取一致性较高的结果作为质量信号。

多方共识不如客观测量可靠，但它是审美和情感领域能达到的最佳标准。

### 验证模式的统一视图

```
verification_type:
  objective        # 传统 postcondition，可自动化
  resonance        # 用户对结果的主观满意度
  longitudinal     # 多次交互中趋势是否正确
  intersubjective  # 多个判断主体的意见是否一致
```

**选择哪种验证模式**——按以下顺序判断：

| 判断条件 | 选择 |
|---|---|
| 结果状态可自动检测（文件存在、测试通过、API 返回值匹配） | objective |
| 结果质量取决于单个用户的主观感受（语气、风格、情感回应） | resonance |
| 效果需要多次交互才能观察（习惯改变、关系质量、学习进步） | longitudinal |
| 没有单一权威判断者，需要多人交叉评估（设计方案、内容质量） | intersubjective |

这四种模式不是互斥的，而是可以组合的。一个"帮我写周报"的任务可能同时需要：
- objective：格式是否正确、长度是否合适
- resonance：语气是否符合用户风格
- intersubjective：同事/领导是否认可

## 对知识库的影响

### Verify 阶段的扩展

当前 Verify 阶段的 schema 应支持 `verification_type` 字段：

```yaml
verify:
  verification_type: resonance
  method: user_feedback
  signal: continuation_rate
  threshold: "3-turn conversation continuation > 70%"
```

这不是破坏现有架构，而是扩展 Verify 阶段的表达能力。

### 品类架构的差异化

不同品类的 Agent 应采用不同的默认验证策略。映射依据是各品类的核心验收标准差异——任务交付型的验收标准是客观状态变更，创作型的验收标准是用户主观满意，陪伴型的验收标准是长期关系质量：

| 品类 | 主要验证类型 | 辅助验证类型 |
|---|---|---|
| Coding Agent | objective | - |
| Workflow Agent | objective | - |
| Research Agent | objective + intersubjective | longitudinal |
| Creative Agent | resonance + intersubjective | longitudinal |
| Companion Agent | resonance + longitudinal | intersubjective |
| Coaching Agent | longitudinal | resonance |

### Evaluation 框架的补充

`evaluation/subjective-eval.md` 已经创建，提供了主观性任务的具体评估指标和方法。本文是其哲学基础。

## 扩展验证模式的意义

扩展验证模式后，知识库可以覆盖工程任务之外的主观性 Agent 品类。

当前知识库面向构建工程型 Agent 的架构师——关注"代码是否正确"、"API 是否调通"、"数据是否一致"。但 Companion Agent 的验收标准是"用户是否感到被理解"，Creative Agent 的验收标准是"作品是否打动人"，Coaching Agent 的验收标准是"用户是否在成长"——这些都不是 postcondition 能捕获的。

从 postcondition 到 resonance，从单次检查到纵向追踪，从客观测量到多方共识——这三步扩展让 Agent 架构能处理主观性验收场景。

---

## 延伸阅读

- `evaluation/subjective-eval.md` — 主观性任务的具体评估框架
- `concepts/representation-and-effects.md` — 表示、接口与效果（验证主义的核心文档）
- `architecture/planes/effects/overview.md` — Effect Plane 架构
- `categories/` — 各品类 Agent 的验证需求差异
- `design-space/lessons-learned/single-model-judge.md` — 同源 Judge 的失败案例
