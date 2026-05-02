# 工作记忆动力学——上下文不是简单缓冲

> **Evidence Status** — mixed. 工作记忆理论来自认知心理学（Baddeley、Cowan、Miller），LLM Agent 映射为实践推导。

## 1. 为什么需要这篇

多数 Agent 系统把 Context Window 当作一个先进先出的缓冲区：新消息追加、旧消息截断。这种处理忽略了认知科学中关于工作记忆的核心发现——容量有限、注意力驱动、主动维护与被动衰减并存。理解这些机制，能帮助我们设计更有效的上下文管理策略。

## 2. 经典认知科学中的工作记忆

### 2.1 容量限制

Miller（1956）提出短期记忆容量约 7 +/- 2 个组块（chunk）。Cowan（2001）修正为约 4 个组块。关键不是绝对数量，而是：

- 容量以**组块**计，不以原子信息计——有效组块化（chunking）可以在固定容量内装更多信息
- 容量是硬约束，不是可以通过"努力"突破的软限制

### 2.2 注意力驱动

Baddeley 的工作记忆模型包含一个**中央执行器**（Central Executive），负责：

- 决定哪些信息进入工作记忆
- 分配注意力资源
- 协调多个子系统（语音环路、视觉空间画板等）

工作记忆不是被动接收，而是主动选择。

### 2.3 维护与衰减

- **主动维护**（active maintenance）：通过复述（rehearsal）保持信息——需要注意力资源
- **被动衰减**（passive decay）：不被复述的信息逐渐消退
- **干扰效应**（interference）：新信息可能覆盖或干扰旧信息的提取

## 3. LLM Agent 的工作记忆 = Context Window

| 认知科学概念 | LLM Agent 对应 | 说明 |
|---|---|---|
| 容量限制 | Token 限制 | 128K/200K tokens 看似很大，但对长任务仍然不够 |
| 组块化 | Context Pack 设计 | 把相关信息打包成结构化组块，比散乱追加高效 |
| 被动衰减 | Context Rot | 早期信息在长上下文中被"遗忘"——不是物理删除，而是注意力权重下降 |
| 干扰效应 | 新工具输出覆盖旧推理 | 大量工具返回结果可能冲淡之前的推理链 |
| 主动维护 | Pinning / 关键信息标记 | 把重要信息显式保持在上下文中 |
| 中央执行器 | Context Engine 策略 | 决定什么该保留、什么该驱逐、什么该从 LTM 检索 |

### 3.1 Context Rot 的认知解释

Context Rot 不是简单的"旧信息被删了"。在 Transformer 架构中，早期 token 的注意力权重会被后续大量 token 稀释。这与认知科学中的干扰效应高度类似：不是信息消失了，而是被新信息"淹没"了。

对策不是"保留所有旧信息"，而是：

1. 识别关键信息并主动维护（pinning）
2. 对非关键信息进行组块化压缩
3. 将低频但重要的信息转移到长期记忆（LTM），需要时再检索

### 3.2 超越简单缓冲的设计

**注意力分配**：不是所有上下文内容权重相等。关键信息（当前目标、约束、最近的关键观察）应该被主动维护，而背景信息可以被压缩或外化。

```text
高优先级（pin）：当前任务目标、用户约束、关键错误信息
中优先级（keep）：最近 N 步的推理链、工具结果摘要
低优先级（compress/evict）：早期探索的细节、已完成子任务的中间过程
```

**组块化**：有效利用有限容量的核心策略。不是"删掉旧内容"，而是"把 10 条工具输出压缩成 1 个结构化摘要"。

**中央执行器**：Context Engine 不应该只做 FIFO 截断。它应该：

- 根据当前任务阶段动态调整保留策略
- 在驱逐信息前，先将其写入外部存储（State Plane / Memory Plane）
- 在需要时从 LTM 主动检索相关信息回填

## 4. 多模态工作记忆

Baddeley 模型中的工作记忆不是单一缓冲，而是包含多个子系统：语音环路（phonological loop）、视觉空间画板（visuospatial sketchpad）和情景缓冲器（episodic buffer）。LLM Agent 的工作记忆同样可能包含多种模态的信息：

| 认知子系统 | Agent 对应 | 管理策略 |
|---|---|---|
| 语音环路 | 文本对话历史 | 主线上下文，按对话轮次管理 |
| 视觉空间画板 | 截图、图表、UI 状态 | 多模态 token 成本高，优先用文字描述替代 |
| 情景缓冲器 | 跨工具结果的整合视图 | 需要显式构造，不会自动形成 |

设计启发：当 Agent 同时处理代码、日志、截图和对话时，不同模态的信息应该有不同的保留策略。截图的 token 成本远高于文字摘要——在不损失关键信息的前提下，应优先将视觉信息转化为结构化文字描述。

情景缓冲器尤其重要：Agent 在执行多步任务时，需要一个**整合视图**把多个工具返回的碎片信息拼成连贯画面。这不会自动发生——需要在 Context Pack 中显式构造。

## 5. 与运行时模块的映射

| 运行时模块 | 认知角色 | 设计影响 |
|---|---|---|
| Context Plane | 工作记忆的容器 | 需要支持优先级标记、组块化、动态重组 |
| Memory Plane | 长期记忆（LTM） | 通过 retrieval 将信息加载进工作记忆；检索策略应考虑当前任务阶段 |
| Prompting Plane | 中央执行器的指令部分 | System Prompt 是"永久 pin"的工作记忆内容 |
| State Plane | 工作记忆的外化存储（scratchpad） | Scratchpad 文件 = 工作记忆的溢出区，不受 token 限制 |
| World State Plane | 外部环境的内部表征 | World State 快照是"从外部世界进入工作记忆的观察" |

## 6. 设计启发

### 6.1 上下文压缩不是"删旧内容"

正确的压缩策略：

1. 识别当前任务阶段的信息需求
2. 将不再直接需要但未来可能需要的信息写入 LTM
3. 用摘要替代原始细节
4. 从 LTM 检索与当前阶段最相关的历史信息

错误的压缩策略：

- 简单截断最早的 N 条消息
- 不区分信息类型和优先级的均匀压缩
- 压缩后不保留任何恢复路径

### 6.2 Context Pack 应按任务阶段动态重组

不同任务阶段需要不同的工作记忆内容：

| 阶段 | 工作记忆侧重 |
|---|---|
| 任务理解 | 用户需求、约束、上下文背景 |
| 方案设计 | 现有架构、相关代码、设计模式 |
| 实现 | 具体文件内容、API 签名、测试用例 |
| 验证 | 测试结果、期望行为、边界条件 |
| 交付 | 变更摘要、影响范围、注意事项 |

### 6.3 检查清单

```text
上下文管理是否区分了信息优先级（pin / keep / compress / evict）？
是否有从工作记忆到 LTM 的溢出路径？
上下文压缩是否保留了恢复/检索的能力？
Context Pack 是否根据任务阶段动态调整？
是否监控了 Context Rot 的信号（如重复询问已提供的信息）？
多模态信息是否有差异化的保留策略（截图 vs 文字）？
是否显式构造了跨工具结果的整合视图？
```

### 6.4 常见反模式

| 反模式 | 症状 | 修正 |
|---|---|---|
| 无限追加 | 上下文越来越长，响应越来越慢 | 引入压缩和驱逐策略 |
| 一刀切截断 | 截断后 Agent 重复已完成的工作 | 截断前写入 LTM，保留摘要 |
| 全量 pin | 所有信息都标为高优先级 | pin 数量应有上限，定期审计 |
| 忽略阶段转换 | 进入实现阶段仍保留大量需求讨论细节 | 阶段切换时触发 Context Pack 重组 |

## 7. 延伸阅读

- Baddeley, A. (2000). "The episodic buffer: a new component of working memory?" *Trends in Cognitive Sciences*
- Cowan, N. (2001). "The magical number 4 in short-term memory" *Behavioral and Brain Sciences*
- Miller, G. A. (1956). "The magical number seven, plus or minus two" *Psychological Review*
- `architecture/planes/state/overview.md` -- State Plane 作为外化存储
- `paradigms/memory-paradigms.md` -- 记忆范式选择
- `design-space/patterns/scratchpad-progress-file.md` -- Scratchpad 模式
- `design-space/patterns/checkpoint-hydration.md` -- 上下文恢复模式
