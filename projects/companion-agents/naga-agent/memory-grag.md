# NagaAgent GRAG 记忆系统


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

## 系统架构

NagaAgent 采用**双层混合架构**，支持本地图谱存储和远程微服务两种运行模式：

```
┌─────────────────────────────────────────────────────────────┐
│              Message Manager（消息管理器）                     │
│  • 维护会话历史（持久化到 ~/.naga/sessions/）                 │
│  • 记忆触发点（自动调用 memory_manager）                      │
└────────────────┬────────────────────────────────────────────┘
                 │ 优先级链路
         ┌───────┴────────┐
         ▼                ▼
    ┌─────────┐      ┌──────────┐
    │ Remote  │      │  Local   │
    │ Memory  │      │  Memory  │
    │(登录态) │      │ (GRAG)   │
    └─────────┘      └──────────┘
```

---

## 五元组数据结构

所有记忆以**五元组**形式存储：

```
(主体, 主体类型, 关系, 客体, 客体类型)
```

示例：
```python
("小明", "人物", "在", "公园", "地点")
("用户", "人物", "询问", "天气", "概念")
("娜迦", "AI", "回答", "问题", "事件")
```

**提取规则**：
- 仅提取**事实性**信息（行为、关系、属性）
- 严格过滤修辞手法、假设、纯情感表达
- 用户需求、偏好、计划也被提取为记忆
- 自动去重和冗余检测

**实体类型**：人物、地点、组织、物品、概念、时间、事件、活动

---

## 双重持久化策略

### 文件存储（主存储）

```
~/.naga/knowledge_graph/quintuples.json
```

- 所有五元组的集合（自动去重）
- 异步写入，确保数据不丢失
- 作为离线知识库备份

### Neo4j 图存储（可选加速）

```cypher
(:Entity {name: "实体名", entity_type: "类型"})
    -[relation {metadata: ...}]->
(:Entity)
```

- 支持复杂 Cypher 查询
- 可视化展示（PyVis）

配置：
```python
class GRAGConfig:
    enabled: bool = True
    neo4j_uri: str = "neo4j://127.0.0.1:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "your_password"
```

---

## 异步任务管理

`QuintupleTaskManager` 实现完整的任务队列系统：

```python
class QuintupleTaskManager:
    max_workers: int = 3          # 工作线程数
    max_queue_size: int = 100     # 任务队列大小
    task_timeout: int = 30        # 单任务超时（秒）
    auto_cleanup_hours: int = 24  # 自动清理间隔
```

任务生命周期：
```
PENDING → RUNNING → COMPLETED
               ├→ FAILED
               └→ CANCELLED
```

回调机制：
```python
task_manager.on_task_completed = memory_manager._on_task_completed_wrapper
task_manager.on_task_failed = memory_manager._on_task_failed
```

---

## 五元组提取机制

**双提取策略**：

1. **优先：结构化输出**（OpenAI beta.chat.completions.parse）
   ```python
   response_format = QuintupleResponse  # Pydantic 模型验证
   ```

2. **回退：JSON 解析**（传统 prompt）
   ```
   从以下中文文本中抽取有价值的五元组...
   输出格式：[["主体", "类型", "关系", "客体", "类型"], ...]
   ```

**Pydantic 数据模型**：
```python
class Quintuple(BaseModel):
    subject: str          # 主体
    subject_type: str     # 主体类型
    predicate: str        # 谓语/关系
    object: str           # 客体
    object_type: str      # 客体类型

class QuintupleResponse(BaseModel):
    quintuples: List[Quintuple]
```

---

## RAG 查询机制

在 `quintuple_rag_query.py` 中的 `query_knowledge()` 函数：

```python
# Step 1: 用户问题 + 最近上下文 → 提取关键词
prompt = f"""
基于以下上下文和用户问题，提取与知识图谱相关的关键词...
上下文：{recent_context}
问题：{user_question}
"""

# Step 2: LLM 返回关键词列表
keywords = [提取的关键词]

# Step 3: 在 Neo4j 中查询
quintuples = query_graph_by_keywords(keywords)

# Step 4: 格式化结果
answer = "我在知识图谱中找到以下相关信息：\n"
for h, h_type, r, t, t_type in quintuples:
    answer += f"- {h}({h_type}) —[{r}]→ {t}({t_type})\n"
```

---

## 与 LLM 上下文的交互

**提示词注入流程**：

```
用户输入 → Message Manager
           ↓
        拼接最近对话（短期记忆）
           ↓
        调用 query_memory() 获取长期记忆
           ↓
        构建最终提示：
        ┌─────────────────────┐
        │ 系统提示             │
        │ 干员长期记忆摘录    │  ← {agent_long_term_memory_prompt}
        │ 可用技能            │
        │ 最近对话历史        │  ← recent_context (短期)
        │ 当前用户消息        │
        └─────────────────────┘
           ↓
        发送给 LLM
```

**上下文配置**：
```python
class APIConfig:
    max_history_rounds: int = 100      # 最多保留 100 轮对话
    persistent_context: bool = True    # 启用持久化上下文
    context_load_days: int = 3         # 加载 3 天内历史

class GRAGConfig:
    context_length: int = 5            # 查询时传入的上下文轮数
    similarity_threshold: float = 0.6  # 记忆检索阈值
```

---

## 双模式架构（本地 vs 远程）

**模式选择逻辑**：
```python
def should_prefer_remote_memory() -> bool:
    # 优先级：Naga 登录态 > 配置 token > 无
    if naga_auth.is_authenticated():
        return True
    if config.memory_server.token:
        return True
    return False
```

**远程 API 端点**：
```
POST /quintuples              # 添加五元组
GET  /quintuples?limit=...    # 获取五元组列表
POST /quintuples/query        # 关键词查询
POST /add                     # 添加对话记忆
POST /query                   # 查询记忆
GET  /health                  # 健康检查
```

---

## 创新点

| 创新 | 说明 |
|------|------|
| **五元组知识图谱** | 将中文对话提取为 (主体, 类型, 关系, 客体, 类型) 结构，通过 Cypher 按关系类型和实体查询 |
| **异步任务管理** | 3 线程任务队列并发提取，30s 超时，不阻塞主对话循环 |
| **双重持久化** | JSON 文件作为离线主存储，Neo4j 可选启用以支持图遍历和 Cypher 查询 |
| **故障转移机制** | 结构化输出失败时回退到 JSON prompt 提取；远程服务不可用时切换本地存储 |
| **去重缓存** | 对已提取文本做哈希判重，跳过重复内容，减少 API 调用 |

---

## 关键文件

| 文件 | 核心功能 |
|------|--------|
| `summer_memory/quintuple_extractor.py` | 五元组提取（双策略） |
| `summer_memory/quintuple_graph.py` | 图存储与查询 |
| `summer_memory/task_manager.py` | 异步任务队列管理 |
| `summer_memory/memory_manager.py` | 记忆统一接口与任务回调 |
| `summer_memory/memory_client.py` | 远程记忆微服务客户端 |
| `summer_memory/quintuple_rag_query.py` | RAG 查询与关键词提取 |
