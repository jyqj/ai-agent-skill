# Mainline Map

> **Evidence Status** — synthesized. 给这套 skill 一条稳定主干，避免读者在概念、范式、品类、模块、项目之间跳跃断层。


## 主干层级

| 层级 | 问题 | 主入口 | 产出 |
|---|---|---|---|
| L0 哲学基础 | 为什么 Agent 架构必须是这样？ | `../concepts/foundations/` | 有界理性、意向立场、BDI、元认知、价值对齐、具身认知 |
| L1 本体论 | Agent 是什么？边界是什么？ | `../concepts/` | 概念、边界、认识论、超越验证 |
| L1.5 认知架构 | Agent 的认知应该如何组织？ | `../cognitive-architecture/` | 工作记忆、目标层级、推理模式、心智理论、元认知控制 |
| L2 范式论 | 有哪些根本不同的做法？ | `../paradigms/` | 选择矩阵和方法论 |
| L3 品类架构 | 某类 Agent 的完整设计？ | `../categories/` | 任务、表示、行动、闭环、eval |
| L4 运行时 | 模块如何设计、交互、流转？ | `../architecture/` | 9 域 25 plane、多模型架构、演化机制 |
| L5 证据与评估 | 真实项目怎么做？怎么验收？ | `../projects/` + `../evaluation/` | 项目证据、评估框架、主观性评估 |
| 横切 设计空间 | 可复用模式/反模式/经验教训/前沿观察？ | `../design-space/` | patterns / anti-patterns / lessons-learned / frontier |
| 横切 综合 | 跨项目与跨框架趋势？ | `../synthesis/` | 对比分析 |
| 横切 索引 | 快速导航和成熟度对照？ | `../index/` | 意图导航 / 成熟度阶梯 / checklist |
| 横切 实践指南 | 如何从知识到实践？ | `../guides/` | 端到端构建指南 |
| 横切 参考骨架 | 如何映射到参考代码？ | `../starter-kit/` | reference-only starter kits |

## 层级关系

```text
L0  concepts/foundations/       为什么必须这样（哲学根基）
     ↓
L1  concepts/                   Agent 是什么（本体论 + 认识论）
     ↓
L1.5 cognitive-architecture/    认知如何组织（认知科学 → 工程）
     ↓
L2  paradigms/                  用什么做法（范式选择）
     ↓
L3  categories/                 某类 Agent 怎么设计（品类架构）
     ↓
L4  architecture/               模块怎么实现（运行时 9 域 25 plane）
     ├── planes/                各域各 plane 的深入设计
     ├── multi-model/           多模型异构架构
     └── evolution/             长期演化机制
     ↓
L5  projects/ + evaluation/     真实证据 + 验收回归
```

## 推荐阅读路线

### 从零设计 Agent

```text
concepts/foundations/bounded-rationality.md（可选：理解为什么需要 Harness）
  → concepts/what-is-agent.md
  → concepts/representation-and-effects.md
  → cognitive-architecture/goal-hierarchy.md（可选：理解目标分解）
  → design-space/methodology/agent-product-model.md
  → design-space/methodology/autonomy-and-depth.md
  → paradigms/decision-trees.md
  → paradigms/<relevant>-paradigms.md
  → categories/<type>/README.md
  → architecture/complexity-levels.md
  → index/maturity-ladders.md（对照 4 套阶梯）
  → architecture/reference-topologies.md
  → architecture/plane-interaction-matrix.md
  → index/design-checklist.md
  → starter-kit/README.md（可选参考代码映射）
```

### 深入某个模块

```text
architecture/planes/<module>/overview.md（注意顶部的"所属域"标注）
  → architecture/planes/<module>/*.md（深入文件：如 prompting/ 的 instruction-layering、reasoning-mode-selection、prompt-security）
  → architecture/plane-interaction-matrix.md
  → architecture/runtime-data-flow.md
  → paradigms/<related>-paradigms.md
  → cognitive-architecture/<related>.md（可选：认知层解释，含桥接文件 cognitive-to-plane-mapping）
  → design-space/patterns/<pattern>.md
  → design-space/frontier/<topic>.md
  → projects/<category>/<project>/README.md
```

### 设计多模型 Agent

```text
architecture/multi-model/README.md
  → architecture/multi-model/model-role-allocation.md
  → architecture/multi-model/confidence-aggregation.md
  → architecture/multi-model/world-models.md（如需世界模型）
  → architecture/multi-model/neuro-symbolic-hybrid.md（如需符号推理）
  → architecture/planes/cost/model-routing.md（成本维度）
```

### 设计非工程类 Agent（Companion / Creative）

```text
concepts/beyond-verification.md
  → evaluation/subjective-eval.md
  → categories/companion-agent/README.md（或其他品类）
  → concepts/foundations/value-and-alignment.md
  → architecture/evolution/value-drift.md
```

### 跟着指南构建 Agent

```text
guides/README.md（了解指南定位和目录关系）
  → guides/build-research-agent.md（端到端构建 Research Agent）
  → 指南中交叉引用的知识库文件（按需深入）
  → index/design-checklist.md（最终 review）
```

### 从项目沉淀知识

```text
projects/<category>/<project>/README.md
  → architecture/planes/<module>/overview.md
  → categories/<type>/implementation-map.md
  → design-space/patterns/ or frontier/
  → design-space/lessons-learned/（已知失败的设计教训）
  → index/project-module-map.md
```

### 理解哲学层

```text
concepts/foundations/bounded-rationality.md
  → concepts/foundations/intentional-stance.md
  → concepts/foundations/bdi-and-active-inference.md
  → concepts/foundations/metacognition.md
  → concepts/foundations/value-and-alignment.md
  → concepts/foundations/embodiment-and-situation.md
```

## 成熟度阶梯速查

知识库中有 4 套阶梯体系，统一映射见 `maturity-ladders.md`：

| 阶梯 | 维度 | 使用场景 |
|---|---|---|
| C0-C6 | 架构复杂度 | 架构决策：启用哪些 plane |
| D0-D6 | 执行深度 | 任务分析：Agent 执行到多深 |
| MVA-0 到 MVA-6 | 构建起点 | 项目启动：从哪里开始 |
| Autonomy Level L0-L5 | 自主权 | 产品定位：Agent 有多大自由 |
