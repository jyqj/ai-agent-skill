# Agentic RAG and Citation Loops

> **Evidence Status** — theoretical. 基于 RAG 研究（Self-RAG、Adaptive-RAG 等）、citation-backed report 系统与 Research Agent 实践。属于 frontier 方向。

## 为什么这是 frontier

传统 RAG 假设流程是：

```text
query → retrieve → stuff context → answer
```

而 Agentic RAG 变成：

```text
plan question tree
→ retrieve
→ inspect evidence quality
→ decide whether to retrieve again / switch query / preserve conflict / stop
→ synthesize with citations
```

难点不再是“能不能检索”，而是：

- 什么时候继续搜；
- 什么时候停；
- 什么时候该承认找不到；
- 什么时候必须保留冲突而不是继续压平。

## 四段闭环

| 阶段 | 核心对象 | 关键 gate |
|---|---|---|
| Query Planning | question tree、sub-queries | 是否分解正确 |
| Retrieval Fanout | source list、ranked hits | 是否覆盖关键角度 |
| Evidence Binding | claim/evidence/citation chain | 是否出现 orphan claim |
| Synthesis | report sections、uncertainty notes | 是否保留冲突与 freshness |

## 关键设计选择

### Query 不是一次性对象

Research Agent 应把 query 视为可进化对象：

```text
初始问题
→ 澄清定义
→ 展开子问题
→ 针对冲突来源生成新 query
→ 针对 freshness 问题触发 refresh query
```

### Citation loop 应早于最终报告

很多系统在最后一步才补 citation，导致引用变成 cosmetic layer。更稳妥的顺序是：

```text
先绑定 claim 和 evidence
再允许 claim 进入 synthesis state
```

### Retrieval stop 需要成本与覆盖共同决定

停止检索的条件不只是“工具上限到了”，而是：

- 核心子问题是否都有支撑来源；
- 关键冲突是否已经显式存在于 output；
- 最新性要求是否满足；
- 继续检索的边际收益是否低于成本。

## 本知识库的落点

- 稳定部分进入 `categories/research-agent/`。
- 可复用模式沉淀为 `citation-chain.md` 与 `conflict-preserving-synthesis.md`。
- cost/quality tradeoff 进入 `architecture/planes/cost/benchmarking.md` 与 `evaluation/cost-evals.md`。

## Agentic RAG vs 传统 RAG vs Agent Memory

三者在学术和工程实践中边界日益模糊（Memory Survey 2026）：

| 维度 | 传统 RAG | Agentic RAG | Agent Memory |
|---|---|---|---|
| 知识库 | 外部静态语料 | 外部动态语料 + 自主检索 | 内部持久、自演化 |
| 检索控制 | 固定 pipeline | Agent 自主决定何时/如何/检索什么 | Agent 自主读/写/遗忘 |
| 跨任务持续 | 否 | 部分（可学习检索策略） | 是（核心特征） |
| 与 Agent Memory 交集 | 低 | 高（Agentic RAG ≈ Agent Memory 的检索子系统） | — |

Agentic RAG 的四大增强（Agents Companion 2025）：
1. **Context-Aware Query Expansion**：多轮 query 改写而非单次检索
2. **Multi-Step Reasoning**：将复杂查询分解为逻辑步骤，顺序检索
3. **Adaptive Source Selection**：动态选择最优知识源而非固定向量库
4. **Validation and Correction**：检索后用 evaluator 交叉检查幻觉和矛盾

## 与 Corpus-in-Context 的选择

| 场景 | 选择 |
|---|---|
| 数据量 ≤ 上下文窗口、需要跨段落关联 | Corpus-in-Context |
| 数据量 >> 上下文窗口 | RAG |
| 数据动态变化 + 需要自主检索 | Agentic RAG |
| 知识来自 Agent 自身经验 | Agent Memory |

详见 `../../paradigms/methodology/performance-optimization.md`。

## 仍在演进的问题

- retrieval 和 reasoning 由同一模型控制还是拆分更稳。
- citation-aware output 与 strict schema output 如何共存。
- 一次报告中多轮 refresh 的 stop condition 如何自动学习。
- Agentic RAG 与 Agent Memory 的边界在何处收敛。
- RL 是否能自动学习 retrieval stop condition 和 query 改写策略。
