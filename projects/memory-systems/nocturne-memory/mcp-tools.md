# MCP Server 与工具设计


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

## 架构概览

```
FastMCP Server
  ├─ Lifespan Hook (异步 DB 初始化)
  ├─ URI Parser (domain://path 格式化)
  ├─ 7 个 MCP Tools
  ├─ 4 个系统 URI (动态视图)
  └─ 文本规范化引擎 (Unicode + patch 匹配)
```

## 7 个核心工具

| 工具 | 模式 | 返回值 | 核心职责 |
|-----|------|--------|---------|
| `read_memory` | 只读 | 格式化字符串 | 读取 + 4 个系统 URI |
| `create_memory` | 写 | URI | 新建节点 + 内容 |
| `update_memory` | 写 | 消息 | patch/append 更新内容 |
| `delete_memory` | 写 | 消息 | 级联删除路径 |
| `add_alias` | 写 | 消息 | 创建别名路径 |
| `manage_triggers` | 写 | 列表 | 关键词绑定 |
| `search_memory` | 只读 | 结果列表 | 全文搜索 |

## 系统 URI 设计

| URI | 功能 | 生成方式 |
|-----|------|---------|
| `system://boot` | 核心身份启动视图 | CORE_MEMORY_URIS 配置 |
| `system://index` | 全局记忆树索引 | 动态遍历 |
| `system://recent` | 最近 N 条修改 | 时间排序 |
| `system://glossary` | 触发词索引 | 聚合关键词 |

### system://boot 实现

```python
CORE_MEMORY_URIS = os.getenv("CORE_MEMORY_URIS", "").split(",")

async def _generate_boot_memory_view():
    """一次加载所有核心身份记忆"""
    loaded, failed = [], []

    for uri in CORE_MEMORY_URIS:
        try:
            memory = await read_single_memory(uri)
            loaded.append(memory)
        except Exception as e:
            failed.append((uri, str(e)))

    return format_boot_view(loaded, failed, recent_5)
```

**关键设计**：
- 环境变量驱动，无需改代码
- 失败诊断透明化（报告加载失败的 URI）
- 附加最近修改，提供时间感知

---

## 工具参数设计模式

### 参数验证三层

```python
# Layer 1: 类型（FastMCP 自动）
# Layer 2: 业务逻辑
domain, path = parse_uri(uri)
if domain not in VALID_DOMAINS:
    return "Error: Unknown domain"

# Layer 3: 语义（互斥字段检查）
if old_string is not None and append is not None:
    return "Error: Cannot use both old_string and append"
```

### 返回值规范

```
成功: "Success: Memory created at 'core://agent'"
错误: "Error: old_string found multiple times. Provide more context."
```

**设计原则**：告诉 AI "做错了什么" + "怎么修"

### 条件式工具注册

```python
def write_tool():
    """只读部署时不注册写操作"""
    def decorator(func):
        if PUBLIC_READONLY_MCP:
            return func  # 不注册为 MCP 工具
        return mcp.tool()(func)
    return decorator

@write_tool()
async def create_memory(...):
    ...
```

---

## 文本补丁匹配引擎

### 问题场景

LLM 重新生成文本时的字符差异：
- 系统引号（U+201C）→ 直引号（"）
- Em-dash（U+2014）→ hyphen（-）
- 多空格折叠
- CRLF/LF 混合

### 规范化流程

```python
def _normalize_with_positions(text):
    """
    返回 (规范化文本, 位置映射)
    位置映射用于逆向转换回原坐标系
    """
    # Step 1: Unicode NFC
    # Step 2: 引号/破折号 ASCII 化
    # Step 3: 行尾空格去除
    # Step 4: 连续空格折叠（保留首行缩进）
    return norm_text, pos_map
```

### Indent Sliding 防护

**问题**：`old_string = "  def foo()"` 可能在 4 空格缩进区域内错误匹配

**解决**：
```python
def _find_valid_matches(norm_content, norm_old, pos_map):
    for match in all_matches:
        prefix = norm_content[line_start:match.start()]
        if all(c in ' \t' for c in prefix) and indent_collapsed:
            continue  # 拒绝缩进区域内的模糊匹配
    return valid_matches
```

### CRLF 保留

```python
# 匹配后保留原文换行风格
if '\r\n' in original_content:
    new_string = new_string.replace('\n', '\r\n')
```

---

## Disclosure 参数设计

### 错误示例 vs 正确示例

```markdown
❌ BAD: "When I start lecturing about nutrition"
   问题: 已经在失败中途，来不及改变行为

✅ GOOD: "When the user mentions skipping a meal"
   特点: 具体可观测的触发信号，在失败前激活
```

### 在读取时显示

```python
async def read_memory(uri):
    memory = await get_memory(uri)

    if memory.get("disclosure"):
        lines.append(f"Disclosure: {memory['disclosure']}")

    for child in memory.get("children", []):
        if child.get("disclosure"):
            lines.append(f"  When to recall: {child['disclosure']}")
```

### 索引中的提醒

```python
# 如果 disclosure 为空，显式提醒 AI 补充
if disclosure:
    lines.append(f"   disclosure: {disclosure}")
else:
    lines.append("   disclosure: (NOT SET — consider adding one)")
```

---

## 工具组合模式

### 典型流程 1：发现旧记忆需要更新

```
1. read_memory("core://user/health")
2. [AI 分析发现信息过时]
3. update_memory(..., old_string=..., new_string=...)
4. read_memory("core://user/health")  # 验证
```

### 典型流程 2：创建别名并绑定触发词

```
1. add_alias("writer://character", "core://user/identity")
2. manage_triggers("core://user/identity", add=["Salem", "User"])
```

### 典型流程 3：发现并消除重复

```
1. search_memory("job")
2. read_memory("core://user/job_history")
3. read_memory("core://career/current_role")  # 发现重复
4. add_alias("core://career/current_role", "core://user/job_history")
5. delete_memory("core://career/current_role")  # 删除冗余
```

---

## 可复用的 MCP 设计模式

### 模式 1：Lifespan 管理异步资源

```python
@contextlib.asynccontextmanager
async def lifespan(server: FastMCP):
    db = get_db_manager()
    await db.init_db()
    yield
    await db.close()

mcp = FastMCP(..., lifespan=lifespan)
```

### 模式 2：系统 URI 工厂

```python
if uri == "system://boot":
    return await _generate_boot_view()
elif uri.startswith("system://index"):
    return await _generate_index_view(domain_filter)
# 统一入口，虚拟资源无 I/O 开销
```

### 模式 3：参数互斥验证

```python
if mode_a and mode_b:
    return "Error: Cannot use both"
if mode_a and not required_field:
    return "Error: Field required with this mode"
```

### 模式 4：工具链依赖文档

```python
"""
工具间依赖：
read_memory (无依赖) ← 其他所有工具都依赖它来验证修改
  ├─ create_memory (需验证 parent_uri 存在)
  ├─ update_memory (需读取当前内容做 patch)
  └─ delete_memory (需验证 URI 存在)

最佳实践：修改前必须先读，确保 AI "知道自己在改什么"
"""
```
