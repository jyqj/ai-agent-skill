# Creative Agent Implementation Map

> **Evidence Status** — synthesized. Sight AI 六角色管线、DeeVid Seedream、Adobe Firefly、StyleAligned、Jasper 品牌声音系统的设计观察。

## 项目覆盖矩阵

| 设计问题 | Sight AI | DeeVid | Adobe Firefly | StyleAligned | Jasper |
|---|---|---|---|---|---|
| 内容生成 | ★★★ 六角色管线 | ★★★ Seedream 4.0 | ★★★ Generative Extend | ★★ 图像生成 | ★★★ 品牌文案 |
| 风格一致性 | ★★ 编辑角色把关 | ★★★ 种子控制 | ★★ 风格预设 | ★★★ 注意力共享 | ★★★ 品牌声音规则 |
| 多模态 | ★ 纯文本 | ★★★ 视频全流程 | ★★★ 图像+视频 | ★★ 图像组 | ★ 纯文本 |
| 品牌合规 | ★ 事实核查角色 | ★ | ★★ 内容策略 | ★ | ★★★ 品牌声音引擎 |
| 版权安全 | ★ | ★ | ★★★ 训练数据合规 | ★ | ★★ |
| 评估/质检 | ★★ Editor+Fact-Checker | ★★ 一致性检测 | ★★ 质量评估 | ★★ 风格评估 | ★★ 品牌评分 |
| 批量生产 | ★★★ 管线批量执行 | ★★ 批量视频 | ★★ 批量处理 | ★★★ 批量图像 | ★★★ 批量文案 |
| 编排/管线 | ★★★ 多角色编排 | ★★★ 视频管线 | ★★ Agent Assistant | ★ 单步 | ★★ 模板管线 |
| 记忆/学习 | ★ | ★ | ★★ 用户偏好 | ★ | ★★★ 品牌记忆 |
| 人机交互 | ★★ 对话式 | ★★ 参数控制 | ★★★ Agentic 交互 | ★ API 调用 | ★★★ 团队协作界面 |

## 品类模块 -> 项目证据

| 品类模块 | 参考项目 | 观察 |
|---|---|---|
| Representation | Jasper / Sight AI | Jasper 将品牌声音结构化为可检测规则（BrandVoiceProfile）；Sight AI 用 Research Agent 构建内容知识表示 |
| Context | Sight AI / Adobe Firefly | Sight AI 通过角色间传递上下文（Research -> Outliner -> Writer）；Adobe Firefly 用 Agentic Assistant 维护创意上下文 |
| Tools | DeeVid / Adobe Firefly | DeeVid 集成 Seedream 4.0 等生成工具；Adobe Firefly 整合图像/视频生成和编辑工具链 |
| Execution | DeeVid / Sight AI | DeeVid 的视频生成管线包含多步执行（脚本->分镜->生成->后处理）；Sight AI 的六角色串行执行 |
| Control | Jasper / Adobe Firefly | Jasper 的品牌规则引擎作为硬约束；Adobe Firefly 的内容安全和版权合规机制 |
| Style Consistency | StyleAligned / DeeVid / Jasper | StyleAligned 的注意力共享、DeeVid 的种子控制、Jasper 的品牌声音规则是三种不同的一致性机制 |
| Evaluation | Sight AI / Jasper | Sight AI 的 Editor + Fact-Checker 角色承担评估；Jasper 的品牌评分系统 |
| Effects | Adobe Firefly / Jasper | Adobe 的 Generative Extend 直接产出可发布资产；Jasper 直接对接 CMS 发布 |
| Memory | Jasper | Jasper 的品牌声音配置作为长期记忆；跨团队共享的品牌知识库 |
| Orchestration | Sight AI / DeeVid | Sight AI 的六角色管线编排；DeeVid 的视频全流程管线 |

## 参考阅读路径

### 学多 Agent 内容管线

```text
项目：Sight AI
核心模式：六角色串行管线（Research -> Outliner -> Writer -> SEO -> Editor -> Fact-Checker）
学习点：
  - 角色分工如何提升内容深度
  - 上下文在角色间如何传递和精炼
  - Editor 和 Fact-Checker 如何作为质量闭环
来源：trysight.ai
```

### 学视频/多模态一致性

```text
项目：DeeVid
核心模式：Seedream 4.0 种子控制 + 多步视频生成管线
学习点：
  - 种子控制如何保持角色/环境跨帧一致
  - 视频生成管线的分步执行（脚本->分镜->生成->后处理）
  - 一致性与多样性的平衡
来源：digen.ai
```

### 学品牌声音一致性

```text
项目：Jasper
核心模式：Brand Voice Engine + 结构化品牌规则
学习点：
  - 品牌声音如何结构化为可检测规则
  - 跨团队品牌一致性的技术实现
  - 品牌记忆和长期维护
来源：jasper.ai
```

### 学视觉风格一致性

```text
项目：StyleAligned
核心模式：注意力共享实现跨图像风格一致
学习点：
  - 通过共享 attention key/value 实现风格统一
  - 在一致性和多样性之间的控制
  - 批量图像生成的风格锚定
来源：arXiv 2409.14993
```

### 学 Agentic 创意助手

```text
项目：Adobe Firefly
核心模式：Agentic AI Assistant + Generative Extend
学习点：
  - 生成式 AI 如何嵌入专业创作工具
  - 内容安全和版权合规的产品化实践
  - 人机协作的交互模式
来源：adobe.com
```

## 知识库 Plane -> 实现映射

| Plane | 关键问题 | 参考实现 |
|---|---|---|
| Representation | 创意意图和风格规则如何结构化？ | Jasper BrandVoiceProfile、Sight AI Research 输出 |
| Context | 长创作流程中如何保持上下文？ | Sight AI 角色间上下文传递、Adobe Firefly 会话上下文 |
| Memory | 品牌规则和风格偏好如何持久化？ | Jasper 品牌记忆、StyleGuide 版本化 |
| Tools | 生成、评估、发布需要哪些工具？ | DeeVid Seedream、Adobe Firefly 工具链 |
| Execution | 多步生成管线如何执行？ | Sight AI 六角色串行、DeeVid 视频管线 |
| Effects | 如何验证发布效果？ | Jasper CMS 集成、Adobe 资产发布 |
| Control | 品牌规则和版权如何作为硬约束？ | Jasper 品牌规则引擎、Adobe 版权机制 |
| Interaction | 如何支持迭代式人机协作？ | Adobe Firefly Agentic 交互、Jasper 团队界面 |
| Orchestration | 多角色/多模态如何编排？ | Sight AI 六角色编排、DeeVid 视频管线 |
| World State | 品牌规则和市场趋势如何刷新？ | Jasper 品牌配置更新、Sight AI Research Agent |
| Security | 版权和内容安全如何保障？ | Adobe 训练数据合规、版权检测管线 |
| Operations | 生产环境如何监控和运维？ | Jasper 品牌评分仪表盘、批量质检报告 |

## 实现对比结论

| 结论 | 含义 |
|---|---|
| 多 Agent 角色管线提升内容深度但增加编排复杂度 | Sight AI 的六角色管线适合深度内容，简单任务不必全部启用 |
| 风格一致性有多种机制，需按场景选择 | 文本用品牌规则引擎（Jasper），图像用注意力共享（StyleAligned），视频用种子控制（DeeVid） |
| 品牌规则必须具体到可检测 | "专业但友好" 不够，需要拆解为禁止用语、句式偏好、情感基调等可度量维度 |
| 版权合规需要多层防线 | 生成时约束 + 生成后检测 + 发布前审查，Adobe 的做法最系统化 |
| 评估是创意 Agent 的核心难点 | 客观指标（格式、版权）容易自动化，风格和质量需要 LLM-as-Judge + 人工混合 |
| 长期一致性需要 Memory + Longitudinal Verification | 仅靠 prompt 注入无法保证跨月一致，需要持久化品牌记忆和定期审计 |
| 批量生产的一致性和多样性是一对矛盾 | 种子控制和模板保证一致，但容易同质化；需要在两者间找平衡点 |
| Agentic 交互是趋势 | Adobe Firefly 的 Agentic Assistant 表明创意工具正在从"工具"演化为"协作者" |

## 待补证据

- Sight AI 六角色管线的具体上下文传递协议和 OutputContract 设计。
- DeeVid Seedream 种子控制在复杂场景（多角色、场景切换）中的一致性极限。
- Jasper 品牌声音引擎的具体规则引擎架构和评分算法。
- StyleAligned 注意力共享在生产环境中的性能和可扩展性。
- Adobe Firefly 的版权合规机制的具体技术实现。
- 不同评估方法（LLM-as-Judge vs 人工 vs A/B）在创意任务中的一致性对比数据。
- 长期品牌维护中"有意演化"与"无意漂移"的区分机制。
