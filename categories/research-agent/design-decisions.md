# Research Agent Design Decisions

> **Evidence Status** — speculative. research/report systems、citation workflows、frontier 文档与成本/交互/安全 plane。

## 检索策略

| 决策 | 默认 | 升级触发器 |
|---|---|---|
| Breadth vs Depth | 先 breadth 建 source map，再对高价值 claim depth verify | 冲突多、结论风险高 |
| Query Fanout | 小批量并行，避免无限 retrieval | coverage 不足或 authority 不够 |
| Refresh | 对时间敏感 claim 做 targeted refresh | latest/current/recent 任务 |

## 上下文策略

Research Agent 的上下文以 claim 和 evidence 为中心进行组装：

```text
question → claim → evidence → citation → unresolved gaps
```

默认：

- 用 snippets 和 source metadata 组上下文；
- 保留 raw refs，不直接塞全文；
- 对章节级 synthesis 采用 progressive disclosure；

## 成本策略

| 资源 | 默认约束 |
|---|---|
| Search | 限制 fanout 和重复 query |
| Fetch / Read | 先 metadata / relevant sections，再全文 |
| Synthesis | 先 section draft，再总报告整合 |
| Refresh | 只对高影响、时间敏感 claim 触发 |

## 交互策略

| 情况 | 默认交互 |
|---|---|
| 任务范围模糊 | 只问最阻塞的一问 |
| 证据不够但已有部分结果 | partial completion |
| 结论冲突 | 明示冲突，不装作已经解决 |
| 成本接近预算 | 提供“继续检索 / 现在交付”的选择 |

## 控制策略

Research Agent 的关键控制点是以下四个 gate：

- fabricated citation gate
- freshness gate
- conflict preservation gate
- publish / send gate

## 运维策略

进入持续使用后，应至少记录：

```text
[ ] query fanout
[ ] source diversity
[ ] section-level citation density
[ ] unresolved conflict count
[ ] cost per completed brief
[ ] refresh hit rate
```

## 升级触发器

| 观察 | 升级 |
|---|---|
| 经常出现 citation drift | 引入 stricter citation chain tooling |
| 结论常被 freshness 打脸 | 强化 refresh policy |
| 报告容易拼贴 | 引入 section-level synthesis state |
| 长任务断裂 | checkpoint + partial deliver |
| 研究主题反复出现 | 引入 scoped memory / source preference memory |

## 多 Agent 编排架构（2026 更新）

> 来源：Egnyte Deep Research Agent 架构、Deep Research Agents 综述 (arXiv 2506.18096)、Perplexity Computer

### Egnyte 五 Agent + DAG 编排

Egnyte 的生产架构由五个专业化 Agent + Master 编排器组成：

```text
[用户查询] → Master Agent → Planner Agent → [DAG 研究计划]
                                                    ↓
                              Master Agent (调度循环)
                              ├─ Schedule: DAG 拓扑遍历，找到依赖已满足的节点
                              ├─ Dispatch: 并行启动多个 Researcher Agent (map/reduce)
                              ├─ Synchronize: 收集结构化 Question Analysis
                              └─ Loop: 直到所有 DAG 节点处理完毕
                                                    ↓
                              Writer Agent → [最终报告]
```

- **Planner Agent**：探索性搜索 → 综合为关键研究角度 → 构造 DAG 建模依赖关系，支持 human-in-the-loop 计划验证
- **Searcher Agent**：策略性查询构造 → 并行多源搜索 → Cross-encoder 重排序 → MMR 选择多样片段 → 条件路由决定是否追加查询
- **Researcher Agent**：多实例并行运行，输出结构化 Question Analysis（发现 + 引用 + 缺口标识），前序缺口分析驱动后续查询
- **Writer Agent**：切换到更强模型，执行跨全部 Question Analysis 的元分析 → 并行按主题写作 → 组装报告
- **技术栈**：LangGraph 编排、FastAPI REST API、LangGraph checkpointing 状态持久化

### 三种规划策略

| 策略 | 机制 | 代表系统 |
|---|---|---|
| Planning-Only | 直接从用户提示生成计划 | Grok, H2O, Manus |
| Intent-to-Planning | 先通过定向提问澄清意图，再生成计划 | OpenAI Deep Research |
| Unified Intent-Planning | 生成初步计划 + 交互式用户确认 | Gemini DR |

### 引用链已知缺陷

引用完整性仍有持续性问题："正确引用附加到不被支持的主张上"等细微错误持续存在。多数系统依赖 LLM 推理能力评估信息质量，**缺乏形式化冲突解决协议**。事实核查被多篇论文标识为关键开放挑战。

### Perplexity 19 模型编排架构

Perplexity Computer 对每个子任务路由到最优模型（19 模型编排）：

| 子任务类型 | 路由模型 |
|---|---|
| 推理和软件工程 | Claude Opus 4.6 |
| 深度研究和视觉输出 | Gemini |
| 长上下文召回 | GPT-5.2 |

子 Agent 并行执行，系统持续监控质量并自纠正。市场背景：2025.01 超 90% 企业 AI 任务通过仅两个模型运行；到 2025.12 单一模型处理不超过 25% 的使用量。
