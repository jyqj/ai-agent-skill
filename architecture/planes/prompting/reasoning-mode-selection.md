# Reasoning Mode Selection — 运行时推理模式选择

>
> **所属域**：2. Cognition & Continuity — 指令结构与推理模式
>
> **Evidence Status** — grounded. Framework of Thoughts (arXiv 2602.16512) 对推理拓扑的统一有向多重图抽象；DR-CoT (Nature 2025) 对 Chain-of-Thought 动态路由的实证研究；Claude Adaptive Thinking 文档中 effort 参数与 interleaved thinking 的生产实践；DSPy / TextGrad 的元优化模式。

**Principle Refs**: BR-01, EM-02 — 推理消耗受资源预算约束；能力 = 模型 × Harness 设计。

推理模式不是固定配置。生产 Agent 需要在运行时根据任务复杂度、风险等级和可用预算动态选择推理策略。

## 1. 推理模式谱系

从简单到复杂，推理模式构成一个成本递增的谱系：

| 模式 | 核心机制 | Token 消耗倍率 | 适合 | 风险 |
|---|---|---|---|---|
| Direct | input → output | 1x | 简单问答、低风险格式化 | 复杂任务过度简化 |
| Tool-Augmented | input → tool call → output | 2-5x | 查询、计算、单步检索 | 工具滥用 |
| ReAct | Thought → Action → Observation 循环 | 5-15x | 边做边看的探索性任务 | 循环、观察溢出 |
| Plan-Execute | plan → step execution → aggregation | 10-20x | 多步骤可拆解任务 | 计划僵化 |
| Reflection | output → critique → revise | 10-25x | 需要质量自检的高风险输出 | 反思空转 |
| Tree/Graph Search | branch → evaluate → prune/merge | 20-50x | 方案探索、多候选比较 | 成本爆炸 |

### Token 消耗的非线性特征

```text
Direct:      ████ (1x)
Tool-Aug:    ████████████ (2-5x)
ReAct:       ████████████████████████████████ (5-15x)
Plan-Exec:   ████████████████████████████████████████████████████ (10-20x)
Reflection:  ██████████████████████████████████████████████████████████████████ (10-25x)
Tree/Graph:  ██████████████████████████████████████████████████████████████████████████████████████████████████████ (20-50x)
```

## 2. Framework of Thoughts (FoT)

FoT (arXiv 2602.16512) 提出了一种统一视角：所有推理模式都是有向多重图（directed multigraph）上的不同拓扑。

### 统一表示

```text
FoT Graph = (Nodes, Edges, Topology)

Node = 一个推理步骤（thought / action / observation / critique）
Edge = 步骤间的依赖或信息流
Topology = 图的结构约束

Chain (CoT):    A → B → C → D          线性
Tree (ToT):     A → {B1, B2, B3} → C   分支 + 剪枝
Graph (GoT):    A → {B, C}, B → D, C → D   合并 + 交叉
Adaptive:       运行时动态构造拓扑
```

### FoT 的设计价值

| 价值 | 说明 |
|---|---|
| 统一框架 | CoT、ToT、GoT、Self-Consistency 等都是同一图上的特例 |
| 动态拓扑 | 运行时根据中间结果决定下一步是分支、合并还是回溯 |
| 可组合 | 不同推理模式可以在同一任务的不同阶段切换 |
| 可分析 | 图结构可用于成本估算、瓶颈检测和 trace 分析 |

## 3. 运行时选择标准

推理模式的选择由四个维度共同决定：

### 3.1 选择矩阵

| 维度 | 低值 | 高值 | 对推理模式的影响 |
|---|---|---|---|
| 任务复杂度 | 单步可完成 | 多步骤、多约束 | 低 → Direct；高 → Plan-Execute / Tree |
| 风险等级 | read-only、可逆 | 写操作、不可逆 | 低 → ReAct；高 → Reflection + Verification |
| 可用预算 | 严格 token/cost 限制 | 充裕预算 | 低 → Direct / Tool-Aug；高 → 按需升级 |
| 模型能力 | 小模型、推理弱 | 大模型、强推理 | 弱 → 外部验证；强 → 可信赖内部反思 |

### 3.2 动态路由逻辑

```text
RouteReasoning(task, context, budget):
  complexity = assess_complexity(task)
  risk = assess_risk(task.effects)
  remaining_budget = budget - context.tokens_used

  if complexity == low AND risk == low:
    return Direct
  if complexity == low AND needs_external_data:
    return ToolAugmented
  if complexity == medium AND risk <= check:
    return ReAct(max_iterations=5)
  if complexity == high AND task.is_decomposable:
    return PlanExecute(checkpoint_interval=3)
  if risk == high OR task.requires_verification:
    return Reflection(evidence_bound=true)
  if task.has_multiple_valid_approaches:
    return TreeSearch(branch_budget=3, evaluator=rubric)

  # 预算兜底
  if remaining_budget < threshold:
    return downgrade(current_mode)
```

## 4. Claude Adaptive Thinking

Claude 的自适应思考是运行时推理模式选择的生产实现：

### 4.1 effort 参数

| effort | 含义 | 适合 | Token 开销 |
|---|---|---|---|
| `low` | 最小思考，快速响应 | 简单问答、格式转换 | 最低 |
| `medium` | 默认平衡 | 大多数任务 | 中等 |
| `high` | 深度推理 | 复杂分析、多步骤任务 | 较高 |
| `max` | 最大推理深度 | 数学证明、复杂代码架构 | 最高 |

### 4.2 模型自评复杂度

Claude 在收到请求后会自评任务复杂度，决定思考深度：

```text
用户请求 → 复杂度自评 → 选择思考深度 → 推理 → 输出

自评信号：
  - 任务类型（问答 / 分析 / 编码 / 规划）
  - 约束数量（多约束 → 深思考）
  - 歧义程度（高歧义 → 需要更多推理）
  - 显式 effort 参数覆盖自评结果
```

### 4.3 Interleaved Thinking

在 Agentic 工作流中，Claude 支持交错思考模式：

```text
Think → Act → Observe → Think → Act → Observe → ...

每次 Observe 后，模型重新评估：
  - 是否需要调整推理深度
  - 是否需要切换推理模式
  - 是否有足够信息直接输出
```

这与 ORDA-VU 闭环中的 Decide 阶段天然对应：每轮 Observe 后的 Think 就是 Decide 前的推理。

## 5. DR-CoT：动态路由 Chain-of-Thought

DR-CoT (Nature 2025) 的核心发现是：并非所有问题都需要 Chain-of-Thought，强制 CoT 在简单问题上反而降低准确率。

### DR-CoT 路由策略

| 问题特征 | 路由决策 | 依据 |
|---|---|---|
| 模型置信度 > 95% | 跳过 CoT，直接回答 | 简单问题上 CoT 引入噪声 |
| 模型置信度 60-95% | 标准 CoT | 中等难度受益于显式推理 |
| 模型置信度 < 60% | 增强 CoT + 自一致性 | 困难问题需要多路径验证 |
| 模型置信度极低 | 升级模型或请求外部帮助 | 当前模型能力不足 |

### 与 Agent 的整合

```text
Agent Loop 中的 Decide 阶段：
  1. 生成初步推理
  2. 评估推理置信度
  3. 置信度高 → 直接 Act
  4. 置信度低 → 增加推理深度或切换模式
  5. 推理深度增加后仍低 → 请求外部验证或用户确认
```

## 6. 元提示与自优化

### 6.1 DSPy 模式

DSPy 把 prompt 工程转化为可编程的模块优化：

| 概念 | 含义 |
|---|---|
| Signature | 输入/输出类型声明 |
| Module | 可组合的推理步骤 |
| Optimizer | 自动搜索最优 prompt/few-shot/模式组合 |
| Metric | 任务级评估指标 |

```text
Signature: question → reasoning, answer
Module: ChainOfThought(Signature)
Optimizer: BootstrapFewShot(metric=accuracy, max_demos=5)
```

### 6.2 TextGrad 模式

TextGrad 用"文本梯度"迭代优化 prompt：

```text
Round 1: 运行 prompt → 评估结果 → 生成文本反馈（gradient）
Round 2: 用反馈修改 prompt → 重新评估 → 生成新反馈
...
收敛：结果满足指标或达到迭代上限
```

### 6.3 Self-Refinement 循环

```text
Generate → Critique → Refine → Evaluate

约束：
  - 每轮 Critique 必须有具体证据，不能空泛地说"可以更好"
  - Refine 次数有上限（通常 2-3 轮）
  - Evaluate 应使用外部指标，避免模型自我满足
```

## 7. 推理模式与 PromptContract 映射

| PromptContract.reasoning_mode | 推荐实现 | 关键控制 |
|---|---|---|
| `direct` | Direct / Tool-Augmented | claim caution、来源声明 |
| `react` | ReAct Loop | max_iterations、observation normalization |
| `plan_execute` | Plan-and-Execute | plan checkpoint、step verification |
| `reflection` | Critique-Revise | evidence-bound、revision budget |
| `critique` | Independent Verifier | rubric、外部证据 |
| `adaptive` | FoT Dynamic Topology | budget monitor、mode switching |

## 8. 反模式

| 反模式 | 问题 | 修复 |
|---|---|---|
| Always-CoT | 所有请求都强制 CoT，简单问题浪费 token | 按复杂度路由 |
| Reflection Without Evidence | 反思不引入新信息，原地空转 | 每轮 critique 必须有外部证据 |
| Static Mode Lock | 启动时选定模式，全程不变 | 运行时动态评估和切换 |
| Budget Blindness | 不考虑 token 预算，高开销模式跑满 | 预算监控 + 降级策略 |
| Over-Planning | 简单任务也生成详细计划 | 复杂度评估前置 |
| Self-Satisfying Refinement | 模型自评越改越好，实际无提升 | 外部评估指标 |

## 9. 关联模块

- `overview.md` — PromptContract 中的 reasoning_mode 定义
- `instruction-layering.md` — 推理模式执行依赖正确的指令层级
- `../../../paradigms/reasoning-paradigms.md` — 推理范式的静态选择矩阵
- `../../../paradigms/paradigm-routing.md` — 运行时范式切换的触发条件和状态迁移
- `../../../cognitive-architecture/` — 工作记忆、元认知控制对推理深度的约束
- `../control/overview.md` — 控制面管理推理预算和降级策略
- `../../cross-cutting/` — Paradigm × Cost 交叉设计

## 10. 检查清单

- [ ] 是否根据任务复杂度选择推理模式，而非一律使用最复杂的模式？
- [ ] 运行时是否有预算监控和降级机制？
- [ ] Reflection 是否绑定了外部证据要求？
- [ ] 推理模式切换时，中间状态是否正确迁移？
- [ ] 是否为 Agentic 工作流启用了 interleaved thinking？
- [ ] 元优化（DSPy / TextGrad）的迭代次数是否有上限？
