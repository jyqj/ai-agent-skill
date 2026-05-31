# Context Assembly 算法：从持久基底到注意力窗口的投影

> **所属域**：2. Cognition & Continuity — 上下文组装与投影
>
> **Evidence Status** — grounded. Anthropic 2026 Context Engineering 博客、Manus 2025 "Context Engineering for AI Agents" 博客、Google ADK 多 Agent 上下文传递机制、Zylos 投影模型、Park et al. 2023 "Generative Agents" 的三元评分。

**Principle Refs**: BR-02, BR-01 — 上下文信息随时间退化；窗口受显式资源预算约束。

---

## 1. 核心模型：投影，而非存储

上下文窗口是从持久基底到当前注意力的**投影面**，而非信息的存储容器。

```text
持久基底（文件系统 / Memory Plane / World State / Tool Registry）
    │
    │  Context Assembly Algorithm（投影函数）
    ▼
上下文窗口（有限 token 空间 × 有限注意力分辨率）
```

Zylos 投影模型将这个关系形式化：Agent 的所有知识、历史、工具定义构成一个巨大的"信息基底"，每次 LLM 调用只能看到基底的一个有限投影。投影函数的质量——选什么、排什么、压什么——直接决定推理质量。

**关键推论**：

- 信息不在窗口中 = 模型不可用；信息在窗口中但位置不当 = 模型可能忽略。
- 投影函数每个 ORDA-VU 循环都需要重新执行（参见 `../../../concepts/context-engineering.md`）。
- 投影的目标是"使期望结果概率最大化的最小高信号 token 集合"。

---

## 2. 三元评分模型

Park et al.（2023）在 Generative Agents 中提出的记忆检索评分公式，已成为上下文组装的经典参考：

```text
score = α · recency + β · importance + γ · relevance
```

| 维度 | 含义 | Agent 上下文中的映射 |
|---|---|---|
| Recency（时近性） | 信息最后被访问或产生的时间距离 | 最近 N 轮消息、最新工具输出 |
| Importance（重要性） | 信息的固有重要程度 | 用户目标、约束条件、关键决策点 |
| Relevance（相关性） | 信息与当前查询/任务的语义匹配度 | 与当前 milestone 语义相关的历史片段 |

**权重调优实践**：

| 场景 | α（recency） | β（importance） | γ（relevance） | 说明 |
|---|---|---|---|---|
| Coding Agent 调试循环 | 0.5 | 0.3 | 0.2 | 最近的错误信息最关键 |
| Research Agent 综合分析 | 0.2 | 0.3 | 0.5 | 语义相关性主导 |
| Enterprise 长流程 | 0.2 | 0.5 | 0.3 | 审批决策等关键节点不可丢失 |
| Browser Agent 导航 | 0.6 | 0.2 | 0.2 | 当前页面状态最重要 |

三元评分不要求精确计算，它提供的是一个**优先级排序框架**，用于在上下文空间不足时做取舍决策。

---

## 3. Cache-Aware 布局优化

KV-Cache 是生产 Agent 系统的核心成本杠杆。Manus 团队报告：缓存命中与未命中的 token 成本差异可达 **10 倍**。布局优化的目标是最大化 KV-Cache 命中率。

### 3.1 最优布局顺序

```text
┌─────────────────────────────────────────────┐
│ 1. Tool Definitions      （最稳定，几乎不变）  │  ← Cache 命中率最高
│ 2. System Instructions   （会话级稳定）       │
│ 3. Static Documents      （任务级稳定）       │
│ 4. History（含压缩摘要）  （缓慢增长）         │
│ 5. Current Observation   （每轮变化）         │  ← Cache 命中率最低
└─────────────────────────────────────────────┘
```

**核心原则**：稳定性从高到低排列。越稳定的内容放越前面，前缀越长命中率越高。

### 3.2 Append-Only 上下文

Cache 命中要求前缀严格匹配。因此：

- **追加而非插入**：新消息只能追加在末尾，不能插入到历史中间。
- **时间戳是 Cache 杀手**：在 system prompt 中嵌入当前时间（`Current time: 2026-05-07T10:23:45Z`）会导致每次调用都 cache miss。如需时间信息，放在最末尾的 observation 中。
- **工具定义顺序固定**：每次调用传入的 tool definitions 必须保持完全相同的顺序和内容。

### 3.3 KV-Cache 命中率作为生产指标

| 指标 | 健康范围 | 警告阈值 | 说明 |
|---|---|---|---|
| Cache Hit Rate | > 80% | < 60% | 前缀命中比例 |
| Cached Token Ratio | > 50% | < 30% | 缓存 token 占总输入 token 的比例 |
| Cost per Turn | 持续下降 | 突然跳升 | cache miss 会导致成本跳变 |

---

## 4. Position-Aware 放置策略

### 4.1 Lost in the Middle

Liu et al.（2023）的研究证实：当关键信息被放在长上下文的**中间位置**时，模型的提取准确率显著下降。模型对**开头**和**结尾**的信息利用率最高。

```text
注意力利用率
  高 ████                              ████
  中 ██                                  ██
  低      ████████████████████████████
     [开头]        [中间]          [结尾]
```

### 4.2 放置规则

| 信息类型 | 推荐位置 | 理由 |
|---|---|---|
| 系统指令 / 角色定义 | 开头 | 最高注意力 + cache 稳定 |
| 当前任务目标 | 开头（紧接系统指令） | 全程可见 |
| 不可压缩约束 | 开头 | 不能被忽略的硬约束 |
| 历史消息 | 中间 | 可容忍部分注意力损失 |
| 当前观察 / 最新工具输出 | 结尾 | 高注意力，紧邻模型输出位置 |
| todo.md 注意力召回 | 结尾 | 见 4.3 节 |

### 4.3 todo.md 注意力召回模式

Manus 团队发现的实践模式：在上下文末尾（紧接当前 observation 之前或之后）插入一段从 `todo.md` 文件读取的任务清单，强制模型在生成前"复述"当前目标和进度。

```text
[... 历史消息 ...]
[Current todo.md content]    ← 注意力召回锚点
[Latest observation]
[Model generation]
```

这个模式直接对抗 Lost-in-the-Middle 效应：即使早期的目标描述已经被淹没在中间位置，末尾的 todo 复述重新激活了目标注意力。

---

## 5. Action Space 管理

当 Agent 拥有大量工具时（> 20），工具定义本身成为上下文的主要消费者。

### 5.1 Mask Token Logits，而非移除工具

传统做法是动态增减可用工具列表。但这会破坏 cache：

```text
反模式：每轮根据状态动态传入不同的工具子集
  → tool definitions 变化 → cache 前缀失效 → 10x 成本跳变

正模式：始终传入完整工具列表，通过 logit masking 屏蔽不可用工具
  → tool definitions 不变 → cache 稳定 → 成本可控
```

Logit masking 在 token 采样阶段将被禁用工具的 function name token 概率置零，效果等同于移除工具，但不改变上下文内容。

### 5.2 工具分层加载

当工具数量极大（> 50）时，可采用分层策略：

| 层级 | 工具类型 | 策略 |
|---|---|---|
| 常驻层 | 核心工具（read、write、bash 等） | 始终在上下文中 |
| 按需层 | 领域工具（database、API 等） | 首次使用后常驻 |
| 发现层 | 长尾工具 | 工具注册表描述在上下文中，完整定义按需加载 |

---

## 6. Just-in-Time vs. Pre-Loading

两种上下文组装策略的对比：

| 维度 | Pre-Loading | Just-in-Time (JIT) |
|---|---|---|
| 策略 | 会话开始时加载所有可能需要的信息 | 每轮根据当前需要动态检索 |
| 优点 | 实现简单，无检索延迟 | token 效率高，信息新鲜 |
| 缺点 | 浪费 token，注意力稀释 | 检索质量依赖，增加延迟 |
| 适用场景 | 短会话、信息量可控 | 长会话、大知识库 |
| Cache 影响 | 首轮成本高但后续稳定 | 每轮检索结果变化可能影响 cache |

**生产建议**：混合模式，核心信息 pre-load，辅助信息 JIT。Anthropic 三策略中的 Sub-Agent 架构是 JIT 的极端形式：子 Agent 按需创建隔离上下文。

---

## 7. Google ADK: Narrative Reframing

Google Agent Development Kit 在多 Agent 上下文传递中引入了 Narrative Reframing（叙事重构）模式：

上下文从 Agent A 传递给 Agent B 时，A 的上下文会被**重构为 B 视角的叙事**，而非原样传递历史消息：

```text
Agent A 上下文：
  [用户请求] → [A 的工具调用] → [A 的中间推理] → [A 的结论]

Narrative Reframing 后传给 Agent B：
  "Agent A 已完成 X 任务，发现 Y，决策 Z。你的任务是基于此继续..."
```

**优势**：

- 消除 B 不需要的中间细节，降低 token 消耗
- 以 B 的任务视角重构信息，提高相关性
- 避免跨 Agent 的 prompt injection 风险（A 的原始用户输入不传给 B）

---

## 8. 组装流程总览

```text
┌────────────────────────────────────────────────┐
│              Context Assembly Pipeline          │
├────────────────────────────────────────────────┤
│ 1. 计算可用预算                                  │
│    available = window_limit - system - tools    │
│    - reserved_for_output - safety_buffer        │
│                                                │
│ 2. 评估持久基底                                  │
│    score(item) = α·recency + β·importance       │
│                + γ·relevance                    │
│                                                │
│ 3. 排序与选择                                    │
│    按 score 降序，填充至 available 预算           │
│                                                │
│ 4. Position-Aware 排列                          │
│    开头 ← 指令 / 目标 / 约束                     │
│    中间 ← 历史 / 摘要                            │
│    结尾 ← 最新观察 / todo 召回                    │
│                                                │
│ 5. Cache 兼容性检查                              │
│    验证前缀是否与上一轮匹配                        │
│    如不匹配，评估是否值得为 cache 牺牲排列         │
│                                                │
│ 6. 输出 Context Pack                            │
│    送入 Decide 阶段                              │
└────────────────────────────────────────────────┘
```

---

## 相关文件

| 主题 | 文件路径 |
|---|---|
| Context Plane 总览 | `overview.md` |
| Context Rot 退化模型 | `context-rot-model.md` |
| 压缩策略 | `compression-strategies.md` |
| Context Engineering 概念 | `../../../concepts/context-engineering.md` |
| 工作记忆动力学 | `../../../cognitive-architecture/working-memory-dynamics.md` |
| Compaction 模式 | `../../../design-space/patterns/compaction.md` |
| Memory Plane | `../memory/overview.md` |
