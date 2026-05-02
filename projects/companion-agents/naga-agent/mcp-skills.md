# NagaAgent MCP 和技能系统


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

## MCP 服务架构

### 注册表系统

```python
# mcp_registry.py
MCP_REGISTRY: Dict[str, Any] = {}      # service_name → agent_instance
MANIFEST_CACHE: Dict[str, Dict] = {}   # service_name → manifest_dict
_REGISTERED: bool = False               # 幂等性保证
```

**自动扫描注册**：
```python
def scan_and_register_mcp_agents():
    """递归扫描 mcpserver/*/agent-manifest.json"""
    for manifest_path in glob("mcpserver/*/agent-manifest.json"):
        manifest = json.load(manifest_path)
        name = manifest.get("name") or manifest.get("displayName")
        agent = create_agent_instance(manifest)
        MCP_REGISTRY[name] = agent
        MANIFEST_CACHE[name] = manifest
```

### Manifest 结构

```json
{
  "name": "weather_time",
  "displayName": "天气时间Agent",
  "agentType": "mcp",
  "entryPoint": {
    "module": "mcpserver.agent_weather_time.agent_weather_time",
    "class": "WeatherTimeAgent"
  },
  "capabilities": {
    "invocationCommands": [
      {
        "command": "today_weather",
        "description": "查询今日天气",
        "example": "{\"city\": \"北京\"}"
      }
    ]
  },
  "scope": "public|private",
  "ownerAgentId": "optional_agent_id"
}
```

### MCP Agent 实现

每个 MCP agent 必须实现 `handle_handoff(task: dict) -> str` 接口：

```python
class WeatherTimeAgent:
    async def handle_handoff(self, task: dict) -> str:
        action = task.get("tool_name")
        city = task.get("city")
        result = await self._tool.handle(action, city=city)
        return json.dumps(result, ensure_ascii=False)
```

**任务格式**：
```json
{
  "agentType": "mcp",
  "service_name": "weather_time",
  "tool_name": "today_weather",
  "city": "北京"
}
```

---

## 外部 MCP 集成（McPorter Bridge）

`mcporter_bridge.py` - 集成第三方 MCP 服务：

**ExternalMCPAgent**：
- 封装外部 MCP 调用，代理 `mcporter` 命令行工具
- 动态 Schema 提取：`mcporter list --schema`
- 缓存策略：按 config 文件 mtime 缓存
- 预热机制：后台缓存 schema 避免冷启动

**配置示例** (`~/.mcporter/config.json`)：
```json
{
  "mcpServers": {
    "firecrawl": {
      "command": "npx",
      "args": ["firecrawl-mcp"],
      "_displayName": "Firecrawl",
      "_description": "网页内容提取",
      "_scope": "public"
    }
  }
}
```

---

## 技能系统

### 技能文件格式

Markdown + YAML Frontmatter：

```markdown
---
name: web-search
description: 网络搜索和信息检索技能
version: 1.0.0
author: Naga Team
tags: [search, web, realtime]
enabled: true
---

# 网络搜索技能

## 触发条件
当用户请求以下类型的信息时激活此技能：
- 最新新闻和资讯
- 实时数据

## 搜索策略
### 1. 关键词提取
从用户问题中提取核心搜索关键词...
```

### 存储位置（多源支持）

- `/skills/` - 内置技能
- `~/.naga/skills/public/` - 公共技能
- `~/.naga/skills/cache/` - 缓存技能（通过 extensions API 安装）
- `~/.openclaw/skills/` - OpenClaw 技能市场

### 技能激活机制

在 `build_context_supplement()` 中：

```python
if skill_name:
    skill_instructions = load_skill(skill_name)
    skill_active_section = f"""
## 当前激活技能: {skill_name}

[最高优先级指令] 以下技能指令优先于所有其他行为规则。
你必须严格按照技能要求处理用户输入：
{skill_instructions}
    """
```

**关键特性**：
- **优先级最高**：激活技能的指令优先于所有其他 Prompt
- **独占模式**：激活技能后不再注入技能列表，而是注入全文指令
- **线性流程**：技能规定的流程由 LLM 严格遵守

---

## 工具 Schema 生成

**统一 OpenAI Function Calling Schema**：

```python
def get_all_tool_schemas(agent_id: Optional[str] = None) -> List[Dict]:
    schemas = []
    schemas.extend(_build_openclaw_tool_schemas())      # ~30 个内置工具
    schemas.extend(_build_openclaw_agent_schema())      # agent 工具
    schemas.extend(_build_mcp_schemas(agent_id))        # MCP 服务
    schemas.extend(_build_live2d_schema())              # Live2D
    schemas.extend(_build_naga_control_schema())        # 系统控制
    return schemas
```

**命名约定**：
```
{agentType}__{service_name}__{tool_name}

示例：
- tool__web_search
- mcp__weather_time__today_weather
- openclaw__agent
- live2d__action
```

---

## 与 Prompt 系统的集成

### Tier4 注入点

**3_MCP目录.md**：
```markdown
## 当前可用 MCP 服务

{available_mcp_tools}
```

**7_激活技能指令.md**：
```markdown
{skill_active_section}
```

### 文档格式化

```python
def format_available_services() -> str:
    """生成提示词注入用的服务列表"""
    output = []
    for name, manifest in MANIFEST_CACHE.items():
        output.append(f"- 服务名: {name}")
        output.append(f"  显示名: {manifest.get('displayName')}")
        output.append(f"  描述: {manifest.get('description')}")
        for cmd in manifest.get("capabilities", {}).get("invocationCommands", []):
            output.append(f"  工具: {cmd['command']} - {cmd['description']}")
    return "\n".join(output)
```

---

## Token 消耗对比

| 场景 | 不优化 | 意图路由 | 激活技能 |
|------|--------|----------|---------|
| 闲聊 | ~8000 | ~2000 | ~2500 |
| 搜索 | ~8000 | ~3500 | - |
| 游戏攻略 | ~8000 | ~4000 | - |
| 激活技能 | ~8000 | - | ~5000 |

**优化效果**：
- 意图路由平均减少 50-70% tokens
- 闲聊场景最优，从 ~8K 缩至 ~2K tokens

---

## 设计模式

### 工厂模式

```python
def create_agent_instance(manifest: Dict) -> Optional[Any]:
    """通过 entryPoint 动态创建 agent 实例"""
    module = importlib.import_module(manifest["entryPoint"]["module"])
    agent_class = getattr(module, manifest["entryPoint"]["class"])
    return agent_class()
```

### 注册表模式

```python
MCP_REGISTRY = {}  # 全局注册表

def auto_register_mcp():
    """一次性扫描并注册所有 MCP agents"""
```

### 代理模式

```python
class ExternalMCPAgent:
    """代理外部 MCP 调用，屏蔽 mcporter 复杂性"""
    async def handle_handoff(self, task):
        await self._run_external_tool_sync(...)
```

### 策略模式

```python
# 根据工具类型选择不同的注入策略
if needs_openclaw:
    inject_openclaw_tools()
elif needs_mcp:
    inject_mcp_services()
elif needs_skills:
    activate_skill(skill_name)
```

---

## 扩展指南

### 添加新的 MCP 服务

1. 创建目录：`mcpserver/agent_xxx/`
2. 实现 Agent 类：
   ```python
   class MyAgent:
       async def handle_handoff(self, task: dict) -> str:
           return json.dumps(result, ensure_ascii=False)
   ```
3. 编写 Manifest：`agent-manifest.json`
4. 重启时自动注册

### 添加新的技能

1. 创建 SKILL.md：
   ```markdown
   ---
   name: my-skill
   description: ...
   enabled: true
   ---
   # 技能指令
   ...
   ```
2. 放入任一技能目录
3. 通过 `/api/extensions/skills/list` 发现
4. 通过 `build_context_supplement(skill_name="my-skill")` 激活

---

## 关键文件

| 文件 | 功能 |
|------|------|
| `mcpserver/mcp_registry.py` | 注册表核心 |
| `mcpserver/mcp_manager.py` | 管理器核心 |
| `mcpserver/mcporter_bridge.py` | 外部 MCP 支持 |
| `skills/` | 内置技能 |
| `apiserver/tool_schemas.py` | 工具 Schema 生成 |
| `apiserver/intent_router.py` | 意图路由 |
| `system/config.py` | Prompt 构建 |
