# Toolkit

> **Evidence Status** — synthesized. 操作层；从主干知识压缩成构建、诊断、升级和评审入口。

本目录是知识库的操作入口层，详见 [SKILL.md](../SKILL.md)。

## 使用流程

```text
你要做什么？
│
├─ 构建新 Agent ──→ choose-agent-type → mva-planner → module-picker → eval-planner → review-checklist
│
├─ 诊断已有 Agent ──→ failure-router → 命中的 plane overview → pattern 或 anti-pattern
│
├─ 升级已有 Agent ──→ upgrade-planner → module-picker → pattern-migration
│
└─ 做架构评审 ──→ review-checklist → ../index/design-checklist.md
```

## 工具列表

| 工具 | 用途 |
|---|---|
| `choose-agent-type.md` | 选择 Agent 品类（30 秒决策） |
| `mva-planner.md` | 定最小版本 + 判断风险与深度 |
| `module-picker.md` | 从 5 域 / 25 plane 中选最小模块集 |
| `failure-router.md` | 从症状定位架构边界与修复入口 |
| `eval-planner.md` | 把设计转成验收和回归 |
| `review-checklist.md` | 做轻量架构 review |
| `upgrade-planner.md` | 从当前 MVA 级别规划增量升级路径 |
| `pattern-migration.md` | 已有系统渐进引入 pattern 的迁移指南 |

## 设计原则

每个工具只回答一个问题，给出：30 秒判断 → 最小产出 → 3 个以内的深入入口。

选择设计模式不需要单独的工具——用 `../index/category-pattern-matrix.md` 从品类出发选择，或用 `../design-space/patterns/README.md` 按场景浏览。
