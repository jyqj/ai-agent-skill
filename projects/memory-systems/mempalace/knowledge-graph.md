# Knowledge Graph 设计


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> **时间感知的实体关系图：事实有生命周期**

## 数据模型

### 表结构

**entities 表**
```sql
id TEXT PRIMARY KEY           -- 规范化 ID (lowercase, 去空格)
name TEXT                     -- 原始实体名称
type TEXT                     -- person, place, project, concept, unknown
properties TEXT               -- JSON 额外属性
created_at TEXT               -- 创建时间戳
```

**triples 表**
```sql
id TEXT PRIMARY KEY           -- t_<subject>_<predicate>_<object>_<hash>
subject TEXT → entities(id)   -- 主体
predicate TEXT                -- 关系类型 (normalized)
object TEXT → entities(id)    -- 客体
valid_from TEXT               -- 有效期起点 (ISO date)
valid_to TEXT                 -- 有效期终点 (NULL = 当前有效)
confidence REAL               -- 置信度 (0.0-1.0)
source_closet TEXT            -- 来源记忆点 ID
source_file TEXT              -- 来源文件路径
extracted_at TEXT             -- 提取时间戳
```

## 时间有效性

### 状态矩阵

| 状态 | valid_from | valid_to | 含义 |
|-----|------------|----------|------|
| 当前 | 任意 | NULL | 目前有效 |
| 过期 | 日期 | 日期 | 曾经有效，现已失效 |
| 未来 | 未来日期 | NULL | 已知将来的事实 |
| 范围 | 日期 | 日期 | 特定时间段内 |

### 查询过滤逻辑

```sql
-- as_of="2026-01-15" 的过滤
WHERE (valid_from IS NULL OR valid_from <= ?)
  AND (valid_to IS NULL OR valid_to >= ?)
```

### 生命周期示例

```python
# Max 的体育历史
kg.add_triple("Max", "does", "swimming", valid_from="2025-01-01")
kg.add_triple("Max", "loves", "chess", valid_from="2025-10-01")

# 查询 2025 年 6 月
kg.query_entity("Max", as_of="2025-06-01")
# → 返回 swimming（有效期内），不返回 chess（还未开始）

# Max 游泳伤愈
kg.invalidate("Max", "does", "swimming", ended="2026-02-15")

# 查询 2026 年 3 月
kg.query_entity("Max", as_of="2026-03-01")
# → 不返回 swimming（已过期），返回 chess（仍有效）
```

## API 操作

### 写操作

```python
# 添加事实
kg.add_triple(
    subject="Kai",
    predicate="works_on",
    obj="Orion",
    valid_from="2025-06-01",
    confidence=0.95,
    source_closet="drawer_123"
)

# 标记失效
kg.invalidate(
    subject="Kai",
    predicate="works_on",
    obj="Orion",
    ended="2026-03-01"
)
```

### 查询操作

```python
# 实体关系查询
kg.query_entity("Kai", as_of="2026-01-20", direction="both")
# → [Kai → works_on → Orion, Kai → recommended → Clerk]

# 关系类型查询
kg.query_relationship("works_on", as_of="2026-01-20")
# → 所有 works_on 关系

# 时间线
kg.timeline("Orion")
# → 按 valid_from 排序的项目完整历史
```

---

## Entity Registry

> **三层优先级系统：Onboarding > Learned > Researched**

### 优先级

```
优先级 1: Onboarding     (用户明确定义，置信度 100%)
    ↓
优先级 2: Learned        (从会话历史推断，置信度 75-95%)
    ↓
优先级 3: Researched     (Wikipedia 查询，置信度 60-90%)
    ↓
Unknown (未分类)
```

### 注册表结构

```json
{
  "version": 1,
  "mode": "personal|work|combo",
  "people": {
    "Riley": {
      "source": "onboarding",
      "contexts": ["personal"],
      "aliases": ["Riley Marie"],
      "relationship": "daughter",
      "confidence": 1.0
    }
  },
  "projects": ["MemPalace", "Acme"],
  "ambiguous_flags": ["grace", "will", "may"],
  "wiki_cache": {...}
}
```

### 实体检测

**Phase 1: 候选提取**
- 正则：`\b([A-Z][a-z]{1,19})\b` — 首字大写
- 过滤 stopwords（420+ 词）
- 阈值：频率 ≥ 3

**Phase 2: 信号评分**
```
人物信号：
  对话标记（"Riley: ..."）         →  3x 乘数
  动作动词（Riley said）           →  2x 乘数
  直接称呼（hey Riley）            →  4x 乘数
  代词邻近（she/he 3 行内）        →  2x 乘数

项目信号：
  项目动词（building X）           →  2x 乘数
  阶段标记（MyProject second edition）         →  3x 乘数
  代码引用（import MyProject）     →  3x 乘数
```

**Phase 3: 分类**
```python
if person_ratio >= 0.7 AND has_two_signal_types AND person_score >= 5:
    type = "person"
elif person_ratio <= 0.3:
    type = "project"
else:
    type = "uncertain"
```

### 消歧

**问题**：Grace 既可是人名，也是"优雅"

```python
PERSON_CONTEXT = [
    r"\b{name}\s+said\b",           # Grace said
    r"\b{name}(?:'s|s')\b",         # Grace's
    r"\bmy\s+daughter\s+{name}\b"   # my daughter Grace
]

CONCEPT_CONTEXT = [
    r"\b{name}\s+of\b",             # grace of God
]

# 模式计数比较决定类型
```

---

## 与 Palace Graph 的协作

```
文本 → Entity Detector → candidates
            ↓
       Entity Registry (lookup)
            ↓
    确认人物/项目/未知
            ↓
   Knowledge Graph (add_triple)
   + Palace Graph (update room metadata)
            ↓
       记忆体系完整，支持时间查询与跨域遍历
```

---

## 对比其他系统

| 特性 | MemPalace KG | Zep (Graphiti) |
|-----|-------------|----------------|
| 存储 | SQLite (local) | Neo4j (cloud) |
| 成本 | 免费 | $25/mo+ |
| 时间有效性 | Yes | Yes |
| 自托管 | Always | Enterprise only |
