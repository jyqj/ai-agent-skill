# 品类认知特化：不同 Agent 的认知需求差异

> **Evidence Status** — synthesized. 基于知识库已有品类架构和认知架构的交叉分析。

## 1. 为什么需要这篇

认知架构层的每篇文档（记忆、推理、目标、注意力、元认知、情绪/动机、创意认知）都假设对所有品类适用。理论上成立，因为每个 Agent 都有某种形式的记忆和推理。但在实践中，**需求差异巨大**：

- Coding Agent 需要极强的演绎推理和工作记忆，但几乎不需要情绪系统
- Companion Agent 需要极强的心智理论和情感响应，但推理复杂度较低
- Creative Agent 需要发散认知和风格一致性，但目标层级相对简单

如果不区分这些差异，设计者容易犯两类错误：

1. **过度设计**：为任务交付型 Agent 添加不必要的情绪模块
2. **设计不足**：为 Companion Agent 使用纯工具调用架构而忽略心智理论

本文通过热力图和差异分析，帮助设计者快速定位某个品类的认知重点。

## 2. 认知需求热力图

H = 高需求（核心能力，缺失则品类不成立）
M = 中需求（有明确收益，但非核心）
L = 低需求（可选，大多数场景不需要）

| 品类 | 工作记忆 | 目标层级 | 推理模式 | 注意力 | 心智理论 | 元认知 | 情绪/动机 | 创意认知 |
|---|---|---|---|---|---|---|---|---|
| Coding Agent | H | H | H(演绎/溯因) | H | M | H | L | M |
| Research Agent | H | M | H(归纳/溯因) | H | L | H | L | M |
| Browser/Desktop | H | M | M | H(视觉) | M | M | L | L |
| Enterprise Workflow | M | H | M(演绎) | M | M | M | L | L |
| Companion Agent | H | M | M | M | H | M | H | M |
| Creative Agent | M | L | M(类比) | M | M | H | M | H |
| Security Agent | H | H | H(溯因) | H | L | H | L | L |
| Ops/SRE Agent | H | H | H(溯因/因果) | H | L | M | L | L |
| Data/BI Agent | M | M | H(演绎) | M | L | M | L | L |
| Personal Memory | M | L | M | M | H | M | M | L |
| Embodied Robot | H | H | H(因果) | H(多模态) | M | H | L | L |

## 3. 关键差异说明

### 3.1 Coding Agent vs Companion Agent

这是差异最大的品类对，代表了两种截然不同的认知重心：

| 维度 | Coding Agent | Companion Agent | 差异原因 |
|---|---|---|---|
| 推理模式 | H — 代码理解需要演绎+溯因 | M — 日常对话不需要深度推理 | 代码有精确语义，对话有模糊性 |
| 心智理论 | M — 理解用户意图有帮助 | H — 核心能力，必须理解用户状态 | Companion 的价值在于"理解你" |
| 情绪/动机 | L — 外部 TaskEnvelope 驱动 | H — 需要感知和回应情感 | 任务驱动 vs 关系驱动 |
| 元认知 | H — 需要判断"方案是否正确" | M — 需要判断"回应是否恰当" | 两者都需要，但触发条件不同 |
| 目标层级 | H — 分解复杂需求为子任务 | M — 目标较简单（陪伴、支持） | 任务复杂度的差异 |

**设计启发**：不要用 Coding Agent 的架构模板去构建 Companion Agent。Coding Agent 的核心是 Plan-Execute-Verify 循环；Companion Agent 的核心是 Perceive-Understand-Respond 循环。

### 3.2 Research Agent vs Creative Agent

两者都涉及"生成新内容"，但认知路径不同：

| 维度 | Research Agent | Creative Agent | 差异原因 |
|---|---|---|---|
| 推理模式 | H(归纳/溯因) — 从证据归纳结论 | M(类比) — 跨域迁移和组合 | 研究追求真，创意追求新 |
| 创意认知 | M — 需要生成新假设 | H — 核心能力 | 假设生成 vs 方案创造 |
| 目标层级 | M — 研究问题相对明确 | L — 创意方向可以自由发散 | 收敛 vs 发散的侧重 |
| 元认知 | H — 需要评估证据质量 | H — 需要评估创意质量 | 都需要高元认知，但评估标准不同 |
| 注意力 | H — 海量文献中筛选相关信息 | M — 信息输入相对集中 | 信息过载程度的差异 |

**设计启发**：Research Agent 的管线以**证据质量**为核心指标；Creative Agent 的管线以**输出多样性 + 风格一致性**为核心指标。两者的元认知都很重要，但 Research Agent 的元认知问"这个结论可靠吗？"，Creative Agent 的元认知问"这个方案有趣吗？"。

### 3.3 Security Agent vs Browser/Desktop Agent

两者都与计算机环境交互，但认知需求差异明显：

| 维度 | Security Agent | Browser/Desktop Agent | 差异原因 |
|---|---|---|---|
| 推理模式 | H(溯因) — 从异常回溯根因 | M — 多为确定性操作序列 | 安全分析需要深度推理 |
| 目标层级 | H — 多目标平衡（检测+响应+修复） | M — 通常单目标任务链 | 安全场景的复杂性更高 |
| 注意力 | H — 海量日志中发现异常 | H(视觉) — GUI 元素识别和定位 | 注意力的模态不同 |
| 元认知 | H — 误报/漏报的自我评估 | M — 操作成功/失败相对明确 | 安全分析的不确定性更高 |

**设计启发**：Security Agent 需要更强的溯因推理引擎和不确定性管理；Browser/Desktop Agent 需要更强的视觉感知和操作确认机制。

### 3.4 Ops/SRE Agent vs Data/BI Agent

同样面向"数据密集"场景，但认知侧重不同：

| 维度 | Ops/SRE Agent | Data/BI Agent | 差异原因 |
|---|---|---|---|
| 推理模式 | H(溯因/因果) — 故障根因分析 | H(演绎) — 从数据推导结论 | 故障诊断 vs 数据分析 |
| 目标层级 | H — 恢复+预防+优化多层目标 | M — 查询→分析→报告较线性 | SRE 目标更复杂 |
| 工作记忆 | H — 需要同时追踪多个系统状态 | M — 通常单数据集操作 | 系统复杂度的差异 |
| 注意力 | H — 多源告警中优先级排序 | M — 数据源相对集中 | 信息源数量的差异 |

## 4. 对架构选择的影响

认知特化直接影响运行时 plane 的配置优先级：

### 4.1 Memory Plane 配置

```text
高工作记忆需求（Coding, Research, Security, Ops, Embodied）：
  → 更大的上下文窗口或显式工作记忆缓冲区
  → 更积极的记忆压缩和摘要策略
  → 多层记忆（工作记忆 + 长期记忆 + 情境记忆）

低工作记忆需求（Creative, Personal Memory）：
  → 标准上下文窗口通常足够
  → 重点放在长期记忆的持久化和检索
```

### 4.2 Reasoning Engine 配置

```text
高推理需求 + 演绎为主（Coding, Data/BI）：
  → 需要代码执行验证环、形式化验证支持
  → 推理链要求可追溯、可审计

高推理需求 + 溯因为主（Security, Ops/SRE）：
  → 需要假设生成-验证循环
  → 多假设并行追踪

中推理需求 + 类比为主（Creative）：
  → 需要跨域知识检索
  → 约束放松机制（见 creative-cognition.md）
```

### 4.3 Interaction Plane 配置

```text
高心智理论需求（Companion, Personal Memory）：
  → 用户状态建模模块
  → 情感检测和响应策略
  → 对话历史中的关系追踪

低心智理论需求（Research, Security, Data/BI）：
  → 标准的指令-响应交互即可
  → 重点放在输出的准确性和可解释性
```

### 4.4 Control Plane 配置

```text
高元认知需求（Coding, Research, Security, Creative, Embodied）：
  → 显式的反思触发机制（见 metacognitive-control.md）
  → 置信度追踪
  → 策略切换逻辑

低元认知需求（Browser/Desktop, Enterprise Workflow）：
  → 基于规则的执行控制通常足够
  → 失败重试 + 上报即可
```

## 5. 使用指南

1. **确定品类**：你要构建的 Agent 最接近哪个品类？
2. **查阅热力图**：找到该品类行，识别 H 列（核心能力）和 L 列（可省略）
3. **深入 H 列**：对每个 H 维度，阅读对应的认知架构文档获取设计指导
4. **跳过 L 列**：除非有特殊需求，L 维度不需要投入设计资源
5. **关注 M 列**：M 维度根据具体场景决定是否投入，通常可以用简单实现覆盖

## 6. 延伸阅读

- `../cognitive-architecture/working-memory-dynamics.md` — 工作记忆
- `../cognitive-architecture/goal-hierarchy.md` — 目标层级
- `../cognitive-architecture/reasoning-modes.md` — 推理模式
- `../cognitive-architecture/attention-and-salience.md` — 注意力
- `../cognitive-architecture/theory-of-mind.md` — 心智理论
- `../cognitive-architecture/metacognitive-control.md` — 元认知
- `../cognitive-architecture/emotion-and-motivation.md` — 情绪与动机
- `../cognitive-architecture/creative-cognition.md` — 创意认知
