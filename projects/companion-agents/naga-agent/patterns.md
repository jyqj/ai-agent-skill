# NagaAgent 设计模式提取


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

从 NagaAgent 项目中提取的可复用设计模式。

---

## 1. 四层 Prompt 分离

**问题**：AI 角色系统的上下文信息有不同生命周期，混在一起难以管理和更新。

**解法**：按变更频率和所有权分四层存储和装配：

```
Tier1: 基础人格（极低频变更）  → 角色模板级
Tier2: 工具规则（低频变更）    → 平台级
Tier3: 实例灵魂（中频变更）    → 干员实例级
Tier4: 动态上下文（高频变更）  → 会话级
```

**实现要点**：
- 每层独立目录存储模板文件
- 占位符 `{variable}` 在运行时渲染
- 不同层可独立更新，互不影响

**权衡**：
- (+) 清晰的关注点分离
- (+) 支持引擎切换时保留部分层
- (-) 需要理解四层边界
- (-) 装配逻辑相对复杂

---

## 2. 选择性 Prompt 注入（Intent Routing）

**问题**：全量工具文档注入导致 token 浪费（~8K tokens），闲聊场景不需要工具。

**解法**：用轻量 nano 模型预判意图，按需注入：

```python
# 1. Nano 模型快速分类（~100ms）
route_result = classify_intent(user_message)

# 2. 按需注入
if route_result.needed_mcp:
    inject_mcp_docs(route_result.needed_mcp)
if route_result.needed_skills:
    inject_skill_docs(route_result.needed_skills)
if not route_result.needs_tools:
    skip_all_tool_instructions()  # 闲聊场景，~2K tokens
```

**实现要点**：
- Few-shot 示例加速定向
- 回退机制：nano 失败 → 全量注入
- 工具列表缓存，MCP/Skill 变更时清除

**权衡**：
- (+) 平均减少 50-70% tokens
- (+) 闲聊场景响应更快
- (-) 依赖 nano 模型可用性
- (-) 增加一次 LLM 调用延迟

---

## 3. 事件驱动心跳（Heartbeat v3）

**问题**：固定轮询的心跳系统浪费资源，用户活跃时不需要主动思考。

**解法**：从轮询改为事件驱动，对话结束后延迟触发：

```python
class DogTagScheduler:
    def on_conversation_started(self):
        # 取消所有心跳倒计时
        self.cancel_all_event_driven()

    def on_conversation_ended(self):
        # 启动 300s 倒计时
        for duty in self.get_event_driven_duties():
            self.schedule_delayed(duty, delay=300)

    def on_timer_expired(self, duty):
        # 再次检查条件
        if self.check_activation_conditions(duty):
            await self.execute_duty(duty)
```

**实现要点**：
- `TriggerType.EVENT_DRIVEN` vs `TriggerType.PERIODIC`
- 激活条件：时间窗口、窗口模式、用户活跃度
- 心跳结果：纯 ACK 静默丢弃，有内容才推送 UI

**权衡**：
- (+) 用户活跃时零资源消耗
- (+) 静默期自动激活主动思考
- (-) 实现复杂度高于简单轮询
- (-) 需要完整的条件检查系统

---

## 4. 六分区上下文压缩

**问题**：长对话超过 100K tokens，简单截断丢失重要信息。

**解法**：按语义分区压缩，保留结构化摘要：

```
压缩结果结构：
1. Key Facts（关键事实）
2. User Preferences（用户偏好）
3. Important Decisions（重要决定）
4. Action Items（待办事项）
5. Background Context（背景信息）
6. Recent Status（最近状态）
```

**实现要点**：
- 按 loop 切分消息（一轮 = user + 后续响应）
- 保留最近 10 轮 + 10K tokens
- 早期对话压缩为 `<compress>` 块注入 system prompt
- 跨会话继承：读取上次摘要，滚动累积

**权衡**：
- (+) 支持无限长对话
- (+) 保留语义结构
- (-) 压缩需要 LLM 调用
- (-) 压缩质量依赖 prompt 工程

---

## 5. 五元组知识图谱（GRAG）

**问题**：向量 RAG 信息密度低，语义漂移导致检索不准。

**解法**：自动提取结构化五元组，用图数据库存储：

```
五元组结构：(主体, 主体类型, 关系, 客体, 客体类型)

存储：
- 本地：quintuples.json
- 图谱：Neo4j (Cypher 查询)

检索：
- 提取关键词 → Cypher 查询 → 格式化注入
```

**实现要点**：
- 双提取策略：结构化输出优先，JSON 解析回退
- 异步任务队列：3 workers，不阻塞主对话
- 自动去重：SHA-256 避免重复提取
- 过滤规则：仅保留事实，排除修辞/假设

**权衡**：
- (+) 精确关系查询
- (+) 支持推理链
- (+) 可视化展示
- (-) 提取需要 LLM 调用
- (-) 需要 Neo4j 基础设施

---

## 6. MCP 统一注册表

**问题**：工具散落各处，难以统一管理和发现。

**解法**：中心化注册 + 动态扫描：

```python
# 全局注册表
MCP_REGISTRY: Dict[str, AgentInstance] = {}
MANIFEST_CACHE: Dict[str, Dict] = {}

def scan_and_register():
    """扫描 mcpserver/*/agent-manifest.json"""
    for manifest in glob_manifests():
        agent = create_instance(manifest)
        register(manifest.name, agent, manifest)

def unified_call(service_name, task):
    """统一调用入口"""
    agent = MCP_REGISTRY.get(service_name)
    return await agent.handle_handoff(task)
```

**实现要点**：
- Manifest 声明元数据（name, entryPoint, capabilities）
- importlib 动态导入
- 可见性控制：`scope` + `ownerAgentId`
- 外部 MCP 通过 McPorter Bridge 代理

**权衡**：
- (+) 完全可插拔
- (+) 统一发现和调用
- (-) 需要标准化 Manifest
- (-) 热更新需要手动触发

---

## 7. 流式工具调用提取

**问题**：工具调用混在 LLM 输出中，需要实时提取同时不阻塞显示。

**解法**：状态机逐字符处理，多格式支持：

```python
class StreamingToolCallExtractor:
    def process_chunk(self, chunk: str):
        for char in chunk:
            if self.in_tool_block:
                self.buffer += char
                if self.detect_block_end():
                    yield ToolCall(self.parse_buffer())
            else:
                yield DisplayChar(char)
                if self.detect_block_start():
                    self.in_tool_block = True
```

**支持格式**：
1. ```tool``` 代码块（推荐）
2. `<|tool_calls_section|>` 特殊语法
3. 裸 JSON 行（兜底）

**权衡**：
- (+) 实时显示 + 实时提取
- (+) 兼容多种 LLM 输出格式
- (-) 状态机逻辑复杂
- (-) 需要宽松 JSON 解析

---

## 8. 技能激活优先级

**问题**：通用指令与特定任务指令冲突时如何处理？

**解法**：激活技能时注入最高优先级指令：

```markdown
## 当前激活技能: {skill_name}

[最高优先级指令] 以下技能指令优先于所有其他行为规则。
你必须严格按照技能要求处理用户输入：

{skill_full_instructions}
```

**实现要点**：
- 激活技能时不再注入技能列表
- 技能指令位于 Tier4 最后，最接近用户消息
- 技能内定义完整工作流程

**权衡**：
- (+) 专项任务高度聚焦
- (+) 不受通用规则干扰
- (-) 技能文档需要写完整
- (-) 激活后其他技能不可用

---

## 模式组合示例

**场景**：用户发起一个需要搜索的复杂问题

```
1. Intent Routing → 识别需要 openclaw 搜索
2. 选择性注入 → 只注入 openclaw 工具文档
3. Agentic Loop → LLM 输出 ```tool``` 块
4. 流式提取 → 实时显示 + 并行提取工具调用
5. 工具执行 → MCP 统一调用
6. 结果注入 → 工具结果回流到 messages
7. 继续循环 → 直到无工具调用
8. 记忆存储 → GRAG 异步提取五元组
9. 压缩检查 → 超限则六分区压缩
10. 心跳调度 → 对话结束后重置倒计时
```

这些模式协同工作，构成完整的 Agent 执行框架。
