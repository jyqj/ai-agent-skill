# Memory Paradigms

> **Evidence Status** — grounded. `architecture/planes/memory/overview.md`、Nocturne Memory、MemPalace、NagaAgent、Generic Agent 与 Context/Memory/World State 边界文档。


## 范式总览

| 范式 | 核心机制 | 适合 | 主要风险 |
|---|---|---|---|
| In-context Memory | 把相关信息直接放进当前 ContextPack | 短任务、少量事实、用户实时交互 | context rot、成本膨胀 |
| RAG | query → retrieve chunks → inject context | 文档问答、知识库检索、引用型研究 | 检索污染、片段断章取义 |
| Disclosure / Progressive Memory | 只在条件满足时披露记忆或证据 | 长记忆、隐私敏感、需要最小暴露 | disclosure policy 错配 |
| Layered Memory | Working / Session / Project / Long-term / Skill 分层 | 跨会话偏好、项目约定、技能固化 | 写入策略混乱、过期未失效 |
| Graph Memory | entity / relation / event 组成知识图谱 | 人际、项目、长期关系、推理路径 | 图谱幻觉、边权和 provenance 缺失 |
| Episodic / Trace Memory | 保存任务轨迹、结果、失败原因 | 复盘、技能提炼、回归评估 | 把一次性事件泛化成规则 |
| World State Snapshot | 刷新外部对象当前状态 | 写操作前后、CI、ticket、repo、CRM | stale snapshot、最终一致性 |
| Generative Memory | 模型直接生成记忆内容，而非原样检索 | 需要整合、推理或重构的记忆场景 | 生成幻觉、与原始事实偏离 |

### Generative Memory 范式

传统记忆范式是 **retrieve-then-use**：从存储中检索原始条目，注入上下文。Generative Memory 引入两种新路径：

- **Retrieve-then-Generate**：先检索相关记忆片段，再由模型综合生成新的记忆表述（摘要、归纳、关联推理）。适合记忆碎片多且需要整合的场景，如从 20 条零散 episode 中生成一条策略级 insight。
- **Direct Generation**：不依赖显式检索，模型基于参数化知识直接生成。这是 Parametric Memory 的受控使用方式，风险是无法追溯 provenance。

**与传统范式的关系**：Generative Memory 不替代 Layered / Graph / Episodic 等范式，而是在检索之后增加一个生成层。原始记忆条目仍需保留（作为 provenance 和审计依据），生成结果标注为 `derived`，与原始条目区分。

**风险控制**：生成的记忆必须标注来源记忆的 ID 列表，用户可以追溯到原始条目验证。生成记忆不应直接进入 Skill 层，它是 Strategy 层的候选，需经 eval gate 才能固化。

## 关键边界

```text
Context  = 当前模型能看见什么，是注意力预算
Memory   = 系统保存的历史主张资产，必须有 provenance 和失效策略
World State = 外部对象当前/近期状态的快照，写前要刷新，写后要验证
```

不要用 Memory 代替 World State。用户偏好可以来自长期记忆，仓库当前分支、CI 状态、ticket 状态必须来自可刷新快照。

## 记忆功能抽象谱系（Experiential Memory Ladder）

记忆不仅按生命周期分层，还按**功能抽象程度**形成四级谱系。越靠上层，复用面越广，维护成本越高。

| 层级 | 存储什么 | 抽象程度 | 典型来源 | 适用场景 |
|---|---|---|---|---|
| Case-based | 原始 episode（输入-输出-结果三元组） | 最低 | 任务 trace 直接归档 | 复盘、回归、相似任务检索 |
| Strategy-based | 从多 case 中提炼的 Insights / Workflows / Patterns | 中 | 跨 case 归纳或人类标注 | 指导决策、缩短试错 |
| Skill-based | 可直接执行的 SOP / 脚本 / 模板 | 高 | Strategy 经 eval gate 固化 | 自动化重复子任务 |
| Hybrid | 上述三层共存，按任务复杂度动态选取 | 自适应 | 系统自动路由 | 生产环境常态 |

**设计要点**：
- Case → Strategy 的提炼需要足够样本量和人工或 LLM 审核，过早泛化会引入错误规则。
- Strategy 层是 Agent 经验的主要复利来源，它比 Case 更紧凑、比 Skill 更灵活。
- Hybrid 模式下，检索优先级通常为 Skill > Strategy > Case，但当 Skill 执行失败时应回退到 Strategy 或 Case 重新探索。

## 记忆形态维度（Forms）

除按生命周期分层外，记忆还可按承载形态分三类：

| 形态 | 承载方式 | 优势 | 局限 |
|---|---|---|---|
| Token-level | 显式离散单元（文本/图/树） | 透明、可编辑、可审计 | 规模增长时检索成本高 |
| Parametric | 模型参数编码（fine-tuning/LoRA） | 零延迟访问、隐式泛化 | 不透明、难编辑单条 |
| Latent | 隐状态/连续向量 | 与推理深度集成 | 可解释性最差 |

Token-level 按拓扑进一步分为 Flat(1D)、Planar(2D)、Hierarchical(3D)。

详见 `../design-space/frontier/memory-forms-and-dynamics.md`。

## 记忆动态三算子

| 算子 | 作用 | 对应实践 |
|---|---|---|
| Formation | 从交互中选择性生成记忆候选 | 摘要、蒸馏、结构化构建 |
| Evolution | 合并、更新、遗忘已有记忆 | 冲突解决、低效用淘汰 |
| Retrieval | 按任务上下文检索相关记忆 | 向量相似、图遍历、混合排序 |

Agent Memory 的独特性在于**持久性 + 自演化 + 跨任务积累**，区别于 RAG（静态外部知识）和 Context Engineering（单次资源调度）。

## 范式选择矩阵

| 场景特征 | 推荐记忆范式 | 必备约束 |
|---|---|---|
| 单轮问答，只需少量背景 | In-context | 明确 context source |
| 文档库问答，需要引用 | RAG | chunk provenance、citation、trust tier |
| 个人长期偏好或隐私信息 | Disclosure + Layered | 最小披露、用户纠错、删除机制 |
| 项目约定、构建命令、代码风格 | Project Memory + Skill Memory | repo scope、freshness、验证记录 |
| 多实体关系、长期关系推理 | Graph Memory | edge provenance、confidence、review policy |
| 想让 Agent 从成功任务中进化 | Episodic Trace → Skill Crystallization | eval 通过后才能固化 |
| 即将修改外部系统 | World State Snapshot | TTL、refresh、read-after-write |

## 记忆写入策略

```text
candidate detected
  → classify: working / session / project / long-term / skill / world-state
  → assess: stable? reusable? sensitive? user-owned? project-scoped?
  → attach: provenance, timestamp, raw ref, confidence, expiry/review policy
  → approve: auto / ask user / reject / keep ephemeral
  → store: with audit log and deletion path
  → evaluate: does recall improve task success without increasing hallucination?
```

| 信息类型 | 默认动作 |
|---|---|
| 当前任务临时事实 | 只进 TaskState / Context，不进长期记忆 |
| 用户明确偏好 | 候选 → 用户确认 → Long-term Memory |
| 项目构建命令 | 候选 → 通过执行验证 → Project Memory |
| 成功工作流 | 候选 → eval 通过 → Skill Memory |
| 外部对象当前状态 | World State Snapshot，按 TTL 失效 |
| 敏感信息 | 默认不写，除非显式确认并可删除 |

## 与模块层的连接

| 记忆范式 | 主要模块 | 相关模式 / 项目 |
|---|---|---|
| RAG | Representation、Context、Memory、Security | `../design-space/patterns/untrusted-context-boundary.md` |
| Disclosure | Context、Memory、Interaction | Nocturne Memory |
| Layered Memory | Memory、State、Learning | `../design-space/patterns/layered-memory.md` |
| Graph Memory | Memory、Representation、Tools | MemPalace、NagaAgent |
| Skill Memory | Learning、Memory、Evaluation | Generic Agent、`../design-space/patterns/skill-crystallization.md` |
| World State | World State、Effects、Control | `../architecture/planes/world-state/overview.md` |

## 反模式

| 反模式 | 问题 | 替代 |
|---|---|---|
| Memory-as-Database | 把所有事实都塞进“记忆”，没有边界 | 区分 Memory / World State / Trace |
| Unverified Skill | 一次成功就固化成技能 | eval gate + governance / invalidation |
| Invisible Recall | 召回内容无来源无置信度 | recall item 必须携带 provenance |
| Permanent Mood | 把用户一次性情绪写成长期偏好 | 只写稳定、可复用、经确认信息 |

相关文件：`../architecture/planes/memory/overview.md`、`../synthesis/context-memory-state-boundaries.md`、`../projects/memory-systems/nocturne-memory/`、`../projects/memory-systems/mempalace/`。


## 决策树速用

```text
当前任务临时信息 → Context / TaskState
外部对象当前状态 → WorldStateSnapshot + TTL
文档知识问答 → RAG + citation + trust tier
用户偏好/隐私 → Disclosure + user control
项目约定 → Project Memory + validation
成功路径 → Skill candidate + eval gate
多实体长期关系 → Graph Memory + provenance
```

完整跨范式决策树见 `decision-trees.md`。
