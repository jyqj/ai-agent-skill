# Exploration & Discovery

> **Evidence Status** — synthesized. Gulli (2025) *Agentic Design Patterns* Ch21 + Google Co-Scientist 架构归纳。

## 问题

大多数 Agent 是 reactive 的：给定任务 → 执行 → 交付。它们缺乏在未知空间中主动探索、生成假设、验证发现的能力。这限制了 Agent 在科学研究、开放式问题求解、创意探索等领域的应用。

## 解法

Exploration & Discovery 模式赋予 Agent 主动探索未知空间的能力，通过假设-验证循环在不确定性中渐进式推进。

## 与 Exploitation 的权衡

| | Exploitation（利用） | Exploration（探索） |
|---|---|---|
| **目标** | 最大化已知策略的回报 | 发现新策略或新知识 |
| **风险** | 低：使用经过验证的路径 | 高：结果不确定 |
| **适用** | 重复性任务、生产环境 | 研究、创新、开放式问题 |
| **成本** | 可预测 | 不可预测，需要预算上限 |

**平衡策略**：
- epsilon-greedy：大部分时间利用，小概率探索
- 预算分配：为探索预留固定比例资源
- 信息增益驱动：优先探索预期信息增益最高的方向

## 核心架构：假设-验证循环

以 Google Co-Scientist 为参考，完整的探索系统包含多个专业化 Agent：

```text
┌─────────────────────────────────────────────────┐
│              Exploration Loop                    │
│                                                  │
│  Generation Agent ──→ Reflection Agent           │
│       ↑                     ↓                    │
│  Evolution Agent      Ranking Agent              │
│       ↑                     ↓                    │
│  Proximity Agent ←── Meta-review Agent           │
│                                                  │
└─────────────────────────────────────────────────┘
```

| Agent | 职责 |
|---|---|
| **Generation** | 通过文献探索和模拟辩论生成初始假设 |
| **Reflection** | 作为同行评审，批判性评估假设（正确性、新颖性、质量） |
| **Ranking** | 通过 Elo-based 锦标赛比较和排序假设 |
| **Evolution** | 持续精炼排名靠前的假设（简化、综合、非常规推理） |
| **Proximity** | 计算假设相似度图谱，聚类相近想法 |
| **Meta-review** | 综合所有评审和辩论的洞察，识别跨假设的模式 |

## 探索阶段模型

### Phase 1: Literature / Knowledge Review
- 自主收集和批判性分析已有知识
- 识别知识缺口和矛盾点
- 输出：知识地图 + 开放问题清单

### Phase 2: Hypothesis Generation & Experimentation
- 协作式实验设计
- 数据准备、代码生成/执行
- 假设的可证伪性检验

### Phase 3: Synthesis & Reporting
- 自动生成研究报告
- 知识共享（如 AgentRxiv 概念——Agent 间知识发布平台）

## 适用品类

| 品类 | 探索维度 | 示例 |
|---|---|---|
| Research Agent | 科学假设空间 | 药物靶点发现、材料性质预测 |
| Coding Agent | 解决方案空间 | 算法优化、架构替代方案 |
| Creative Agent | 创意空间 | 叙事可能性、风格变体 |
| Security Agent | 攻击面空间 | 漏洞发现、渗透路径探索 |
| Data/BI Agent | 数据模式空间 | 异常检测、隐藏相关性发现 |

## 与知识库其他模块的关系

| Plane | 交互方式 |
|---|---|
| Learning & Adaptation | 探索结果固化为可学习对象 |
| Cost | 探索需要预算上限（不可预测的成本） |
| Memory | 探索历史（已尝试的假设、失败的方向）需要持久化 |
| Orchestration | 多 Agent 探索需要编排（Generation → Reflection → Ranking） |
| Observability | 探索过程需要完整 trace 以支持事后分析 |

## 反模式

- **Blind Exploration**：无方向随机探索 → 需要信息增益或好奇心信号引导
- **Premature Convergence**：过早收敛到第一个"足够好"的假设 → 需要多样性保持机制
- **Exploration Without Exploitation**：只探索不利用 → 需要将发现转化为可执行策略
- **No Memory**：重复探索已知失败的方向 → 需要探索历史记录

## 参考

- Gulli, A. (2025). *Agentic Design Patterns*, Ch21: Exploration and Discovery.
- Google Co-Scientist: Multi-agent hypothesis generation, debate, and evolution.
- AgentRxiv: Agent 间知识共享平台概念.
- Schmidhuber, J. (2010). "Formal Theory of Creativity, Fun, and Intrinsic Motivation" — 好奇心驱动探索的理论基础.
