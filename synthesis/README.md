# 综合分析

> **Evidence Status** — synthesized. 本页来自项目横向分析与本 skill 的架构抽象汇总，用于跨品类比较和设计取舍。

> **定位**：跨项目的横向比较、趋势判断和开放问题。不止于单个项目的视角。

这一层回答的问题包括：

- 不同品类的 Agent 在同一设计维度上做了什么不同选择？
- 哪些边界划分在多个项目中反复出现？
- 主流框架的抽象与本知识库的抽象如何映射？
- 哪些问题至今没有标准答案？

建议阅读顺序：

1. `local-reference-systems-reflection.md` — 对照根目录真实项目后的设计修正
2. `representation-and-effect-boundaries.md` — 品类间的关键差异
4. `context-memory-state-boundaries.md` — 四种容易混淆的对象
5. `execution-depth-across-agent-types.md` — 不同品类需要做到多深
6. `runtime-vs-world-state.md` — 任务状态与外部状态的分离
7. `tool-effect-verification.md` — 工具成功与任务完成的鸿沟
8. `framework-comparison.md` — 本知识库如何补充主流框架
9. `local-agent-runtime-practices.md` — 6 个参考项目共证的运行时契约（含[运行时契约检查表](#)，可直接用于架构评审）
10. `agent-loop-patterns.md` — Agent Loop 的共性结构与变体
11. `error-recovery-comparison.md` — 错误恢复策略的跨项目对比
12. `cross-project-patterns.md` — 跨项目共识模式提炼
13. `tool-boundary-comparison.md` — 工具边界与权限的横向对比
