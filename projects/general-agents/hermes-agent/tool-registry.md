# 工具注册系统

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> 来源：`tools/registry.py`, `model_tools.py`, `toolsets.py`, `mcp_tool.py`, `kanban_tools.py`

## 注册模式

```python
# tools/some_tool.py
from tools.registry import registry

schema = {
    "name": "web_search",
    "description": "Search the web for information",
    "parameters": {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"]
    }
}

def web_search_handler(args, **kwargs) -> str:
    # 所有 handler 返回 JSON string
    return json.dumps({"results": [...]})

registry.register(
    name="web_search",
    toolset="web",
    schema=schema,
    handler=web_search_handler,
    check_fn=lambda: bool(os.getenv('WEB_API_KEY')),  # 可用性检查
    requires_env=['WEB_API_KEY'],
    is_async=False,
    emoji="🔍",
    max_result_size_chars=50000,
)
```

**洞察**：模块加载时 `register()` 被调用。`check_fn` 动态控制可用性，不可用的工具被过滤，LLM 不见。

---

## Schema 生成与过滤

```python
def get_definitions(self, tool_names: Set[str]) -> List[dict]:
    result = []
    check_cache: Dict[Callable, bool] = {}  # 缓存 check_fn 结果

    for name in sorted(tool_names):
        entry = self._tools.get(name)
        if not entry:
            continue

        # 可用性检查（缓存）
        if entry.check_fn:
            if entry.check_fn not in check_cache:
                try:
                    check_cache[entry.check_fn] = bool(entry.check_fn())
                except Exception:
                    check_cache[entry.check_fn] = False
            if not check_cache[entry.check_fn]:
                continue  # 过滤不可用工具

        schema_with_name = {**entry.schema, "name": entry.name}
        result.append({"type": "function", "function": schema_with_name})

    return result
```

**洞察**：同一 check_fn 可跨多个工具共享（如同一 API key 检查），缓存避免重复调用。

---

## Toolset 组合

```python
TOOLSETS = {
    "web": {"tools": ["web_search", "web_extract"], "includes": []},
    "debugging": {"tools": ["terminal", "process"], "includes": ["web", "file"]},
    "hermes-cli": {"tools": _HERMES_CORE_TOOLS, "includes": []},
}

def resolve_toolset(name: str, visited: Set[str] = None) -> List[str]:
    if visited is None:
        visited = set()
    if name in {"all", "*"}:
        return [tool for ts in get_all_toolsets() for tool in resolve_toolset(ts, set())]
    if name in visited:
        return []  # 循环检测
    visited.add(name)

    toolset = TOOLSETS.get(name)
    if not toolset:
        return []

    tools = set(toolset.get("tools", []))
    for included in toolset.get("includes", []):
        tools.update(resolve_toolset(included, visited))
    return list(tools)
```

**洞察**：`includes` 支持递归组合。`all` / `*` 别名自动包含未来新 toolset。`visited` 防止循环。

---

## 异步工具桥接

```python
def _run_async(coro):
    """透明桥接异步工具到同步循环。"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # 在 async 上下文中 → 线程池避免死锁
        with ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result(timeout=300)

    if threading.current_thread() is not threading.main_thread():
        # 工作线程 → 持久 per-thread loop
        return _get_worker_loop().run_until_complete(coro)

    # 主线程 → 全局持久 loop
    return _get_tool_loop().run_until_complete(coro)
```

**洞察**：持久 loop 防止缓存客户端（httpx/AsyncOpenAI）在死 loop 上清理失败。

---

## 参数类型强制转换

```python
def coerce_tool_args(tool_name: str, args: Dict) -> Dict:
    """LLM 常返回 '42' 而非 42，按 schema 类型转换。"""
    schema = registry.get_schema(tool_name)
    properties = schema.get("parameters", {}).get("properties", {})

    for key, value in args.items():
        if not isinstance(value, str):
            continue
        expected = properties.get(key, {}).get("type")
        if expected == "integer":
            try:
                args[key] = int(value)
            except ValueError:
                pass  # 保留原值
        elif expected == "number":
            try:
                args[key] = float(value)
            except ValueError:
                pass
        elif expected == "boolean":
            args[key] = value.lower() in ("true", "1", "yes")

    return args
```

**洞察**：失败时保留原值避免崩溃。整数优先（`42.0` → `42`）。

---

## MCP 工具集成（新）

```python
# tools/mcp_tool.py (~128KB) — 完整 MCP 实现
# tools/mcp_oauth.py, mcp_oauth_manager.py — OAuth 认证流
# tools/schema_sanitizer.py — MCP schema 标准化

# 工具发现：MCP 服务通过 schema discovery 注册
# 与本地 self-registering 的区别：
#   本地工具：模块加载时 register() 被调用
#   MCP 工具：运行时通过 schema discovery 动态注册
# schema_sanitizer 处理 Pydantic/MCP 不规范输出（类型不匹配、缺失字段等）
```

**洞察**：MCP 集成的核心挑战是 schema 标准化——上游 MCP 服务输出不一致，schema_sanitizer 是必要的适配层。

---

## Kanban 工具组（新）

```python
# tools/kanban_tools.py — 7 个 agent 工具
KANBAN_TOOLS = [
    "kanban_create",     # 创建任务
    "kanban_update",     # 更新任务状态
    "kanban_complete",   # 标记完成
    "kanban_block",      # 标记阻塞
    "kanban_list",       # 列出任务
    "kanban_assign",     # 分配给 worker
    "kanban_summary",    # 任务摘要
]

# 运行时 gating：检查 HERMES_KANBAN_TASK 环境变量或 toolsets 包含 "kanban"
# Worker 通过环境变量握手获得隔离上下文：
#   HERMES_KANBAN_TASK → 当前任务 ID
#   HERMES_KANBAN_RUN_ID → 当前执行 ID

# Dispatcher 生命周期：spawn → watch → escalate/complete
# Diagnostics engine：检测 distress signals（任务卡住、worker 超时等）
```

**洞察**：Kanban 实现了 Agent 团队的分布式协作——Dispatcher 负责全局调度，Worker 通过环境变量获得隔离的工具集和上下文。

---

## 浏览器引擎切换（新）

```python
# 配置：browser.engine: lightpanda | chrome | auto
# 环境变量：AGENT_BROWSER_ENGINE

# Lightpanda：Zig 实现的无头浏览器
#   导航速度 1.3-5.8x 快于 Chrome
#   内存占用显著更低
#   缺陷：无图形能力（screenshot 需回退到 Chrome）

# 自动降级逻辑：
def _needs_lightpanda_fallback(task_type):
    """screenshot / 视觉任务自动路由到 Chrome"""

def _chrome_fallback_screenshot():
    """Lightpanda 失败时回退到 Chrome 截图"""
```

**洞察**：双引擎设计让 agent 在大多数场景使用 Lightpanda 获得速度优势，仅在需要视觉能力时回退到 Chrome。

---

## 子代理工具隔离

```python
DELEGATE_BLOCKED_TOOLS = frozenset([
    "delegate_task",  # 防递归
    "clarify",        # 子代理不能问用户
    "memory",         # 不污染共享记忆
    "send_message",   # 不直接发消息
    "execute_code",   # 安全考虑
])

child = AIAgent(
    enabled_toolsets=parent_toolsets & requested_toolsets,  # 交集
    ephemeral_system_prompt=child_prompt,  # 独立提示
    skip_memory=True,  # 无记忆污染
    parent_session_id=parent.session_id,  # 链路追踪
)
child._delegate_depth = parent._delegate_depth + 1  # 深度限制
```

**洞察**：工具交集确保子代理无权限提升。深度限制防止递归委派（默认最大 2 层）。
