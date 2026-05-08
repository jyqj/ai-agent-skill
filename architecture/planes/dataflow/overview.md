# Dataflow Plane
>
> **所属域**：6. Coordination — 批量、流式与管道
>
> **Evidence Status** — synthesized. 批量任务、流式处理、持续事件响应、Agent pipeline 的生产需求。

**Principle Refs**: IS-01, BR-02 — 数据是对世界的表征而非世界本身；数据新鲜度随时间结构性衰减

## 1. 定义

Dataflow Plane 负责批量、流式、管道式 Agent 处理：当输入不是单个任务而是一组对象或持续事件流时，Agent 需要管道、窗口、回压和错误传播。

## 2. 处理模式

| 模式 | 适合 | 关键机制 |
|---|---|---|
| Batch | 多文件、多记录、批量审核 | chunking、dedup、checkpoint |
| Stream | 日志、告警、实时事件 | window、watermark、backpressure |
| Pipeline | Agent A 输出给 Agent B | output contract、error propagation |
| Map-Reduce | 大规模可并行任务 | worker fanout、merge verifier |
| Continuous Monitor | 长期观察和触发行动 | subscription、incident gate |

## 3. FlowRun

```yaml
flow_run:
  flow_id: flow_...
  mode: batch | stream | pipeline | monitor
  input_refs: []
  stages:
    - name: represent
      input_schema: object
      output_schema: object
      error_policy: retry | skip | quarantine | stop
  backpressure:
    max_queue_size: integer
    overflow_policy: drop_low_priority | pause_input | ask_human
  metrics:
    throughput: number
    latency_ms: number
    error_rate: number
```

## 4. 流式处理的陷阱

流式模式下有三类容易被忽视的故障场景：

**长尾异步结果**：Agent 提交异步任务后用户断开连接，结果返回时无消费者。

- 结果必须写入持久队列或 dead-letter，不得丢弃。
- 恢复时由 Orchestrator 决定：重新投递给用户、合并到下次 session、或标记为 expired。
- 过期策略须在 FlowRun 中显式声明，默认不应是静默丢弃。

**背压（Backpressure）**：上游产出速度超过下游消费能力时的三种策略。

| 策略 | 适用场景 | 副作用 |
|---|---|---|
| drop_low_priority | 实时告警流，低优先级事件可丢弃 | 可能丢失长期统计所需的低频信号 |
| pause_input | 批量处理，上游可暂停 | 上游堆积可能触发上游自身的超时 |
| ask_human | 下游是审批或人工环节 | 人工响应延迟不可控，需设超时降级 |

**部分结果与断点恢复**：流式传输中断后，已处理的 item 不应重复处理。

- 每个 stage 的 checkpoint 记录最后成功处理的 item offset。
- 恢复时从 checkpoint offset + 1 继续，而非从头重放。
- 幂等性要求：如果 stage 有外部 effect，重复执行必须安全。

## 5. 数据管道设计

**扇入 / 扇出（Fan-in / Fan-out）**：多 Agent 并行产出结果，汇聚后由单 Agent 消费。

```text
Fan-out：Orchestrator 将输入集合分片 → N 个 Worker 并行处理
Fan-in：Merge Verifier 收集 N 个 Worker 的输出 → 校验一致性 → 合并为单一结果
```

关键约束：Fan-in 节点必须处理部分 Worker 失败的情况——不能因为 1/10 失败就丢弃其余 9 个的结果。处理策略由 FlowRun 的 `error_policy` 决定。

**数据血缘（Data Lineage）**：每个数据片段从原始输入到最终输出的转换链。

```yaml
data_lineage:
  item_id: string
  origin: input_ref          # 原始输入引用
  transformations:
    - stage: string          # 处理阶段名
      agent_id: string       # 处理该阶段的 Agent
      timestamp: datetime
      operation: string      # 转换操作描述
  current_confidence: float  # 经过多次转换后的置信度
```

血缘的价值：当最终输出有误时，沿血缘链回溯可定位是哪个 stage 引入了错误，而不需要全链路重放。

## 5.5 生产验证：工具输出截断与持久化

> **Evidence Status** — production-validated. 工具输出截断已在 hermes-agent（BudgetConfig）落地；结果持久化已在多个 Coding Agent 中落地。

工具返回的数据量往往远超 Agent 的 context window 容量。不做截断，context 会被单次工具调用的巨量输出淹没；不做持久化，被截断的信息就永久丢失。生产系统需要两层防线。

### 工具输出截断：per-tool threshold + turn-level budget

hermes-agent 的 BudgetConfig 实现了两级截断机制：

```yaml
budget_config:
  per_tool_threshold:          # 单工具输出上限
    Read: 50000 chars          # 文件读取：保留前 50k 字符
    Bash: 20000 chars          # 命令输出：保留前 20k 字符
    WebFetch: 30000 chars      # 网页内容：保留前 30k 字符
    default: 10000 chars       # 未列出的工具：10k 字符
  turn_level_budget: 100000 chars  # 单轮所有工具输出总上限
  truncation_strategy: head | tail | head_tail_split
  truncation_notice: true      # 截断时在结果中注入提示信息
```

**截断策略**：
- `head`：保留开头（适合日志、文件内容）
- `tail`：保留末尾（适合命令输出、错误信息）
- `head_tail_split`：保留开头和末尾各一半（适合长文件，保留首尾上下文）

**关键设计**：截断发生时必须注入截断提示（如 `"[TRUNCATED: 150000 chars → 50000 chars, tail omitted]"`），让模型知道信息不完整，避免基于截断数据做出错误推理。

### 工具结果持久化：超阈值外存到文件

当工具输出超过 per-tool threshold 时，完整结果不应直接丢弃，而是外存到文件系统，在 context 中只保留摘要 + 文件引用：

```text
maybe_persist_tool_result(tool_output):
  if len(tool_output) > per_tool_threshold:
    file_path = write_to_temp(tool_output)      # 完整结果写入临时文件
    summary = truncate(tool_output, threshold)   # 截断后的摘要
    return {
      summary: summary,
      full_result_ref: file_path,               # 文件引用
      original_size: len(tool_output),
      persisted: true
    }
  else:
    return { content: tool_output, persisted: false }
```

**设计价值**：Agent 可以在后续需要时通过 `Read(full_result_ref)` 按需获取完整数据，而不是在每一轮都携带全量数据。这将"推模式"（push 全量进 context）转变为"拉模式"（按需 pull），显著降低 context 压力。

### Data Lineage 追踪增强

在基础的数据血缘之上，生产系统需要为每个数据块标注更丰富的元信息：

```yaml
data_lineage_enhanced:
  item_id: string
  origin:
    source_tool: string        # 产出该数据的工具名
    tool_call_id: string       # 关联的工具调用 ID
    timestamp: datetime        # 产出时间
    trust_level: high | medium | low | unknown  # 信任层级
  transformations:
    - stage: string
      agent_id: string
      timestamp: datetime
      operation: string
      confidence_delta: float  # 该步骤对置信度的影响
  freshness:
    captured_at: datetime      # 数据采集时间
    ttl_seconds: integer       # 数据有效期
    stale: boolean             # 是否已过期
  truncation:
    was_truncated: boolean
    original_size: integer
    retained_size: integer
    full_result_ref: string    # 完整数据的外存引用（如有）
```

**信任层级规则**：
- `high`：来自用户直接输入、已验证的 API 响应
- `medium`：来自模型推理、未验证的外部数据
- `low`：来自缓存数据、过期数据、截断后的推断
- `unknown`：来源无法追溯的数据

**设计启示**：当数据流经多个 stage 时，信任层级只能降低不能升高（除非经过显式验证步骤）。这防止了"洗白"——低信任数据经过几轮转换后被当作高信任数据使用。

## 6. 与其他 Plane 的数据契约

Dataflow 不独立运行，它与相邻 Plane 之间有明确的职责边界：

| 相邻 Plane | Dataflow 的职责 | 对方的职责 | 边界 |
|---|---|---|---|
| **Concurrency** | 数据路由、分片、合并 | 并发上限、锁、取消传播 | Dataflow 决定数据往哪走；Concurrency 决定同时走几路 |
| **Context** | 数据流入 context 前的过滤和优先级排序 | context window 管理、淘汰策略 | Dataflow 负责"送什么进来"；Context 负责"装得下多少" |
| **Execution** | 将数据交给 stage 的执行请求 | 沙箱内实际执行 | Dataflow 管数据生命周期；Execution 管单次执行生命周期 |
| **Recovery** | 报告 stage 失败和受影响的 item 范围 | 决定恢复策略（retry / skip / compensate） | Dataflow 上报故障；Recovery 决定怎么处理 |
| **Observability** | 每个 stage 发出 throughput / latency / error_rate 指标 | 聚合展示和告警 | Dataflow 产出原始指标；Observability 消费和展示 |

## 7. 错误传播

```text
upstream representation error
  → quarantine item
  → do not pass as fact
  → preserve raw ref
  → report aggregate uncertainty
```

```text
downstream effect failure
  → stop dependent stages
  → mark pending effects
  → compensate if necessary
  → keep successful independent items
```
