# Context Engineering

> **Evidence Status** — grounded。基于 Anthropic 2026 年工程博客 "Effective Context Engineering for AI Agents"、Compaction API 文档、成本优化语料（Zylos Token Economics）、以及本知识库 ORDA-VU 闭环和 Plane 体系的交叉综合。

---

## 从 Prompt Engineering 到 Context Engineering

2025-2026 年间，Agent 架构实践的一个核心认知升级是：**Prompt Engineering 不再足够描述我们实际在做的事情**。

Prompt Engineering 关注的是"如何写好一段提示词"——措辞、Few-shot 示例、格式约束。它隐含的假设是：上下文窗口足够装下所有信息，问题仅在于如何组织这些信息。

但在生产级 Agent 系统中，真正的瓶颈不是措辞，而是：

1. **上下文是有限资源**——128K 窗口看似很大，但 10 轮 ReAct 循环可消耗 50x 的 token，attention 矩阵以 n² 缩放。
2. **更长上下文必然降低精度和召回率**——transformer 的注意力稀释效应意味着"塞进去的信息越多，每条信息被利用的概率越低"。
3. **Agent 的上下文是动态组装的**——工具定义、工具返回值、历史消息、外部检索结果、子 Agent 摘要……这些在运行时持续变化。

**Context Engineering** 正是对这一现实的回应：它是一种**架构选择**，而不仅仅是 prompt 技巧。

---

## 定义：Context Engineering 是什么

Context Engineering 的核心公式：

> **发现"使期望结果概率最大化的最小高信号 token 集合"。**

具体而言，Context Engineering 关注以下问题：

- 此刻模型真正需要哪些信息？（信号选择）
- 哪些信息可以延迟到需要时再加载？（Just-In-Time 检索）
- 哪些信息已经过时，可以被摘要或丢弃？（Compaction）
- 如何在多轮交互中维持关键状态不丢失？（结构化笔记）
- 如何让子任务只看到与自己相关的上下文？（Sub-Agent 隔离）

它不是单一技术，而是一组协调使用的策略。

---

## Anthropic 三策略

Anthropic 在 2026 年工程博客和 Claude Code 实践中总结了三个核心 Context Engineering 策略：

### 策略一：Compaction API

**问题**：长会话中消息历史持续膨胀，最终撞上上下文窗口限制或导致注意力稀释。

**方案**：Compaction API (`compact-2026-01-12`) 在上下文接近极限时自动摘要旧消息，保留架构决策和关键状态，丢弃冗余输出。

**效果**：

- 有效会话长度延长 2-3x
- 摘要保留了"做了什么决策、为什么这样做"，丢弃了具体的中间输出文本
- 与 Prompt Caching 配合使用时，缓存命中率进一步提升

**设计要点**：

- Compaction 是有损操作——需要仔细设计摘要策略，确保关键上下文不被误丢
- 架构决策、约束条件、用户偏好应被标记为"不可压缩"
- 工具返回的原始数据是主要压缩对象

### 策略二：结构化笔记 / Scratchpad

**问题**：Agent 在长任务中容易"忘记"早期的上下文——即使信息还在窗口内，注意力稀释也会导致利用率下降。

**方案**：Agent 维护外部记忆文件（如 `NOTES.md`、`SCRATCHPAD.md`），主动将关键发现、决策和待办事项写入其中。

**效果**：

- 跨上下文重置持久化——即使上下文窗口被清空或 compaction，结构化笔记仍在
- Agent 的"工作记忆"从上下文窗口内迁移到外部文件，减少上下文压力

**设计要点**：

- 笔记应结构化（标题、编号、状态标记），而非自由文本
- Agent 需要被指示何时写入笔记、何时读取笔记
- 笔记更新本身消耗 token——需要平衡写入频率和收益

### 策略三：Sub-Agent 架构

**问题**：单一 Agent 处理复杂任务时，上下文中混杂了大量与当前步骤无关的信息。

**方案**：将复杂任务拆分给专用子 Agent，每个子 Agent 拥有隔离的上下文，只接收与自己任务相关的信息，完成后返回精炼摘要（1000-2000 token）。

**效果**：

- 上下文隔离——子 Agent 不被无关信息干扰
- 成本降低——子 Agent 的小上下文意味着更少的 token 消耗
- 质量提升——聚焦的上下文提高了任务完成质量

**设计要点**：

- 子 Agent 摘要的质量是关键——太简略会丢失信息，太详细会失去隔离的意义
- 主 Agent 需要足够的推理能力来正确分配和整合子任务
- 子 Agent 之间应避免共享上下文（除非通过主 Agent 显式传递）

---

## 与 Context Plane、Memory Plane、Prompting Plane 的关系重定义

Context Engineering 的出现促使我们重新审视知识库中三个相关 Plane 的边界和协作关系：

### 传统理解

- **Context Plane**：管理上下文窗口中的信息
- **Memory Plane**：管理跨会话的持久化记忆
- **Prompting Plane**：管理 system prompt 和提示策略

三者被视为相对独立的层面。

### Context Engineering 视角下的重定义

Context Engineering 揭示了这三个 Plane 实际上是**同一个信息流的不同阶段**：

```text
信息源（Memory Plane 存储）
    → 检索与选择（Context Engineering 决策）
    → 组装与排列（Context Plane 管理）
    → 格式与指令（Prompting Plane 呈现）
    → 模型消费
```

**关键变化**：

| Plane | 传统职责 | Context Engineering 后的职责 |
|-------|---------|---------------------------|
| **Memory Plane** | 存储与检索 | 存储 + **信号标记**（标注信息的时效性、重要性、压缩优先级） |
| **Context Plane** | 窗口管理 | **动态组装**（Just-In-Time 检索、Compaction、Sub-Agent 上下文隔离） |
| **Prompting Plane** | 指令设计 | **最小有效指令**（System Prompt Goldilocks Zone——足够具体但不脆弱） |

**新增的协调层**——Context Assembly：

Context Engineering 本质上是在 Memory Plane 和 Context Plane 之间插入了一个**协调决策层**，负责回答"此刻需要什么信息"。这个层面以前由 Prompt Engineering 隐式处理，现在需要显式设计。

---

## 对 ORDA-VU 的影响

Context Engineering 对 ORDA-VU 闭环最显著的影响在 **Represent → Decide** 之间——需要一个 **Context Assembly** 步骤：

```text
Observe    接收输入、工具结果、外部状态
    ↓
Represent  构造 Observation / ContextPack / WorldStateSnapshot
    ↓
[Context Assembly]  ← Context Engineering 的核心作用点
    │
    ├─ 评估当前上下文利用率
    ├─ 决定是否触发 Compaction
    ├─ 决定是否需要从 Memory Plane 检索更多信息
    ├─ 决定是否派发子 Agent（上下文隔离）
    └─ 组装最终送入 Decide 阶段的 token 集合
    ↓
Decide     基于精选上下文做出行动决策
    ↓
Act        执行工具调用
    ↓
Verify     结果校验
    ↓
Update     更新 TaskState / Memory / 结构化笔记
```

**关键洞察**：

1. Context Assembly 不是一次性操作——每次 ORDA-VU 循环都需要重新执行。
2. Update 阶段负责将新信息写入结构化笔记和 Memory Plane，为下一轮的 Context Assembly 提供输入。
3. 当推理模型参与时（参见 `paradigms/reasoning-model-integration.md`），推理 token 本身也成为上下文管理的对象——过度推理会挤占工具结果和检索信息的空间。

---

## 设计启发

### 1. "做最简单的有效方案"

Anthropic 的核心设计哲学。不要因为 Context Engineering 概念丰富就全部用上——从最简单的策略开始，仅在实际遇到瓶颈时升级：

```text
Level 0: 良好的 System Prompt + 必要的工具定义
Level 1: + Prompt Caching
Level 2: + Compaction API（长会话场景）
Level 3: + 结构化笔记（跨轮次/跨重置场景）
Level 4: + Sub-Agent 架构（复杂多步任务）
Level 5: + 动态工具发现（工具数量 > 10）
```

### 2. "更聪明的模型需要更少的规定性工程"

模型能力提升会减少 Context Engineering 的手动工作量。Adaptive Thinking 就是例子——模型自主决定推理深度，减少了手动 budget 管理。但这不意味着可以不做 Context Engineering，而是意味着策略可以更高层次。

### 3. 工具设计是 Context Engineering 的一部分

重叠或歧义的工具浪费 token 在决策上；工具应返回 token 高效的结果。工具定义的体积直接影响上下文利用率。

### 4. 信号密度优于信息量

```text
反模式：将 20 页文档全文注入上下文
正模式：提取关键段落 + 结构化摘要 + 按需深入检索
```

Just-In-Time 检索模式类似人类使用索引而非记忆全文。

### 5. Token 预算是上下文的硬约束

```text
可用 Context = 窗口限制 - System Prompt - 工具定义 - 推理 Token 预留
实际有效 Context < 可用 Context（注意力稀释）
```

推理模型的 extended thinking token 会挤占可用上下文——Context Engineering 需要与推理预算管理协调。

### 6. 压缩 + 路由 + 缓存的组合效果

单一策略的效果有限，组合使用是生产最佳实践：

| 策略组合 | 预期效果 |
|---------|---------|
| Prompt Caching 单独 | ~70-80% 缓存 token 成本削减 |
| + Model Routing | + 最高 87% 非缓存成本削减 |
| + Compaction | + 2-3x 有效会话延长 |
| 三者组合 | 60-80% 总成本削减 |

---

## 与知识库的映射

| 本文主题 | 知识库对应文件 | 关系 |
|---------|--------------|------|
| 三 Plane 关系重定义 | `architecture/planes/` | 重新定义 Context/Memory/Prompting Plane 的边界 |
| ORDA-VU 影响 | `paradigms/reasoning-paradigms.md` | 在 Represent → Decide 间插入 Context Assembly |
| 推理模型交互 | `paradigms/reasoning-model-integration.md` | 推理 token 与上下文空间的张力关系 |
| Compaction | `architecture/lifecycle.md` | Compaction 是生命周期中上下文管理的关键环节 |
| Sub-Agent 架构 | `architecture/multi-model/` | Sub-Agent 是 Context Engineering 的架构级手段 |
| 工具设计 | `architecture/planes/tool-integration/` | 工具定义体积是上下文预算的组成部分 |
| 成本优化 | `paradigms/control-paradigms.md` | Token 预算管理是控制范式的新维度 |
| 结构化笔记 | `paradigms/memory-paradigms.md` | 结构化笔记是工作记忆外化的具体手段 |
| 设计哲学 | `concepts/design-principles.md` | "做最简单的有效方案"对接设计原则 |

---

相关文件：`../paradigms/reasoning-paradigms.md`、`../paradigms/reasoning-model-integration.md`、`../architecture/planes/`、`../paradigms/memory-paradigms.md`、`../concepts/design-principles.md`。
