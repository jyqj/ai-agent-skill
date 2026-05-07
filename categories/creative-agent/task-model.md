# Creative Agent Task Model

> **Evidence Status** — synthesized. creative agent 参考项目（Sight AI、DeeVid、Jasper、StyleAligned、Adobe Firefly）与 `evaluation/failure-taxonomy.md` 的任务/失败抽象。

## 任务类型

| 类型 | 用户输入示例 | 默认深度 | 默认自治 | 成功定义 |
|---|---|---|---|---|
| 单次生成 | "写一篇关于 AI 趋势的博客" / "生成一张产品宣传图" | D1-D2 | L2 | 用户接受输出，风格/品牌合规 |
| 迭代精炼 | "这篇文章语气再轻松一点" / "背景颜色偏冷色调" | D2-D3 | L2-L3 | 用户满意 + 版本收敛 + 不超过最大轮次 |
| 批量内容生产 | "为 10 个产品各写一篇介绍" / "生成 20 张社交媒体图" | D3-D4 | L3-L4 | 品牌一致性达标率 + 单篇质量合格 |
| 多模态工作流 | "制作一段 30 秒产品视频，含旁白和字幕" | D4-D5 | L3-L4 | 完整作品交付 + 跨模态一致性 |
| 长期品牌维护 | "持续为品牌账号生产周更内容" | D5-D6 | L4 | 品牌声音跨月一致 + 风格无漂移 |

## TaskEnvelope

Creative Agent 接受任务时应生成或补全 TaskEnvelope：

```yaml
task_envelope:
  task_type: single_gen | iterative_refine | batch_production | multimodal_workflow | brand_maintenance
  user_goal: string
  creative_brief:
    theme: string
    tone: string
    target_audience: string
    constraints: []
  style_guide_ref: string | null
  reference_works: []
  success_criteria:
    - observable outcome
  constraints:
    - no copyright infringement
    - brand voice compliance
    - content safety
  allowed_actions:
    generate: true
    style_evaluate: true
    publish: ask | deny
  risk_level: low | medium | high
  depth_target: D0 | D1 | D2 | D3 | D4 | D5 | D6
  autonomy_level: L0 | L1 | L2 | L3 | L4
  verification_plan:
    - style consistency check
    - copyright scan
    - user review
  stop_gate:
    - user accepted or max iterations reached
    - copyright check passed
    - brand compliance verified
```

## 任务类型详解

### 单次生成

**输入结构**：CreativeBrief（主题、语调、目标受众、长度/尺寸约束）+ 可选 StyleGuide + 可选 ReferenceWork。

**成功标准**：
- 输出符合 brief 的主题和语调要求
- 通过品牌规则检测（如有 StyleGuide）
- 无版权风险
- 用户首次或少量修改后接受

**失败分类**：
- 主题偏离：生成内容与 brief 主题无关
- 风格不匹配：语调、用词与 StyleGuide 不一致
- 质量不足：可读性差、逻辑断裂、视觉混乱
- 内容安全问题：含不适当内容

### 迭代精炼

**输入结构**：初始 ContentDraft + 用户反馈指令（自然语言修改要求）+ 可选参考对比。

**成功标准**：
- 每轮修改有实质性改进（可量化：EvaluationScore 单调上升或在目标维度提升）
- 最终版本通过用户验收
- 总轮次不超过配置上限（默认 5 轮）

**失败分类**：
- 无限修改循环：用户反馈模糊导致 Agent 无法收敛
- 过度修改：修改了用户未要求改的部分
- 回退：新版本在某些维度退步
- 收敛失败：多轮后 EvaluationScore 无提升

### 批量内容生产

**输入结构**：模板 + 参数集（产品列表、主题列表等）+ StyleGuide + 质量阈值配置。

**成功标准**：
- 所有输出通过品牌一致性检测（风格偏差 < 阈值）
- 品牌合规率 100%
- 单篇质量评分 >= 最低阈值
- 批次内无重复/同质化问题

**失败分类**：
- 风格漂移：批次后半段输出与前半段风格偏差增大
- 品牌违规：部分输出违反品牌规则
- 同质化：输出高度相似，缺乏变化
- 参数映射错误：产品 A 的描述用了产品 B 的信息

### 多模态工作流

**输入结构**：完整 CreativeBrief（含各模态的要求）+ 素材资源 + 跨模态一致性约束。

**成功标准**：
- 各模态输出在风格、角色、色调上一致
- 完整作品可交付（无缺失环节）
- 技术规格合规（分辨率、时长、格式）
- 无版权问题

**失败分类**：
- 一致性断裂：视觉风格与文字描述不匹配，角色跨场景不一致
- 版权问题：使用了受保护素材
- 技术规格不符：分辨率/时长/格式不满足交付要求
- 管线中断：某一环节生成失败导致后续环节无法继续

### 长期品牌维护

**输入结构**：StyleGuide（长期有效）+ 内容日历/计划 + 历史输出记录 + 品牌演化规则。

**成功标准**：
- 跨月输出品牌声音一致
- 风格漂移检测指标持续达标
- 能适应品牌策略的有意调整（区分漂移 vs 演化）

**失败分类**：
- 价值漂移：品牌核心价值表达逐渐偏移
- 风格侵蚀：语调/视觉风格在长期中缓慢变化
- 记忆丢失：Agent 遗忘之前建立的品牌约定
- 无法区分漂移与演化：把有意的品牌调整当作错误纠正

## 深度等级细分

| 深度 | 含义 | 创意场景示例 |
|---|---|---|
| D0 | 直接输出，无分析 | 模板填充 |
| D1 | 理解意图，单步生成 | 根据 brief 写一段文案 |
| D2 | 理解意图 + 风格匹配 | 按 StyleGuide 生成品牌文案 |
| D3 | 多步规划 + 迭代优化 | 写文章 → 评估 → 修改 → 再评估 |
| D4 | 跨模态/跨工具协调 | 文案 + 配图 + 排版一体化 |
| D5 | 复杂管线编排 + 质量保证 | 视频制作全流程（脚本→分镜→生成→剪辑） |
| D6 | 长期策略 + 品牌演化 | 品牌内容策略持续执行 |

## 自治等级细分

| 自治 | 含义 | 创意场景示例 |
|---|---|---|
| L0 | 仅建议，不执行 | 提供创意方向建议 |
| L1 | 每步确认 | 生成草稿后等用户确认再继续 |
| L2 | 在边界内自主执行 | 按 StyleGuide 自主生成，偏离时暂停 |
| L3 | 自主完成子任务 | 批量生成 + 自动质检，异常时上报 |
| L4 | 全自主，仅异常上报 | 自动化内容管线，版权/品牌问题时升级 |

## 成功标准

| 成功维度 | 问题 | 证据 |
|---|---|---|
| Goal Fit | 是否满足创意 brief？ | 输出与 brief 要求的映射 |
| Style Consistency | 是否符合风格要求？ | 风格一致性评分 + StyleGuide 对照 |
| Originality | 是否有创意价值？ | 非重复性检测 + 新颖性评分 |
| Brand Compliance | 是否符合品牌规则？ | 品牌规则检测器结果 |
| Copyright Safety | 是否存在版权风险？ | 相似度检测 + 版权扫描 |
| User Satisfaction | 用户是否满意？ | 用户反馈 / 接受率 |

## 失败分类

| 失败 | 表现 | 恢复策略 |
|---|---|---|
| Style Drift | 输出风格偏离 StyleGuide | 重新注入 style guide + 降低 temperature |
| Copyright Risk | 输出与已有作品高度相似 | 标记 + 人工审查 + 替换素材 |
| Infinite Loop | 用户反馈不收敛 | 设置最大迭代次数 + 请求明确验收标准 |
| Creative Exhaustion | 输出高度同质化 | 增加 temperature / 切换模型 / 引入随机参考 |
| Brand Violation | 输出违反品牌规则 | 品牌规则检测器拦截 + 重新生成 |
| Modality Mismatch | 跨模态输出不一致 | 锚定主模态 + 重新生成偏离模态 |
| Context Loss | 长对话中遗忘之前约定 | 关键约束写入 StyleGuide 或长期记忆 |
| Over-editing | 修改了用户未要求改的部分 | diff 对比 + 仅修改指定区域 |

## 任务分解原则

```text
单次生成：brief → generate → evaluate → deliver。简单 ReAct 即可。
迭代精炼：generate → evaluate → user feedback → refine → re-evaluate，循环到收敛或上限。
批量生产：先确定模板和种子 → 批量生成 → 抽样质检 → 修复异常 → 整批交付。
多模态工作流：按模态分阶段，每阶段内独立 ReAct，跨阶段做一致性检查。
长期维护：按时间窗口分 checkpoint，每个 checkpoint 包含风格审计和漂移检测。
```

## 输出契约

最终回答至少包含：

```text
1. 做了什么：按内容/模态说明
2. 风格一致性：与 StyleGuide 的对照结果
3. 版权检查：扫描结果和风险说明
4. 还剩什么：未验证、风险、建议下一步
5. 审查入口：草稿预览、版本对比、评分详情
```

相关：`../../evaluation/failure-taxonomy.md`、`../../design-space/methodology/autonomy-and-depth.md`、`../../concepts/beyond-verification.md`。
