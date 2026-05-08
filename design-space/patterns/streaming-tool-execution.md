# Streaming Tool Execution

> **Evidence Status** — production-validated. 来自 Claude Code 的 StreamingToolExecutor 生产实现，实测节省 40-60% turn 延迟。

## 问题

传统 Agent 循环是串行的：等待模型 API 完整返回 → 解析工具调用 → 执行工具 → 拼装结果 → 下一轮。但在流式 API 场景下，模型返回一个 tool_use block 后可能还会继续输出更多 block（文本、其他工具调用）。如果等到流完全结束才开始执行，工具的 I/O 延迟被白白浪费——尤其当工具涉及文件读取、网络请求或子进程时，这段等待占了一个 turn 延迟的大头。

## 核心机制

**在模型流式输出期间并行执行工具，不等 API 响应完成。**

当流式事件中出现一个完整的 tool_use block 时，立即将该工具放入执行队列。模型继续流式输出其余内容，工具在后台并发执行。

### 工具状态机

每个工具调用经历四个状态：

```
queued → executing → completed → yielded
```

- **queued**: tool_use block 解析完毕，等待执行器调度
- **executing**: 工具函数已启动，正在运行
- **completed**: 执行结束，结果已就绪，但尚未提交给调用方
- **yielded**: 结果已交付给 Agent 循环，可用于拼装下一轮消息

状态机保证结果按**原始顺序**（而非完成顺序）交付：即使 tool_3 先完成，也必须等 tool_1 和 tool_2 都 yielded 后才能 yield。这是因为模型对工具结果的消费顺序必须与调用顺序一致。

### 故障隔离

每个工具执行绑定一个**子 abort controller**，从流级别的 abort controller 派生：

```
stream abort controller
  ├── tool_1 abort controller
  ├── tool_2 abort controller
  └── tool_3 abort controller
```

- 单个工具超时或异常只取消该工具，不影响其他并行工具
- 流级别取消（如用户中断）会级联取消所有子工具
- 工具失败时生成错误类型的 tool_result，而非直接抛出异常

### 并发控制

并非所有工具都适合并行执行。需要根据工具属性决定并发策略：

- **只读工具**（文件读取、搜索、API 查询）：可安全并行
- **有副作用的工具**（文件写入、命令执行）：需要按依赖关系排序或串行化
- **重资源工具**（启动子进程、大文件操作）：需要并发上限

## 项目对照

| 项目 | 实现方式 |
|---|---|
| Claude Code | StreamingToolExecutor：流式解析 + 即时入队 + 有序 yield，生产环境节省 40-60% turn 延迟 |
| Cursor Agent | 类似思路，在流式阶段预执行工具，但具体状态机未公开 |

## 与其他 plane/pattern 的关系

| 相关模式 | 关系 |
|---|---|
| `concurrent-tool-partition.md` | 本模式关注"何时开始执行"（流式期间），concurrent-tool-partition 关注"哪些工具可并行"（依赖分析） |
| `tool-registry.md` | Registry 提供工具的元信息（是否只读、超时配置），供本模式做并发决策 |
| `depth-budgeting.md` | 流式并行执行可能加速预算消耗，需要 depth budget 协调 |
| `loop-detection.md` | 并行执行多个工具时，循环检测需要感知"同一批次"内的调用，避免误报 |

## 适用条件

**适用：**
- 使用流式 API（SSE / WebSocket）的 Agent
- 单个 turn 内可能触发多个工具调用
- 工具执行涉及 I/O 等待（文件、网络、子进程）

**不适用：**
- 非流式 API（batch 模式）——无流式事件可监听
- 工具执行极快（< 10ms）——并行化收益微乎其微
- 工具间存在强顺序依赖且无法拓扑排序——强制并行会产生竞态

## 反模式

| 反模式 | 表现 | 修复 |
|---|---|---|
| 无序 yield | 工具结果按完成顺序而非调用顺序返回，模型解析混乱 | 强制有序 yield |
| 全局 abort | 任一工具失败取消所有并行工具 | 子 abort controller 隔离 |
| 无限并发 | 同时执行大量重资源工具导致系统过载 | 并发上限 + 工具分类 |

## 参考实现

- Claude Code: `StreamingToolExecutor` — 流式工具执行引擎
- Claude Code: `processToolCall` — 工具状态管理与有序交付
