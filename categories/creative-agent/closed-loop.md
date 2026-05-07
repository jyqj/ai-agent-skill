# Creative Agent Closed Loop

> **Evidence Status** — synthesized. `architecture/lifecycle.md`、`architecture/kernel/agent-loop.md`、creative agent 参考项目中的生成-评估-迭代循环、验证和恢复模式、`concepts/beyond-verification.md` 四种验证模式。

## ORDA-VU for Creative Agent

```text
Observe
  用户 brief、StyleGuide、参考作品、用户反馈、历史输出、品牌规则
Represent
  TaskEnvelope、CreativeBrief、StyleGuide、ReferenceWork、ContentDraft、EvaluationScore、BrandVoiceProfile
Decide
  任务类型、生成策略、模型选择、参数配置、迭代策略、审批点
Act
  generate / refine / evaluate / copyright_check / brand_check / publish
Verify
  风格一致性检查、品牌合规检测、版权扫描、用户预览、跨模态一致性验证
Update
  ContentDraft 新版本、EvaluationScore 更新、VersionHistory 追加、记忆候选项、最终交付
```

## Happy Path

```text
1. Intake
   - 解析 CreativeBrief：主题、语调、受众、格式、约束
   - 加载关联 StyleGuide 和 BrandVoiceProfile
   - 确认参考作品版权状态

2. Context Assembly
   - 构建 CreativeContextPack
   - 选择相关 StyleGuide 规则片段（不全量加载）
   - 索引匹配的 ReferenceWork

3. Strategy
   - 确定生成策略：单模型 vs 多模型管线
   - 设置参数：model、temperature、seed、style prompt
   - 定义验证策略和审批点

4. Generate
   - 执行生成（文本/图像/视频/音频）
   - 记录生成参数到 ContentDraft

5. Evaluate
   - 风格一致性评估（StyleGuide 对照）
   - 品牌合规检测（禁止用语、语调、视觉规范）
   - 版权相似度扫描
   - 质量评分（多维度）

6. Review Gate
   - 如果评估全部通过：进入用户预览
   - 如果评估未通过：自动修复或重新生成（见 Failure Loops）

7. User Feedback
   - 用户接受：进入交付
   - 用户要求修改：记录修改指令，进入 Refine 循环

8. Refine (conditional)
   - 根据修改指令调整草稿
   - 重新评估
   - 循环到收敛或上限

9. Deliver
   - 最终版本确认
   - 发布/交付（需审批）
   - 记录 EffectRecord
```

## Failure Loops

### Style Drift Loop（风格偏离）

```text
style_consistency_score < threshold
  -> 诊断偏离维度（语调？用词？视觉？）
  -> 重新注入 StyleGuide 偏离片段到 prompt
  -> 降低 temperature
  -> 重新生成或局部修改
  -> 重新评估
  -> if still drifted after 2 attempts: escalate to human review
```

### Copyright Risk Loop（版权风险）

```text
copyright_similarity > high_risk_threshold
  -> 标记风险内容区域
  -> 分析相似来源
  -> 策略选择：
      替换素材 | 修改偏离区域 | 完全重新生成
  -> 重新版权扫描
  -> if still flagged: block + human review + legal escalation
```

### Infinite Iteration Loop（无限迭代）

```text
iteration_count >= max_iterations AND NOT converged
  -> 检查收敛趋势：
      if scores_improving: 允许额外 1-2 轮
      if scores_flat: 请求用户重新定义验收标准
      if scores_declining: 回退到最佳版本，请求用户确认
  -> 输出当前最佳版本 + 迭代历史 + 不收敛原因分析
  -> 建议：重新定义 brief / 调整期望 / 人工介入
```

### Creative Exhaustion Loop（创意枯竭）

```text
outputs_too_similar across batch OR iterations
  -> 度量同质化程度（语义相似度、结构重复率）
  -> 策略梯度：
      level 1: 增加 temperature
      level 2: 切换模型或 prompt 策略
      level 3: 引入随机参考作品
      level 4: 请求用户提供新的创意方向
  -> 重新生成
  -> 重新评估多样性指标
```

### Brand Violation Loop（品牌违规）

```text
brand_compliance = fail
  -> 识别违规类型：
      critical（禁止用语、严重语调偏离）: 必须修复
      warning（轻微语调偏差）: 自动修复尝试
  -> 自动修复：替换禁止用语、调整语调
  -> 重新品牌检测
  -> if critical still present: block + human review
```

### Modality Mismatch Loop（跨模态不一致）

```text
cross_modal_consistency < threshold
  -> 确定锚定模态（通常是用户最关注的模态）
  -> 重新生成偏离模态，以锚定模态为约束
  -> 重新评估跨模态一致性
  -> if still mismatched: 简化跨模态约束 + human review
```

## Stop Gate

Creative Agent 只有满足 stop gate，才能进入最终交付：

```text
[ ] 输出符合 CreativeBrief 的主题、语调、格式要求
[ ] StyleGuide 一致性评分 >= 阈值（默认 0.8）
[ ] 品牌合规检测通过（无 critical 违规）
[ ] 版权扫描通过（无 high-risk 标记）
[ ] 用户显式接受输出 或 达到最大迭代次数且最后版本评分 >= 阈值
[ ] 发布/交付操作已获得必要审批
[ ] 最终回答包含：内容、评估结果、版权状态、剩余风险
```

## 验证模式

创意验证不能只用客观 postcondition。按 `concepts/beyond-verification.md` 的四种验证模式：

### Objective Verification（客观验证）

可自动化的规则检查：

| 检查项 | 工具 | 标准 |
|---|---|---|
| 版权相似度 | 相似度检索/版权 API | similarity < threshold |
| 禁止用语 | 规则引擎 | 0 matches |
| 格式规范 | 格式验证器 | 满足长度/尺寸/分辨率 |
| 品牌色彩（视觉） | 色彩提取器 | 色彩在 palette 范围内 |
| 可读性（文本） | 可读性公式 | 满足目标 readability level |

### Resonance Verification（共鸣验证）

用户是否认为输出"好"：

| 信号 | 采集方式 | 注意事项 |
|---|---|---|
| 用户接受/拒绝 | 交互记录 | 最直接的信号，但受用户期望影响 |
| 修改轮次 | 迭代计数 | 轮次少 = 更好匹配用户意图 |
| 用户情感反馈 | 对话分析 | "太好了" vs "凑合吧" |
| 使用率 | 发布后追踪 | 用户是否真的使用了交付物 |

### Intersubjective Verification（主体间验证）

多评审者间的一致性：

| 方法 | 适用场景 | 最低要求 |
|---|---|---|
| A/B 测试 | 比较不同生成策略 | 10,000+ 轨迹/臂（统计显著性） |
| 专家评分 | 高 stakes 内容 | >= 3 位评审者 + 一致性度量 |
| LLM-as-Judge 多评委 | 批量内容评估 | >= 3 个不同 prompt/model + 一致性检查 |
| 用户群反馈 | 受众验证 | 目标受众样本 + 结构化反馈 |

### Longitudinal Verification（纵向验证）

长期品牌一致性追踪：

| 指标 | 频率 | 警报条件 |
|---|---|---|
| 风格一致性均值 | 每批/每周 | 均值连续 3 期下降 |
| 品牌合规率 | 每批/每周 | 低于 99% |
| 语调漂移指标 | 每月 | 与基线偏差 > 阈值 |
| 用户满意度趋势 | 每月 | 连续下降 |
| 创意多样性指标 | 每月 | 过低（同质化）或过高（失控） |

## Final Response Contract

```text
Summary
- 创建/修改了什么内容，为哪个 brief

Content
- 最终版本预览或链接
- 版本号和迭代历史摘要

Evaluation
- 风格一致性评分
- 品牌合规状态
- 版权扫描结果
- 质量评分

Risks / Follow-ups
- 未验证的维度
- 长期一致性注意事项
- 建议的下一步
```

## 与范式层的关系

- 外层：ORDA-VU。
- 单次生成：ReAct（generate → evaluate → deliver）。
- 迭代精炼：ReAct + Reflection（evaluate → feedback → refine）。
- 批量生产：Plan-and-Execute（计划 → 批量执行 → 抽样验证）。
- 多模态工作流：Plan-and-Execute + 跨模态一致性约束。
- 长期维护：持续监控 + Longitudinal Verification。

相关：`../../paradigms/reasoning-paradigms.md`、`../../paradigms/control-paradigms.md`、`../../architecture/lifecycle.md`、`../../concepts/beyond-verification.md`。
