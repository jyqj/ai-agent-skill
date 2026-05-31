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

Registry 模式的主要风险在**模块加载顺序**：工具通过 `register()` 自注册，如果模块未被导入，工具就不会出现在注册表中。Hermes 通过在入口点显式导入所有工具模块来解决；OpenCode 通过文件扫描自动发现。两种方案各有取舍：显式导入更可控但容易遗漏，自动扫描更方便但增加了约定（文件必须放在特定目录、导出特定接口）。

`check_fn` 的副作用也需要留意：如果可用性检查涉及网络调用或文件系统操作，在工具列表生成时可能引入意外延迟。缓存可以缓解但不能完全消除这个问题。

对于工具数量少于 5 个的简单 Agent，Registry 是过度设计。但当工具超过 10 个、需要按场景动态组合时，它几乎是必需的基础设施。

## 参考实现

- Hermes Agent: `tools/registry.py`, `model_tools.py`, `toolsets.py`
- `projects/coding-agents/opencode/tool-system.md` -- Effect.js 工具系统

## Single Source of Truth Registry (Trellis)

> **Evidence**: Trellis — AI_TOOLS registry 驱动 14 平台

Trellis 的 `AI_TOOLS` 是一个比传统 tool registry 更上层的抽象 —— 它不注册工具本身，而是注册"平台能力"，然后从中派生出工具/skill/hook/agent 的完整配置。

**设计**：
```
AI_TOOLS: Record<AITool, AIToolConfig> = {
  "claude-code": { configDir: ".claude", cliFlag: "claude", agentCapable: true, hasHooks: true, ... },
  "codex":       { configDir: ".codex",  cliFlag: "codex",  agentCapable: true, hasHooks: false, ... },
  // ... 14 个平台
}
```

**派生链**：AI_TOOLS → configurator → writeSkills() + writeAgents() + writeHooks() + writeSettings()

**关键原则**：
- 从不 hardcode 平台列表，所有代码从 `Object.keys(AI_TOOLS)` 派生
- 新增平台 = 新增 AI_TOOLS 条目 + 新增 configurator 文件
- collectPlatformTemplates / getManagedPaths 等函数全部是 registry 查询

## Manifest-First Plugin Discovery (OpenClaw)

> **Evidence**: OpenClaw — 125 extensions, manifest-driven

传统 tool registry 靠代码注册（import-time side effects 或显式 register() 调用）。OpenClaw 走了 manifest-first 路线：

**机制**：每个 extension 通过 `openclaw.plugin.json` 声明 capability，runtime 在启动时扫描 manifest 决定加载哪些 plugin。

**Plugin SDK Boundaries**：
- 插件只能通过 `openclaw/plugin-sdk/*` subpath 和本地 `api.ts` / `runtime-api.ts` facade 访问 core
- 禁止访问 `src/**`、`src/plugin-sdk-internal/**`、其他 extension `src/**`
- 这种边界确保 plugin 与 core 的契约稳定

**Capability Provider 模式**：
- Provider plugin 声明 auth methods (oauth/api-key/credential)
- Channel plugin 声明 transport + allowlist policy
- Memory plugin 声明 search/store interface
- Runtime 按需解析 capability，不做全量加载

**与 Code-Registration 的对比**：
| 维度 | Code Registration | Manifest-First |
|------|-------------------|---------------|
| 发现时机 | import-time | 启动时扫描 manifest |
| 副作用 | 可能有 | 无（声明式） |
| 边界强制 | 靠约定 | SDK subpath + facade |
| 条件加载 | 运行时判断 | manifest 声明 requires |
| 规模 | 适合 <50 工具 | 适合 100+ extensions |
