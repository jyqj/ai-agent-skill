# 设计空间

> **Evidence Status** — synthesized. 跨项目观察归纳。


## 层级说明

| 子目录 | 含义 | 成熟度 |
|---|---|---|
| `principles/` | 稳定的高层设计原则，解释为什么 | 高 |
| `patterns/` | 被 2+ 项目验证或被多个品类需要的可复用做法 | 中 |
| `frontier/` | 尚未成熟的新观察、猜想、生态演进与协议边界 | 低 |
| `anti-patterns/` | 常见 Agent 架构反模式，与 `patterns/` 配套使用 | 中 |
| `methodology/` | 方法论文档（从 `concepts/` 迁入），涵盖 Harness 工程、决策框架、经济学等 | 中 |
| `lessons-learned/` | 真实失败案例与经验教训档案 | 中 |

## 当前重点

推荐先读：

- `principles/core-design-principles.md`
- `principles/representation-first-design.md`
- `patterns/untrusted-context-boundary.md`
- `patterns/effect-ledger.md`
- `patterns/tool-registry.md`
- `patterns/compaction.md`
- `patterns/citation-chain.md`
- `patterns/conflict-preserving-synthesis.md`
- `patterns/dual-channel-gui-verification.md`
- `patterns/contract-agent.md`
- `patterns/guard-model.md`

## Frontier 入口

当前已补的 frontier 主题：

- `frontier/agent-protocols-and-boundaries.md`
- `frontier/agentic-rag-and-citation-loops.md`
- `frontier/reasoning-tool-coupling.md`
- `frontier/long-horizon-runtime.md`
- `frontier/multimodal-and-computer-use.md`
- `frontier/observability-control-plane.md`
- `frontier/memory-forms-and-dynamics.md`
- `frontier/agentic-commerce-and-protocols.md`
- `frontier/automated-harness-evolution.md`
- `frontier/rl-driven-memory.md`
- `frontier/multi-agent-governance.md`
- `frontier/agent-governance-frameworks.md`
- `frontier/agent-protocols.md`

## 与主干的关系

`design-space/` 是横切层，不属于单一主干层级。使用方式：

```text
先用 concepts/paradigms/categories 确定设计方向
再用 architecture/planes 定义模块边界
再用 patterns / anti-patterns 选择复用做法
最后用 frontier 判断未来扩展和生态演进方向
```

品类到模式的推荐矩阵见：`../index/category-pattern-matrix.md`。
