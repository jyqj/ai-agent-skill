# Developer Reading Path

> **Evidence Status** — synthesized. 面向开发者的渐进阅读路径；目标是在不读完整知识库的情况下完成一次 Agent 设计、实现或评审。

## 10 分钟：能开始设计

```text
START-HERE.md
→ toolkit/choose-agent-type.md
→ toolkit/mva-planner.md
→ toolkit/module-picker.md
```

产出：

```yaml
agent_type: ""
mva_level: ""
required_modules: []
deferred_modules: []
```

## 30 分钟：能写架构草案

```text
toolkit/risk-depth-calculator.md
→ categories/<type>/README.md
→ toolkit/pattern-picker.md
→ toolkit/eval-planner.md
```

产出：

```yaml
required_depth: ""
key_patterns: []
verification_plan: []
risk_controls: []
```

## 90 分钟：能做完整 review

```text
index/design-checklist.md
→ architecture/plane-interaction-matrix.md
→ synthesis/local-reference-systems-reflection.md
→ index/project-module-map.md
```

产出：

```yaml
architecture_review:
  must_fix: []
  should_fix: []
  intentionally_deferred: []
  reference_projects: []
```

## 按角色选择路径

| 角色 | 只读这些 |
|---|---|
| 产品/架构负责人 | `START-HERE.md`, `toolkit/choose-agent-type.md`, `toolkit/risk-depth-calculator.md`, `index/design-checklist.md` |
| 工程实现者 | `toolkit/module-picker.md`, 对应 category, 相关 plane overview, `starter-kit/README.md` |
| 评估负责人 | `toolkit/eval-planner.md`, `evaluation/eval-framework.md`, `evaluation/fixtures/README.md` |
| AI 助手 | `index/ai-routing-pack.md` |
| 知识库维护者 | `meta/guide.md`, `scripts/validate_skill.py`, `meta/feedback/README.md` |

## 不要读全仓的情况

- 只是做 MVA-1/MVA-2 原型；
- 只是需要一个设计建议；
- 只是排查一个明确失败症状；
- 只是查某个 pattern。

这些场景优先走 `../toolkit/`。
