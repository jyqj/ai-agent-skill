# Agent Economics

> **Evidence Status** — synthesized. 从 cost plane（模型路由、缓存、预算）和 paradigms/methodology（MVA 阶梯）扩展；结合生产 Agent 的常见采纳失败模式。经济学建模在 Agent 领域仍缺乏标准化方法。

## 1. 问题

架构知识库详细讨论了"如何构建 Agent"，但缺少对以下问题的回答：

- **值不值得用 Agent？**（ROI 判断）
- **Agent 到底省了什么？**（价值度量）
- **什么任务不应该用 Agent？**（反向判断）
- **Agent 的隐性成本是什么？**（全周期成本）

没有经济学模型的 Agent 项目容易陷入两个极端：要么"什么都用 Agent"（成本失控），要么"Agent 太贵了"（价值低估）。

## 2. Agent 成本模型

### 2.1 全周期成本

```text
Total Cost of Agent = Build Cost + Run Cost + Maintain Cost + Risk Cost

Build Cost:
  - 架构设计与范式选择
  - 工具集成与测试
  - Prompt 工程与调优
  - 评估体系构建
  - 安全边界与合规审查

Run Cost:
  - LLM API 调用（token 消耗）
  - 工具执行（外部 API、计算资源）
  - 存储（上下文、记忆、checkpoint、trace）
  - 人工监督（审批、纠错、教学）
  - 基础设施（运行时、队列、数据库）

Maintain Cost:
  - 模型升级适配
  - 工具变更跟踪
  - Prompt 漂移修复
  - 评估回归
  - 新能力集成

Risk Cost:
  - 错误操作的修复成本
  - 安全事件的响应成本
  - 合规违规的处罚成本
  - 用户信任损失的机会成本
```

### 2.2 单任务运行成本分解

```text
Task Run Cost = Σ(turn_cost) + overhead

turn_cost = model_cost(input_tokens, output_tokens, model_tier)
          + tool_cost(api_calls, compute_time)
          + verification_cost(readback, external_check)

overhead = context_management(compression, retrieval)
         + state_persistence(checkpoint, world_state_refresh)
         + trace_storage(events, retention)
```

## 3. Agent 价值模型

### 3.1 价值维度

| 维度 | 度量方式 | 示例 |
|---|---|---|
| 时间节省 | (人工时间 - Agent 时间) × 人工单价 | 代码审查从 30min 降到 5min |
| 质量提升 | 减少的错误数 × 单个错误修复成本 | 减少 20% 的生产事故 |
| 规模化 | 人工不可能的并行度 | 同时监控 1000 个服务 |
| 一致性 | 减少的人为疏忽 | 100% 执行 checklist |
| 可用性 | 7×24 可用 vs 工作时间 | 凌晨自动响应告警 |
| 知识沉淀 | 隐性知识显式化 | 运维经验转化为可复现流程 |

### 3.2 ROI 计算

```text
ROI = (Value_generated - Total_cost) / Total_cost

Value_generated = time_saved × hourly_rate
               + errors_avoided × error_cost
               + scale_premium
               + availability_premium

Break-even: Total_cost = Value_generated
```

**注意**：ROI 计算必须包含 Build Cost 和 Maintain Cost，不能只看 Run Cost。许多 Agent 项目的 ROI 失算是因为低估了构建和维护成本。

## 4. 任务适用性判断

### 4.1 适合用 Agent 的任务

| 特征 | 原因 | 示例 |
|---|---|---|
| 高频 + 低变异 | 构建成本可以被大量执行摊薄 | 日常代码审查、日报生成 |
| 高认知负载 + 低创造性 | Agent 擅长处理信息密集但模式化的任务 | 日志分析、合规检查 |
| 需要 7×24 响应 | 人工不可能持续值班 | 告警响应、监控 |
| 需要跨系统协调 | Agent 可以同时操作多个系统 | 发布流水线、多系统数据同步 |
| 有明确验证标准 | 可以构建效果闭环 | 测试通过、文件存在、API 返回 200 |

### 4.2 不适合用 Agent 的任务

| 特征 | 原因 | 示例 |
|---|---|---|
| 一次性 + 高构建成本 | ROI 为负 | 一次性数据迁移（写脚本更划算） |
| 高创造性 + 主观判断 | Agent 无法可靠替代人类判断 | 产品战略决策、品牌设计 |
| 极高风险 + 不可逆 + 无验证通道 | 效果闭环不可构建 | 直接执行金融交易（无沙盒） |
| 低频 + 高变异 | 每次都需要大量适配 | 偶发性特殊客户需求 |
| 依赖隐性知识且无法形式化 | Agent 无法获取必要表示 | 依赖"第六感"的故障诊断 |
| 法律要求人类决策 | 合规约束 | 医疗诊断、贷款审批（需人类签字） |

### 4.3 决策矩阵

```text
                    高频                          低频
            ┌──────────────────┬──────────────────┐
  可验证     │  ★ Agent 最佳区   │  Agent 可能值得    │
            │  ROI 高，闭环好   │  看构建成本        │
            ├──────────────────┼──────────────────┤
  难验证     │  Agent + 人工监督  │  ✗ 不建议用 Agent  │
            │  需要交互层投入    │  用脚本或人工更划算  │
            └──────────────────┴──────────────────┘
```

## 5. 成本优化策略

| 策略 | 适用场景 | 节省幅度 | 风险 |
|---|---|---|---|
| 模型分层路由 | 混合简单/复杂子任务 | 30-60% LLM 成本 | 路由错误导致质量下降 |
| Prompt 缓存 | 高频相似任务 | 20-50% token 消耗 | 缓存失效导致过期回答 |
| 上下文压缩 | 长任务 | 40-70% token 消耗 | 压缩损失关键信息 |
| 批量执行 | 独立同构任务 | 并行节省时间成本 | 单任务失败不应影响其他 |
| 提前终止 | 低价值任务 | 避免沉没成本 | 误判导致有价值任务被中止 |
| MVA 阶梯 | 新 Agent 产品 | 降低初始投资 | 过早停在低 MVA 阶段 |

## 6. 经济学反模式

| 反模式 | 表现 | 修复 |
|---|---|---|
| Hidden Cost Explosion | 只算 API 费用，忽略维护和监督成本 | 全周期成本核算 |
| Agent for Everything | 所有任务都用 Agent，包括不适合的 | 任务适用性评估 |
| Premature Optimization | 在验证价值之前就优化成本 | 先 MVA 验证，再优化 |
| Sunk Cost Fallacy | Agent 已经建了所以必须用 | 定期重新评估 ROI |
| Free Lunch Illusion | 忽略人工监督成本 | 把监督时间纳入 Run Cost |
| Metric Theater | 度量 token 数而不是业务价值 | 用业务指标衡量 ROI |

## 7. 经济学检查清单

```text
[ ] 这个任务是否满足"适合用 Agent"的特征？
[ ] 构建成本预估是否包含了安全、评估和维护？
[ ] 运行成本预估是否包含了人工监督？
[ ] 是否有明确的效果验证标准来衡量价值？
[ ] ROI 计算是否基于保守假设？
[ ] 是否有提前终止的退出标准？
[ ] 是否从 MVA-1 开始验证而不是一步到位？
```

## 8. 与本框架其他层的关系

| 层 | 关系 |
|---|---|
| `cost/overview.md` | Cost Plane 处理运行时预算；本文档处理全周期经济学 |
| `methodology/minimum-viable-agent.md` | MVA 阶梯是降低初始经济风险的核心策略 |
| `methodology/autonomy-and-depth.md` | 更高自治度 = 更高构建成本 + 更低运行时人工成本 |
| `evaluation/` | 评估体系本身有成本，需要 ROI 合理 |
| `design-space/anti-patterns/hidden-cost-explosion.md` | 经济学反模式的详细案例 |

## Evidence Status

混合来源。成本模型和任务适用性判断基于多个生产 Agent 项目的实际数据归纳。ROI 计算框架和经济学反模式为理论总结，定量结论需要根据具体场景调整。
