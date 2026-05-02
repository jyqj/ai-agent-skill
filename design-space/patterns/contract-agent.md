# Contract Agent Pattern

> **Evidence Status** — grounded. Google Agents Companion (2025) 的"From Agents to Contractors"提案；企业级任务分解、协商与验收的需求；多 Agent 子任务标准化的需求。

## 问题

Agent 接收的任务定义往往 underspecified：只有粗略目标和工具列表。当任务复杂度上升、stakes 变高时，这种松散定义导致：
- 交付物模糊，无法自动验证
- 无法协商优先级和成本
- 子任务拆分缺乏标准协议
- 反馈循环不规范

## 解法

将 Agent 任务升级为"契约"(Contract)：一个结构化的协议对象，明确定义交付物、验收标准、成本预期、反馈机制和协商通道。

## Contract Schema

```yaml
contract:
  contract_id: string
  initiator: user_id | agent_id
  contractor: agent_id

  # 核心定义
  task_description: string           # 详细描述期望达成什么
  deliverables:                      # 精确的交付物和验收标准
    - artifact: string
      specification: string          # 什么使交付物可接受
      verification_method: string    # 如何验证交付物满足要求
  scope:                             # 明确范围和排除项
    in_scope: []
    out_of_scope: []

  # 约束
  expected_cost: cost_envelope       # 成本预期（token / time / API calls）
  expected_duration: duration        # 时长预期
  input_sources: []                  # 可使用的输入来源

  # 协作机制
  reporting:
    frequency: string                # 进度报告频率
    channel: string                  # 反馈通道
    escalation_trigger: string       # 何时升级

  # 状态
  status: proposed | negotiating | accepted | executing | delivered | verified | failed
  negotiation_log: []                # 协商历史
  subcontracts: []                   # 子契约引用
```

## Contract 生命周期

```text
Propose → Negotiate → Accept → Execute → Deliver → Verify
                ↑                    ↓
                └── Feedback / Clarification ──┘
```

### 1. Propose
发起方定义契约，尽可能精确描述交付物和验收标准。

### 2. Negotiate
Contractor（Agent）可以：
- 指出 underspecification，请求澄清
- 就成本进行协商（任务复杂度 vs 分配资源）
- 标记风险
- 请求额外输入数据

```yaml
negotiation_message:
  underspecification: []   # 需要澄清的方面
  cost_negotiation: string # 成本异议
  risk: []                 # 潜在风险
  additional_input_needed: [] # 需要的额外信息
```

### 3. Execute
Contractor 按契约规格执行。关键行为：
- 优先质量和完整性而非延迟
- 可生成多种方案，评分选择最优
- 可自我验证结果对照验收标准
- 可自我纠正直到 validators 通过

### 4. Subcontract
当任务过于复杂时，Contractor 可拆分为子契约：
- 子契约遵守相同 schema
- 统一的格式使任意 Agent 可处理
- 子契约的进入执行队列

### 5. Verify
交付物对照 `deliverables.verification_method` 验证。

## 与现有架构的关系

| 架构模块 | Contract Pattern 的作用 |
|---|---|
| TaskEnvelope | Contract 是 TaskEnvelope 的增强版：增加协商、验收标准和成本约束 |
| Orchestration | Subcontract 是 Worker Orchestration 的标准化协议 |
| Effects | Contract deliverables 直接映射到 EffectRecord |
| Interaction | Negotiation 是结构化的人机/Agent 间交互 |
| Cost | Contract 显式包含成本预期和资源协商 |
| Stop Gate | 验收标准定义何时任务可以停止 |

## 何时使用

| 场景 | 推荐 |
|---|---|
| 简单单轮工具调用 | 不需要 Contract，TaskEnvelope 即可 |
| 高 stakes 多步任务 | 使用 Contract + 验收标准 |
| 多 Agent 委派 | 使用 Contract + Subcontract |
| 长时间异步任务 | 使用 Contract + 进度报告 + 协商 |
| 需要成本控制的企业场景 | 使用 Contract + 成本协商 |

## 与 Output Contract 的区别

| 维度 | Output Contract | Agent Contract |
|---|---|---|
| 范围 | 只约束输出格式 | 约束全流程：目标、验收、成本、协商 |
| 方向 | 单向（约束 Worker） | 双向（允许 Contractor 协商） |
| 验证 | 结构验证 | 业务语义验证 |
| 生命周期 | 无 | 完整生命周期状态机 |

## 反模式

| 反模式 | 表现 | 修复 |
|---|---|---|
| 空壳契约 | 只有 task_description 没有验收标准 | 必须有 deliverables + verification_method |
| 过度规格 | 契约太详细导致比直接做还慢 | 契约粒度应与任务复杂度和风险匹配 |
| 无限协商 | Agent 不断请求澄清不开始执行 | 设置 negotiation budget 和 max_rounds |

## 参考来源

- Google "Agents Companion" (2025): From Agents to Contractors
- Google Co-Scientist: Generate-Debate-Evolve 模式
- AlphaCode: 验证驱动的迭代生成
