# 认知模块到架构 Plane 的反向索引

> **Evidence Status** — synthesized. Memory Survey (arXiv 2603.07670) 提供了 Agent 记忆系统的分类框架；Baddeley 工作记忆模型、ACT-R 产生式规则、Tulving 情节/语义记忆划分、编码特异性原则 (Tulving & Thomson 1973) 提供了认知科学基础；Global Neuronal Workspace Theory (Baars/Dehaene) 提供了意识可及性的理论映射。本文为认知模块到工程 plane 的交叉映射推导。

## 1. 为什么需要这篇

认知架构层的文档以认知模块为中心（记忆、推理、注意力、元认知……），`architecture/planes/` 以运行时模块为中心（Context Plane、Memory Plane、Control Plane……）。两个视角各有价值，但缺少显式的**反向索引**：

- 设计者读完 `working-memory-dynamics.md`，想知道"这些原则落地到哪些 plane？"
- 设计者在实现 Context Plane 时，想知道"认知科学对上下文管理有什么未被利用的启发？"

本文提供这个双向映射，并标注每个映射关系中值得关注的认知科学发现。

## 2. 认知模块 → Plane 映射总表

| 认知模块 | 主要相关 Plane | 次要相关 Plane | 核心设计含义 |
|---|---|---|---|
| 工作记忆动力学 | Context Plane | State Plane, Memory Plane | 组块化、优先级标记、Context Rot 对策 |
| 注意力与显著性 | Context Plane | Representation Plane | 优先级评分、trust lane 中的注意力分配 |
| 目标层级 | Control Plane | State Plane | 任务分解、goal stack 维护、冲突解决 |
| 推理模式 | Prompting Plane | Context Plane | 推理模式选择影响 prompt 策略和上下文组装 |
| 程序性 vs 陈述性记忆 | Memory Plane | Learning Plane | 分层存储、skill 固化生命周期 |
| 心智理论 | Interaction Plane | Orchestration Plane | 用户建模、Agent 间信念推理 |
| 元认知控制 | Control Plane | Recovery Plane | 深度预算、失败检测、反思触发 |
| 技能习得 | Learning Plane | Memory Plane | Dreyfus 阶段 → skill 生命周期 |
| 情绪与动机 | Interaction Plane | Economics Plane | 情感响应策略、优先级加权 |
| 创意认知 | — (跨切面) | Evaluation 框架 | 多样性采样、约束放松、主观评估 |

## 3. 逐模块映射详解

### 3.1 工作记忆动力学 → Context Plane

**认知科学基础**：Baddeley 模型（中央执行器 + 子系统）、Cowan 容量限制（~4 组块）。

| 认知概念 | Plane 实现 | 设计要点 |
|---|---|---|
| 容量限制（~4 组块） | Context Pack 的 token 预算 | 不是 token 数越大越好；有效组块化比增大窗口更重要 |
| 中央执行器 | Context Engine 策略层 | 决定 pin / keep / compress / evict 的逻辑不应是简单 FIFO |
| 主动维护（rehearsal） | Pinning 机制 | 关键信息显式标记保留；pin 数量有上限 |
| 被动衰减 | Context Rot 检测 | 见 `working-memory-dynamics.md` §3.1 |
| 情景缓冲器 | 跨工具结果整合视图 | 需要在 Context Pack 中显式构造，不会自动形成 |
| 溢出到 LTM | State Plane 外化存储 | Scratchpad = 工作记忆溢出区 |

### 3.2 注意力与显著性 → Context Plane + Representation Plane

**认知科学基础**：选择性注意力（Broadbent 过滤模型）、显著性驱动的注意力捕获。

| 认知概念 | Plane 实现 | 设计要点 |
|---|---|---|
| 选择性注意力 | Context Pack 中的信息筛选 | 不是所有观察都进入上下文；需要相关性评分 |
| 注意力捕获 | 异常检测触发关注 | 工具输出中的错误、异常值应提高显著性权重 |
| Trust lane 注意力分配 | Representation Plane 的 trust tier | 不同来源的信息应有不同的注意力权重 |
| 注意力瓶颈 | Context Pack 大小限制 | 信息过载时优先保留与当前目标最相关的内容 |

### 3.3 目标层级 → Control Plane + State Plane

**认知科学基础**：ACT-R goal stack、Soar subgoaling、BDI 架构。

| 认知概念 | Plane 实现 | 设计要点 |
|---|---|---|
| Goal stack | State Plane 的目标栈 | 支持 push/pop + 当前活跃目标追踪 |
| Subgoaling | Control Plane 的任务分解 | 子目标失败时能回退到父目标重新规划 |
| 目标冲突 | Control Plane 的优先级仲裁 | 安全约束 > 用户指令 > 效率优化 |
| 终极目标 vs 即时目标 | System Prompt（终极） vs TaskEnvelope（即时） | 两者冲突时终极目标优先 |

### 3.4 推理模式 → Prompting Plane + Context Plane

**认知科学基础**：六种推理模式（见 `reasoning-modes.md`）。

| 认知概念 | Plane 实现 | 设计要点 |
|---|---|---|
| 推理模式选择 | Prompting Plane 的 prompt 策略 | 不同推理模式需要不同的 prompt 结构（见 reasoning-modes.md §5） |
| 推理与范式的关系 | 范式路由 | 见 `cognitive-to-paradigm-routing.md` |
| 推理链追踪 | Context Plane 保留推理过程 | 推理链不应在 compaction 中被完全丢弃 |

### 3.5 程序性 vs 陈述性记忆 → Memory Plane + Learning Plane

**认知科学基础**：Tulving 情节记忆 / 语义记忆划分、ACT-R 陈述性/程序性模块。

| 认知概念 | Plane 实现 | 设计要点 |
|---|---|---|
| 陈述性记忆（事实） | Memory Plane 的知识层 | 可检索、可验证、可失效的主张 |
| 程序性记忆（技能） | Memory Plane 的 skill 层 + Learning Plane | 已验证的行动序列模板；见 skill-acquisition.md |
| 情节记忆 | Memory Plane 的事件日志 | 保留时间标记和情境上下文，不仅仅是语义向量 |
| 语义记忆 | Memory Plane 的概念索引 | 从多次情节中抽象出的稳定知识 |
| 记忆固化 | Learning Plane 的 skill 生命周期 | 从情节记忆 → 程序化模板 → 固化 skill |

### 3.6 心智理论 → Interaction Plane + Orchestration Plane

**认知科学基础**：Theory of Mind（对他人信念、意图、知识状态的推理）。

| 认知概念 | Plane 实现 | 设计要点 |
|---|---|---|
| 用户心智模型 | Interaction Plane 的用户建模 | 追踪用户的技术水平、偏好、当前情绪状态 |
| Agent 间信念推理 | Orchestration Plane 的 Agent 建模 | 多 Agent 场景中推理其他 Agent 的知识边界 |
| 共同注意力 | Interaction Plane 的 progress report | 确保人和 Agent 关注同一件事 |

### 3.7 元认知控制 → Control Plane + Recovery Plane

**认知科学基础**：元认知监控（Metacognitive Monitoring）、Nelson & Narens 的元认知框架。

| 认知概念 | Plane 实现 | 设计要点 |
|---|---|---|
| 自信度监控 | Control Plane 的置信度追踪 | 低自信时触发 Reflection 或求助 |
| 策略选择 | Control Plane 的深度预算 | 元认知判断当前策略是否有效 |
| 失败检测 | Recovery Plane 的异常处理 | impasse 检测 → 升级或切换策略 |
| 学习判断 | Learning Plane 的 skill 评估 | 判断某行为模式是否值得固化为 skill |

### 3.8 技能习得 → Learning Plane

**认知科学基础**：Dreyfus 五阶段模型（新手 → 高级新手 → 胜任 → 精通 → 专家）。

| Dreyfus 阶段 | Agent 对应 | Learning Plane 行为 |
|---|---|---|
| 新手 | 严格遵循 prompt 指令 | 全 System 2 推理；高 token 消耗 |
| 高级新手 | 识别情境中的模式 | 开始建立情境-行动关联 |
| 胜任 | 能选择合适策略 | 形成 skill 候选；进入评估 |
| 精通 | 直觉性模式识别 | skill 固化；部分决策转为 System 1 |
| 专家 | 流畅、直觉、无需审慎推理 | 完全编译的 skill；最低 token 开销 |

### 3.9 情绪与动机 → Interaction Plane + Economics Plane

| 认知概念 | Plane 实现 | 设计要点 |
|---|---|---|
| 情感感知 | Interaction Plane 的情感检测 | Companion Agent 核心能力 |
| 情感响应 | Interaction Plane 的响应策略 | 需要维持一致性（不同会话间） |
| 任务优先级信号 | Economics Plane 的优先级加权 | 紧急任务 > 重要任务 > 例行任务 |

## 4. 关键认知科学发现对 Plane 设计的启发

这些发现尚未在多数 Agent 系统中被充分利用：

### 4.1 编码特异性原则（Encoding Specificity Principle）

**发现**：Tulving & Thomson (1973) 证明，记忆检索效果取决于编码时的上下文与检索时的上下文的匹配程度。一个在"钢琴"上下文中编码的"调音"记忆，用"音乐"作为检索线索可能失败。

**对 Memory Plane 的启发**：情节记忆的检索不应仅依赖语义相似度（embedding 距离）。应该刻意构造检索线索（deliberate cue construction），在写入时记录编码上下文，在检索时尝试重建该上下文。

```text
当前做法：query → embedding → cosine similarity → top-k
改进方向：query + task_context + encoding_context → multi-signal retrieval
```

### 4.2 上下文窗口 ≈ 全局工作空间（GNWT）

**发现**：Baars 的 Global Neuronal Workspace Theory 认为，意识的功能是使信息在全脑范围内"广播可用"。不在工作空间中的信息虽然存在（如长期记忆中），但无法参与当前认知过程。

**对 Context Plane 的启发**：Context Window 是 Agent 的"意识"，不在窗口中的信息，模型字面意义上无法利用。这意味着：
- Context Pack 的组装质量直接决定 Agent 的认知质量
- "从 LTM 检索到了正确信息但没放进上下文"等于没检索到
- 信息进入上下文的时机和位置（不仅仅是内容）影响可用性

### 4.3 记忆再巩固（Memory Reconsolidation）

**发现**：认知科学发现，每次提取记忆都会使记忆进入可塑状态（labile state），提取后需要重新巩固。在这个窗口期，记忆可以被更新或修改。

**对 Memory Plane 的启发**：记忆的"读取"不应是只读操作。每次检索都是更新记忆的机会：添加新上下文、修正过时信息、增强记忆强度。这为 Memory Plane 提供了自然的更新机制设计依据。

### 4.4 传播激活（Spreading Activation）

**发现**：ACT-R 中，检索一个概念会沿关联网络"激活"相关概念，使它们更容易被后续检索。

**对 Memory Plane 的启发**：检索一条记忆后，可以预激活（priming）相关记忆，降低后续检索的延迟。这超越了简单的 top-k retrieval，可以实现基于关联网络的"联想式检索"。

## 5. 研究缺口

| # | 缺口 | 认知科学视角 | 工程现状 |
|---|---|---|---|
| 1 | 编码特异性在 RAG 中的应用 | 理论成熟，实验证据充分 | 几乎所有 RAG 系统仍只用语义相似度 |
| 2 | 工作记忆的动态组块化 | Cowan 模型清晰描述了组块机制 | Context compaction 缺乏认知理论指导 |
| 3 | 元认知的量化测量 | Nelson & Narens 提出了框架 | Agent 的元认知主要靠硬编码规则 |
| 4 | 情节记忆与语义记忆的自动区分 | Tulving 的划分在心理学中已被广泛验证 | Agent 记忆系统很少做这个区分 |
| 5 | 传播激活在 Agent 记忆中的实现 | ACT-R 有成熟的激活公式 | 缺乏在 LLM Agent 中的实验验证 |
| 6 | 双过程理论的自动调度 | SOFAI 提出了架构但缺乏 LLM 实证 | 依赖手动规则而非自适应调度 |

## 6. 使用指南

1. **从认知模块出发**：如果你在研究某个认知能力，查 §2 总表找到对应的 plane，再到 `architecture/planes/` 读工程实现。
2. **从 Plane 出发**：如果你在实现某个 plane，反向查总表找到相关的认知模块，再到 `cognitive-architecture/` 读理论基础。
3. **找设计启发**：§4 的认知科学发现可以直接转化为 plane 的设计改进。

## 7. 延伸阅读

- `working-memory-dynamics.md` — 工作记忆的详细认知模型和 Agent 映射
- `reasoning-modes.md` — 六种推理模式
- `category-cognitive-profiles.md` — 品类认知需求热力图
- `cognitive-to-paradigm-routing.md` — 认知需求如何驱动范式选择
- `../architecture/planes/context/overview.md` — Context Plane 工程实现
- `../architecture/planes/memory/overview.md` — Memory Plane 工程实现
- `../architecture/planes/control/overview.md` — Control Plane 工程实现
- `../architecture/learning/overview.md` — Learning 子系统
- Tulving, E. & Thomson, D. M. (1973). "Encoding specificity and retrieval processes in episodic memory"
- Baars, B. J. (1988). *A Cognitive Theory of Consciousness* — Global Workspace Theory
- Baddeley, A. (2000). "The episodic buffer" *Trends in Cognitive Sciences*
- Anderson, J. R. (2007). *How Can the Human Mind Occur in the Physical Universe?* — ACT-R
- Memory Survey (arXiv 2603.07670) — Agent 记忆系统综述
