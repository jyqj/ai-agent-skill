# Memory Stack 设计


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> **核心原则：只加载你需要的，在你需要时才加载**

## 四层架构

```
┌────────────────────────────────────────────────────────────────┐
│ L0 — Identity                                                   │
│ ~100 tokens | Always loaded | ~/.mempalace/identity.txt        │
│ "I am Atlas, assistant for Alice. Traits: warm, remembers all" │
├────────────────────────────────────────────────────────────────┤
│ L1 — Essential Story                                            │
│ ~500-800 tokens | Always loaded | Top 15 drawers by importance │
│ Auto-generated: most important moments, grouped by room        │
├────────────────────────────────────────────────────────────────┤
│ L2 — On-Demand Recall                                           │
│ ~200-500 tokens | When topic comes up | Metadata filter         │
│ "What about auth?" → load wing=myapp, room=auth                 │
├────────────────────────────────────────────────────────────────┤
│ L3 — Deep Search                                                │
│ Unlimited | Explicit query | Semantic search across all         │
│ ChromaDB vector similarity + optional wing/room filter          │
└────────────────────────────────────────────────────────────────┘
```

## 唤醒成本

| 启动 | Tokens | 留给对话 |
|-----|--------|---------|
| L0 + L1 | ~600-900 | 95%+ 上下文空间 |

## L1 生成逻辑

```python
# 1. 批量读取所有 drawers（分 500 条批次，避免 SQLite 限制）
# 2. 按 importance/weight 排序
# 3. 取 TOP 15
# 4. 按 room 分组
# 5. 硬性限制 3200 字符

MAX_DRAWERS = 15
MAX_CHARS = 3200

for (doc, meta) in sorted_by_weight[:15]:
    by_room[meta["room"]].append(doc)

if total_len > MAX_CHARS:
    lines.append("... (more in L3 search)")
```

## L3 搜索机制

```python
# ChromaDB 语义搜索
results = col.query(
    query_texts=["pricing strategy"],
    n_results=5,
    include=["documents", "metadatas", "distances"],
    where={"wing": "business"}  # 可选过滤
)

# 距离转相似度
similarity = round(1 - dist, 3)  # [0, 1]
```

**关键：返回逐字原文，不做 LLM 总结**

---

## AAAK 压缩方言

> **有损压缩，用于上下文加载，不是存储格式**

### 状态（诚实）

- AAAK 是有损的（regex 缩写，非可逆压缩）
- 小文本不省 token（overhead 大于收益）
- **大规模重复实体时有效**（团队名出现数百次）
- LongMemEval: AAAK 84.2% vs Raw 96.6%（下降 12.4 点）

### Zettel 格式

```
ZID:ENTITIES|topic_keywords|"key_quote"|WEIGHT|EMOTIONS|FLAGS

例：
042:ALC+BOB|consciousness_identity|"I finally understand"|0.85|vul+joy|PIVOT+CORE
```

### 字段说明

| 字段 | 含义 |
|-----|------|
| ZID | 记忆 ID（简化的 UUID 尾数） |
| ENTITIES | 参与者（3 字符大写，如 ALC=Alice） |
| topic_keywords | 2-3 个关键词，下划线连接 |
| key_quote | 最情感重的一句话（8-55 字符） |
| WEIGHT | 情感权重 [0.0-1.0] |
| EMOTIONS | 最多 3 个情感代码（vul, joy, fear...） |
| FLAGS | 属性标记（PIVOT, CORE, ORIGIN, DECISION...） |

### 情感编码（20+）

```
vul = vulnerability    joy = joy           fear = fear
trust = trust         grief = grief        wonder = wonder
rage = rage           love = love          hope = hope
despair = despair     peace = peace        humor = humor
tender = tenderness   raw = raw_honesty    doubt = self_doubt
anx = anxiety         exhaust = exhaustion convict = conviction
passion = quiet_passion  determ = determination
```

### 标志位

| Flag | 触发词示例 | 含义 |
|-----|----------|------|
| ORIGIN | founded, started, born | 起源时刻 |
| CORE | essential, principle, never forget | 核心信念 |
| PIVOT | turning point, breakthrough | 转折点 |
| DECISION | decided, chose, switched | 显式决策 |
| TECHNICAL | api, database, deploy | 技术细节 |

---

## 设计权衡

| 选择 | 理由 |
|-----|------|
| L1 只取 15 条 | 将启动成本锁定在 ~600-900 tokens，即使记忆库增长到数千条也保持恒定 |
| 原文存储 | LongMemEval 测试中原文保留达 96.6% 准确率，LLM 总结会引入信息丢失（AAAK 压缩降至 84.2%） |
| AAAK 是可选层 | 仅在大规模重复实体场景（如团队名出现数百次）启用，避免小文本场景下 overhead 超过收益 |
| 按 room 分组 | 将 L1 记忆按主题聚类呈现，减少 AI 在扁平列表中扫描定位的上下文消耗 |
