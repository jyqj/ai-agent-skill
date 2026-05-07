# Patterns

> **Evidence Status** — synthesized. 本目录汇总可复用 Agent 架构模式；其中单个模式文件各自声明 grounded / synthesized / theoretical 等证据级别。

## 定位

`patterns/` 存放可以跨品类复用的具体做法。它不是概念层，也不是项目摘要；一个模式应回答：

- 解决什么反复出现的问题；
- 适用 / 不适用场景；
- 运行时需要哪些对象或 gate；
- 常见反模式；
- 可回查的参考项目或评估证据。

如果一个做法只在单个项目里出现，优先放 `../../projects/`；如果已经被 2+ 项目或多个品类需求共同支撑，再提升到本目录。

## 按问题选择模式

| 问题 | 优先看 |
|---|---|
| 任务规格不清、验收不明 | `contract-agent.md`、`milestone-gated-execution.md` |
| 工具成功但现实未变 | `effect-ledger.md`、`self-verification.md` |
| 上下文过大或关键信息丢失 | `compaction.md`、`tool-output-offloading.md`、`progressive-disclosure.md` |
| 不可信输入、工具输出注入 | `untrusted-context-boundary.md`、`tool-output-sanitization.md`、`guard-model.md` |
| 需要长期记忆或技能复用 | `layered-memory.md`、`skill-crystallization.md`、`frozen-snapshot.md` |
| 多 Agent / Worker 协作 | `subagent.md`、`worker-orchestration.md`、`checkpoint-hydration.md` |
| 需要可回放评估 | `property-based-agent-testing.md`、`shadow-mode-regression.md`、`citation-chain.md` |

## 升级规则

新模式进入本目录前，至少要满足一项：

1. 由 `../../projects/` 中 2+ 个项目支撑；
2. 被 2+ 个 `../../categories/` 品类明确需要；
3. 虽未成熟但对运行时边界特别关键，并在文件中标为 synthesized / theoretical。

写入后应同步检查：

- `../../index/category-pattern-matrix.md`
- `../../index/design-checklist.md`
- 相关 `../../architecture/planes/<plane>/overview.md`
- 相关 `../../synthesis/` 对比文件
