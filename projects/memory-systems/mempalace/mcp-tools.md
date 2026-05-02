# MCP 工具设计


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> **19 个工具，5 个功能域，AI 自动学习使用**

## 工具分类

### A. 阅读工具（Read - 6 个）

| 工具 | 职责 |
|-----|------|
| `mempalace_status` | Palace 概览 + AAAK spec + memory protocol |
| `mempalace_list_wings` | Wings 及其 drawer 计数 |
| `mempalace_list_rooms` | 按 wing 列 rooms |
| `mempalace_get_taxonomy` | 完整 {wing → {room → count}} 树 |
| `mempalace_search` | 语义搜索 + wing/room 过滤 |
| `mempalace_check_duplicate` | 存储前重复检查（阈值 0.9） |

### B. 写工具（Write - 2 个）

| 工具 | 职责 |
|-----|------|
| `mempalace_add_drawer` | 存储原文到 palace（先检查重复） |
| `mempalace_delete_drawer` | 按 ID 删除 |

### C. Knowledge Graph（5 个）

| 工具 | 职责 |
|-----|------|
| `mempalace_kg_query` | 查询实体关系（支持 as_of 时间过滤） |
| `mempalace_kg_add` | 添加三元组事实 |
| `mempalace_kg_invalidate` | 标记事实过期（设置 valid_to） |
| `mempalace_kg_timeline` | 时间线查询 |
| `mempalace_kg_stats` | KG 统计概览 |

### D. 导航工具（Navigation - 3 个）

| 工具 | 职责 |
|-----|------|
| `mempalace_traverse` | 从一个 room 出发 BFS 遍历 |
| `mempalace_find_tunnels` | 找连接两个 wings 的 rooms |
| `mempalace_graph_stats` | 图统计 |

### E. 日记工具（Diary - 2 个）

| 工具 | 职责 |
|-----|------|
| `mempalace_diary_write` | 写 agent 日记（AAAK 格式） |
| `mempalace_diary_read` | 读最近 N 条日记 |

### F. 协议工具（Protocol - 1 个）

| 工具 | 职责 |
|-----|------|
| `mempalace_get_aaak_spec` | 获取 AAAK 方言完整规范 |

---

## 工具描述最佳实践

### 模式总结

| 维度 | 最佳实践 | 示例 |
|------|---------|------|
| **简明开口** | 动词 + 对象，不冗长 | ✓ "Palace overview — total drawers, wing counts" |
| **用途说明** | 说何时用，不说怎么用 | "Query the KG for an entity's relationships" |
| **举例比说明好** | 具体例子让 AI 明白场景 | "E.g. 'Max' → child_of Alice, loves chess" |
| **比喻增加理解** | 用隐喻解释概念 | "Find rooms that bridge two wings — the hallways" |
| **参数精准** | 类型 + 含义 + 默认值 | `"limit": {"type": "integer", "description": "Max results (default 5)"}` |
| **结果透明** | 说清返回什么，不说格式细节 | "Returns verbatim drawer content with similarity scores" |

### 优秀描述示例

```python
# 好 — 清晰、有例子、说明用途
"mempalace_traverse": {
    "description": "Walk the palace graph from a room. Shows connected ideas across wings — the tunnels. Like following a thread: start at 'chromadb-setup' in wing_code, discover it connects to wing_myproject."
}

# 好 — 时间维度明确
"mempalace_kg_query": {
    "description": "Query the knowledge graph for an entity's relationships. Returns typed facts with temporal validity. E.g. 'Max' → child_of Alice, loves chess. Filter by date with as_of to see what was true at a point in time."
}

# 好 — 对比说明
"mempalace_add_drawer": {
    "description": "File verbatim content into the palace. Checks for duplicates first."
}
```

### 避免的描述模式

```python
# 差 — 太冗长
"This tool is used to return statistics about the palace including..."

# 差 — 无用途说明
"Returns a JSON object with fields..."

# 差 — 太抽象
"Performs operations on the knowledge graph"
```

---

## AI 自动学习

**mempalace_status 返回包含：**
1. Palace 统计（drawers, wings, rooms）
2. **PALACE_PROTOCOL** — 完整的记忆交互协议
3. **AAAK_SPEC** — 压缩方言规范

AI 调用 `mempalace_status` 后自动学会：
- 如何组织 wing/room
- 如何使用 AAAK 方言
- 何时触发搜索 vs 存储

---

## MCP Server 架构

```python
# mcp_server.py 核心结构

TOOLS = {
    "mempalace_status": {...},
    "mempalace_search": {...},
    # ... 19 个工具定义
}

PALACE_PROTOCOL = """
When working with MemPalace:
1. On session start, call mempalace_status to learn the palace layout
2. Before storing, call mempalace_check_duplicate
3. Use wing/room filters to narrow search
...
"""

AAAK_SPEC = """
AAAK Format:
  ZID:ENTITIES|topic_keywords|"key_quote"|WEIGHT|EMOTIONS|FLAGS
...
"""
```

---

## Specialist Agents

每个 agent 有自己的 wing 和 diary：

```
~/.mempalace/agents/
  ├── reviewer.json       # 代码质量、模式、bug
  ├── architect.json      # 设计决策、权衡
  └── ops.json            # 部署、事故、基础设施
```

**Agent 日记写入：**
```python
mempalace_diary_write("reviewer",
    "PR#42|auth.bypass.found|missing.middleware.check|★★★★")
```

**Agent 日记读取：**
```python
mempalace_diary_read("reviewer", last_n=10)
# → 最近 10 条发现，AAAK 压缩格式
```

每个 agent 是特定领域的专家镜头。Reviewer 记住每个 bug 模式，Architect 记住每个设计决策，Ops 记住每个事故。
