# Creative Agent Design Decisions

> **Evidence Status** — synthesized. Sight AI 六角色管线、DeeVid Seedream 种子控制、Jasper 品牌声音、StyleAligned 注意力共享、Adobe Firefly Agentic Assistant 的设计观察。

## 生成模型选择

| 策略 | 适合 | 风险 | 默认建议 |
|---|---|---|---|
| 单模型（通用 LLM） | 单模态文本生成、简单图像 | 质量天花板受限于单一模型 | 大多数文本任务的默认选择 |
| 多模型管线 | 多模态、复杂工作流 | 管线复杂度高、一致性挑战 | 视频/多媒体任务 |
| 专用模型 + 通用编排 | 特定领域高质量需求 | 集成成本、模型切换开销 | 品牌级高要求内容 |
| 多 Agent 角色管线 | 复杂内容生产 | 角色间上下文传递损耗 | 长篇/深度内容 |

### 多 Agent 角色管线（Sight AI 模式）

```text
Research Agent  ->  研究主题，收集素材和数据
Outliner Agent  ->  基于研究生成内容大纲
Writer Agent    ->  按大纲撰写完整内容
SEO Agent       ->  优化搜索引擎可见性
Editor Agent    ->  编辑润色，风格一致性
Fact-Checker    ->  事实核查和来源验证
```

升级触发器：
- 单模型生成质量不足 -> 引入专用模型
- 需要多模态输出 -> 多模型管线
- 内容深度/准确性要求高 -> 多 Agent 角色管线

## 风格一致性机制

四层递进策略：

| 层级 | 机制 | 成本 | 效果 | 适用场景 |
|---|---|---|---|---|
| L1 System Prompt | 在 system prompt 中注入 StyleGuide 规则 | 低 | 基础一致性 | 所有场景的默认起点 |
| L2 Fine-tuning | 用品牌语料微调模型 | 高（训练成本） | 深度内化风格 | 高频品牌内容、长期项目 |
| L3 Memory | 将风格规则和成功案例写入长期记忆 | 中 | 跨会话一致 | 持续合作的品牌项目 |
| L4 Post-filter | 生成后通过规则引擎/检测器过滤 | 中 | 兜底保障 | 批量生产、高合规要求 |

### StyleAligned 注意力共享（图像一致性）

```text
原理：通过共享注意力层的 key/value，使多张生成图像在风格上保持一致。
适用：需要一组视觉风格统一的图像（产品系列、系列插图）。
限制：需要支持注意力共享的模型架构；对内容多样性有一定约束。
```

### Jasper 品牌声音（文本一致性）

```text
原理：将品牌声音规则结构化（语调、用词、句式偏好），在生成时作为硬约束注入。
适用：跨团队品牌内容一致性。
关键点：规则必须具体到可检测，不能只是"专业但友好"这样的笼统描述。
```

默认策略：L1 起步，漂移检测失败时逐步升级。

```text
风格一致性评分持续达标 -> 维持当前层级
评分偶尔低于阈值 -> 升级到下一层
批量生产场景 -> 至少 L1 + L4
长期品牌项目 -> L1 + L3，必要时 L2
```

## 评估方式选择

| 策略 | 适合 | 成本 | 可靠性 |
|---|---|---|---|
| 纯自动（规则引擎） | 格式检查、禁止用语、版权扫描 | 低 | 高（但覆盖面窄） |
| LLM-as-Judge | 风格一致性、质量评分、受众匹配 | 中 | 中（需校准） |
| LLM-as-Judge + 人工抽检 | 批量生产的默认模式 | 中-高 | 高 |
| 全量人工审查 | 高 stakes 内容（法律、品牌核心） | 高 | 最高 |
| A/B 测试 | 策略比较、长期优化 | 高（需要流量） | 高（但需要量） |

### LLM-as-Judge 校准

```text
1. 用人工标注的金标准数据集校准 Judge prompt
2. 定期比对 LLM-as-Judge 与人工评分的一致性
3. 对不一致 case 进行分析和 prompt 调整
4. 使用多个 Judge prompt/model 交叉验证
```

默认策略：LLM-as-Judge + 人工抽检。高 stakes -> 全量人工审查。

## 版权检查策略

| 策略 | 适合 | 覆盖面 | 默认建议 |
|---|---|---|---|
| 基于规则的相似度检测 | 文本抄袭、图像翻转 | 中 | 所有场景的默认层 |
| 嵌入空间相似度 | 语义级相似、风格模仿 | 中-高 | 图像和音频场景 |
| 专业版权服务 API | 法律级合规 | 高 | 高法律风险场景 |
| 人工版权审查 | 边界 case、争议判断 | 最高 | 版权争议或法律要求 |

```text
默认管线：
生成内容 -> 规则相似度检测 -> if flagged: 嵌入空间相似度 -> if still flagged: 人工审查
高风险场景：
生成内容 -> 专业版权 API -> 人工审查（无论结果）
```

## 迭代控制

| 参数 | 默认值 | 说明 |
|---|---|---|
| max_iterations | 5 | 最大迭代轮次 |
| convergence_window | 2 | 连续 N 轮评分无提升视为不收敛 |
| min_improvement | 0.02 | 每轮最小评分提升 |
| rollback_on_decline | true | 评分下降时回退到最佳版本 |
| escalation_on_stall | true | 不收敛时请求用户重新定义 brief |

### 收敛检测

```text
scores = [iteration_1_score, iteration_2_score, ...]

converged = latest_score >= acceptance_threshold
stalled = max(scores[-convergence_window:]) - min(scores[-convergence_window:]) < min_improvement
declining = scores[-1] < scores[-2] < scores[-3]

if converged: deliver
if stalled: escalate (request brief clarification)
if declining: rollback to best version + escalate
if iteration_count >= max_iterations: deliver best version + report
```

## 批量一致性

| 机制 | 原理 | 适用场景 |
|---|---|---|
| 模板 + 参数化 | 固定结构，变化参数 | 产品描述、社交媒体帖子 |
| 种子控制 | 固定种子保持可重现性 | 图像系列、视频角色一致 |
| 风格锚定 | 用首个输出或参考作品锚定后续生成 | 视觉系列、系列文章 |
| 抽样质检 | 从批次中随机抽样进行完整评估 | 大规模批量生产 |
| 注意力共享（StyleAligned） | 跨生成共享注意力 key/value | 视觉风格统一的图像组 |

### DeeVid Seedream 种子控制

```text
原理：通过控制扩散模型的种子值和条件输入，使不同帧/场景中的角色和环境保持一致。
适用：AI 视频制作中的角色一致性、环境一致性。
关键参数：seed、character embedding、environment embedding。
限制：种子控制只能保证部分一致性，复杂场景仍需后处理。
```

默认策略：

```text
批量文本：模板 + 参数化 + 抽样质检（5% 或至少 3 篇）
批量图像：种子控制 + 风格锚定 + 抽样质检
批量视频：Seedream 种子控制 + 逐段一致性检查
```

## 上下文策略

| 问题 | 策略 |
|---|---|
| StyleGuide 过长 | 按任务类型只加载相关规则片段 |
| 参考作品过多 | 限制数量（默认 3-5 个），按相关性排序 |
| 长迭代 context rot | 保留最近 2 轮完整上下文 + 之前轮次的摘要 + 关键约束 |
| 跨模态上下文 | 每个模态维护独立上下文，共享全局约束 |
| 版本历史膨胀 | 只保留当前版本 + 最佳版本 + 变更日志 |

## 记忆策略

| 信息 | 放哪 | 写入条件 |
|---|---|---|
| 当前生成参数/评分 | TaskState / EffectRecord | 不进长期记忆 |
| 品牌规则 / StyleGuide | Project Memory（版本化） | 品牌方更新时 |
| 用户风格偏好 | Long-term/User Memory | 多次一致的偏好表达 |
| 成功的风格配方 | Skill Memory | 多次成功且评分高 |
| 失败案例 | Eval/Trace | 用于回归和改进 |

## 控制策略

默认 policy：

```text
deny > ask > allow
```

| Action | Policy |
|---|---|
| read brief/style guide/reference | allow |
| generate draft | allow with evaluation gate |
| evaluate/score | allow |
| refine within scope | allow with version tracking |
| use external reference | check copyright status first |
| publish/deliver | ask / explicit approval |
| override brand rules | deny / explicit approval |
| use copyrighted material | deny unless licensed |
| access user data beyond brief | deny unless scoped |

Hook 建议：

```text
pre_generate: brief completeness check + style guide loaded
post_generate: auto-evaluate (style + brand + copyright)
before_refine: version snapshot
after_refine: re-evaluate + diff from previous version
before_publish: stop gate verification + approval check
before_memory_write: classify (brand/user/skill/eval)
```

## Operations 策略

Creative Agent 进入生产或团队环境后，至少需要：

```text
[ ] ConfigFingerprint: model / prompt / style guide version / evaluation criteria / brand rules version
[ ] TraceEvent: generation params, evaluation scores, user feedback, publish decisions
[ ] Regression suite: representative briefs + failure cases + brand compliance tests
[ ] Shadow mode: 先生成建议不发布，比较人类/agent 输出
[ ] Canary: 小范围启用自动发布
[ ] Incident response: 品牌违规、版权问题、风格漂移、用户投诉处理
```

## 升级触发器

| 观察 | 升级 |
|---|---|
| 风格一致性频繁低于阈值 | 从 L1 System Prompt 升级到 L2 Fine-tuning 或 L4 Post-filter |
| 版权风险频繁检出 | 从规则检测升级到专业版权 API |
| 批量同质化严重 | 引入 StyleAligned 注意力共享或种子控制策略 |
| 迭代经常不收敛 | 优化 brief 引导流程 + 引入结构化验收标准 |
| 长期品牌声音漂移 | 引入 Longitudinal Verification + 定期风格审计 |
| 多模态一致性差 | 升级到多模型管线 + 跨模态约束 |
| 单模型质量瓶颈 | 升级到多 Agent 角色管线 |
| 上下文经常爆 | StyleGuide 分片加载 + 上下文压缩策略 |

相关：`../../paradigms/tool-paradigms.md`、`../../paradigms/control-paradigms.md`、`../../architecture/planes/operations/overview.md`。
