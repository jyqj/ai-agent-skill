# Tool Registry

> **Evidence Status** — grounded. 来自 Hermes Agent（Python 实现）和 OpenCode（TypeScript / Effect.js 实现）的生产代码。

当 Agent 可用的工具超过十几个，分散在不同模块中时，工具管理本身就成了问题：schema 怎么生成、handler 怎么调度、哪些工具在当前环境可用、怎么按场景组合工具集？Tool Registry 用一个中心化注册表（Registry）解决这些问题，让工具定义成为单一真实源（Single Source of Truth）。

## 注册表结构

注册表的核心是一个从工具名到工具条目（Tool Entry）的映射。每个条目包含：

```python
@dataclass
class ToolEntry:
    name: str
    toolset: str                              # 所属工具集
    schema: dict                              # 给模型看的 JSON Schema
    handler: Callable                         # 实际执行函数
    check_fn: Optional[Callable[[], bool]]    # 动态可用性检查
    requires_env: List[str]                    # 依赖的环境变量
```

工具通过 `register()` 在模块加载时自注册，注册表在运行时提供两个核心能力：

- **`get_definitions(tool_names)`**：返回指定工具的 schema 列表，同时执行 `check_fn` 过滤掉不可用的工具（比如缺少 API Key）。`check_fn` 的结果会被缓存，避免重复调用。
- **`dispatch(name, args)`**：根据名称查找 handler 并执行，统一处理错误。

## Toolset 组合

工具集（Toolset）是工具的分组机制，支持嵌套包含：

```python
TOOLSETS = {
    "web":  {"tools": ["search", "extract"], "includes": []},
    "full": {"tools": ["terminal"], "includes": ["web", "file"]},
}
```

`full` 工具集包含自身的 `terminal` 加上 `web` 和 `file` 两个子集的所有工具。解析时需要做循环检测，防止 `A includes B includes A` 导致无限递归。

## OpenCode 的三层注册

OpenCode 将工具来源分为三层：

1. **内置工具** -- 硬编码在 registry 中，始终可用
2. **本地插件** -- 扫描项目目录下的 `{tool,tools}/*.{js,ts}` 文件，自动加载
3. **插件托管** -- 从 Plugin.Service 远程加载

在此基础上，OpenCode 还做了动态过滤（Dynamic Filtering）：根据当前使用的模型 Provider 决定哪些工具可用（比如 `codesearch` 只对特定 Provider 开放），处理互斥工具（有 `edit` 就不暴露 `apply_patch`），以及基于权限配置过滤。

工具的定义接口使用 Zod schema 做参数校验，执行结果统一返回 `{ title, metadata, output, attachments? }` 结构，支持流式更新元数据和运行时权限请求。

## 权衡

Registry 模式的主要风险在**模块加载顺序**：工具通过 `register()` 自注册，如果模块未被导入，工具就不会出现在注册表中。Hermes 通过在入口点显式导入所有工具模块来解决；OpenCode 通过文件扫描自动发现。两种方案各有取舍——显式导入更可控但容易遗漏，自动扫描更方便但增加了约定（文件必须放在特定目录、导出特定接口）。

`check_fn` 的副作用也需要留意：如果可用性检查涉及网络调用或文件系统操作，在工具列表生成时可能引入意外延迟。缓存可以缓解但不能完全消除这个问题。

对于工具数量少于 5 个的简单 Agent，Registry 是过度设计。但当工具超过 10 个、需要按场景动态组合时，它几乎是必需的基础设施。

## 参考实现

- Hermes Agent: `tools/registry.py`, `model_tools.py`, `toolsets.py`
- `projects/coding-agents/opencode/tool-system.md` -- Effect.js 工具系统
