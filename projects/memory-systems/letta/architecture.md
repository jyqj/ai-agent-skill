# Letta (MemGPT) 架构分析


> **Evidence Status** — synthesized. 基于 Letta V1 架构文档、Cloud 服务说明、Codecademy 课程与官方博客，非源码级分析。

## 基本信息

- **类型**：memory-system / agent-framework
- **项目定位**：OS 风格记忆层级的有状态 Agent 框架，Agent 自主管理自身记忆。
- **关键版本**：V0（MemGPT 论文）→ V1（2025，原生推理架构）
- **部署形态**：Letta Cloud（托管服务）、Letta Code（本地运行）
- **学习来源**：V1 架构文档、官方博客、Codecademy 课程。

## 核心创新：上下文窗口即稀缺内存资源

Letta 的核心洞察来自操作系统：**上下文窗口是有限的 RAM，必须用 OS 内存管理原则（分页、缓存、淘汰）来治理**。Agent 不是被动接收上下文，而是主动管理自己的记忆——决定什么留在 RAM、什么写入磁盘、什么从磁盘调回。

```
┌─────────────────────────────────────────────────────────────────┐
│                     CONTEXT WINDOW (RAM)                        │
├─────────────────────────────────────────────────────────────────┤
│  System Prompt        │  固定指令，始终在上下文中               │
│  Core Memory          │  Agent 可读写的结构化记忆块             │
│  Recall Summary       │  最近对话的压缩摘要                     │
│  Working Context      │  当前对话消息                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
┌───────────────────────┐  ┌───────────────────────┐
│   ARCHIVAL MEMORY     │  │   RECALL MEMORY       │
│   (Disk)              │  │   (Conversation DB)   │
├───────────────────────┤  ├───────────────────────┤
│  向量存储的长期记忆   │  │  完整对话历史         │
│  Agent 主动写入/检索  │  │  支持搜索和时间过滤   │
│  无大小上限           │  │  自动索引             │
└───────────────────────┘  └───────────────────────┘
```

## 三层记忆层级

| 层级 | 类比 | 位置 | 容量 | 管理方式 | 语义 |
|------|------|------|------|----------|------|
| **Core Memory** | RAM | 上下文内 | 有限（~2K tokens） | Agent 通过工具读写 | 用户画像、Agent 人格、关键事实 |
| **Archival Memory** | 磁盘 | 上下文外 | 无限 | Agent 主动存取 | 长期知识、历史事实、参考材料 |
| **Recall Memory** | 搜索引擎 | 上下文外 | 自动增长 | Agent 查询检索 | 对话历史、交互记录 |

### Core Memory 的内部结构

Core Memory 不是一个黑盒，而是由 Agent 可操作的**记忆块（blocks）**组成：

```
Core Memory
├── human block     # 用户信息：姓名、偏好、历史
├── persona block   # Agent 人格：角色定义、行为准则
└── custom blocks   # 自定义块：项目上下文、领域知识等
```

Agent 通过工具调用修改这些块：
- `core_memory_append(block, content)` — 追加信息
- `core_memory_replace(block, old, new)` — 替换内容

### 记忆操作工具集

| 工具 | 作用域 | 操作 |
|------|--------|------|
| `core_memory_append` | Core | 向指定块追加内容 |
| `core_memory_replace` | Core | 替换块中的特定文本 |
| `archival_memory_insert` | Archival | 写入长期存储 |
| `archival_memory_search` | Archival | 语义搜索长期存储 |
| `conversation_search` | Recall | 搜索对话历史 |
| `conversation_search_date` | Recall | 按时间范围搜索对话 |

## V1 架构转变

V1 是 Letta 架构的重大转折点，反映了前沿模型能力的根本性变化。

### V0 → V1 对比

| 维度 | V0 (MemGPT) | V1 (2025) |
|------|-------------|-----------|
| **控制流** | 必须通过工具调用驱动（heartbeat 循环） | 模型原生推理 + 直接生成 |
| **消息生成** | `send_message` 工具调用 | 直接 assistant message |
| **持续思考** | `heartbeat` 工具触发下一步 | 模型自主决定何时停止 |
| **推理可见性** | 隐式（通过工具调用序列推断） | 显式（模型原生 reasoning） |
| **模型依赖** | 对弱模型也能工作（脚手架补偿） | 依赖前沿模型的原生能力 |

### V1 核心洞察

> **前沿模型的原生推理能力正在替代显式控制流工具。**

V0 时代，模型不够强，需要 `heartbeat` 工具作为"继续思考"的脚手架，需要 `send_message` 工具来区分"内部思考"和"外部输出"。V1 发现，GPT-5 和 Claude 4.5 Sonnet 级别的模型已经能自主管理推理过程，不再需要这些拐杖。

### V1 性能观察

V1 在 GPT-5 和 Claude 4.5 Sonnet 上取得了显著改进，验证了"模型能力提升 → 脚手架可简化"的趋势。

## Conversations API 与跨体验共享

```
┌──────────────────────────────────────────────────┐
│                   Agent Instance                  │
│              (Core Memory + Archival)              │
├──────────────────────────────────────────────────┤
│                                                    │
│  Conversation A      Conversation B                │
│  (User: Alice)       (User: Bob)                  │
│  ┌──────────┐        ┌──────────┐                 │
│  │ Recall A │        │ Recall B │                 │
│  └──────────┘        └──────────┘                 │
│                                                    │
│  共享 Core Memory + Archival Memory               │
│  各自独立的 Recall Memory                          │
└──────────────────────────────────────────────────┘
```

**设计要点**：
- 同一 Agent 可以同时服务多个用户/会话
- Core Memory 和 Archival Memory 跨会话共享——Agent 的"人格"和"长期知识"是统一的
- Recall Memory 按会话隔离——每段对话的历史独立
- 支持"跨并行用户体验的共享记忆"场景

## Letta Code：本地深度个性化

Letta Code 是本地运行的变体，面向开发者的深度个性化场景：
- 代码库上下文作为 Archival Memory
- 开发者偏好和习惯作为 Core Memory
- 本地文件系统访问
- 隐私敏感数据不离开本地

## Plane 映射

| Plane | 覆盖深度 | 说明 |
|-------|----------|------|
| **Memory** | 深 | 核心创新——OS 风格三层记忆层级，Agent 自主管理 |
| **Context** | 深 | 上下文窗口作为稀缺资源，主动分页和淘汰 |
| **State** | 深 | 跨会话持久化，Core Memory 维持 Agent 身份连续性 |
| **Tools** | 中 | 记忆操作工具集，V1 精简了控制流工具 |
| **Identity** | 中 | persona block 定义 Agent 身份，跨会话一致 |
| **Interaction** | 中 | Conversations API 支持多用户并行交互 |
| **Orchestration** | 弱 | 单 Agent 架构，无内建多 Agent 协调 |
| **Security** | 弱 | 无显式权限模型，Core Memory 可被 Agent 任意修改 |
| **Observability** | 弱 | V1 的推理过程依赖模型原生能力，外部可观测性有限 |

## 与其他记忆系统对比

| 维度 | Letta | MemPalace | Nocturne Memory | Mem0 |
|------|-------|-----------|-----------------|------|
| **记忆管理者** | Agent 自身 | 系统/结构 | 系统/版本链 | 系统/自动提取 |
| **设计隐喻** | OS 内存管理 | 记忆宫殿导航 | Node-Memory-Edge 图 | 记忆基础设施层 |
| **上下文策略** | Agent 主动分页 | L0-L3 按需加载 | 按 URI 路由 | 选择性注入 |
| **存储什么** | Agent 自选 | 原文保留 | 版本化内容 | LLM 自动提取 |
| **个性化机制** | Core Memory 自编辑 | 结构导航 | Namespace 隔离 | 四维 scope |
| **多用户** | Conversations API | — | Namespace | user_id scope |
| **成本** | $20-200/mo | 免费（本地） | 自托管 | $19-249/mo |

**关键对比**：Letta 是 **agent-centric**（Agent 管理自己的记忆），而 MemPalace/Nocturne/Mem0 是 **system-centric**（外部系统管理记忆，Agent 只是消费者）。这个区别决定了个性化能力的上限——自编辑记忆能产生真正的"自我认知"，但也带来安全风险（Agent 可能覆盖关键记忆）。

## 设计权衡

| 决策 | 收益 | 代价 |
|------|------|------|
| **Agent 自管理记忆** | 深度个性化，记忆与推理紧耦合 | 安全风险，Agent 可能腐蚀自身记忆 |
| **OS 内存隐喻** | 直觉清晰，开发者易理解 | 与真实 OS 内存管理的相似性有限 |
| **V1 去除控制流工具** | 架构简化，性能提升 | 强依赖前沿模型能力，弱模型退化严重 |
| **Core Memory 有限容量** | 迫使 Agent 做信息优先级决策 | 关键信息可能被淘汰 |
| **跨会话共享 Core/Archival** | 统一 Agent 身份 | 多用户场景下的隐私隔离挑战 |

## 经验教训

1. **自编辑记忆是个性化的关键机制**：让 Agent 自己决定记住什么、遗忘什么，比外部系统替 Agent 决定更能产生持续的行为改变。Core Memory 的 append/replace 操作虽然简单，但足以支撑长期人格演化。

2. **OS 内存隐喻是有力的抽象**：RAM/磁盘/搜索三层映射到上下文内/向量存储/对话检索，为开发者提供了立即可用的心智模型。这个隐喻的成功说明：好的架构隐喻能同时降低设计复杂度和学习成本。

3. **V1 证明了"模型追上脚手架"的趋势**：V0 需要 heartbeat 和 send_message 作为控制流拐杖；V1 发现前沿模型已经不需要。这意味着：**今天作为"架构创新"的脚手架，明天可能被模型原生能力淘汰**。架构师应区分"补偿模型缺陷的临时方案"和"不随模型能力变化的持久设计"。

4. **上下文窗口是 Agent 架构的核心约束**：Letta 的整个设计围绕"上下文窗口有限"这一约束展开。随着上下文窗口扩大（1M+ tokens），OS 内存管理的必要性会降低，但"什么信息值得占用注意力"的决策仍然必要——只是约束从"放不下"变成了"注意力稀释"。

5. **agent-centric 记忆 vs system-centric 记忆是设计光谱的两端**：Letta 选择了 agent-centric，赋予 Agent 最大自主权；Mem0 选择了 system-centric，由基础设施层统一管理。两者各有适用场景——个性化 companion 倾向前者，多 Agent 平台倾向后者。
