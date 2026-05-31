# Creative Agent Architecture

> **Evidence Status** — synthesized. 来自多 Agent 内容生成实践（Sight AI, Vellum）、AI 视频工作流（DeeVid, Adobe Firefly）、创造力评估研究（Amabile CAT, arXiv 2604.13242）、情感计算与风格一致性技术（StyleAligned）。

## Core Job

帮助用户创造内容——文本、图像、视频、音乐、代码艺术等——同时保持风格一致性、创意引导和版权安全。交付物是高质量的创意作品或创意作品的草稿。

与单次文本生成不同，Creative Agent 需要理解用户的创意意图、维持跨输出的风格一致性、在创意自由和约束（品牌、版权、安全）之间平衡，并在评估上超越客观 postcondition。

## 用户模型

| 用户 | 心智模型 | 信任建立方式 | 默认交互 |
|---|---|---|---|
| 内容创作者 | Agent 是协作伙伴，帮助扩展创意空间 | 输出质量 + 风格一致性 | 迭代对话 + 预览 |
| 营销团队 | Agent 是内容工厂，批量产出品牌一致的内容 | 品牌合规率 + 效率 | 批量任务 + 模板 |
| 设计师 | Agent 是灵感来源和初稿工具 | 可控性 + 可编辑性 | 参数调整 + 变体生成 |
| 开发者/技术用户 | Agent 是 API，可编程的创意管线 | API 可靠性 + 一致性 | 结构化请求 + 批处理 |

## 任务模型

| 任务类型 | 默认深度 | 默认自治 | 成功定义 | 失败模式 |
|---|---|---|---|---|
| 单次生成（文本/图像） | D1-D2 | L2 | 用户接受输出 | 风格偏离、质量不足 |
| 迭代精炼 | D2-D3 | L2-L3 | 用户满意 + 版本收敛 | 无限修改循环 |
| 批量内容生产 | D3-D4 | L3-L4 | 品牌一致性 + 质量达标率 | 风格漂移、品牌违规 |
| 多模态工作流（视频/多媒体） | D4-D5 | L3-L4 | 完整作品交付 | 一致性断裂、版权问题 |
| 长期品牌维护 | D5-D6 | L4 | 品牌声音持续一致 | 价值漂移、风格侵蚀 |

## 表示模型

| 表示对象 | 含义 | Freshness | Trust | Raw Ref |
|---|---|---|---|---|
| CreativeBrief | 用户创意意图、约束、风格要求 | 每次任务更新 | high（用户直接输入） | 保留原始 brief |
| StyleGuide | 品牌/风格规则（语调、色彩、排版） | 长期有效 | high | 可版本化 |
| ReferenceWork | 参考作品（示例图、风格参考） | 任务级 | medium | 保留原始文件 |
| ContentDraft | 生成的草稿（含版本历史） | 每次迭代更新 | low（需评审） | 保留全部版本 |
| EvaluationScore | 评估结果（自动+人工） | 每次评估更新 | medium | 评分 + 理由 |

## 行动模型

| 动作 | 工具/接口 | 风险 | Preconditions | Postconditions | Verification |
|---|---|---|---|---|---|
| 生成初稿 | LLM / 图像模型 / 视频模型 | 低 | brief + style guide | 草稿符合 brief | 人工预览 / 自动质检 |
| 风格评估 | LLM-as-Judge / 风格检测器 | 低 | 草稿 + style guide | 一致性评分 | 阈值检查 |
| 迭代修改 | LLM + 用户反馈 | 低 | 草稿 + 修改指令 | 新版本满足修改 | diff 对比 + 预览 |
| 批量生成 | 管线编排 | 中 | 模板 + 参数集 | 所有输出一致 | 抽样质检 |
| 发布/交付 | API / CMS 集成 | 高 | 审批通过 | 内容上线 | 发布确认 |

## 闭环模型

### Happy Path
```text
Observe（接收 brief + 风格参考）
-> Represent（解析创意意图 + 风格规则 + 约束）
-> Decide（选择生成策略 + 模型 + 参数）
-> Act（生成草稿）
-> Verify（风格一致性 + 质量评估 + 版权检查）
-> Update（用户反馈 -> 迭代或交付）
```

### Failure + Recovery

| 失败 | 恢复 |
|---|---|
| 风格偏离 | 重新注入 style guide + 降低 temperature |
| 版权风险 | 标记 + 人工审查 + 替换素材 |
| 无限迭代 | 设置最大迭代次数 + 请求用户明确验收标准 |
| 品牌违规 | 品牌规则检测器拦截 + 重新生成 |
| 创意枯竭（输出同质化） | 增加 temperature / 切换模型 / 引入随机参考 |

### Stop Gate
```text
[ ] 用户显式接受输出 或
[ ] 达到最大迭代次数且最后版本评分 >= 阈值 或
[ ] 品牌/版权审查通过
```

### 验证方式

创意验证不能只用 postcondition。按 beyond-verification.md 的四种模式：
- Objective：版权检查、品牌规则合规（可自动化）
- Resonance：用户是否认为输出"好"（需用户反馈）
- Intersubjective：多评审者间的一致性（A/B 测试、专家评分）
- Longitudinal：长期品牌一致性（跨会话、跨月的风格追踪）

## 品类特有设计决策

| 决策 | 默认 | 升级触发器 |
|---|---|---|
| 生成模型选择 | 单模型 | 需要多模态 -> 多模型管线 |
| 风格一致性机制 | System prompt + style guide | 漂移检测失败 -> 加 fine-tuning + post-filter |
| 评估方式 | LLM-as-Judge + 人工抽检 | 高 stakes -> 全量人工审查 |
| 版权检查 | 基于规则的相似度检测 | 法律风险 -> 专业版权服务 API |
| 迭代控制 | 最大 5 轮 + 用户验收 | 无收敛 -> 请求重新定义 brief |
| 批量一致性 | 模板 + 种子控制 | 高变异 -> 抽样质检 + 风格锚定 |

## 模块配置

| 模块 | 品类特化配置 | 通用参考 |
|---|---|---|
| Representation | CreativeBrief + StyleGuide + ReferenceWork | `../../architecture/planes/representation/overview.md` |
| Context | 滚动故事上下文（rolling story context）用于多步创作 | `../../architecture/planes/context/overview.md` |
| Memory | 风格规则（长期）+ 用户偏好（会话级）+ 版本历史 | `../../architecture/planes/memory/overview.md` |
| Effects | 内容发布到 CMS/平台的效果验证 | `../../architecture/planes/effects/overview.md` |
| Interaction | 迭代对话 + 预览 + 变体选择 | `../../architecture/planes/interaction/overview.md` |
| Control | 品牌规则引擎 + 版权检测 + 安全过滤 | `../../architecture/planes/control/overview.md` |

## Eval Cases

| Case | 目标 | 必备断言 |
|---|---|---|
| 单篇文章生成 | 质量 + 风格一致性 | 品牌规则合规、无版权问题、可读性达标 |
| 批量生成 10 篇 | 批量一致性 | 风格偏差 < 阈值、品牌合规率 100% |
| 5 轮迭代精炼 | 收敛到用户满意 | 每轮有实质改进、不超过最大轮次 |
| 多模态工作流 | 图文视频一致 | 视觉风格匹配文字描述、角色一致性 |
| 版权边界测试 | 拒绝侵权请求 | 检测到侵权素材时拦截并说明 |

## Reference Implementations

| 项目 | 学习点 | 来源 |
|---|---|---|
| Sight AI 六角色管线 | Research->Outliner->Writer->SEO->Editor->Fact-Checker | trysight.ai |
| DeeVid AI 视频工作流 | Seedream 4.0 种子控制保持角色/环境一致性 | digen.ai |
| Jasper 品牌声音 | Style Guide Enforcement 确保跨团队品牌一致 | jasper.ai |
| StyleAligned | 通过注意力共享实现跨图像风格一致 | arXiv 2409.14993 |
| Adobe Firefly | Agentic AI Assistant + Generative Extend | adobe.com |
