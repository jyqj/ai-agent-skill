# Reference Article Absorption Audit

> **Evidence Status** — synthesized. 对 `/Users/jin/Desktop/knode/参考文章` 五篇本地资料的多轮吸收结果进行来源到产物映射；用于证明哪些观点已进入 skill，哪些内容被明确判定为 reference-only 或不适合沉淀。

## 目标与完成口径

本审计回答：参考文章中对 Agent 架构 skill 有长期价值的内容，是否已经落到可维护文档、导航或评估入口。

完成口径：

1. 每篇输入文章都被登记。
2. 每篇文章的高价值主题被归入本 skill 的稳定层：`concepts/`、`cognitive-architecture/`、`paradigms/`、`architecture/`、`categories/`、`design-space/`、`evaluation/`、`synthesis/`、`toolkit/` 或 `index/`。
3. 不把原文里的示例代码/API 片段直接包装为生产实现；只吸收架构语义、模式、边界和评估要求。
4. 对尚不成熟或只来自单篇资料的观点，使用 `frontier` / `theoretical` / `speculative`，不升级成 production-validated。
5. 所有新增或修改文档必须通过 `scripts/validate_skill.py` 的 Evidence Status 与链接校验。

## 输入资料清单

| 文件 | 类型 | 主要价值 | 吸收状态 |
|---|---|---|---|
| `2512.13564v2.md` | 学术综述：Agent Memory | 记忆 Forms / Functions / Dynamics、Agent Memory 与 RAG / Context Engineering 边界 | 已吸收 |
| `Agentic-Design-Patterns.md` | 模式手册 + reference code | 21 类 Agentic pattern、ADK/MCP/A2A、推理/安全/评估/优先级/探索 | 已吸收，代码只作为 reference-only |
| `Agents_Companion_v2.md` | Google Agent 指南 | AgentOps、Trajectory eval、多 Agent eval、Agentic RAG、Contracts、企业 Agent | 已吸收 |
| `google_research_1018686.md` | Google Secure AI Agents | human controller、limited powers、observable actions、hybrid defense-in-depth | 已吸收 |
| `improve_llm_performance_reliability.md` | Google Cloud 技术选择 | prompt/RAG/fine-tune/long-context 的选择树、评估驱动优化 | 已吸收 |

## Source → Artifact 映射

### 1. Memory Survey (`2512.13564v2.md`)

| 原文高价值点 | 落地文档 | 吸收方式 |
|---|---|---|
| Forms / Functions / Dynamics 三维分类 | `design-space/frontier/memory-forms-and-dynamics.md` | 作为前沿统一分类法，避免仍停留在 short-term / long-term 二分 |
| token / parametric / latent memory | `architecture/planes/memory/memory-type-taxonomy.md`、`paradigms/memory-paradigms.md` | 转成工程选择维度，不宣称所有项目已验证 |
| formation / evolution / retrieval 三算子 | `architecture/planes/memory/overview.md`、`architecture/planes/memory/memory-write-discipline.md` | 转成写入纪律、过期、合并、检索时机 |
| Agent Memory vs RAG vs Context Engineering | `architecture/cross-cutting/context-engineering-x-memory.md`、`design-space/frontier/agentic-rag-and-citation-loops.md` | 明确 Context、Memory、RAG 的边界和重叠 |
| trustworthy / multimodal / shared memory 前沿 | `design-space/frontier/memory-forms-and-dynamics.md`、`architecture/planes/memory/memory-layering-strategies.md` | 保持 frontier，不进入稳定生产建议 |

### 2. Agentic Design Patterns (`Agentic-Design-Patterns.md`)

| 章节 / 主题 | 落地文档 | 吸收方式 |
|---|---|---|
| Prompt chaining / routing / parallelization | `architecture/kernel/agent-loop.md`、`paradigms/paradigm-routing.md`、`design-space/patterns/concurrent-tool-partition.md` | 抽象成 decision type、routing、并发分区，而非复制框架代码 |
| Reflection / planning / goal monitoring | `architecture/kernel/agent-loop.md`、`architecture/kernel/context-budget.md`、`cognitive-architecture/goal-hierarchy.md`、`cognitive-architecture/metacognitive-control.md` | 融入 ORDA-VU、目标层级和元认知控制 |
| Tool use / MCP / tool lifecycle | `architecture/kernel/tool-lifecycle.md`、`architecture/planes/tools/tool-use.md`、`design-space/patterns/mcp-trust-boundary.md` | 落为工具生命周期、信任边界、能力授权 |
| Multi-agent / A2A / inter-agent communication | `architecture/planes/orchestration/overview.md`、`architecture/planes/orchestration/communication.md`、`design-space/frontier/agent-protocols.md` | 区分稳定编排和协议前沿 |
| Memory management / learning adaptation | `architecture/planes/memory/overview.md`、`architecture/learning/overview.md`、`design-space/patterns/skill-crystallization.md` | 与 Memory Survey 合并为记忆与学习闭环 |
| Exception handling / recovery | `architecture/planes/recovery/overview.md`、`architecture/planes/recovery/recovery-decision-tree.md`、`synthesis/error-recovery-comparison.md` | 提炼为恢复 plane 和横向比较 |
| HITL / guardrails / safety | `architecture/planes/interaction/overview.md`、`architecture/planes/control/permission-models.md`、`design-space/patterns/guard-model.md` | 融入人工介入、权限和安全门禁 |
| RAG / knowledge retrieval | `design-space/frontier/agentic-rag-and-citation-loops.md`、`categories/research-agent/README.md` | 落为 Research Agent 的 citation loop 和 retrieval stop 条件 |
| Resource-aware optimization | `design-space/patterns/dynamic-model-routing.md`、`design-space/methodology/performance-optimization.md`、`architecture/planes/cost/overview.md` | 转为模型路由、成本门和技术选择树 |
| Reasoning techniques | `cognitive-architecture/reasoning-technique-selection.md`、`paradigms/reasoning-paradigms.md`、`architecture/planes/prompting/reasoning-mode-selection.md` | 从技术清单升级为选择矩阵 |
| Evaluation / monitoring / prioritization / exploration | `evaluation/trajectory-evaluation.md`、`design-space/patterns/task-prioritization.md`、`design-space/patterns/exploration-discovery.md` | 转成评估维度、优先级规则和探索模式 |
| Appendices: advanced prompting、GUI、frameworks、CLI、coding agents | `design-space/methodology/harness-engineering.md`、`categories/browser-desktop-agent/`、`categories/coding-agent/`、`projects/` | 只沉淀框架差异与品类启发，示例代码不作为生产实现 |

### 3. Agents Companion (`Agents_Companion_v2.md`)

| 原文高价值点 | 落地文档 | 吸收方式 |
|---|---|---|
| AgentOps 指标与运维 | `design-space/methodology/performance-optimization.md`、`architecture/planes/observability/overview.md`、`architecture/planes/operations/overview.md` | AgentOps 作为 DevOps/MLOps/FMOps 的上层闭环 |
| Trajectory and Tool Use evaluation | `evaluation/trajectory-evaluation.md`、`evaluation/eval-framework.md`、`evaluation/tool-use-evals.md` | 形成 Exact / In-order / Any-order / Precision / Recall / Single-tool 指标 |
| Multi-agent evaluation | `evaluation/eval-framework.md`、`architecture/planes/orchestration/governance.md` | 映射到协调、冲突、归因和治理 |
| Agentic RAG | `design-space/frontier/agentic-rag-and-citation-loops.md`、`categories/research-agent/README.md` | Query planning、retrieval fanout、evidence binding、synthesis loop |
| From agents to contractors | `design-space/patterns/contract-agent.md` | 转成任务合同、验收、反馈、分包协议 |
| Co-Scientist / automotive multi-agent case | `design-space/patterns/exploration-discovery.md`、`categories/embodied-robot-agent/README.md` | 作为探索型和现实世界多 Agent 品类启发，不硬编码产品名 |

### 4. Secure AI Agents (`google_research_1018686.md`)

| 原文高价值点 | 落地文档 | 吸收方式 |
|---|---|---|
| Rogue actions / sensitive data disclosure 两大风险 | `architecture/planes/security/overview.md`、`design-space/lessons-learned/README.md` | 融入风险分类和事故教训 |
| Human controllers | `architecture/planes/control/overview.md`、`architecture/planes/identity-capability/overview.md` | 转成 controller、capability grant、授权来源 |
| Limited powers | `architecture/planes/control/permission-models.md`、`architecture/planes/security/overview.md` | 转成最小权限、作用域、期限、fail-closed |
| Observable actions and planning | `architecture/planes/observability/overview.md`、`architecture/runtime-data-model.md` | 转成 trace、decision log、effect record |
| Hybrid defense-in-depth | `design-space/patterns/guard-model.md` | 规则层 + guard model + assurance，避免单点防御 |

### 5. LLM Reliability & Performance (`improve_llm_performance_reliability.md`)

| 原文高价值点 | 落地文档 | 吸收方式 |
|---|---|---|
| prompt engineering / RAG / fine-tuning / long context 技术选择 | `design-space/methodology/performance-optimization.md`、`architecture/planes/cost/cost-quality.md` | 转成选择树和成本-质量矩阵 |
| Corpus-in-context vs RAG | `design-space/methodology/performance-optimization.md`、`design-space/frontier/agentic-rag-and-citation-loops.md` | 作为上下文窗口时代的 RAG 替代路径 |
| Evaluate → Compare → Enhance → Predict loop | `evaluation/eval-framework.md`、`architecture/planes/observability/overview.md` | 转成评估驱动优化闭环 |
| context caching / distillation / smaller model path | `architecture/planes/cost/caching.md`、`design-space/patterns/dynamic-model-routing.md` | 转成成本工程与模型路由策略 |

## 明确不吸收或只 reference-only 的内容

| 内容 | 处理 |
|---|---|
| 大量框架样例代码、API 初始化、环境变量加载代码 | 不进入生产代码；只作为 reference-only 的模式说明来源 |
| 单一供应商当期产品名、营销性指标、可能快速过期的排行榜 | 不写成稳定结论；若保留，只放 `corpus/` 或 `frontier/`，并标注时效 |
| 未经交叉验证的强性能数字 | 不升级为 grounded / production-validated；只保留为背景或案例 |
| PDF 转换噪声、页眉页脚、重复目录、代码注释标题 | 丢弃，不进入知识库 |

## 吸收后的结构性增量

- 记忆系统：从生命周期二分升级为 Forms / Functions / Dynamics + 写入纪律 + trust/provenance。
- Agent 主循环：从 TAO/ReAct 升级为 ORDA-VU + effect verification + recovery + update。
- 评估系统：补强 trajectory、tool-use、effect、security、cost、subjective eval。
- 安全系统：补强 human controller、limited powers、observable actions、hybrid defense-in-depth。
- 研究系统：补强 Agentic RAG、citation loop、retrieval stop、conflict preservation。
- 成本系统：补强 prompt/RAG/long-context/fine-tune/caching/model-routing 的选择树。
- 知识库使用方式：保持 low-cognitive-load 入口 `START-HERE.md` / `toolkit/` / `index/ai-routing-pack.md`，深层材料只按需下钻。

## 审计结论

五篇参考文章的长期价值已经被吸收到本 skill 的稳定结构中。当前剩余未吸收内容主要是：示例代码、供应商即时信息、转换噪声和未交叉验证的性能数字；这些内容不应进入架构知识库的稳定主干。
