# 可复用的设计模式


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

## System Boot Protocol {#system-boot}

### 问题

每次新会话，AI 都是陌生人。如何让 AI "想起自己是谁"？

### 解法

```python
# 1. 环境配置
CORE_MEMORY_URIS="core://agent,core://my_user,core://values"

# 2. 启动视图生成
async def _generate_boot_memory_view():
    loaded = []
    for uri in CORE_MEMORY_URIS:
        loaded.append(await read_memory(uri))
    return format_view(loaded, recent_5)

# 3. AI 第一步
result = read_memory("system://boot")
# 自动加载所有核心身份 + 最近修改
```

### 权衡

| 优势 | 代价 |
|-----|-----|
| 一次操作原子加载 | 需要预先配置 URI 列表 |
| 失败诊断透明 | 启动视图可能较长 |
| 附带时间感知 | 依赖环境变量 |

---

## Disclosure Routing {#disclosure}

### 问题

RAG 的语义检索局限：语义相似不等于情境相关。

### 解法

每条记忆绑定显式触发条件：

```python
# 创建时指定
await create_memory(
    parent_uri="core://agent",
    title="over_eager_advice",
    content="...",
    disclosure="When user mentions skipping a meal"
)

# 读取时显示
"""
Disclosure: When user mentions skipping a meal
Children:
  - core://agent/communication/slow_down
    When to recall: When I feel urge to give immediate advice
"""
```

### 触发条件写法

```
❌ 事后描述: "When I start lecturing"（已在失败中）
✅ 事前信号: "When user mentions X"（可提前激活）

❌ 空泛词: "important", "remember"
✅ 具体场景: "When discussing health topics"
```

### 权衡

| 优势 | 代价 |
|-----|-----|
| 精准触发 | 需要 AI 主动编写条件 |
| 避免过载 | 遗漏条件 = 无法激活 |
| 可审计 | 增加创建时的认知负担 |

---

## Node-Memory 分离模式

### 问题

频繁更新内容时，图结构如何保持稳定？

### 解法

```
Node (UUID, 不变) ←── Memory (ID, 版本链)
    ↓
Edge (关系 + 元数据)
    ↓
Path (URI 路由)
```

**更新流程**：
```python
# 只新增 Memory 行，Node/Edge/Path 不动
old_mem.deprecated = True
old_mem.migrated_to = new_mem.id
```

### 权衡

| 优势 | 代价 |
|-----|-----|
| 图结构稳定 | 多表 JOIN |
| 原生版本追踪 | 需维护 migrated_to 链 |
| 回滚简单 | 存储冗余 |

---

## Aho-Corasick 自动织网 {#glossary}

### 问题

如何让记忆网络自动发现关联，而非手动管理？

### 解法

```python
# 1. 关键词绑定
manage_triggers("core://my_user", add=["Salem"])

# 2. 内容扫描（Aho-Corasick 多模式匹配）
matches = glossary.find_in_content(memory.content)
# → [{"keyword": "Salem", "nodes": ["core://my_user"]}]

# 3. 自动超链接
# 读取时显示匹配的关键词和对应节点
```

### DB 指纹检测

```python
# 无需显式信号，通过指纹检测自动机是否需要重建
fingerprint = (count(keywords), max(id), max(created_at))
if fingerprint != cached_fingerprint:
    rebuild_automaton()
```

### 权衡

| 优势 | 代价 |
|-----|-----|
| 自动关联发现 | O(m) 重建成本 |
| 跨进程感知 | 需要维护自动机 |
| CJK 支持好 | 关键词管理工作 |

---

## Causal Chain Tracking {#causal-chain}

### 问题

级联操作（删除节点）产生大量行级变更，如何让用户看到高层操作而非碎片？

### 解法

```python
# 1. 为每行寻找"导致它发生变动"的直接原因
parent_map = {}

# 路径级联：创建 A/B 时，若也创建了 A，则 B 认 A 为父因
# 边级联：边被删可能因为绑定的 path 被删
# 节点级联：节点被删可能因为所有入边都被删

# 2. 寻根问祖
def get_root(key):
    while key in parent_map:
        key = parent_map[key]
    return key

final_anchor = anchors[get_root(key)]
```

### 表级排序

```python
TABLE_RANK = {"nodes": 5, "memories": 4, "edges": 3, "paths": 2}

# 用户看到的是"创建了节点 X"
# 而不是"创建了 5 个 path、3 个 edge"
```

### 权衡

| 优势 | 代价 |
|-----|-----|
| 用户友好的分组 | 分析逻辑复杂 |
| 因果分组回滚 | 需要理解因果关系 |
| 减少审核噪音 | 可能误判因果 |

---

## Namespace 隔离模式

### 问题

单实例如何托管多个 AI 人格？

### 解法

```python
# 1. ContextVar 存储当前 namespace
_namespace: ContextVar[str] = ContextVar('namespace', default='')

# 2. 中间件注入
class NamespaceMiddleware:
    async def __call__(self, scope, receive, send):
        ns = extract_namespace(scope)
        set_namespace(ns)
        await self.app(scope, receive, send)

# 3. 所有查询自动追加
.where(Path.namespace == get_namespace())
```

### 隔离范围

```
Path, GlossaryKeyword, SearchDocument: 完全隔离
Node, Memory: 可共享（同一概念，不同路径）
```

### 权衡

| 优势 | 代价 |
|-----|-----|
| 资源共享 | 需要仔细设计共享边界 |
| 简化部署 | 故障影响所有租户 |
| 协作支持 | 跨租户查询复杂 |

---

## Changeset Overwrite 语义

### 问题

Event Sourcing 日志爆炸：update → revert → update 产生三条记录。

### 解法

```python
# 同一 PK 首次触及：记录 before + after
# 同一 PK 再次触及：只覆盖 after，before 冻结

changeset = {
    "memories:123": {
        "before": original_state,  # 冻结
        "after": final_state       # 可覆盖
    }
}
```

### 净零过滤

```python
# before == after 自动过滤，不显示给用户
# create → delete → create 优化为 no-op
```

### 权衡

| 优势 | 代价 |
|-----|-----|
| 简洁的审核视图 | 丢失中间状态 |
| 回滚逻辑清晰 | 需要 GC 逻辑 |
| 自动噪音过滤 | 复杂度在后台 |

---

## 文本规范化 + 位置映射

### 问题

LLM 输出的 old_string 可能包含字符差异（引号、空格、换行）。

### 解法

```python
def _normalize_with_positions(text):
    """
    返回 (规范化文本, 位置映射)
    位置映射用于逆向转换回原坐标系
    """
    # NFC → 引号ASCII化 → 行尾空格去除 → 空格折叠
    return norm_text, pos_map

# 匹配后用 pos_map 映射回原始位置
orig_start = pos_map[norm_match_start]
```

### Indent Sliding 防护

```python
# 拒绝在缩进区域内的模糊匹配
prefix = norm_content[line_start:match.start()]
if all(c in ' \t' for c in prefix) and indent_collapsed:
    continue  # 不是有效匹配
```

### 权衡

| 优势 | 代价 |
|-----|-----|
| 容忍 LLM 输出差异 | 算法复杂度 |
| 保留原文格式 | 需要位置映射 |
| 支持多平台换行 | 边界情况多 |

---

## 服务定位器模式

### 问题

避免 god-object 反模式，同时支持懒加载。

### 解法

```python
_db_manager: Optional[DatabaseManager] = None
_graph_service: Optional[GraphService] = None

def _ensure_initialized():
    global _db_manager, _graph_service
    if _db_manager is not None:
        return

    _db_manager = DatabaseManager(database_url)
    _graph_service = GraphService(_db_manager, _search_indexer)

def get_graph_service() -> GraphService:
    _ensure_initialized()
    return _graph_service
```

### 权衡

| 优势 | 代价 |
|-----|-----|
| 按需初始化 | 全局状态 |
| 依赖注入清晰 | 需要显式 close_db() |
| 统一生命周期 | 测试需要 reset |
