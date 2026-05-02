# 工具注册系统

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> 来源：`tools/registry.py`, `model_tools.py`, `toolsets.py`

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
