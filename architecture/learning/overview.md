# Learning & Skill Crystallization

> **Evidence Status** — grounded. Generic Agent 的 self-evolution、VCPToolBox 的 TagMemo、memory 系统对知识沉淀的实践；this repository 对技能提炼、验证、修订追踪和退役的统一抽象。

## 定义

Learning 模块从成功任务中提炼可复用技能，从失败中改进 Harness 设计。

成熟 Learning 不是“把成功路径直接存起来”，而是：

```text
verified trace → distilled candidate → replay / second-use validation → governed activation → monitored retirement
```

## 学习类型

| 类型 | 输入 | 输出 | 持久化 |
|---|---|---|---|
| Skill Crystallization | 成功任务 trace | 可复用工具组合 / SOP / 脚本 | Skill Memory |
| Convention Learning | 项目文件 | 构建 / 测试 / 风格约定 | Project Memory |
| Failure-driven Improvement | 失败 trace | Harness 配置更新 | Hook / Policy / Eval 更新 |
| Eval Feedback | 评估结果 | 模型 / 策略 / prompt 调优 | Eval 基准更新 |
| Knowledge Distillation | 长 trace（30+ 步） | 压缩后的 skill candidate | Skill Memory |

## Skill 生命周期

Skill 不能从一次成功直接进入 active 状态。推荐状态机：

```text
verified trace
  → distilled candidate
  → replay / second-use validation
  → governed activation
  → monitored use
  → refine / deprecate / rollback
```

| 阶段 | 动作 |
|---|---|
| Candidate | 从成功执行中提炼候选技能 |
| Validate | 在 eval / replay / second use 中验证 |
| Activate | 满足阈值后允许检索使用 |
| Monitor | 追踪命中率、成功率、退化情况 |
| Deprecate | 环境变化、冲突或失效后停用 |
| Rollback | 技能导致回归时一键撤回 |

## 设计模式

| 模式 | 详见 |
|---|---|
| Skill Crystallization | `../../design-space/patterns/skill-crystallization.md` |
| Skill Governance | `skill-governance.md` |
| Knowledge Distillation | `knowledge-distillation.md` |
| Safety Guardrails | `safety-guardrails.md` |
| Incident-Driven Evolution | `incident-driven-evolution.md` |
| Online Adaptation | `online-adaptation.md` |

## 参考实现

- **Generic Agent**：Self-evolution 系统，见 `projects/general-agents/generic-agent/self-evolution.md`
- **VCPToolBox**：TagMemo 自动记忆标签算法，见 `projects/tool-platforms/vcptoolbox/tagmemo-algorithm.md`

## 关联文档

- `feedback-loops.md`
- `skill-governance.md`
- `knowledge-distillation.md`
- `safety-guardrails.md`
- `incident-driven-evolution.md`
- `online-adaptation.md`
- `../../design-space/patterns/skill-crystallization.md`
