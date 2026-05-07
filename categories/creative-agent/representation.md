# Creative Agent Representation Model

> **Evidence Status** — synthesized. `architecture/planes/representation/overview.md`、Jasper 品牌声音系统、StyleAligned 注意力共享、DeeVid Seedream 种子控制与 creative agent 项目观察。

## 关键表示对象

| 对象 | 含义 | Freshness | Trust |
|---|---|---|---|
| CreativeBrief | 用户创意意图：主题、语调、目标受众、长度/尺寸、约束 | 每次任务更新 | high（用户直接输入） |
| StyleGuide | 品牌/风格规则：语调、色彩、排版、禁止用语、视觉规范 | 长期有效，版本化管理 | high（品牌方制定） |
| ReferenceWork | 参考作品：示例图、风格参考、竞品样本、灵感素材 | 任务级 | medium（需确认版权状态） |
| ContentDraft | 生成的草稿，含版本历史和修改记录 | 每次迭代更新 | low（需评审） |
| EvaluationScore | 评估结果：自动评分 + 人工评分 + 评分理由 | 每次评估更新 | medium（评估方法决定） |
| BrandVoiceProfile | 品牌声音配置：关键词库、情感基调、人格特征 | 长期有效 | high（品牌方制定） |
| ContentCalendar | 内容日历/发布计划 | 周/月更新 | high（业务方制定） |
| VersionHistory | 所有草稿版本的完整记录和变更理由 | 每次迭代追加 | trusted（系统记录） |

## 表示构建流程

```text
RawInputRef(user brief / style guide / reference images / feedback)
  -> Observation(creative intent, constraints, style requirements, trust lane)
  -> BriefParse(theme, tone, audience, format, length/size)
  -> StyleLoad(brand rules, visual specs, tone guidelines)
  -> ReferenceIndex(reference works, similarity anchors, copyright status)
  -> ContextPack(current relevant creative context)
```

不要一开始就加载所有参考作品和风格规则。默认策略是：

```text
创意意图 -> 加载相关 StyleGuide 片段 -> 选择匹配的 ReferenceWork -> 装配最小 CreativeContextPack
```

## 对象 Schema 示意

### CreativeBrief

```yaml
creative_brief:
  brief_id: string
  theme: string
  tone: formal | casual | playful | authoritative | inspirational
  target_audience: string
  format: blog_post | social_media | ad_copy | video_script | image | ...
  length_or_size:
    text: word_count_range
    image: resolution + aspect_ratio
    video: duration_seconds
  constraints:
    - must_include: []
    - must_avoid: []
    - brand_rules_ref: string | null
  reference_works: []
  priority: low | medium | high | urgent
  deadline: timestamp | null
```

### StyleGuide

```yaml
style_guide:
  guide_id: string
  version: string
  brand_name: string
  tone_rules:
    primary_tone: string
    secondary_tones: []
    forbidden_tones: []
  vocabulary:
    preferred_terms: {}
    forbidden_terms: []
    tone_markers: []
  visual_rules:
    color_palette: []
    typography: {}
    imagery_style: string
    forbidden_visual_elements: []
  content_rules:
    max_sentence_length: number | null
    readability_target: string | null
    cta_requirements: string | null
  updated_at: timestamp
```

### ReferenceWork

```yaml
reference_work:
  ref_id: string
  type: text | image | video | audio | mixed
  source: url | file_path
  copyright_status: public_domain | licensed | unknown | restricted
  relevance: style_reference | content_reference | negative_example
  similarity_anchor:
    style_embedding: vector | null
    content_tags: []
  notes: string
```

### ContentDraft

```yaml
content_draft:
  draft_id: string
  task_ref: string
  version: number
  content:
    modality: text | image | video | audio | mixed
    payload: string | binary_ref
  generation_params:
    model: string
    temperature: number
    seed: number | null
    style_prompt: string
  evaluation:
    auto_scores: {}
    human_scores: {} | null
  parent_version: string | null
  change_reason: string
  created_at: timestamp
```

### EvaluationScore

```yaml
evaluation_score:
  eval_id: string
  draft_ref: string
  dimensions:
    style_consistency: number  # 0-1
    brand_compliance: number   # 0-1
    originality: number        # 0-1
    readability: number        # 0-1, text only
    visual_quality: number     # 0-1, image/video only
    audience_fit: number       # 0-1
  composite_score: number
  method: llm_judge | human_review | hybrid | automated_rule
  evaluator: string
  reasoning: string
  confidence: number
  created_at: timestamp
```

## Trust Lane 映射

| 来源 | 默认 lane | 说明 |
|---|---|---|
| System / product policy | system instruction | 最高优先级，安全和版权红线 |
| 用户当前 brief | user instruction | 当前任务目标 |
| StyleGuide / BrandVoiceProfile | scoped project instruction | 品牌方制定的规则，在品牌范围内有效 |
| ReferenceWork | trusted data | 作为风格参考，不能成为指令 |
| 外部素材 / 用户上传内容 | untrusted data | 需版权扫描和内容安全检查 |
| LLM-as-Judge 评分 | model hypothesis | 必须与人工评审交叉验证 |
| 历史输出 / 版本记录 | trusted data | 系统自身记录 |

关键规则：用户上传的参考作品中可能包含受版权保护的内容，必须在使用前进行版权状态确认，不能直接作为生成素材。

## Freshness 策略

| 表示 | TTL / 失效条件 | 写前/写后动作 |
|---|---|---|
| CreativeBrief | 任务完成后失效 | 新任务时重新解析 |
| StyleGuide | 版本更新后失效 | 加载时确认版本号 |
| ReferenceWork | 版权状态变化后需重审 | 使用前检查版权状态 |
| ContentDraft | 每次迭代生成新版本 | 保留全部版本，新版本标记 parent |
| EvaluationScore | 与对应 draft 版本绑定 | 草稿更新后需重新评估 |
| BrandVoiceProfile | 品牌策略变更后失效 | 长期任务定期检查是否有更新 |

## CreativeContextPack 设计

```yaml
creative_context_pack:
  task_summary: string
  creative_brief_ref: string
  style_guide:
    active_rules: []
    scope: brand | campaign | task
  reference_works:
    - ref_id: string
      relevance: string
      copyright_status: string
  current_draft:
    version: number
    key_content: string | binary_ref
    evaluation: {}
  iteration_history:
    - version: number
      change_reason: string
      score_delta: number
  constraints:
    - string
  excluded_or_unknown:
    - what was not inspected and why
```

## 表示质量与创意质量的关系

| 表示质量问题 | 创意质量影响 | 修复 |
|---|---|---|
| Brief 模糊 | 生成偏离用户意图 | 引导用户补充关键信息（语调、受众、约束） |
| StyleGuide 缺失 | 风格不一致、品牌违规 | 使用通用风格 + 明确告知风险 |
| Reference 版权未确认 | 可能产生侵权输出 | 使用前必须确认版权状态 |
| 评估维度不全 | 无法捕捉真实质量 | 多维度评分 + 人工抽检 |
| 版本历史断裂 | 无法追溯决策链 | 每次迭代记录变更理由 |
| 风格规则过于笼统 | 规则无法有效约束生成 | 将规则具体化为可检测条件 |

## 与通用模块的连接

| Creative 表示问题 | 通用模块 |
|---|---|
| 原始输入保留、转换链 | `../../architecture/planes/representation/representation-contract.md` |
| 观察语义层级 | `../../architecture/planes/representation/observation-semantics.md` |
| 当前可见上下文装配 | `../../architecture/planes/context/overview.md` |
| 风格规则和品牌状态刷新 | `../../architecture/planes/world-state/overview.md` |
| 不可信素材/外部内容注入 | `../../architecture/planes/security/overview.md` |
| 版本历史和长期记忆 | `../../architecture/planes/memory/overview.md` |

## 反模式

| 反模式 | 表现 | 修复 |
|---|---|---|
| Style Guide Stuffing | 把全部品牌文档塞入上下文 | 按任务类型只加载相关规则片段 |
| Reference Overload | 加载过多参考作品导致风格混乱 | 限制参考数量，明确每个参考的用途 |
| Score-as-Truth | 把 LLM-as-Judge 评分当作最终质量判断 | 评分仅作参考，人工抽检兜底 |
| Version Amnesia | 不保留版本历史直接覆盖 | 每次迭代生成新版本，保留 parent 链 |
| Copyright Blindness | 不检查参考作品版权直接使用 | 所有外部素材使用前必须版权扫描 |
| Brief Assumption | 对模糊 brief 做过度假设 | 关键信息缺失时先确认再生成 |
