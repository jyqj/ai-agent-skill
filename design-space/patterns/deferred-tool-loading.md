# Deferred Tool Loading

> **Evidence Status** — production-validated. 来自 Claude Code 的 ToolSearch 元工具生产实现，工具数 > 100 时降低一个数量级的 token 开销。

## 问题

Agent 的工具越多，每轮对话传给模型的 tool schema 就越大。一个典型的工具定义（name + description + parameters JSON Schema）约 200-500 tokens；当工具数超过 30 个时，schema 本身就占用 6K-15K tokens，超过 100 个时可能达到 50K+ tokens。这些 token 在绝大多数轮次中是浪费的——模型在单轮中通常只调用 1-3 个工具。

粗暴的解决方案（如按类别分组、只传最常用工具）要么需要预先知道用户意图，要么会遗漏低频但关键的工具。

## 核心机制

**只传精简 schema（name + searchHint），通过 ToolSearch 元工具按需加载完整 schema。**

### 两阶段工具暴露

**第一阶段：启动时**

所有工具以精简形式出现在 system prompt 或 available-tools 列表中：

```
<available-deferred-tools>
Read
Write
Edit
Bash
Glob
Grep
WebSearch
WebFetch
mcp__github__create-issue
mcp__github__list-prs
mcp__slack__send-message
... (100+ tools, 每个只占 1 行)
</available-deferred-tools>
```

精简形式只包含工具名（和可选的一句话 searchHint），不包含参数 schema。模型知道这些工具存在，但无法直接调用——因为没有参数定义。

**第二阶段：按需加载**

ToolSearch 是唯一一个始终拥有完整 schema 的元工具。模型通过它按需获取目标工具的完整定义：

```
ToolSearch(query="select:Read,Edit,Grep")         → 精确选择，返回 3 个工具的完整 schema
ToolSearch(query="github pull request")            → 关键词搜索，返回最匹配的 N 个工具
ToolSearch(query="+mcp__slack send message")       → 要求名称包含 "mcp__slack"，按剩余词排序
```

返回的完整 schema 立即可用——模型在后续输出中可以直接调用这些工具，无需等到下一轮。

### 搜索策略

ToolSearch 支持三种查询模式：

| 模式 | 语法 | 用途 |
|---|---|---|
| 精确选择 | `select:Tool1,Tool2` | 已知工具名，直接加载 |
| 关键词搜索 | `keyword1 keyword2` | 模糊查找，按相关性排序 |
| 名称约束搜索 | `+prefix keyword` | 限定名称前缀，再按关键词排序 |

关键词搜索匹配范围包括工具名、description 和 searchHint。结果数量通过 `max_results` 参数控制（默认 5）。

### Token 收益

```
传统方式：100 个工具 × 300 tokens/工具 = 30,000 tokens/轮
Deferred：100 行工具名 (~500 tokens) + ToolSearch schema (~200 tokens) = ~700 tokens/轮
按需加载：平均每轮加载 3 个工具 × 300 tokens = 900 tokens

总计：~1,600 tokens vs 30,000 tokens → 降低约 95%
```

## 项目对照

| 项目 | 实现方式 |
|---|---|
| Claude Code | ToolSearch 元工具：精确选择 + 关键词搜索 + 名称约束搜索，生产环境 100+ 工具（含 MCP 工具） |
| ChatGPT Plugins（早期） | 类似思路，插件描述精简传递，按需加载 API spec，但粒度是整个插件而非单个工具 |

## 与其他 plane/pattern 的关系

| 相关模式 | 关系 |
|---|---|
| `tool-registry.md` | Registry 提供工具元信息（name, description, searchHint），是 Deferred Loading 的数据源 |
| `progressive-disclosure.md` | 同属"按需暴露"理念——Progressive Disclosure 用于信息，Deferred Loading 用于工具 |
| `compaction.md` | 两者共同降低上下文占用：Compaction 压缩历史，Deferred Loading 压缩工具定义 |
| `layered-tool-host.md` | 多层工具宿主中，每层的工具可独立 defer，ToolSearch 跨层搜索 |

## 适用条件

**适用：**
- 工具数量 > 30 的 Agent
- 集成多个 MCP server 导致工具爆炸的场景
- 上下文窗口紧张的模型（如 32K/64K 窗口）

**不适用：**
- 工具数量 < 10——schema 开销可忽略，增加 ToolSearch 反而多一次调用
- 每轮都需要所有工具的场景（罕见）
- 模型不支持动态工具注入的 API

## 反模式

| 反模式 | 表现 | 修复 |
|---|---|---|
| 过度 defer | 连常用工具也 defer，导致每轮都要先 ToolSearch | 高频工具（如 Read, Bash）保持完整 schema |
| searchHint 缺失 | 工具名晦涩且无 hint，模型搜不到 | 为每个工具提供简短的自然语言 hint |
| 单次加载过多 | ToolSearch 一次返回 20+ 工具的完整 schema | 限制 max_results，分批加载 |

## 参考实现

- Claude Code: `ToolSearch` 元工具 — 精简 schema + 按需加载
