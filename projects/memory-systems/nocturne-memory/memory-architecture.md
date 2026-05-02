# 记忆架构：Node-Memory-Edge-Path 四层模型


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

## 核心设计理念

**内容与访问路径分离**：同一段记忆可由多个 URI 访问（别名），每条路径有独立的 priority 和 disclosure。

```
概念层 (Persistent)          版本层 (Mutable)
        Node                    Memory
      (UUID)                    (ID)
        ↓                         ↓
    node_uuid ──── (FK) ──── node_uuid
    created_at                 content (Text)
                               deprecated (Boolean)
                               migrated_to (Int → 版本链)
```

## 四层数据模型

### Layer 0: Node（概念实体）

```python
class Node(Base):
    uuid: str  # PK, 版本无关的身份
    created_at: datetime

    # 关系
    memories: List[Memory]  # 版本链
    child_edges: List[Edge]
```

**设计理由**：
- Node 是不变的概念锚点
- 修改内容只需创建新 Memory，图结构无需变动
- 支持多版本历史追踪

### Layer 1: Memory（内容版本）

```python
class Memory(Base):
    id: int  # PK
    node_uuid: str  # FK → Node
    content: str
    deprecated: bool  # 旧版本标记
    migrated_to: Optional[int]  # 版本链指针
    created_at: datetime
```

**版本链语义**：
```
old_mem.deprecated = True
old_mem.migrated_to = new_mem.id
new_mem.deprecated = False
```

### Layer 2: Edge（关系 + 元数据）

```python
class Edge(Base):
    id: int  # PK
    parent_uuid: str  # FK → Node
    child_uuid: str   # FK → Node

    # 元数据（不在 Memory 上，在 Edge 上）
    priority: int      # 0 = 最高
    disclosure: str    # 触发条件
    name: str          # 显示名

    # 约束：(parent_uuid, child_uuid) UNIQUE
```

**设计要点**：priority 和 disclosure 属于**访问关系**，不属于内容本身。

### Layer 3: Path（URI 路由缓存）

```python
class Path(Base):
    # 复合 PK
    namespace: str  # 多租户隔离
    domain: str     # core, writer, game, ...
    path: str       # agent/identity/shame_log

    edge_id: int    # FK → Edge
```

**URI 格式**：`domain://path`
```
core://agent                    → 根节点
core://agent/identity           → 子节点
writer://novel/character_a      → 不同域
```

**别名机制**：多条 Path 指向同一 Edge = 同一内容的多个访问入口

---

## Namespace 多租户隔离 {#namespace}

### 隔离级别

```
同一 Node 在不同 Namespace 有不同 Path：

Node uuid-x
  ├─ Path (ns="alice", domain="core", path="projects/foo")
  └─ Path (ns="bob", domain="core", path="work/bar")
```

### 实现机制

```python
from contextvars import ContextVar

_namespace: ContextVar[str] = ContextVar('namespace', default='')

# 中间件注入
class NamespaceMiddleware:
    async def __call__(self, scope, receive, send):
        ns = extract_from_header_or_query(scope)
        set_namespace(ns)
        await self.app(scope, receive, send)

# 所有 DB 查询自动追加 WHERE namespace = ?
```

### 隔离范围

| 表 | Namespace 列 | 隔离效果 |
|---|-------------|---------|
| Path | ✅ | URI 树完全独立 |
| GlossaryKeyword | ✅ | 关键词绑定独立 |
| SearchDocument | ✅ | 搜索结果独立 |
| Node | ❌ | 可跨 namespace 共享 |
| Memory | ❌ | 内容版本共享 |

---

## 版本链与快照机制

### 更新流程

```python
async def update_memory(path, content, ...):
    # 1. 获取当前结构快照
    old_mem = await get_memory_by_path(path)

    # 2. 创建新版本
    new_mem = Memory(node_uuid=old_mem.node_uuid, content=content)
    session.add(new_mem)

    # 3. 标记旧版本
    old_mem.deprecated = True
    old_mem.migrated_to = new_mem.id

    return {"old_memory_id": old_mem.id, "new_memory_id": new_mem.id}
```

### Changeset 审计日志

```json
{
  "rows": {
    "memories:123": {
      "table": "memories",
      "before": {"content": "原始内容", ...},
      "after": {"content": "修改后", ...}
    }
  }
}
```

**语义**：
- 首次触及：记录 before + after
- 多次触及：只覆盖 after，before 冻结
- 净零检测：before == after 自动过滤

---

## 搜索索引设计

### SearchDocument（物化视图）

```python
class SearchDocument(Base):
    namespace: str
    domain: str
    path: str

    node_uuid: str
    memory_id: int
    uri: str
    content: str  # 从 Memory 复制
    search_terms: str  # 聚合的搜索词
    priority: int  # 从 Edge 复制
    disclosure: str
```

### FTS 后端适配

**SQLite FTS5**：
```sql
WHERE fts MATCH '"agent" AND "memory"'
ORDER BY bm25(...) ASC, priority ASC
```

**PostgreSQL tsvector**：
```sql
WHERE tsvector @@ websearch_to_tsquery('agent & memory')
ORDER BY ts_rank_cd(...) DESC, priority ASC
```

### 索引刷新时机

- 创建/更新/删除 Memory
- 添加/删除 Glossary 关键字
- 添加/删除 Path（别名）

---

## 根节点设计

```python
ROOT_NODE_UUID = "00000000-0000-0000-0000-000000000000"
```

**作用**：
- 所有顶层路径的逻辑父节点
- 避免 NULL 引用的 SQLite 唯一约束问题
- `get_children(ROOT_NODE_UUID)` 返回所有域根

---

## 设计权衡

### Node-Memory 分离 vs 单表

| 维度 | 分离模型 | 单表模型 |
|-----|---------|---------|
| 更新成本 | 低（只新增 Memory 行） | 高（需迁移整行） |
| 版本追踪 | 原生支持 | 需要额外字段 |
| 查询复杂度 | JOIN 多 | 简单 |
| 图稳定性 | ✅ 图不动 | ❌ 版本变化可能影响关系 |

### Path 物化 vs 动态计算

| 维度 | 物化缓存 | 动态计算 |
|-----|---------|---------|
| 路由速度 | O(1) | O(depth) |
| 别名支持 | 原生 | 需要额外逻辑 |
| 一致性 | 需主动刷新 | 自动 |
| 存储开销 | 多一张表 | 无 |

**结论**：对于需要快速路由和别名支持的场景，物化缓存是正确选择。
