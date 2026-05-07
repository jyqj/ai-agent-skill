# Meta Guide

> **Evidence Status** — synthesized. 知识库维护流程与结构一致性规范的归纳整理。

> 说明这个 skill 如何维护、如何新增内容，以及如何保持结构一致性。

## 目录定位

| 目录 | 回答什么 | 增长节奏 |
|---|---|---|
| `concepts/` | Agent 是什么、关键边界、认识论 | 慢 |
| `toolkit/` | 低认知负荷使用工具：选品类、定 MVA、选模块、诊断、eval | 中等 |
| `paradigms/` | 有哪些根本不同的做法、何时选哪种 | 中等 |
| `paradigms/methodology/` | 产品画布、Harness、自治/深度、MVA 阶梯 | 中等 |
| `categories/` | 某类 Agent 的完整品类架构 | 中等 |
| `architecture/` | 通用 Agent Runtime 由哪些组件构成 | 慢 |
| `design-space/` | 有哪些可复用模式、原则和反模式 | 中等 |
| `projects/` | 真实项目怎么做的 | 快 |
| `synthesis/` | 跨项目的横向比较和趋势判断 | 中等 |
| `evaluation/` | 怎么验收、怎么分类失败、怎么做回归 | 中等 |
| `index/` | 主干地图、范式地图、交叉索引和 checklist | 跟随更新 |
| `guides/` | 如何从知识到实践（端到端构建指南） | 慢 |
| `meta/` | 模板、维护规则、审计报告 | 慢 |

## 新项目学习流程

### 1. 建目录

在 `projects/<category>/<project-name>/` 下建目录。

### 2. 先写 README.md

按 `meta/templates/project-readme.md` 模板写。至少包含：
- Evidence Status
- 基本信息
- 模块覆盖
- 核心模式
- 独特贡献
- 关键发现

### 3. 放分析文件

- `<topic>.md`：长篇分析
- `<topic>.md`：带源码片段的专题分析

### 4. 沉淀设计知识

- 新做法、尚未成熟 → `design-space/frontier/`
- 被 2+ 项目验证 → `design-space/patterns/`
- 解释一大类系统 → `design-space/principles/`
- 解释一组根本不同做法 → `paradigms/`
- 改变某个品类架构 → `categories/<type>/` 或 `categories/<type>.md`

### 5. 更新关联

- 在相关 `categories/<type>/implementation-map.md` 或 `categories/<type>.md` 里补观察
- 在相关 `architecture/planes/<module>/overview.md` 底部补“参考实现”
- 更新 `index/project-module-map.md`、`index/category-module-map.md`、`index/category-pattern-matrix.md`

## 内容归属规则

| 内容性质 | 放哪 |
|---|---|
| Agent 定义、边界、认识论 | `concepts/` |
| 推理/记忆/工具/协作/控制范式比较 | `paradigms/` |
| 产品画布、自治等级、执行深度、MVA 阶梯 | `paradigms/methodology/` |
| 某类 Agent 的完整共性架构 | `categories/<type>/` |
| 某个项目的具体做法 | `projects/<category>/<project>/` |
| 可复用的具体技术（被 2+ 项目验证） | `design-space/patterns/` |
| 尚未成熟的新观察 | `design-space/frontier/` |
| 稳定的高层设计原则 | `design-space/principles/` |
| 通用运行时组件的架构说明 | `architecture/` |
| Agent 决策的可解释性设计 | `architecture/planes/explainability/` |
| 因果世界模型扩展 | `architecture/planes/world-state/causal-model.md` |
| 意图对齐与认知负载 | `architecture/planes/interaction/intent-alignment.md` |
| 运行时范式切换 | `paradigms/paradigm-routing.md` |
| Agent 经济学与 ROI | `paradigms/methodology/agent-economics.md` |
| 评估体系的元评估 | `evaluation/eval-meta/` |
| 跨项目的对比或趋势分析 | `synthesis/` |
| 评估方法或失败模式 | `evaluation/` |

## 成熟度标注

每个文档标题下方用一行引用块标注证据级别和来源：

```markdown
> **Evidence Status** — <level>. 一句话说明来源。
```

7 级体系（从高到低）：production-validated / prototype-validated / grounded / synthesized / mixed / theoretical / speculative。

例如：`> **Evidence Status** — grounded. 基于 Claude Code、Codex、OpenCode 的源码分析归纳。`

## 新增范式文档要求

使用 `meta/templates/paradigm-template.md`。每个范式文档至少包含：

- 范式定义与核心机制
- 范式间对比表
- 范式选择矩阵
- 与本框架其他层的引用关系
- 常见失败与修复
- Evidence Status

## 新增品类架构要求

使用 `meta/templates/category-architecture-template.md`。成熟品类至少包含：

- 用户模型
- 任务模型
- 表示模型
- 行动模型
- 闭环模型
- 品类特有设计决策
- 模块配置
- Eval Cases
- Reference Implementations

Coding Agent 已作为目录样板：`categories/coding-agent/`。

## 现实闭环相关内容优先落位

以下内容不要再散落在其他文件里，优先落到专门 plane：

- 输入解析、OCR / ASR / DOM / 截断 → `architecture/planes/representation/`
- 外部对象状态、TTL、refresh → `architecture/planes/world-state/`
- 写动作、postcondition、read-after-write → `architecture/planes/effects/`
- 注入、防污染、MCP 信任边界 → `architecture/planes/security/`
- 版本、回归、灰度、事故 → `architecture/planes/operations/`

## 作为 AI 助手知识库使用

推荐读取路径：

1. 先读 `SKILL.md`
2. 再读 `index/mainline-map.md` 或 `index/paradigm-map.md`
3. 需要范式选择时读 `paradigms/`
4. 需要某类 Agent 时读 `categories/`
5. 需要模块细节时读 `architecture/`
6. 需要案例时读 `projects/` README
7. 需要模式时读 `design-space/patterns/`
8. 需要横向视角时读 `synthesis/`

不要一次性全量加载。按需读取，优先沿导航表走。

## 反馈与证据升级

知识库自身也需要 effect verification。Knowledge Fitness Loop 是用于收集使用反馈、驱动 Evidence Status 升降级的闭环机制：

- **反馈机制设计**：`meta/feedback/README.md` — 为什么需要反向验证、反馈如何影响 Evidence Status、收集与分析流程。
- **反馈模板**：`meta/feedback/feedback-template.md` — 结构化反馈格式，涵盖应用场景、有用/缺失/误导内容和实际效果。
- **升降级标准**：`meta/feedback/evidence-upgrade-criteria.md` — 每个 Evidence Status 级别之间的升降级门槛和触发条件。
- **反馈报告归档**：`meta/feedback/reports/` — 按 `YYYY-MM-DD-<project-slug>.md` 格式存放。

使用者完成项目后，按模板提交反馈。维护者按季度分析反馈，判断是否变更相关文件的 Evidence Status。

## 自检

验证命令和流程见 [AGENTS.md 自检清单](../AGENTS.md#必跑自检)。
