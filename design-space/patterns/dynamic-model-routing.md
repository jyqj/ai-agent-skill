# Dynamic Model Routing

> **Evidence Status** — synthesized. 跨项目观察 + Gulli (2025) *Agentic Design Patterns* Ch16 归纳。

## 问题

Agent 对所有查询使用同一模型，导致简单查询浪费预算、复杂查询质量不足。单一模型策略在成本-质量帕累托曲线上只能占据一个点。

## 解法

在运行时根据查询特征动态选择模型，使每次调用尽可能逼近成本-质量帕累托前沿。

## 架构组件

### Router Agent

核心枢纽，负责查询分类和模型路由：

```text
UserQuery → [Router Agent] → classification
  classification == "simple"    → Flash/Mini Model
  classification == "reasoning" → Pro Model
  classification == "search"    → Search Tool + Flash
  classification == "unknown"   → Pro Model (safe default)
```

**分类维度**：

| 类型 | 特征 | 路由目标 |
|---|---|---|
| Simple | 直接事实问答，无多步推理 | 低成本模型 |
| Reasoning | 逻辑推导、数学、多步推理 | 高能力模型 |
| Search | 需要实时信息、训练数据外的内容 | 搜索工具 + 低成本模型 |
| Creative | 开放式生成、风格敏感 | 中-高能力模型 |

**实现方式**：
- 简单启发式：查询长度 / 关键词
- LLM 分类器：用轻量模型做意图分类
- 嵌入相似度：查询向量 → 预定义类别向量最近邻
- ML 分类器：在 (query, optimal_model) 对上微调

### Fallback Chain（多级降级）

当首选模型不可用时，按层级自动回退：

```text
优先级 1 → 首选高质量模型
优先级 2 → 备选经济模型
优先级 3 → 缓存 / 近似答案
优先级 4 → 降级通知用户
```

**触发条件**：过载、限流、内容过滤、服务不可用。

### Critique Agent（反馈环）

独立的质量评估者，驱动路由规则持续优化：

- 检测路由错误：简单查询误送 Pro 模型 → 调整分类阈值
- 检测质量不足：复杂查询用 Flash 且结果差 → 上调复杂度判断
- 累积统计：按查询类型追踪成本-质量分布

## 决策矩阵

| 信号 | 路由 Pro | 路由 Flash | 说明 |
|---|---|---|---|
| 查询含多步推理链 | 是 | - | 需要深层推理 |
| 查询是单事实问答 | - | 是 | 过度分配 |
| 预算剩余 < 20% | - | 是 | 成本约束优先 |
| 延迟 SLA < 2s | - | 是 | 时间约束优先 |
| 任务风险 = critical | 是 | - | 质量优先 |
| 上一轮 Flash 失败 | 是 | - | 自动升级 |

## 与知识库其他模块的关系

| Plane | 交互方式 |
|---|---|
| Cost | Router 的分类结果直接影响 `resource_plan.routing` 选择 |
| Execution | 不同模型对应不同延迟预期和超时策略 |
| Orchestration | 子 Agent 可独立配置模型级别（规划用 Pro、执行用 Flash） |
| Observability | 路由决策必须记入 trace，支持事后审计和 Critique Agent 分析 |
| Learning | 路由规则可作为 CandidateRecord 进入学习循环 |

## 实例

**旅行规划 Agent**：
- 高层规划（理解复杂请求、分解多步骤行程、推理约束）→ Pro
- 执行任务（查航班、查酒店、找餐厅评论）→ Flash
- 成本节省估算：~60-70%（大部分调用是简单工具查询）

## 反模式

- **All-Pro**：所有查询都用最强模型 → 成本失控
- **All-Flash**：所有查询都用最便宜模型 → 复杂任务质量崩塌
- **Static Config**：路由规则硬编码不更新 → 无法适应模型价格和能力变化
- **No Feedback**：没有 Critique Agent → 路由错误无法被发现和修正

## 参考

- Gulli, A. (2025). *Agentic Design Patterns*, Ch16: Resource-Aware Optimization.
- OpenRouter Auto-routing: 系统根据内容智能选模型
- Claude Code: Per-model cost tracking (cache_read vs cache_creation 分离)
