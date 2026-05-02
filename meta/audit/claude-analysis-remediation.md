# Claude Analysis Remediation Report

> **Evidence Status** — synthesized. 记录本轮根据外部结构分析对 skill 进行的优化，便于后续继续迭代。


## 修复摘要

| 发现的问题 | 本轮修复 | 主要文件 |
|---|---|---|
| 第 2 层范式论缺失 | 新增 `paradigms/`，覆盖推理、记忆、工具、协作、控制和方法论 | `paradigms/README.md`、`paradigms/*-paradigms.md` |
| `categories/` 只有配方清单 | 将 Coding Agent 升级为完整品类架构样板 | `categories/coding-agent/` |
| `concepts/` 混杂本体论和方法论 | 新增 `concepts/README.md` 明确边界，并将方法论主入口迁至 `paradigms/methodology/` | `concepts/README.md`、`paradigms/methodology/` |
| 通用模块与品类特化断开 | Coding Agent 文档显式引用 architecture planes，并给出品类特化配置 | `categories/coding-agent/README.md`、`representation.md`、`action-model.md` |
| projects 与 categories 连接弱 | 新增实现映射，把品类模块映射到 Claude Code/Codex/OpenCode/Augment | `categories/coding-agent/implementation-map.md` |
| design-space 横切关系不明确 | 新增品类 × 模式矩阵 | `index/category-pattern-matrix.md` |
| 主干导航不清 | 新增主干地图、范式地图，并更新 SKILL/ARCHITECTURE | `index/mainline-map.md`、`index/paradigm-map.md`、`SKILL.md`、`ARCHITECTURE.md` |
| 轻量级 Agent 空间不足 | 新增 MVA 阶梯，定义从最小闭环到生产级的升级路径 | `paradigms/methodology/minimum-viable-agent.md` |

## 保留的兼容性

- 历史单页 `categories/coding-agent.md` 保留为 compatibility entry。
- `concepts/harness-engineering.md`、`concepts/autonomy-levels.md`、`concepts/decision-frameworks.md`、`concepts/agent-product-model.md` 保留旧内容，并增加主入口迁移提示。
- 旧项目笔记中指向 `concepts/harness-engineering.md` 的链接仍可用。

## 后续建议

1. 按 `categories/coding-agent/` 样板升级 `research-agent` 和 `enterprise-workflow-agent`。
2. 在 `evaluation/fixtures/` 增加至少 5 个 coding-agent 参考 fixture，对应 `eval-cases.md`。
3. 对 `projects/` 中每个项目补充“被哪些 paradigms 支撑”的反向索引。
4. 将 `concepts/design-principles.md` 与 `design-space/principles/core-design-principles.md` 进一步合并。
5. 对所有 Markdown 链接跑一次 link checker，消除历史弱引用。
