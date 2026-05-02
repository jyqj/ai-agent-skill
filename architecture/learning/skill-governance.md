# Skill Governance & Conflict Detection

> **Evidence Status** — grounded. Generic Agent self-evolution 会产生多个竞争 skill；Claude Code / coding-agent 类项目在项目迁移后会出现旧 skill 失效但仍被命中的问题。长期技能库需要作用域、证据、冲突检测、失效和退役机制。

## 为什么需要治理

Skill 库不是静态知识库。项目依赖会升级，API 会改变，用户偏好会修正，组织策略会收紧。同一任务也可能沉淀出多个互相竞争的 skill。

没有治理，skill 库会逐渐退化为“看起来很多、但命中率越来越低”的状态。

## Skill Governance Schema

```yaml
skill_record:
  skill_id: string
  title: string
  scope:
    project: string|null
    domain: coding | research | workflow | memory | ops | browser | platform
    valid_context: []
  content:
    preconditions: []
    steps: []
    tools_required: []
    verification: []
    known_failures: []
    do_not_use_when: []
  evidence:
    successful_runs: []
    failed_runs: []
    replay_refs: []
    human_review_refs: []
  quality:
    success_rate: number
    last_validated_at: datetime|null
    confidence: number
  governance:
    status: candidate | active | quarantined | deprecated | retired
    invalidation_triggers: []
    conflict_refs: []
    retirement_reason: string|null
```

## 冲突检测

| 冲突类型 | 示例 | 处理 |
|---|---|---|
| Scope overlap | 两个 skill 都声称适用于同一项目同一任务 | 通过 precondition 拆分作用域 |
| Tool conflict | 一个 skill 要用 npm，一个要用 pnpm | 读取项目事实，按 Evidence 选择 |
| Policy conflict | skill 建议 `--force`，policy 禁止 | policy 优先，skill 降权或隔离 |
| Verification conflict | skill A 只跑 lint，skill B 要跑 test | 高风险任务选择更强验证 |
| Outcome conflict | 两个 skill 在 eval 中成功率相反 | 保留 evidence，触发人工审核 |

## 召回排序

召回不应只看相似度。推荐排序：

```text
match_score = semantic_match
            × scope_fit
            × evidence_strength
            × recency_of_validation
            × policy_compatibility
            × failure_penalty
```

不要让“最近被写入”成为主要排序依据。最新不等于可靠。

## 失效触发器

```yaml
invalidation_triggers:
  - project_config_changed
  - dependency_changed
  - tool_schema_changed
  - policy_changed
  - eval_regression
  - repeated_runtime_failure
  - user_correction
  - security_finding
```

触发后不应立即删除 skill，而是进入 `quarantined` 或 `deprecated` 状态，等待 replay、修订或退役。

## 治理流程

```text
crystallization → candidate → validate → active
                              ↓
                     conflict / failure / policy change
                              ↓
                    quarantined → refine → validate
                              ↓
                         deprecated / retired
```

## 审计与回放

每次 skill 被召回时记录：

```yaml
skill_use_event:
  skill_id: string
  task_id: string
  match_reason: string
  preconditions_checked: []
  policy_verdict: allow | ask | deny
  result: success | partial | failed | blocked
  evidence_refs: []
```

## 关联文档

- `overview.md` — 学习模块总览
- `knowledge-distillation.md` — 从长 trace 提炼候选 skill
- `safety-guardrails.md` — 有害 skill 的写入防护
- `../../design-space/patterns/skill-crystallization.md` — 固化模式
