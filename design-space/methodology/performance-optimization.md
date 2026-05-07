# Performance Optimization Decision Framework

> **Evidence Status** — grounded. Google "Improving LLM Reliability and Performance" (2024)；Google "Agents Companion" (2025) AgentOps；本知识库 cost plane 和 model-routing。

## 核心命题

Agent 的经济性不是事后统计，而是设计期决策：选择什么技术组合直接决定成本-质量曲线。

## 性能优化决策树

```text
需要额外数据吗？
├── NO → Prompt Engineering
└── YES
    ├── 数据是动态的（每次查询不同）？
    │   └── YES → Prompt Engineering + RAG
    └── 数据是静态的？
        ├── 能放进上下文窗口？
        │   └── YES → Corpus-in-Context + Many-shot
        └── 超出上下文窗口？
            └── Prompt Engineering + RAG

Fine-tuning 何时考虑？
→ 上述方法都无法满足精度要求时
→ 需要特定行为模式（如工具调用格式）时
→ 需要降低推理成本（大模型→小模型蒸馏）时
```

## 技术组合矩阵

| 技术 | 实施复杂度 | 性能提升 | 成本影响 | 适用阶段 |
|---|---|---|---|---|
| Prompt Engineering | 低 | 中-高 | 低 | 始终优先 |
| RAG | 中 | 高 | 中（基础设施） | 需要外部知识时 |
| Long Context / Many-shot | 低-中 | 中-高 | 高（token 量） | 数据可放入窗口时 |
| Fine-tuning (LoRA/QLoRA) | 高 | 高 | 高（训练） + 低（推理） | 精度要求极高时 |
| Distillation | 高 | 中 | 降低推理成本 | 需要缩小模型时 |
| Context Caching | 低 | 无变化 | 降低 75% | 重复上下文场景 |

## AI 用例原型

| 原型 | 描述 | 推荐起点 |
|---|---|---|
| **Search** | 查找和摘要信息 | Prompt + RAG |
| **Execute** | 定制标准内容/代码 | Prompt Engineering |
| **Support** | 回答多样问题、提供指导 | Prompt + RAG |
| **Ideate** | 创造新想法、框架 | Prompt Engineering |
| **Act** | 端到端完成业务流程 | Prompt + RAG + Tools |

## Corpus-in-Context vs RAG

| 维度 | Corpus-in-Context | RAG |
|---|---|---|
| 适用数据量 | 窗口内（≤2M tokens） | 无上限 |
| 实现复杂度 | 低（特殊 prompt engineering） | 中-高 |
| 信息损失 | 低（全量可见） | 中（chunk 切分和检索不完美） |
| 跨段落关联 | 天然支持 | 需要多跳推理 |
| 成本 | token 量大时高 | 检索基础设施成本 |
| 实时性 | 每次需重新注入 | 索引可持久化 |
| 结合 caching | 可大幅降低成本 | N/A |

## 评估驱动开发循环

```text
Evaluate → Compare → Enhance → Predict → Evaluate...

1. Evaluate: 用输入-输出对计算性能指标
2. Compare: 识别精度/风格/成本的差距
3. Enhance: 选择技术提升（prompt/RAG/fine-tune/context）
4. Predict: 用更新的方案跑评估集
```

## Model Routing 策略

```yaml
model_routing:
  default: large_model
  optimization_path:
    - evaluate_with_large_model
    - if_performance_sufficient:
        try_smaller_model_with_finetuning
    - if_still_insufficient:
        try_distillation_from_large_to_small
    - measure_cost_quality_tradeoff

  routing_rules:
    - condition: task_complexity == "simple"
      model: small_fast_model
    - condition: task_complexity == "complex" || high_risk
      model: large_capable_model
    - condition: repeated_context
      strategy: context_caching + small_model
```

## AgentOps：运维体系

Agent 运维是 DevOps + MLOps 的超集：

```text
DevOps（确定性软件）
  └── MLOps（模型训练和部署）
      └── FMOps（基础模型定制）
          ├── PromptOps（提示管理和版本控制）
          ├── RAGOps（检索管道管理）
          └── AgentOps（Agent 运维）
              ├── 工具管理（注册、版本、监控）
              ├── Agent 编排（路由、调度、生命周期）
              ├── 记忆管理（写入策略、失效、审计）
              ├── 任务分解（Contract、子任务管理）
              └── A/B 实验与北极星指标
```

关键指标体系（分层）：

| 层 | 指标 | 采集方式 |
|---|---|---|
| Business KPI | 收入、用户参与度、NPS | 业务系统 |
| Goal Completion | 目标达成率 | Agent trace |
| Critical Task Success | 关键步骤成功率 | Trajectory eval |
| Application Telemetry | 延迟、错误、token 用量 | APM/Trace |
| Human Feedback | 👍👎、定性反馈 | UI 收集 |
| Detailed Trace | 内部决策链路 | Observability |

## 与本知识库的关系

| 现有模块 | 本文档的贡献 |
|---|---|
| `architecture/planes/cost/model-routing.md` | 增加决策树和用例原型维度 |
| `architecture/planes/cost/caching.md` | Context Caching 作为一等优化策略 |
| `architecture/planes/cost/cost-quality.md` | 技术组合矩阵提供选择依据 |
| `paradigms/memory-paradigms.md` | Corpus-in-Context 作为 RAG 的替代选项 |
| `architecture/planes/observability/overview.md` | AgentOps 指标分层体系 |

## 参考来源

- Google Cloud "Improving LLM Reliability and Performance" (Sep 2024)
- Google Cloud "AI Agent Trends 2026"
- Google "Agents Companion" (Feb 2025): AgentOps
