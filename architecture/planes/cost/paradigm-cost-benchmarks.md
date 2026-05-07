# 范式成本基准

> **Evidence Status** — grounded. 数据来源于 2025-2026 年多项公开研究、生产系统成本报告和学术论文，包括 Zylos Token Economics、ACL 2025 TALE 论文、Budget-Aware Agent Scaling 研究、Anthropic Context Engineering 实践、以及六大可观测性平台的公开定价信息。

---

## 全载成本模型

### 问题：仅计 Token 成本低估 40-70%

大多数团队在评估 Agent 成本时仅计算 LLM API 的 token 费用。这种方式系统性低估真实费用 40-70%，因为忽略了以下不可忽视的开销：

| 成本类别 | 占比估算 | 说明 |
|---------|---------|------|
| **LLM Token** | 30-60% | 输入 + 输出 + 推理 token；输出/输入成本比 ~4:1，推理模型可达 8:1 |
| **工具调用** | 10-20% | 外部 API 费用（搜索、数据库、第三方服务）、MCP Server 运行成本 |
| **基础设施** | 10-25% | 计算资源、存储、网络、沙箱环境（Daytona 等）、可观测性平台订阅 |
| **人工审核** | 10-30% | 审核/修正成本、escalation 处理、质量抽检；高风险领域比例更高 |
| **工程维护** | 5-15% | Prompt 迭代、Harness 维护、回归测试、模型版本适配（摊销） |

### 全载成本公式

```
全载成本 = Token 成本 + 工具费用 + 基础设施成本 + 人工审核成本 + 摊销工程维护
```

在 ROI 计算中，必须使用全载成本而非仅 Token 成本。具体 ROI 方法论参见语料中的三层 ROI 模型：L1 完成 ROI、L2 结果 ROI、L3 复合 Agent 价值 (CAV)。

---

## Agent 成本结构

### 3-10x 乘数效应

Agent 工作负载相比单次 LLM 调用贵 **3-10 倍**，原因是多重乘数叠加：

| 成本因素 | 放大倍数 | 机制 |
|---------|---------|------|
| 多轮循环 | 50x | 10 轮 ReAct 循环消耗单次线性传递 50 倍的 token |
| 上下文缩放 | 64x | 128K 窗口 vs 8K 窗口（attention 矩阵 n^2 缩放） |
| 输出溢价 | 3-8x | 输出 token 比输入 token 贵 3-8 倍 |
| 工具开销 | 每轮 +schema/call/result | 工具描述、调用和结果注入消耗额外 token |

### 毛利对比

| 指标 | Agent 产品 | 传统 SaaS |
|------|-----------|----------|
| 毛利率 | 50-60% | 80-90% |
| 边际成本 | 高（每次交互均产生 LLM 费用） | 极低（基础设施边际成本趋近零） |
| 成本可预测性 | 低（推理时间可变、工具调用不确定） | 高（固定基础设施开支） |

未优化的单次 Agent 任务成本为 **$5-8**，复杂会话可达 **$10-$100+**。这意味着 Agent 产品在商业模型上必须更积极地管理成本，才能维持合理毛利。

---

## 六大成本优化策略

组合使用以下策略可达 **60-80% 总成本削减**：

### 策略一览

| # | 策略 | 单独成本削减 | 实现方式 |
|---|------|-----------|---------|
| 1 | **Context Compaction** | 2-3x 更长有效会话 | Anthropic Compaction API (compact-2026-01-12) 自动摘要旧上下文；保留架构决策，丢弃冗余输出 |
| 2 | **模型路由（Model Routing）** | 最高 87% | 静态/动态置信度路由；前沿模型 vs 小模型成本差 190x；RouteLLM 等框架 |
| 3 | **语义缓存 + Prompt 缓存** | ~90%（缓存命中 token） | Anthropic prefix caching (0.1x 基础价格)；语义缓存消除 ~31% 重复查询 |
| 4 | **并行执行** | 因场景而异 | 多独立 agent 并行 + 多数投票/best-of-N；适合可分解任务 |
| 5 | **Token Budget 管理** | 40-67% | TALE 框架 -67%、Budget Tracker -40%、BudgetThinker 周期性控制 token |
| 6 | **Batch API** | 50% 折扣 | 异步工作负载，24 小时周转；适合离线分析、数据处理 |

### 策略详解

**1. Context Compaction**
- 核心公式："发现使期望结果概率最大化的最小高信号 token 集合"
- 关键手段：Just-In-Time 检索（轻量标识符 + 运行时动态加载）、结构化外部记忆（NOTES.md 模式）、Sub-Agent 返回精炼摘要（1000-2000 token）
- 设计哲学："做最简单的有效方案"

**2. 模型路由**
- 层级化推理：简单任务 -> Haiku/Flash/o4-mini；中等 -> Sonnet/GPT-4o；复杂 -> Opus/o3-pro
- Planner-Executor 分离：Planner 用重型推理模型，Executor 用轻量模型，成本降低 45%
- 动态置信度路由：根据查询复杂度实时切换模型层级

**3. 语义缓存 + Prompt 缓存**
- Prompt 缓存对长 system prompt + 工具定义效果显著（agent 场景高度适用）
- 语义缓存基于向量相似度匹配，API 调用前拦截重复查询
- 组合可将缓存命中场景的 token 成本降至原始的 1-10%

**4. 并行执行**
- 顺序扩展鼓励更深探索，并行扩展提升覆盖度
- 并行多 agent + 多数投票可在同等 budget 下提升 2x 准确率
- 需注意并行执行的总成本上限控制

**5. Token Budget 管理**
- TALE-EP：零样本估计 token 预算 -> 嵌入推理提示，标准 CoT 平均 461 tokens 降至 149 tokens
- 关键发现：过度紧缩的 budget 反而增加实际 token 消耗（"放弃合规"效应）
- Budget Tracker 轻量插件：显示剩余/已用资源，40.4% 更少搜索调用

**6. Batch API**
- 适用于非实时场景：数据标注、批量分析、离线评估
- 延迟换成本：24 小时周转但 50% 折扣

---

## 推理模型成本对比表

以下为经过实验验证的成本优化架构方案，基准对比对象为标准 ReAct baseline：

| 方案 | 成本变化 | 性能变化 | 核心机制 | 来源 |
|------|---------|---------|---------|------|
| **Planner-Executor 分离** | **-45%** | 持平或更优 | Planner 用推理模型、Executor 用轻量模型 | Planner-Executor Agentic Framework |
| **Budget-Aware (BATS)** | **-40%** | **+2x** (BrowseComp 24.6% vs 12.6%) | Budget Tracker 显示剩余资源，agent 动态调整搜索深度 | Budget-Aware Tool-Use (arXiv) |
| **TALE-EP** | **-67%** (token), **-59%** (费用) | 持平 | 零样本 token 预算估计 + 嵌入推理提示 | Token-Budget-Aware LLM Reasoning (ACL 2025) |
| **RouteLLM 级联** | **-85%** | 微降 (~2-5%) | 静态/动态置信度路由，190x 成本差模型间切换 | Zylos Token Economics |
| **Prompt Caching** | **-90%** (缓存 token) | 无变化 | Anthropic prefix caching 0.1x 基础价格 | Anthropic 官方文档 |
| **蒸馏部署** | **-90%** (GPU 时间) | 可达纯 RL 性能 | DeepSeek-R1 蒸馏仅需 1/10 GPU 时间 | DeepSeek-R1 论文 |

### 关键发现

- **标准 ReAct baseline 在 budget=100 时饱和**，无法利用更多资源——Budget-Aware 设计是突破 scaling ceiling 的关键
- **Planner-Executor 是最稳健的单一架构优化**：不依赖特定框架，适用面最广
- **RouteLLM 成本削减最激进**，但需要接受少量质量损失；适合大流量、容错高的场景
- **组合策略效果不是简单相加**：Planner-Executor + Budget-Aware + Caching 可实现 70-85% 成本削减

---

## 范式 x 成本影响矩阵

不同 Agent 范式在 token 消耗上具有截然不同的特征：

| 范式 | Token 消耗特征 | 成本驱动因素 | 适用优化策略 | 典型成本区间 |
|------|--------------|------------|------------|------------|
| **ReAct** | 高：每轮完整上下文重传 | 循环次数 x 上下文长度；输出 token 占比高 | Compaction、Caching、迭代上限 | $$-$$$ |
| **Plan-and-Execute** | 中：规划一次，执行多次 | Planner 推理成本高但一次性；Executor 成本低 | 模型路由（Planner/Executor 分离） | $-$$ |
| **ReWOO** | 低：一次性规划，无中间上下文重传 | 初始规划 token；但失败重试成本高 | Batch API（离线规划）、缓存 | $ |
| **Reflexion** | 极高：多轮自我反思 + 完整轨迹重传 | 反思循环次数；每轮需要完整历史 | Budget 管理（反思次数上限）、Compaction | $$$-$$$$ |
| **Tree-of-Thoughts** | 高：多分支探索 | 分支数 x 每分支深度；大量并行生成 | 并行执行、剪枝策略、Budget 上限 | $$-$$$$ |
| **Hybrid (Plan+ReAct)** | 中偏高：全局规划 + 局部循环 | 规划成本 + 局部 ReAct 循环成本 | 模型路由 + Compaction + Budget | $$-$$$ |
| **Multi-Agent** | 可变：取决于拓扑和通信频率 | Agent 间通信开销；每个 Agent 独立上下文 | Sub-Agent 摘要、共享缓存、A2A 协议优化 | $$-$$$$ |

### 成本区间说明
- $：<$0.10/任务；$$：$0.10-$1.00/任务；$$$：$1.00-$10.00/任务；$$$$：>$10.00/任务

### 范式选择的成本决策树

```
任务复杂度评估
  |
  +-- 简单（1-2步）-> ReWOO 或 直接调用 -> $
  |
  +-- 中等（3-6步）
  |     +-- 强审计需求 -> Plan-and-Execute -> $-$$
  |     +-- 快速响应 -> ReAct + 迭代上限 -> $$
  |
  +-- 复杂（7+步）
        +-- 可分解 -> Hybrid (Plan+ReAct) + 模型路由 -> $$-$$$
        +-- 需要自我验证 -> Reflexion + Budget 管理 -> $$$
        +-- 多角色协作 -> Multi-Agent + Sub-Agent 摘要 -> $$-$$$$
```

---

## 可观测性工具对比

成本优化的前提是可观测性。以下是 2026 年六大 Agent 可观测性平台的对比：

### 能力矩阵

| 平台 | 许可证 | Trace 深度 | 成本追踪 | 评估集成 | 非确定性支持 | 会话拼接 |
|------|--------|-----------|---------|---------|------------|---------|
| **Laminar** | Apache 2.0 | 2000+ span | 逐 trace 成本 | Signals + SQL | 完整 | 多进程拼接 |
| **Langfuse** | MIT | 标准 | 逐 trace 成本 | Eval harness | 部分 | 标准 |
| **LangSmith** | 闭源 | 标准 | 按 trace | LangGraph Studio | LangGraph 内 | LangGraph 内 |
| **Arize Phoenix** | Elastic 2.0 | OpenTelemetry 原生 | OpenInference | Phoenix Evals | 标准 | 标准 |
| **W&B Weave** | 闭源 | 标准 | W&B 集成 | Eval 框架 | 标准 | 标准 |
| **Braintrust** | 闭源 | 标准 | 按使用量 | 回归检测 | 实验 harness | 标准 |

### 定价对比

| 平台 | 定价模型 | 入门价 | 自托管 | 成本可预测性 |
|------|---------|-------|--------|------------|
| **Laminar** | 数据量 | $30-150/月 | 免费 | 高（对大 trace 最可预测） |
| **Langfuse** | 可计费单位 | $29-199/月 | 开源自部署 | 中 |
| **LangSmith** | 按席位 + 按 trace | $39/月/席位 | 不支持 | 低（随复杂度增长） |
| **Arize Phoenix** | 开源 + 托管 | 免费（开源） | 免费 | 高 |
| **W&B Weave** | 按量 + 按席位 | W&B 定价 | 不支持 | 中 |
| **Braintrust** | 按使用量 | 企业定制 | 不支持 | 中 |

### 选型建议

- 生产 Agent 深度调试 + 成本追踪 -> **Laminar**（最强 trace 深度 + 数据量定价可预测）
- Prompt 管理 + 版本迭代为核心 -> **Langfuse**（MIT 开源 + prompt 版本化）
- LangGraph 深度用户 -> **LangSmith**（LangGraph Studio 是唯一的 Agent IDE）
- OpenTelemetry 生态 / 已用 Arize -> **Phoenix**（开源免费 + 标准协议）
- 评估驱动开发 -> **Braintrust**（回归检测最强）

---

## 成本评审清单

在 Agent 系统设计和上线前，使用以下清单评审成本管理的完备性：

| # | 检查项 | 通过标准 |
|---|-------|---------|
| 1 | **全载成本核算** | 成本模型包含 Token + 工具 + 基础设施 + 人工审核 + 工程维护；非仅 Token 费用 |
| 2 | **迭代上限设置** | 每个 Agent 循环/工作流有明确的最大迭代次数，防止无限循环耗尽预算 |
| 3 | **Token Budget 分配** | 每个 trace 有 token 预算上限；支出异常触发 2-sigma 告警 |
| 4 | **模型路由策略** | 简单/中等/复杂任务使用不同模型层级；非所有请求均走最贵模型 |
| 5 | **缓存策略** | 已启用 Prompt Caching 和/或语义缓存；缓存命中率有监控 |
| 6 | **Compaction 策略** | 长会话有上下文压缩机制；关键信息（架构决策、约束）在压缩后保留 |
| 7 | **成本可观测性** | 逐 trace 粒度的成本追踪已部署；可查看每工作流运行成本、缓存命中率、输出/输入比 |
| 8 | **毛利可行性** | 已计算 Agent 产品的单位经济模型；毛利率在可持续区间（>50%） |
| 9 | **范式-成本匹配** | 选用的 Agent 范式与任务复杂度和成本约束匹配；非默认使用最贵范式 |
| 10 | **基准对比** | 已建立成本基线，新版本/新策略的成本变化可量化对比 |

---

## 与知识库的映射

本文件所涉内容与知识库其他模块的对应关系：

| 本文主题 | 知识库位置 | 关系说明 |
|---------|-----------|---------|
| 全载成本模型 | `architecture/planes/cost/overview.md` | 本文扩展了 overview 中的成本分类，补充了全载公式和占比数据 |
| 模型路由策略 | `architecture/planes/cost/model-routing.md` | 本文提供路由策略的成本效果量化数据 |
| Token 预算管理 | `architecture/planes/cost/token-budgeting.md` | 本文补充了 TALE、BATS 等学术框架的实验数据 |
| 缓存策略 | `architecture/planes/cost/caching.md` | 本文汇总了 Prompt Caching 和语义缓存的成本削减数据 |
| 范式成本特征 | `paradigms/reasoning-paradigms.md` | 本文从成本维度分析各范式，为范式选择提供成本决策依据 |
| 可观测性工具 | `architecture/planes/cost/benchmarking.md` | 本文扩展了可观测性平台的详细对比，补充定价数据 |
| 模型能力 Profile | `paradigms/model-capability-profile.md` | Profile 的 `cost` 字段直接驱动本文的路由和预算决策 |
| 成本-质量权衡 | `architecture/planes/cost/cost-quality.md` | 本文的范式成本矩阵为成本-质量权衡提供量化基础 |
| 评估基准 | 语料 `agent-evaluation-cost-corpus` | 本文的成本数据来自该语料中的 ROI 衡量和 Token 经济学章节 |
| 推理模型架构 | 语料 `reasoning-models-agent-architecture-corpus` | 本文的 Planner-Executor、Budget-Aware 等方案数据来自该语料 |

---

## 来源

- [Zylos - AI Agent Cost Optimization: Token Economics and FinOps](https://zylos.ai/research/2026-02-19-ai-agent-cost-optimization-token-economics)
- [Anthropic - Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Token-Budget-Aware LLM Reasoning (ACL 2025)](https://arxiv.org/abs/2412.18547)
- [Budget-Aware Tool-Use Enables Effective Agent Scaling](https://arxiv.org/html/2511.17006v1)
- [Digital Applied - AI Agent ROI Measurement Beyond Task Completion](https://www.digitalapplied.com/blog/ai-agent-roi-measurement-beyond-task-completion)
- [CTLabs - AI Agent ROI in 2026](https://ctlabs.ai/blog/ai-agent-roi-in-2026-calculation-methods-industry-benchmarks-and-u-s-business-impact)
- [Laminar - Top 6 Agent Observability Platforms 2026](https://laminar.sh/article/2026-04-23-top-6-agent-observability-platforms)
- [Obvious Works - Token Optimization Saves Up to 80%](https://www.obviousworks.ch/en/token-optimization-saves-up-to-80-percent-llm-costs/)
- [Planner-Executor Agentic Framework](https://www.emergentmind.com/topics/planner-executor-agentic-framework)
- [BudgetThinker](https://arxiv.org/abs/2508.17196)
