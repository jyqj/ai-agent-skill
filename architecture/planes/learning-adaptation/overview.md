# Learning & Adaptation Plane
>
> **所属域**：8. Reflection & Learning — 经验学习与技能治理
>
> **Evidence Status** — synthesized. 长期运行 Agent 会从 trace、用户纠错、eval regression、项目约定和失败恢复中沉淀经验；本文件将这些经验固化为可验证、可撤销、可审计的运行时改进，而不是把”模型学到了”当成黑箱。

**Principle Refs**: BDI-01, MC-02 — 学习即从运行观察中构建信念；自监控发现偏差时触发适应性调整

## 定义

Learning & Adaptation Plane 负责把运行经验转化为可复用的策略、技能、记忆、测试和配置变更。它强调三件事：

1. 只从有证据的运行中学习；
2. 学到的内容先进入候选区，经过验证后再可被召回；
3. 失效、冲突或有害的学习结果必须能降权、隔离或退役。

```text
Trace / user correction / eval failure
  → candidate extraction
  → evidence and safety validation
  → activation under scope
  → monitored reuse
  → deactivation or refinement when evidence changes
```

## 可学习对象

| 对象 | 示例 | 必须验证什么 |
|---|---|---|
| Project Convention | 构建命令、测试入口、代码风格 | 是否来自可信项目文件或成功 trace |
| Tool Recipe | “先搜索再读取再编辑”的工具链 | 是否可 replay，是否有 postcondition |
| Prompt Fragment | 某类任务的输出格式或检查清单 | 是否提升 eval，而非只更像模板 |
| Recovery Strategy | 某工具超时后的替代路径 | 是否减少失败，不引入更高风险 |
| Memory Entry | 用户偏好、长期事实、关系背景 | 是否有 provenance、scope、失效条件 |
| Eval Fixture | 从失败 trace 提炼的回归用例 | 是否能稳定复现关键风险 |

## CandidateRecord Schema

```yaml
candidate_record:
  candidate_id: string
  source: trace | user_correction | eval_failure | project_file | human_review
  scope: global | tenant | project | user | task_type
  content_type: convention | tool_recipe | prompt_fragment | recovery_strategy | memory | eval_fixture
  evidence_refs: []
  preconditions: []
  validation_required: []
  safety_checks: []
  activation_state: candidate | active | quarantined | retired
  invalidation_triggers: []
  last_validation_evidence: []
```

## 学习边界

| 不应学习 | 原因 | 替代做法 |
|---|---|---|
| 一次性外部状态 | 很快过期 | WorldStateSnapshot + TTL |
| 未验证的模型推断 | 容易固化幻觉 | 先进入 hypothesis，不激活 |
| 含 secret / PII 的 trace | 隐私和安全风险 | redact 后只保留结构化经验 |
| 越权但成功的路径 | 会固化安全绕过 | 标记为 anti-pattern fixture |
| 只在单一环境偶然有效的命令 | 过拟合 | 写入 preconditions 和 scope |

## 触发器

| 触发器 | 动作 |
|---|---|
| 同一失败重复出现 | 生成 recovery strategy 候选 + eval fixture |
| 用户纠正同一偏好多次 | 生成 scoped memory 候选 |
| 工具链多次成功 | 生成 tool recipe 候选 |
| 项目配置改变 | 使相关 convention 候选重新验证 |
| eval 退化 | 暂停相关候选召回，进入诊断 |

## 与 architecture/learning 的关系

`architecture/learning/` 是学习机制的专题库；本 plane 是运行时入口，说明学习如何接入 State、Memory、Evaluation、Operations 和 Security。

相关文件：`../../learning/overview.md`、`../../learning/knowledge-distillation.md`、`../../learning/skill-governance.md`、`../../learning/safety-guardrails.md`、`../../../design-space/patterns/skill-crystallization.md`。
