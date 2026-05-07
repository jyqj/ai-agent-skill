# Toolkit

> **Evidence Status** — synthesized. 为降低开发者和 AI 使用本 skill 的认知负荷而设置的操作层 facade；它不替代深层知识库，只负责把问题路由到最少必要文件。

## 设计原则

每个工具页只回答一个问题，并给出：

```text
30 秒判断 → 最小产出 → 何时升级 → 3 个以内深入入口
```

## 工具列表

| 工具 | 用途 |
|---|---|
| `choose-agent-type.md` | 快速选择 Agent 品类 |
| `mva-planner.md` | 规划第一个可交付版本 |
| `module-picker.md` | 从 5 域 / 25 plane 中选最小模块集 |
| `risk-depth-calculator.md` | 按风险和执行深度决定复杂度 |
| `failure-router.md` | 从症状定位架构边界与修复入口 |
| `pattern-picker.md` | 从场景选择 pattern 与反模式 |
| `eval-planner.md` | 把设计转成验收和回归 |
| `review-checklist.md` | 做轻量架构 review |

## 推荐顺序

```text
choose-agent-type → mva-planner → module-picker → risk-depth-calculator
                 → pattern-picker → eval-planner → review-checklist
```

如果是已有系统出问题，直接从 `failure-router.md` 开始。
