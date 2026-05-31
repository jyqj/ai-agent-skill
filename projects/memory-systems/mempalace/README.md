# MemPalace 记忆系统


> **Evidence Status** — grounded. 基于本目录下的 memory stack、palace architecture、KG、benchmark 文档。可信度高。

## 基本信息

- **类型**：memory-system
- **项目定位**：原文优先的长期记忆系统，强调结构导航、时间感知 KG 与 benchmark。
- **学习来源**：本地分析文档。
- **推荐入口**：README → memory-stack.md / palace-architecture.md / knowledge-graph.md。

## 模块覆盖

| 模块 | 覆盖程度 | 证据文件 | 可复用模式 |
|---|---|---|---|
| memory | 深 | memory-stack.md | layered memory |
| representation | 深 | README.md / palace-architecture.md | raw-text-first representation |
| tools | 中 | mcp-tools.md | tool descriptions |
| evaluation | 中 | benchmarks.md | benchmark-driven design |

## 独特贡献

MemPalace 用 LongMemEval 96.6% 的零 API 基线证明：**记忆效果的主要来源是”结构 + 原文保留”，而非 LLM 摘要**。当大多数系统在”存什么”上消耗 LLM 调用时，MemPalace 选择”存一切，让结构使其可找”，用 Wing/Room/Hall 导航替代语义猜测。

## 关键发现

- 记忆系统首先是**表示系统**：Palace 的 Wing/Room/Closet/Drawer 层次不只是存储组织，而是检索的主要路径（+34% R@10 提升来自结构过滤）。
- 长期事实必须带时间感知：知识图谱的 `valid_from / valid_to` 窗口让”2024 年还是 CEO 吗”这类时间敏感查询成为可能。
- Benchmark 可以反向塑造架构：从 96.6% 到 100% 的路径上，每个失败案例都驱动了具体的架构改进。

> **核心理念：存储一切，让它可找**
>
> 不用 LLM 决定什么值得记住。保留原文，用结构让它可导航。

## 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                        MEMORY STACK                              │
├─────────────────────────────────────────────────────────────────┤
│  L0 Identity (~100T)     │  Always loaded - who is this AI?     │
│  L1 Critical Facts (~500T)│  Always loaded - top 15 moments     │
│  L2 On-Demand            │  When topic comes up - wing/room     │
│  L3 Deep Search          │  Explicit query - semantic search    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PALACE STRUCTURE                            │
├─────────────────────────────────────────────────────────────────┤
│  Wing (person/project)                                           │
│    └── Room (topic/idea)                                         │
│          └── Closet (summary pointer)                            │
│                └── Drawer (verbatim content)                     │
│                                                                  │
│  Hall = memory type corridor (facts, events, discoveries...)    │
│  Tunnel = same room across wings (cross-domain connection)      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE GRAPH                               │
├─────────────────────────────────────────────────────────────────┤
│  Temporal Triples: subject → predicate → object                 │
│  Validity Windows: valid_from / valid_to                        │
│  Time-aware queries: "What was true on 2025-06-01?"            │
└─────────────────────────────────────────────────────────────────┘
```

## 性能基线

| 模式 | LongMemEval R@5 | API 依赖 | 备注 |
|-----|----------------|---------|------|
| Raw (ChromaDB only) | **96.6%** | 无 | 最高零 API 分数 |
| Hybrid v4 + rerank | **100%** | Haiku | 完美分数 |

## 模块导航

| 文档 | 内容 |
|-----|------|
| [memory-stack.md](memory-stack.md) | L0-L3 四层设计，AAAK 压缩方言 |
| [palace-architecture.md](palace-architecture.md) | Wing/Room/Hall/Tunnel 导航结构 |
| [knowledge-graph.md](knowledge-graph.md) | 时间感知三元组，实体注册 |
| [mcp-tools.md](mcp-tools.md) | 19 个 MCP 工具，描述写法最佳实践 |
| [hooks.md](hooks.md) | Stop/PreCompact 自动保存机制 |
| [benchmarks.md](benchmarks.md) | 验证方法，从 96.6% 到 100% 的路径 |

## 核心设计决策

| 决策 | 理由 |
|-----|------|
| **原文存储，不总结** | 96.6% 来自完整保留；LLM 总结会丢信息 |
| **结构即检索** | Wing+Room 过滤带来 +34% R@10 提升 |
| **时间感知 KG** | 事实有生命周期，`valid_to` 标记过期 |
| **Hook 触发保存** | AI 主动保存，不依赖用户手动 |
| **本地优先** | ChromaDB + SQLite，零云依赖 |

## 与其他系统对比

| 系统 | 存储 | 检索 | 成本 |
|-----|------|------|------|
| **MemPalace** | 原文 + ChromaDB | 语义 + 结构 | 免费 |
| Mem0 | LLM 提取 | 向量 | $19-249/mo |
| Zep (Graphiti) | Neo4j | 时间图 | $25/mo+ |
| Letta | Agent memory | — | $20-200/mo |

## 源码位置

```
mempalace/
├── layers.py          # L0-L3 记忆栈
├── dialect.py         # AAAK 压缩方言
├── searcher.py        # 语义搜索
├── knowledge_graph.py # 时间感知 KG
├── palace_graph.py    # 导航图
├── mcp_server.py      # 19 个 MCP 工具
├── miner.py           # 项目文件挖掘
├── convo_miner.py     # 对话挖掘
└── onboarding.py      # 引导式设置
```
