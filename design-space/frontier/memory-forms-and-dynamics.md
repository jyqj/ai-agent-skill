# Memory Forms and Dynamics

> **Evidence Status** — speculative. Memory Survey (arXiv:2512.13564v2, Jan 2026) 的 Forms-Functions-Dynamics 统一分类法；本知识库 memory paradigms 和 memory plane 的现有抽象。

## 核心贡献

传统的 short-term/long-term 二分法已不足以描述当代 Agent 记忆系统的多样性。本文档引入学术前沿的三维分类法：

```text
Forms      ─ 记忆以什么形态承载？
Functions  ─ 记忆为什么存在？
Dynamics   ─ 记忆如何运作和演化？
```

## 1. Memory Forms（记忆形态）

### 1.1 Token-level Memory（显式离散记忆）

以可检查、可编辑的离散单元存储。按拓扑组织分三层：

| 层级 | 结构 | 示例 | 适合 |
|---|---|---|---|
| Flat (1D) | 线性序列/无拓扑 | chunk 列表、对话日志、经验轨迹 | 简单追加、快速实现 |
| Planar (2D) | 单层图/树/表 | 知识图谱、推理树、关系表 | 需要关系推理 |
| Hierarchical (3D) | 多层互联结构 | 分层图、金字塔索引 | 跨粒度抽象和推理 |

**优势**：透明、可编辑、可审计
**局限**：规模增长时检索成本上升、维护复杂

### 1.2 Parametric Memory（参数记忆）

通过模型参数编码，前向计算时隐式访问。

| 类型 | 机制 | 示例 |
|---|---|---|
| Internal Parametric | 微调、LoRA、知识蒸馏 | Med-PaLM, domain fine-tuning |
| External Parametric | 独立外部模型参数存储 | Retroformer, early experience replay |

**优势**：访问零延迟、隐式泛化
**局限**：不透明、难以编辑单条记忆、灾难性遗忘

### 1.3 Latent Memory（潜在记忆）

在模型内部隐状态、连续表示或演化潜结构中表达。

| 操作 | 说明 |
|---|---|
| Generate | 从交互中生成新的潜在表示 |
| Reuse | 跨推理步骤复用 KV cache / hidden states |
| Transform | 对潜在状态做压缩、合并、遗忘 |

**优势**：与推理深度集成
**局限**：可解释性最差、调试困难

## 2. Memory Functions（记忆功能）

超越粗粒度时间维度，按功能角色区分：

| 功能 | 存什么 | 为什么需要 | 对应本知识库 |
|---|---|---|---|
| Factual Memory | 用户事实、环境事实 | 个性化、环境理解 | Memory Plane (Long-term, Project) |
| Experiential Memory | 案例、策略、技能 | 从经验中学习、复用成功路径 | Learning & Skill Crystallization |
| Working Memory | 当前任务工作区信息 | 管理当前推理过程 | Context Plane |

### 2.1 Factual Memory
- **User factual**：用户偏好、档案、历史选择
- **Environment factual**：外部系统状态、项目约定、API schema

### 2.2 Experiential Memory
- **Case-based**：保存完整任务轨迹供类比检索
- **Strategy-based**：从多次执行中抽象策略/原则
- **Skill-based**：固化为可执行工具/脚本/模板
- **Hybrid**：混合上述形式

### 2.3 Working Memory
- **Single-turn**：单步内的中间推理（scratchpad、CoT）
- **Multi-turn**：跨步骤的任务状态（compaction、progressive summary）

## 3. Memory Dynamics（记忆动态）

### 3.1 Memory Formation（形成）

```text
Agent 产生信息制品 ϕ_t
  → Formation Operator F: M_{t+1} = F(M_t, ϕ_t)
  → 选择性转化为记忆候选（不是全部存储）
```

形成策略：
| 策略 | 机制 |
|---|---|
| Semantic Summarization | 对交互历史做语义摘要 |
| Knowledge Distillation | 从长 trace 中蒸馏可复用知识 |
| Structured Construction | 构建图/树/表等结构化表示 |
| Latent Representation | 编码为连续向量 |
| Parametric Internalization | 通过训练写入模型参数 |

### 3.2 Memory Evolution（演化）

```text
Evolution Operator E: M_{t+1} = E(M^{form}_{t+1})
```

| 机制 | 作用 |
|---|---|
| Consolidation | 合并冗余条目、强化高频信息 |
| Updating | 更新过时信息、解决冲突 |
| Forgetting | 丢弃低效用信息、释放容量 |

### 3.3 Memory Retrieval（检索）

```text
Retrieval Operator R: m_t = R(M_t, o_t, Q)
```

| 维度 | 选择 |
|---|---|
| Timing | 任务初始化时 / 每步 / 按触发条件 |
| Query Construction | 原始查询 / 改写 / 多查询 |
| Strategy | 向量相似 / 图遍历 / 混合排序 |
| Post-Retrieval | 过滤 / 重排 / 摘要 / 格式化 |

## 4. Agent Memory vs 相关概念

| 概念 | 核心关注 | 与 Agent Memory 的关系 |
|---|---|---|
| LLM Memory | 模型内部 KV cache / 架构改进 | Agent Memory 几乎包含传统 "LLM Memory" |
| RAG | 从外部知识库检索增强生成 | Agent Memory 是持久、自演化的；RAG 是静态外部知识 |
| Context Engineering | 上下文窗口作为约束资源的管理 | Context Engineering 是 Agent Memory 的实现层 |

关键区分：Agent Memory 的独特性在于**持久性 + 自演化 + 跨任务积累**，而非只是单次推理的信息供给。

## 5. 前沿方向

| 方向 | 核心问题 | 状态 |
|---|---|---|
| Automated Memory Management | 不再手工设计记忆策略，用 RL/meta-learning 自动优化 | 活跃研究 |
| RL Meets Memory | 用强化学习训练 Agent 何时读/写/遗忘记忆 | 早期实践 |
| Multimodal Memory | 跨模态（视觉/音频/3D）的统一记忆 | 快速发展 |
| Shared Memory in Multi-Agent | 多 Agent 共享认知基底 | 早期探索 |
| Memory for World Model | 记忆支持内部世界模型构建 | 理论阶段 |
| Trustworthy Memory | 记忆的隐私、安全、可追溯、防污染 | 日益关键 |

## 6. 对本知识库的影响

| 现有模块 | 深化方向 |
|---|---|
| `paradigms/memory-paradigms.md` | 增加 Forms 维度：不只按生命周期分，也按承载形态分 |
| `architecture/planes/memory/overview.md` | 记忆写入策略增加 Formation/Evolution/Retrieval 三算子 |
| `architecture/planes/context/overview.md` | Context Engineering 明确定位为 Agent Memory 的实现层 |
| `architecture/learning/overview.md` | Experiential Memory 是 Skill Crystallization 的上位概念 |
| `design-space/frontier/` | RL+Memory、Multimodal Memory、Shared Memory 是新前沿 |

## 参考来源

- Hu et al. "Memory in the Age of AI Agents: A Survey" (arXiv:2512.13564v2, Jan 2026)
- 本知识库 Memory Paradigms、Memory Plane、Learning & Adaptation
