# NagaAgent 执行层设计


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

## Agent 执行流程全景

```
用户输入 → 意图路由 → 上下文压缩 → Agentic Tool Loop → 响应输出
          ↓
      Intent Router    Context Compressor    LLM Service
      (快速分类)        (token 管理)          (流式调用)
```

---

## Agentic Tool Loop

**核心结构** (`agentic_tool_loop.py`)：

```python
async def run_agentic_loop(
    messages: List[Dict],
    session_id: str,
    max_rounds: int = 5,
    tools: Optional[List[Dict]] = None,
) -> AsyncGenerator[str, None]:
    """每轮流程：
    1. 检查 token 超限 → 上下文压缩
    2. LLM 流式输出 (content + reasoning + tool_calls)
    3. 解析并执行工具
    4. 工具结果注入历史
    5. 判断继续/终止/总结
    """
```

**每轮执行流程**：

| 阶段 | 操作 |
|-----|------|
| 0 | 上下文压缩（若超 100K token） |
| 1 | LLM 流式调用（content + reasoning + native tool_calls） |
| 2 | 工具解析（优先原生 FC → 回退文本解析） |
| 3 | 工具分组（live2d 异步触发 vs 可执行工具并行） |
| 4 | 工具执行（并行调用 MCP / OpenClaw / 本地 tool） |
| 5 | 消息注入（标准 FC 格式或兼容期旧格式） |
| 6 | 队列消息（从 message_queue.drain() 提取排队消息） |
| 7 | 终止判断（无工具 / 连续2轮失败 / max_rounds） |

**终止条件**：
```
无工具调用 ──→ 直接结束，返回本轮 LLM 输出
连续失败 ──→ 提前终止，进入总结轮（不传 tools 参数）
max_rounds ──→ 总结轮强制回复，禁止工具调用
```

---

## 意图路由（Intent Router）

**Nano 路由器**：用轻量模型 `gpt-4.1-nano` 秒级分类用户意图

```python
ROUTER_SYSTEM_PROMPT = """
根据用户最新消息，判断需要调用哪些工具。用 {{工具名}} 格式输出。
如果需要联网搜索，使用 {{openclaw:搜索关键词}} 格式。

可用工具：
## 系统内置
- openclaw: 联网搜索、网页浏览、代码执行、文件操作

## MCP 服务
- game_guide: 游戏攻略知识库问答
- weather_time: 支持天气、时间查询
...
"""
```

**路由结果**：
```python
@dataclass
class RouteResult:
    needed_builtins: List[str]     # ["openclaw"] 或 []
    needed_mcp: List[str]          # ["game_guide", "weather_time"]
    needed_skills: List[str]       # ["web-search"]
    search_query: Optional[str]    # 从 "openclaw:关键词" 提取
```

**上下文优化效果**：
- 闲聊场景 → 跳过所有工具指令 → Prompt 从 ~8K 缩至 ~2K tokens
- 工具需求明确 → 只注入相关工具文档 → 平均减少 30-50% token

---

## 上下文压缩（Context Compressor）

### 启动压缩 (`compress_for_startup`)

**触发**：新会话启动时

```
历史对话 + 旧摘要 → LLM 总结 → 新摘要
新摘要注入到新会话 system prompt：
<compress>
{摘要内容}
</compress>
```

### 运行时压缩 (`compress_context`)

**触发**：agentic loop 每轮开始，若 token 超过 100K

**算法**：
1. 按 loop 切分消息（一轮 = 一条 user + 后续所有非 user）
2. 从末尾向前选取 loop（保留 ≤10 轮 + ≤10K token）
3. 早期 loop 压缩为摘要，注入 system prompt

### 6 分区压缩结构

1. **Key Facts**（关键事实）
2. **User Preferences**（用户偏好）
3. **Important Decisions**（重要决定）
4. **Action Items**（待办事项）
5. **Background Context**（背景信息）
6. **Recent Status**（最近状态）

**SSE 事件流**：
```
compress_start      → 通知压缩开始
compress_progress   → 压缩进度
compress_end        → 完成 + token 节省统计
compress_info       → 插入【已压缩上下文】标记
```

---

## 主动触发机制（DogTag 系统）

**架构概览**：

```
DogTagScheduler (scheduler.py)
  ├─ 周期任务执行器（PERIODIC）→ 主循环每秒 tick
  ├─ 事件驱动倒计时（EVENT_DRIVEN）→ 对话结束后启动延迟执行
  └─ 全局状态管理 → 窗口模式、用户活跃度、时间窗口检查
```

**职责注册表**：
```python
@dataclass
class DogTag:
    duty_id: str                    # "heartbeat" / "screen_vision"
    name: str
    trigger_type: TriggerType       # PERIODIC / EVENT_DRIVEN
    interval_seconds: Optional[int]  # 周期任务间隔
    delay_seconds: Optional[int]     # 事件驱动延迟（通常 300s）
    status: DutyStatus              # ENABLED / PAUSED / DISABLED
    activation: ActivationCondition # 执行条件
```

**执行条件**：
```python
window_modes: Optional[List[str]]            # ["ball", "compact", "full"]
active_hours_start/end: Optional[str]        # "09:00" - "23:00"
requires_user_active: bool
inactive_threshold_minutes: int              # 无活动阈值
```

**调度器状态机**：
```
对话开始 (on_conversation_started):
  └─ 取消所有 EVENT_DRIVEN 倒计时

对话结束 (on_conversation_ended):
  └─ 为所有 ENABLED 的 EVENT_DRIVEN 任务启动倒计时
     倒计时到期 → 检查条件 → 执行职责

主循环 (每秒 tick):
  └─ 遍历 PERIODIC 任务
     若 elapsed >= interval_seconds 且条件满足 → 执行
```

---

## 心跳职责（HeartbeatExecutor）

```python
async def perform_heartbeat():
    """
    1. 调用 LLM 心跳 prompt（带 checklist 上下文）
    2. 解析返回结果中的指令：
       [ADD_ITEM] item_name      → 向 checklist 添加任务
       [DONE_ITEM] item_id       → 标记任务已完成
       [DISMISS_ITEM] item_id    → 删除任务
    3. 检查是否为纯 ACK（"HEARTBEAT_OK"）
       → 是：静默丢弃（不推送 UI）
       → 否：推送到 UI
    """
```

心跳 LLM 配置：
- System: `HEARTBEAT_SYSTEM_PROMPT`
- Context: 当前 session 的压缩摘要
- Context: Pending checklist items
- 温度：0.3（低创意）

---

## 工具调用提取

**多格式支持**（优先级从高到低）：

1. **```tool``` 代码块**（推荐）：
   ```
   这是我的分析：

   ```tool
   {"agentType": "tool", "tool_name": "web_search", "args": {...}}
   ```
   ```

2. **特殊工具调用语法**（OpenAI/Kimi 兼容）：
   ```
   <|tool_calls_section_begin|>
   <|tool_call_begin|>functions.web_search:<|tool_call_argument_begin|>{"query": "..."}
   <|tool_call_end|>
   <|tool_calls_section_end|>
   ```

3. **裸 JSON 行**（向后兼容）

**工具名称规范**：
```
{agentType}__{service_name}__{tool_name}

示例：
- tool__web_search
- mcp__weather_time__today_weather
- openclaw__agent
- live2d__action
- naga_control__command
```

---

## SSE 事件类型

```
content          → 正常回复文本
reasoning        → CoT 思考过程
content_clean    → 移除工具代码块后的清洁文本
tool_calls       → 工具调用列表（执行前）
tool_results     → 工具执行结果摘要
round_start      → 新一轮开始
round_end        → 轮次结束
queued_messages  → 排队消息注入
compress_start   → 上下文压缩开始
compress_end     → 压缩完成
token_refreshed  → Token 刷新成功
auth_expired     → 认证过期
```

---

## 关键设计亮点

| 特性 | 实现 | 优势 |
|------|------|------|
| 极速意图路由 | nano 模型秒级分类 | 闲聊场景无需加载全量工具 |
| 双模式工具调用 | 原生 FC + 兼容期文本解析 | 平滑升级 |
| 动态上下文压缩 | Token 超限自动摘要 | 支持无限长对话 |
| 跨会话背景注入 | 持久化背景消息 | 保持对话连贯性 |
| 原生 function calling | streaming tool_calls | 支持并行工具调用 |
| 消息队列注入 | drain() 合并到工具结果 | 避免连续 user 破坏角色交替 |
| 主动心跳系统 | 对话结束后倒计时触发 | 异步维护界面活性 |
