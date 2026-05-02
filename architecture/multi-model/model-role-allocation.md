# 模型角色分配

> **Evidence Status** — mixed
> 来源：多模型 Agent 系统（AutoGen、CrewAI、CALM、Gorilla）的实践；model routing 和 cascade 文献；生产 Agent 对成本/延迟/安全的折衷需求。

## 1. 问题

当一个 Agent 可以调用多个模型时，需要回答：哪个步骤用哪个模型？为什么？

错误的默认选择是"所有步骤都用最强大模型"。这在成本、延迟和同源偏差三个方面都会付出不必要的代价。

## 2. 常见角色

| 角色 | 典型模型类型 | 职责 | 关键特征要求 |
|---|---|---|---|
| Planner | 大型推理模型 (o3, Claude Opus) | 任务分解、目标设定、策略选择 | 长上下文推理、multi-step planning |
| Critic / Judge | 独立中小模型 | 验证 Planner 输出、检测幻觉 | 异源（与 Planner 不同家族），避免同源偏差 |
| Embedder | 专用 embedding 模型 | 语义检索、相似度计算 | 高吞吐、低延迟、维度对齐 |
| Vision (VLM) | 多模态模型 | 图像理解、GUI 元素识别、文档 OCR | 视觉 grounding 准确率 |
| Tool Router | 微调小模型 | 快速工具选择、参数填充 | 低延迟、高准确率、schema adherence |
| Guard | 独立防护模型 | 输入过滤、输出安全检查 | 独立于生成模型、低误报率 |
| World Model | 专用预测模型 / 模拟器 | 预测动作的后果、模拟环境变化 | 物理/业务规则建模能力 |

## 3. 角色分配的决策维度

### 3.1 任务复杂度

```text
简单分类/格式化 → small model (Tool Router)
多步推理/规划   → large model (Planner)
验证/判断       → medium model (Critic)
```

复杂度不是固定的 -- 同一类任务可能因上下文不同而需要升级模型。

### 3.2 延迟要求

实时交互场景（聊天、GUI 操作）需要低延迟模型做前端响应，大模型做后台推理。

```text
用户输入 → small model 快速应答 / 确认理解
         → large model 后台规划
         → small model 执行工具调用
         → large model 验证结果
```

### 3.3 成本预算

| 策略 | 适用场景 | 成本特征 |
|---|---|---|
| 全大模型 | 高风险、低频任务 | 高成本、高质量 |
| 级联 (cascade) | 多数简单、少数复杂 | 平均成本低 |
| 固定小模型 + 升级 | 成本敏感、可接受偶尔降级 | 最低成本 |
| 并行多模型 + 投票 | 高风险、需要冗余 | 高成本、高可靠 |

### 3.4 安全需求：同源 vs 异源

同源偏差 (same-source bias) 是指同一个模型既生成又验证时，容易对自己的错误"视而不见"。

```text
生成：Model-A → 输出 X
验证：Model-A → "X 看起来没问题"   ← 同源偏差风险

生成：Model-A → 输出 X
验证：Model-B → "X 在第 3 步有逻辑错误" ← 异源校验
```

高风险场景（金融、医疗、安全）应强制异源 Critic。

## 4. 角色间的通信模式

| 模式 | 说明 | 适用场景 |
|---|---|---|
| 结构化消息 | 角色间通过 JSON/YAML 传递结构化数据 | Tool Router 和 Planner 之间 |
| 共享上下文 | 多个角色共享同一个 context window 或 memory store | Planner 和 Critic 之间 |
| Pipeline | 线性传递，上游输出是下游输入 | Embedder → Planner → Critic |
| Pub-Sub | 事件驱动，异步通知 | Guard 监听所有输出 |

### 通信开销

角色越多，通信开销越大。每次跨模型调用都有：

- 序列化/反序列化成本
- 网络延迟
- 上下文信息丢失风险

## 5. 与 Orchestration Plane 的关系

多模型在单 Agent 内的编排是**微观编排**；多 Agent 间的编排是**宏观编排**。

```text
宏观编排 (Orchestration Plane)
├── Agent-A
│   └── 微观编排 (Model Role Allocation)
│       ├── Planner (large)
│       ├── Critic (medium)
│       └── Tool Router (small)
├── Agent-B
│   └── 微观编排
│       ├── VLM
│       └── Guard
└── 通信协议 (MCP / A2A)
```

微观编排不需要跨 Agent 协议，通常在进程内完成。

## 6. 品类映射

不同 Agent 品类对角色分配的需求差异很大：

| Agent 品类 | 典型角色组合 | 关键约束 |
|---|---|---|
| Coding Agent | Planner(large) + Tool Router(small) + Critic(medium) | 延迟可接受较高，准确率最重要 |
| Browser Agent | VLM + Tool Router(small) + Guard | 延迟敏感，需要视觉理解 |
| Customer Service | Planner(medium) + Guard + Embedder | 成本敏感，安全要求高 |
| Ops / SRE | Planner(large) + World Model(时序预测) + Guard | 高风险操作，需要预测和防护 |
| Research Agent | Planner(large) + Embedder + Critic(异源) | 准确率和深度最重要 |
| Data / BI Agent | Planner(medium) + SQL 引擎(符号) + VLM(图表) | 精确计算需求高 |

选择角色组合时，从品类的核心约束出发，而不是从"有哪些模型可用"出发。

## 7. 动态角色调度

静态角色分配是起点，但成熟系统需要动态调度：

```yaml
dynamic_routing:
  rules:
    - condition: "task_complexity < threshold_low"
      allocation: "small model only, skip Critic"
    - condition: "task_complexity >= threshold_high"
      allocation: "large Planner + medium Critic + Guard"
    - condition: "safety_level == critical"
      allocation: "force heterogeneous Critic, add Guard"
    - condition: "latency_budget < 2s"
      allocation: "small model only, async Critic"
  fallback: "medium Planner + small Tool Router"
```

动态调度的前提是有可靠的**任务复杂度估计**。如果估计本身不可靠，宁可用固定分配加升级触发器。

## 8. 反模式

| 反模式 | 症状 | 改进 |
|---|---|---|
| 全大模型 | 成本高、延迟大、同源偏差 | 按步骤分配合适模型 |
| 过度碎片化 | 太多小模型串行调用，总延迟反而更高 | 合并低复杂度步骤 |
| 无异源验证 | 关键决策缺乏独立 Critic | 高风险步骤引入异源 Judge |
| 模型耦合 | 角色间直接传递 raw completion，换模型就崩 | 用结构化接口解耦 |
| 静态分配 | 所有任务用固定的角色分配，不随上下文调整 | 引入动态路由逻辑 |

## 7. 实施检查清单

- [ ] 列出 Agent 执行的所有步骤类型
- [ ] 为每种步骤标注复杂度、延迟要求、安全等级
- [ ] 选择默认模型，定义升级/降级触发条件
- [ ] 高风险步骤是否有异源 Critic？
- [ ] 角色间通信是否使用结构化接口？
- [ ] 是否有总延迟和总成本的监控？

## 延伸阅读

- `confidence-aggregation.md` -- 多模型输出不一致时的聚合策略
- `neuro-symbolic-hybrid.md` -- LLM 与符号系统的混合
- `../planes/cost/model-routing.md` -- 成本维度的模型路由
- `../planes/orchestration/overview.md` -- 宏观编排
- `../../concepts/agent-epistemics.md` -- 认识论中的同源偏差
