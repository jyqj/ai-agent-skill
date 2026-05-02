# Nocturne Memory


> **Evidence Status** — grounded. 本目录下的 context、patterns、memory architecture 文档。

## 基本信息

- **类型**：memory-system
- **项目定位**：AI 可 CRUD 的持久化记忆系统，强调 disclosure 条件触发、版本链和审计。
- **学习来源**：本地分析文档。
- **推荐入口**：README → memory-architecture.md / patterns.md / context-engineering.md。

## 模块覆盖

| 模块 | 覆盖程度 | 证据文件 | 可复用模式 |
|---|---|---|---|
| memory | 深 | memory-architecture.md | node-memory separation |
| representation | 深 | context-engineering.md | disclosure routing |
| context | 中 | context-engineering.md | precision disclosure |
| security | 中 | patterns.md | auditable changesets |

## 独特贡献

Nocturne 是一个**带版本治理和审计能力的 AI 记忆系统**。AI 通过可 CRUD 的记忆获得跨会话身份，人类通过 changeset 快照保持审计和回滚能力——这组张力的平衡是它的核心设计洞察。

## 关键发现

- 记忆召回应由 disclosure 条件触发（”什么时候该想起”），而非依赖语义相似度检索——触发条件必须在失败发生前可观测。
- Node（图结构）与 Memory（内容版本链）的分离让拓扑稳定性和内容演化可以独立管理，避免了一次修改牵动整个图。
- 记忆系统天然需要审计和回滚：AI 拥有完整 CRUD 权限，但每次修改都生成快照，这是建立人机信任的基础设施。

> **AI 可 CRUD 的持久化记忆系统**
>
> AI 通过拥有和管理自身记忆获得跨会话身份。

## 核心洞察

### 与传统 RAG 的对比

| 维度 | 传统 RAG | Nocturne Memory |
|------|---------|-----------------|
| **触发机制** | 语义相似度检索 | 明确的 disclosure 条件 |
| **所有权** | 系统后台摘要 | AI 拥有完整 CRUD 权限 |
| **结构** | 扁平向量空间 | URI 树 + 图混合拓扑 |
| **修正能力** | 只读或追加补丁 | 完整 CRUD + 版本链 |
| **身份持久化** | 无跨会话记忆 | System Boot 自动唤醒 |

> 上表为突出 Nocturne 的设计侧重而做的简化对比。实际系统中，向量检索和图结构常混合使用（例如 Nocturne 本身可接入语义搜索作为 L3 补充），RAG 系统也可以具备 CRUD 和版本管理能力。核心区别在于 Nocturne 将 disclosure 条件和版本链作为一等公民，而非可选附加。

### 核心公式

```
持久化记忆 = 内容版本化(Node-Memory)
         + 访问路径分离(Path)
         + 条件触发(Disclosure)
         + 人类审计(Changeset)
```

## 架构概览

```
┌─────────────────────────────────────────────────────┐
│                   MCP Protocol Layer                │
│            (stdio / SSE-HTTP / WebSocket)           │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│                  Service Layer                      │
│  ┌──────────────┐ ┌──────────────┐ ┌─────────────┐  │
│  │GraphService  │ │SearchIndexer │ │GlossaryServ │  │
│  │(CRUD+版本链) │ │(FTS索引)     │ │(关键词绑定) │  │
│  └──────────────┘ └──────────────┘ └─────────────┘  │
│  ┌───────────────────────────────────────────────┐  │
│  │           ChangesetStore (审计日志)           │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│                   Data Layer                        │
│  Node ← Memory (版本链)                             │
│    ↓                                                │
│  Edge (parent→child + metadata)                     │
│    ↓                                                │
│  Path (URI 路由缓存, 支持别名)                      │
│    ↓                                                │
│  SearchDocument (物化搜索视图)                      │
└─────────────────────────────────────────────────────┘
```

## 核心模式索引

| 模式 | 解决的问题 | 文件 |
|-----|----------|------|
| **System Boot Protocol** | AI 身份持久化 | `patterns.md#system-boot` |
| **Disclosure Routing** | 条件触发 vs 语义检索 | `patterns.md#disclosure` |
| **Node-Memory 分离** | 图结构稳定性 + 结构追踪 | `./memory-architecture.md` |
| **Aho-Corasick 织网** | 记忆自动关联 | `patterns.md#glossary` |
| **Causal Chain Tracking** | 变更分组与智能回滚 | `patterns.md#causal-chain` |
| **Namespace 隔离** | 单实例多 Agent | `memory-architecture.md#namespace` |

## 对 Harness 设计的启示

1. **记忆是身份的基础**
   - AI 不应通过约束得到合作，而通过拥有历史 → 形成身份 → 自主决策
   - 跨会话的"人格"需要显式的记忆系统，而非依赖 prompt caching

2. **条件触发优于语义检索**
   - disclosure 字段描述"什么时候该想起"，而非"内容是什么"
   - 触发条件必须在**失败发生前**可观测

3. **人类审计是信任的桥梁**
   - AI 拥有完整 CRUD 权限，但每次修改都生成快照
   - Dashboard 提供可视化审查与一键回滚

4. **自检机制防止认知漂移**
   - 识别"口头承诺但不落笔"的断裂点
   - 纠正信号触发立即定位并修正记忆

## 技术栈

- **后端**: Python + FastAPI + SQLAlchemy AsyncIO
- **存储**: SQLite (开发) / PostgreSQL (生产)
- **MCP**: FastMCP (stdio + SSE)
- **搜索**: FTS5 (SQLite) / tsvector (PostgreSQL)
- **前端**: React + Vite + TailwindCSS

## 文件索引

- `./memory-architecture.md` - 数据模型深度解析
- `./mcp-tools.md` - MCP Server 和工具设计
- `./context-engineering.md` - System Prompt 和上下文工程
- `./patterns.md` - 可复用的设计模式
