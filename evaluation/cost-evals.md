# Cost Evaluations

> **Evidence Status** — synthesized. Cost Plane、benchmarking、model routing 与可执行 eval 的需求。

## 目标

把成本工程从“账单复盘”变成可回归的评估对象。

## 评估问题

```text
1. 哪种 routing 更省，但不明显伤害 verified success？
2. retrieval/verification 的边际收益在哪里开始递减？
3. 缓存是否真的带来成本和延迟优势？
4. 多 agent / worker fanout 什么时候开始不划算？
```

## 指标

| 指标 | 含义 |
|---|---|
| Cost per Completed Task | 完成任务的平均成本 |
| Cost per Verified Task | 带验证完成的平均成本 |
| Tail Cost | 成本尾部风险 |
| Latency | 平均与尾时延 |
| Token Efficiency | 每单位 token 带来的 verified gain |
| Tool Efficiency | 每个 tool call 的边际收益 |

## 推荐实验

### Model Routing

- single-tier
- tiered routing
- difficulty-aware routing

### Retrieval Budget

- low fanout
- medium fanout
- high fanout

### Verification Depth

- minimal
- standard
- critical

## 读法

成本图最好和 success / verified success 一起看：

```text
便宜但经常假完成
≠
真正更优
```

## 全载成本模型

仅报告 token 成本通常**低估真实费用 40-70%**。全载成本模型（Fully-Loaded Cost Model）须覆盖所有成本组件：

| 成本组件 | 说明 | 常见低估幅度 |
|---------|------|-------------|
| LLM Token 费用 | 输入 + 输出 token，含推理模型溢价 | 基线（通常是唯一被计量的） |
| 工具调用费用 | 外部 API 调用（搜索、数据库、第三方服务） | 10-20% |
| 基础设施成本 | 计算、存储、网络、沙箱环境 | 10-15% |
| 人工审核成本 | 人工监督、修正、质量抽查 | 15-30% |
| 工程维护成本 | Prompt 迭代、评估维护、监控、oncall | 5-15%（摊销） |

**Agent 工作负载比标准聊天贵 3-10x**，因多重乘数效应：
- 多轮循环：10 轮 ReAct 消耗单次线性传递 50x 的 token
- 上下文缩放：128K vs 8K 窗口（attention 矩阵 n² 缩放）
- 输出溢价：输出 token 比输入 token 贵 3-8 倍
- 工具开销：每轮 +schema/call/result 的 token 注入

来源：[Zylos - AI Agent Cost Optimization: Token Economics and FinOps](https://zylos.ai/research/2026-02-19-ai-agent-cost-optimization-token-economics)

## ROI 三层模型

从"完成了多少任务"到"创造了多少价值"的递进衡量：

| 层级 | 名称 | 公式 | 说明 |
|------|------|------|------|
| L1 | **完成 ROI** | 完成任务数 / 全载成本 | 必要基线但不充分 |
| L2 | **结果 ROI** | 结果商业价值 / 全载成本 | 需要将输出向前追踪 1-2 步到实际工作流 |
| L3 | **复合 Agent 价值 (CAV)** | (结果价值 x 质量乘数) / 全载成本 | 质量乘数 0.0-1.0 基于人工修正需求 |

**核心洞察**："完成 95% 任务但产生零业务结果的 Agent，ROI 为零。"

CAV > 1.0 表示 Agent 返回的价值超过消耗，是 Agent 价值的基线判定标准。

**报告节奏**：
- 周报：完成率、错误率、成本指标（捕获运营漂移）
- 月报：结果率、结果价值、质量乘数（足够的量产生信号）
- 季报：CAV 趋势、项目级 ROI、退役/上线总结（对齐预算周期）

来源：[Digital Applied - AI Agent ROI Measurement Beyond Task Completion](https://www.digitalapplied.com/blog/ai-agent-roi-measurement-beyond-task-completion)

## 七大衡量陷阱

| # | 陷阱 | 问题 | 修正 |
|---|------|------|------|
| 1 | 幸存者偏差 | 排除已下线 Agent | 计算中包含所有曾部署的 Agent |
| 2 | 虚荣分母 | 与零基线比较 | 使用时间匹配的人工工作流对比 |
| 3 | 工具调用膨胀 | 将 API 调用计为价值指标 | 仅报告已完成任务；单独追踪工具调用 |
| 4 | 未计价人力 | 忽略审核/修正成本 | 以全载人力成本计入人工监督 |
| 5 | 最佳周报告 | 将异常表现作为基线 | 使用滚动 3 个月中位数 |
| 6 | 结果回填 | 无因果证明的事后归因 | 在 Agent 启动时定义结果和因果关系 |
| 7 | 仅 Token 计价 | 忽略 40-70% 的真实费用 | 始终使用全载成本模型 |

来源：[Digital Applied - Beyond Task Completion](https://www.digitalapplied.com/blog/ai-agent-roi-measurement-beyond-task-completion)

## 关联文档

- `../architecture/planes/cost/benchmarking.md`
- `execution-depth-evals.md`
- `tool-use-evals.md`
