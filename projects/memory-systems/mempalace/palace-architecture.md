# Palace 导航架构


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> **古希腊记忆术：把想法放在建筑的房间里，走过建筑就能找到想法**

## 层级结构

```
PALACE
  │
  ├── WING (person/project)
  │     │
  │     ├── ROOM (topic/idea)
  │     │     │
  │     │     ├── CLOSET (summary pointer)
  │     │     │     │
  │     │     │     └── DRAWER (verbatim content)
  │     │     │
  │     │     └── ... more closets
  │     │
  │     └── ... more rooms
  │
  └── ... more wings

HALL = 连接同 wing 内 rooms 的走廊（记忆类型）
TUNNEL = 连接不同 wings 的隧道（同一 room 跨域出现）
```

## 组件定义

| 组件 | 含义 | 示例 |
|-----|------|------|
| **Wing** | 人或项目 | wing_kai, wing_driftwood |
| **Room** | 具体话题 | auth-migration, graphql-switch |
| **Hall** | 记忆类型走廊 | hall_facts, hall_events |
| **Tunnel** | 跨域连接 | auth-migration 同时在 wing_kai 和 wing_driftwood |
| **Closet** | 摘要指针 | 指向原始内容的索引 |
| **Drawer** | 逐字原文 | 不做任何总结 |

## Hall 类型（5 种）

```
hall_facts        — 决策、选择
hall_events       — 会话、里程碑、调试
hall_discoveries  — 突破、新见解
hall_preferences  — 习惯、偏好
hall_advice       — 建议、解决方案
```

## Tunnel 示例

```
wing_kai       / hall_events / auth-migration  → "Kai debugged OAuth token"
wing_driftwood / hall_facts  / auth-migration  → "team decided to use Clerk"
wing_priya     / hall_advice / auth-migration  → "Priya approved Clerk over Auth0"

同一个 room (auth-migration) 出现在三个 wings → Tunnel 连接它们
```

## 结构带来的检索提升

```
Search all closets:          60.9%  R@10
Search within wing:          73.1%  (+12%)
Search wing + hall:          84.8%  (+24%)
Search wing + room:          94.8%  (+34%)
```

**结构不是装饰，是 +34% 的检索改进**

---

## Palace Graph 实现

### 节点数据结构

```python
{
    "room": str,
    "wings": [list of wings],      # 该 room 跨越的 wings
    "halls": [list of halls],      # 该 room 内的 corridors
    "count": int,                  # 记录数量
    "dates": [sorted list]         # 最近 5 个访问日期
}
```

### 边（Tunnel）结构

```python
{
    "room": str,
    "wing_a": str,
    "wing_b": str,
    "hall": str,
    "count": int
}
```

### 关键操作

**traverse(start_room, max_hops=2)**
- BFS 从起点 room 出发
- 通过共享 wing 连接 rooms
- 返回按 (hop_distance, -count) 排序的结果

**find_tunnels(wing_a, wing_b)**
- 查找连接指定 wings 的所有 rooms
- 按 count 排序
- 识别跨域概念的关键操作

**graph_stats()**
```python
{
    "total_rooms": N,
    "tunnel_rooms": M,           # len(wings) >= 2 的 rooms
    "total_edges": E,
    "rooms_per_wing": {...},
    "top_tunnels": [...]         # 最多跨 wings 的 rooms
}
```

---

## Wing/Room 自动检测

### 项目文件检测优先级

1. **文件夹路径匹配** — 目录名包含 room keyword
2. **文件名匹配** — 文件名包含 room name
3. **内容关键词评分** — 前 2000 字符中 keyword 频率
4. **Fallback** — "general"

### 文件夹映射示例

```python
FOLDER_ROOM_MAP = {
    "frontend" → "frontend",
    "backend" → "backend",
    "docs" / "wiki" → "documentation",
    "design" / "mockups" → "design",
    "test" / "qa" → "testing",
    "config" / "deploy" → "configuration",
    ...
}
```

### 对话 Room 检测（TOPIC_KEYWORDS）

```
technical:    code, bug, deploy, debug
architecture: design, pattern, schema, component
planning:     roadmap, priority, milestone
decisions:    chose, decided, trade-off
problems:     broken, issue, fix, solved
```

---

## 设计原则

| 原则 | 实现 |
|-----|------|
| **零配置可用** | 自动从文件结构推断 wing/room |
| **手动可覆盖** | mempalace.yaml 支持自定义 |
| **跨域连接** | Tunnel 自动发现同概念在不同 wings |
| **按需导航** | traverse() 支持从任意 room 出发探索 |
