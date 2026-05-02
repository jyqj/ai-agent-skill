# Category × Pattern Matrix

> **Evidence Status** — synthesized. 显式连接品类架构和设计模式，避免 pattern 只作为散落链接存在。

Legend: 必须 = 默认应纳入；推荐 = 常用但可按风险取舍；可选 = 场景触发。

| Pattern | Coding | Research | Workflow | Browser/Desktop | Ops/SRE | Memory | Platform |
|---|---|---|---|---|---|---|---|
| Compaction | 必须 | 推荐 | 推荐 | 推荐 | 可选 | 推荐 | 必须 |
| Tool Output Offloading | 必须 | 必须 | 推荐 | 推荐 | 推荐 | 推荐 | 必须 |
| Effect Ledger | 必须 | 推荐 | 必须 | 必须 | 必须 | 可选 | 必须 |
| Self Verification | 必须 | 必须 | 必须 | 必须 | 必须 | 推荐 | 必须 |
| Loop Detection | 必须 | 推荐 | 推荐 | 必须 | 必须 | 推荐 | 必须 |
| Checkpoint Hydration | 必须 | 推荐 | 必须 | 推荐 | 必须 | 推荐 | 必须 |
| Subagent | 推荐 | 推荐 | 可选 | 可选 | 可选 | 可选 | 推荐 |
| Worker Orchestration | 推荐 | 推荐 | 推荐 | 可选 | 推荐 | 可选 | 必须 |
| Tool Registry | 必须 | 推荐 | 必须 | 必须 | 必须 | 推荐 | 必须 |
| Layered Tool Host | 推荐 | 可选 | 推荐 | 推荐 | 必须 | 可选 | 必须 |
| Hook System | 必须 | 可选 | 推荐 | 推荐 | 必须 | 推荐 | 必须 |
| Layered Memory | 推荐 | 推荐 | 推荐 | 可选 | 可选 | 必须 | 推荐 |
| Skill Crystallization | 推荐 | 可选 | 推荐 | 可选 | 推荐 | 推荐 | 必须 |
| Progressive Disclosure | 可选 | 必须 | 可选 | 可选 | 可选 | 必须 | 推荐 |
| Untrusted Context Boundary | 必须 | 必须 | 必须 | 必须 | 必须 | 必须 | 必须 |
| MCP Trust Boundary | 可选 | 推荐 | 推荐 | 推荐 | 推荐 | 可选 | 必须 |
| Citation Chain | 可选 | 必须 | 推荐 | 可选 | 可选 | 推荐 | 推荐 |
| Conflict-Preserving Synthesis | 可选 | 必须 | 推荐 | 可选 | 推荐 | 可选 | 推荐 |
| Dual-Channel GUI Verification | 可选 | 可选 | 可选 | 必须 | 推荐 | 可选 | 推荐 |
| Shadow Mode Regression | 推荐 | 推荐 | 必须 | 推荐 | 必须 | 推荐 | 必须 |
| Property-based Agent Testing | 推荐 | 推荐 | 推荐 | 可选 | 推荐 | 可选 | 推荐 |
| Contract Agent | 可选 | 推荐 | 必须 | 可选 | 推荐 | 可选 | 必须 |
| Guard Model | 推荐 | 推荐 | 必须 | 必须 | 必须 | 推荐 | 必须 |

## 使用方法

1. 先从 `category-module-map.md` 确定品类必备模块。
2. 再用本矩阵选择对应模式。
3. 对“必须”模式，如果不采用，需要在设计文档中解释替代方案。
4. 对“可选”模式，只有在真实失败或需求触发时引入。

相关：`../design-space/patterns/`、`../design-space/anti-patterns/`、`../categories/README.md`。
