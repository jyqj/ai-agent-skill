# Start Here — Agent Development Reference Kit

> **Evidence Status** — synthesized. 面向开发者和 AI 使用本 skill 的低认知负荷入口；把既有知识库重新包装为工具包、路由表和按需展开的参考系统。

## 这个 skill 是什么

它不是需要从头读完的教材，也不是生产框架。它是 Agent 开发过程中的**工具包与参照物**：当你需要做产品决策、模块装配、故障诊断、模式选择、评估设计或架构 review 时，用它快速定位该看什么、该避免什么、下一步产出什么。

```text
Agent Development Reference Kit
= 决策地图 + 架构模式库 + 品类蓝图 + 评审清单 + 参考项目索引 + 评估模板
```

## 先不要做什么

- 不要从 25 个 plane 开始设计；25 plane 是审计底盘，不是起步菜单。
- 不要默认把所有 pattern 都套上；先用 MVA 控制复杂度。
- 不要因为某个模式没有生产验证就丢弃；本 skill 的定位是开发参照物，`conceptual / project-observed / simulated-eval` 也有设计价值。
- 不要把 starter-kit 当生产代码；它只演示架构对象如何衔接。

## 8 个入口

| 你现在要做什么 | 先读 | 产出 |
|---|---|---|
| 快速判断做哪类 Agent | `toolkit/choose-agent-type.md` | 品类、默认深度、首选蓝图 |
| 规划第一个可用版本 | `toolkit/mva-planner.md` | MVA 级别、最小闭环、升级触发器 |
| 选择该启用哪些模块 | `toolkit/module-picker.md` | 必选 / 可选 / 暂缓 plane set |
| Agent 已经出问题 | `toolkit/failure-router.md` | 症状 → 可能边界 → 修复入口 |
| 找可复用做法 | `toolkit/pattern-picker.md` | 场景 → pattern → 反模式 |
| 对照真实项目 | `index/project-module-map.md` | 模块 → 参考项目 → 学习点 |
| 设计验收与回归 | `toolkit/eval-planner.md` | eval case、fixture、trace 要求 |
| 做最终架构评审 | `toolkit/review-checklist.md` | 精简 review checklist 与深入链接 |

## 开发者最短流程

```text
1. choose-agent-type     选品类
2. mva-planner           定最小版本
3. module-picker         选模块，不选模块也要说明
4. pattern-picker        只挑当前风险触发的模式
5. eval-planner          定义 done / verified / blocked
6. review-checklist      交付前查漏
```

## AI 使用最短流程

如果你是 AI，不要一次性读完整仓库。先读：

```text
index/ai-routing-pack.md
```

它会告诉你不同用户意图该读取哪些最少文件，以及哪些层默认不要展开。

## 深入层仍然保留

| 层 | 作用 | 入口 |
|---|---|---|
| 品类蓝图 | 某类 Agent 的对象、动作、闭环、eval | `categories/README.md` |
| 架构底盘 | 25 plane、数据流、边界矩阵 | `architecture/README.md` |
| 模式库 | 可复用做法与反模式 | `design-space/patterns/README.md` |
| 项目证据 | 真实项目如何做 | `projects/README.md` |
| 评估体系 | fixture、trace、failure taxonomy | `evaluation/README.md` |
| 哲学解释 | 为什么这些边界必须存在 | `concepts/foundations/README.md` |

## 证据使用态度

本 skill 不要求所有内容都有生产验证。阅读时按用途判断：

| 证据形态 | 可以怎么用 |
|---|---|
| conceptual / theoretical | 用作思考框架，不能当实现规范 |
| synthesized | 用作架构草案和 checklist，需要结合场景裁剪 |
| grounded / project-observed | 可作为参考实现线索，但要检查上下文差异 |
| simulated-eval | 可作为测试思路，不代表真实 Agent 能力 |
| prototype / production validated | 可作为强参考，但仍需按你的产品约束复核 |
