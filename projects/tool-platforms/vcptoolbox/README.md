# VCPToolBox 项目分析


> **Evidence Status** — grounded. 本目录下的插件、分布式工具、TagMemo、dream system 分析。

## 基本信息

- **类型**：tool-platform
- **项目定位**：AI 中间层 / 工具平台，强调 manifest 插件系统、分布式工具执行和记忆增强。
- **学习来源**：本地项目分析文档。
- **推荐入口**：README → plugin-system.snippet.md / distributed-tools.snippet.md / tagmemo-algorithm.snippet.md。

## 模块覆盖

| 模块 | 覆盖程度 | 证据文件 | 可复用模式 |
|---|---|---|---|
| tools | 深 | plugin-system.snippet.md | plugin registry |
| platform | 深 | README.md / distributed-tools.snippet.md | distributed execution |
| memory | 中 | tagmemo-algorithm.snippet.md / rag-diary.snippet.md | time-aware RAG |
| orchestration | 中 | distributed-tools.snippet.md | star topology |
| operations | 中 | README.md | manifest-driven platform ops |

## 独特贡献

VCPToolBox 的价值在于它是**平台**而非 agent——它展示了当插件系统、分布式工具执行和记忆算法实现为平台级服务时，上层 agent 可以获得怎样的能力组合。TagMemo 浪潮算法（物理学启发的能量分解 + 脉冲扩散）和 AgentDream 梦系统（AI 内省 → 审批 → 执行）是在其他 agent 项目中未见的设计。

## 关键发现

- 平台能力决定上层 agent 的能力上限——工具注册、分布式执行、记忆检索这些基础设施的质量，比任何单个 agent 的 prompt 工程更重要。
- 插件系统需要信任边界和配置级联（插件专属 > 全局 > Schema 默认值），否则 79 个插件的管理会失控。
- 记忆算法可以也应该是平台级能力：TagMemo 作为共享 RAG 引擎服务所有插件，而不是每个 agent 各自实现检索逻辑。

> **项目定位**: Node.js 核心的 AI 中间层系统，通过插件驱动实现 AI 能力增强
> **核心公式**: `VCP = Plugin System + RAG Engine + Distributed Architecture`

## 项目概览

- **规模**: 673 文件，76,448 行代码，79 个活跃插件
- **技术栈**: Node.js + Rust (N-API) + Python + SQLite + WebSocket
- **架构风格**: 扁平化根目录，Manifest 驱动，分布式原生

## 核心三角架构

```
server.js (HTTP/SSE 入口)
    ├── Plugin.js (插件生命周期)
    ├── WebSocketServer.js (分布式通信)
    └── KnowledgeBaseManager.js (RAG/向量索引)
```

## 设计要点

### 1. Harness 工程亮点

| 组件 | VCP 实现 | 设计理念 |
|------|---------|---------|
| **工具注册** | Manifest 驱动 + 热加载 | 声明式配置，零代码注册 |
| **执行环境** | 多运行时 (Node/Python/Rust) | 语言无关的 stdio 协议 |
| **上下文管理** | TagMemo 浪潮算法 | 语义引力 + 向量重塑 |
| **记忆系统** | 日记本 + 向量索引 | 双索引架构，懒加载 |
| **人机协作** | AgentDream 梦审批 | 生成→审批→执行 |
| **分布式** | WebSocket 星型拓扑 | 动态注册，透明文件传输 |

### 2. 独特设计模式

- **VCP 工具协议**: 使用中文分隔符 `「始」「末」`，模型无关
- **浪潮算法**: 物理学启发的 RAG（能量分解 + 脉冲扩散）
- **梦系统**: AI 内省能力的安全实现
- **配置级联**: 插件专属 > 全局 > Schema 默认值

### 3. 可复用模式

- `./plugin-system.snippet.md` - 6 种插件类型架构
- `./tagmemo-algorithm.snippet.md` - 浪潮 RAG 算法
- `./distributed-tools.snippet.md` - 分布式工具执行
- `./dream-introspection.snippet.md` - AI 内省与审批
- `./rag-diary.snippet.md` - 时间感知 RAG

## 文件索引

| 文件 | 内容 |
|------|------|
| `./plugin-system.snippet.md` | 插件系统完整架构 |
| `./tagmemo-algorithm.snippet.md` | TagMemo V8.1 算法 |
| `./distributed-tools.snippet.md` | 分布式工具执行 |
| `./dream-introspection.snippet.md` | AgentDream 梦系统 |
| `./rag-diary.snippet.md` | RAG 日记系统 |
| 服务器架构概览（已合并在本 README） | 核心服务器架构 |

