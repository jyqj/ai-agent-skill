# Creative Agent Action Model

> **Evidence Status** — synthesized. `architecture/planes/tools/overview.md`、`architecture/planes/execution/overview.md`、`architecture/planes/effects/overview.md` 与 creative agent 参考项目（Sight AI 六角色管线、DeeVid、Adobe Firefly、Jasper）的工具系统。

## 动作分类

| 类别 | 动作 | 典型工具 | 默认风险 |
|---|---|---|---|
| Read | 加载 brief、读取 StyleGuide、检索参考作品 | 文件系统/数据库/API | safe |
| Analyze | 解析创意意图、风格分析、受众分析、竞品分析 | LLM/分析模型 | safe |
| Generate | 生成文本/图像/视频/音频草稿 | LLM/扩散模型/视频模型 | check |
| Evaluate | 风格一致性评估、质量评分、品牌合规检测 | LLM-as-Judge/风格检测器 | safe |
| Refine | 基于反馈修改草稿、风格调整、局部重生成 | LLM/图像编辑模型 | check |
| Copyright Check | 版权相似度检测、素材来源验证 | 相似度检索/版权服务 API | safe |
| Brand Check | 品牌规则合规检测、禁止用语扫描 | 规则引擎/LLM 检测器 | safe |
| Publish | 发布到 CMS/平台、交付最终文件 | CMS API/文件系统 | high |
| Batch Orchestrate | 批量任务分发、进度追踪、结果聚合 | 管线编排器 | check |

## 工具风险策略

| 操作 | 默认策略 | 说明 |
|---|---|---|
| read/search/analyze | allow | 只读且低风险 |
| generate draft | allow with review | 生成结果需评估后才能进入下一步 |
| evaluate/score | allow | 评估不修改内容 |
| refine/edit | allow with diff tracking | 修改需记录版本历史 |
| copyright check | allow | 安全检查动作 |
| brand check | allow | 合规检查动作 |
| batch generate | allow with sampling QA | 批量操作需抽样质检 |
| publish/deliver | ask/explicit approval | 对外发布，影响不可撤回 |
| use copyrighted reference | deny unless licensed | 版权保护红线 |
| override brand rules | deny/explicit approval | 品牌规则不可随意突破 |

## Action Contract

每个生成/修改动作都要显式化：

```yaml
action:
  action_id: string
  tool_id: generate_text | generate_image | refine_draft | publish
  target:
    draft_id: string
    modality: text | image | video | audio
  preconditions:
    - brief_parsed_and_validated
    - style_guide_loaded
    - copyright_status_of_references_confirmed
  intended_effect: "generate brand-compliant blog post draft"
  postconditions:
    - draft_exists_in_version_history
    - style_consistency_score >= threshold
    - no_copyright_flags
  verification_method:
    - style_consistency_check
    - brand_compliance_scan
    - copyright_similarity_scan
    - user_preview
  rollback:
    - revert to previous draft version
```

## 动作详解

### Read 动作

| 动作 | 工具 | Preconditions | Postconditions | 风险 |
|---|---|---|---|---|
| 加载 CreativeBrief | 文件/API 读取 | brief 存在 | brief 解析为结构化对象 | safe |
| 读取 StyleGuide | 文件/数据库 | guide 版本已确认 | 规则加载到上下文 | safe |
| 检索参考作品 | 搜索引擎/素材库 | 搜索查询已构建 | 参考列表 + 版权状态 | safe |
| 读取版本历史 | 版本存储 | draft_id 存在 | 历史版本可对比 | safe |

### Generate 动作

| 动作 | 工具 | Preconditions | Postconditions | 风险 |
|---|---|---|---|---|
| 生成文本初稿 | LLM | brief + style guide 已加载 | 草稿符合 brief 主题 | check |
| 生成图像 | 扩散模型 | brief + visual rules 已加载 | 图像符合尺寸/风格要求 | check |
| 生成视频片段 | 视频模型 | 脚本 + 分镜 + 素材就绪 | 视频符合时长/分辨率 | check |
| 生成音频/旁白 | TTS/音乐模型 | 文本/曲风要求已确认 | 音频符合时长/风格 | check |
| 批量生成 | 管线编排 | 模板 + 参数集 + 种子策略 | 所有输出存在且可检索 | check |

### Evaluate 动作

| 动作 | 工具 | Preconditions | Postconditions | 风险 |
|---|---|---|---|---|
| 风格一致性评估 | LLM-as-Judge / 风格检测器 | 草稿 + StyleGuide 已加载 | 一致性评分 + 偏离说明 | safe |
| 品牌合规检测 | 规则引擎 / LLM 检测器 | 草稿 + BrandVoiceProfile | 合规/不合规 + 违规详情 | safe |
| 质量评分 | LLM-as-Judge | 草稿 + 评分维度定义 | 多维度评分 + 理由 | safe |
| 版权相似度检测 | 相似度检索 / 版权 API | 草稿内容 | 相似度报告 + 风险等级 | safe |
| 人工评审请求 | 工单/通知系统 | 草稿准备就绪 | 人工评分记录 | safe |

### Refine 动作

| 动作 | 工具 | Preconditions | Postconditions | 风险 |
|---|---|---|---|---|
| 基于反馈修改文本 | LLM | 当前草稿 + 修改指令 | 新版本仅修改指定内容 | check |
| 风格调整 | LLM + 风格参数 | 偏离诊断 + 调整方向 | 一致性评分提升 | check |
| 局部重生成（图像） | 图像编辑/inpainting | 原图 + 修改区域 + 指令 | 修改区域更新，其余不变 | check |
| 格式/排版调整 | 格式工具 | 内容 + 格式规范 | 符合格式要求 | safe |

### 特殊动作：版权检查

```yaml
action:
  action_id: copyright_check_001
  tool_id: copyright_scanner
  trigger: before_publish | after_generate_with_external_reference
  target:
    content: draft content or generated asset
  preconditions:
    - content_exists
  checks:
    - text_similarity_against_known_works
    - image_reverse_search
    - audio_fingerprint_match
  risk_thresholds:
    high_risk: similarity > 0.85
    medium_risk: similarity > 0.60
    low_risk: similarity <= 0.60
  on_high_risk: block + flag for human review
  on_medium_risk: warn + suggest modification
  on_low_risk: pass
  postconditions:
    - copyright_report_generated
    - high_risk_items_blocked
```

### 特殊动作：品牌合规检查

```yaml
action:
  action_id: brand_compliance_001
  tool_id: brand_rule_engine
  trigger: after_generate | after_refine
  target:
    content: draft content
    brand_profile: BrandVoiceProfile
  checks:
    - forbidden_terms_scan
    - tone_alignment_score
    - visual_palette_compliance
    - messaging_consistency
  on_violation:
    severity_critical: block + auto-fix attempt + human review
    severity_warning: warn + suggest fix
    severity_info: log only
  postconditions:
    - compliance_report_generated
    - critical_violations_resolved_or_escalated
```

## Happy Path 工具链

```text
load brief + style guide
  -> analyze creative intent
  -> select generation strategy + model + params
  -> generate draft
  -> evaluate (style + brand + copyright)
  -> if pass: user preview
  -> if user accepts: publish/deliver
  -> if user requests changes: refine -> re-evaluate -> loop
```

## Failure Recovery

| 失败 | 立即动作 | 不要做 |
|---|---|---|
| 生成质量不足 | 调整参数（temperature、prompt）重新生成 | 直接发布低质量输出 |
| 风格偏离 | 重新注入 style guide + 降低随机性 | 忽略偏离继续迭代 |
| 版权风险检出 | 标记 + 替换素材 + 人工审查 | 绕过版权检查 |
| 品牌违规 | 自动修复尝试 + 人工审查 | 覆盖品牌规则 |
| 模型不可用 | 降级到备选模型 + 通知用户质量可能下降 | 静默降级不告知 |
| 批量中途失败 | 保存已完成结果 + 从断点恢复 | 整批重新开始 |
| 迭代不收敛 | 请求用户重新定义 brief | 无限循环 |

## Effect Ledger for Creative Content

```yaml
effect_record:
  effect_id: string
  target_system: cms | social_platform | file_storage | design_tool
  content_refs:
    - draft://content_draft_v3
    - asset://hero_image_v2
  intended_effect: "publish brand-compliant blog post with hero image"
  tool_calls:
    - generate_text: ...
    - generate_image: ...
    - brand_check: ...
    - copyright_check: ...
    - publish: ...
  actual_observation:
    style_score: 0.92
    brand_compliance: pass
    copyright_status: clear
    publish_status: live
    url: string
  verification_status: verified | failed | partial | unverified
  remaining_risks:
    - long-term style drift not yet assessed
    - A/B performance data pending
```

## 并发策略

| 并发类型 | 默认 |
|---|---|
| 多参考作品检索 | 可并行 |
| 多维度评估（风格/品牌/版权） | 可并行 |
| 同一草稿的修改 | 串行 |
| 批量生成不同内容 | 可并行，但需一致性抽检 |
| 多模态生成（文本 + 图像） | 可并行（如果无依赖），有依赖时串行 |
| 发布操作 | 串行 + 审批 |

## 相关通用模块

- Tool Spec：`../../architecture/planes/tools/overview.md`
- Execution Host：`../../architecture/planes/execution/overview.md`
- Control Policy：`../../architecture/planes/control/overview.md`
- Effect Verification：`../../architecture/planes/effects/overview.md`
- Concurrency：`../../architecture/planes/concurrency/overview.md`
