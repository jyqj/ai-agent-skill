# Agent-as-Contractor 模式

> **Evidence Status** — synthesized. 基于企业工作流和多 Agent 系统中对结构化任务委派的实践归纳。

## 核心思想

将 Agent 视为"承包商"而非"助手"：任务通过结构化 Contract 下发，Agent 在 Contract 约束内自主执行，完成后交付可验收的 Deliverables。

## Contract 结构

```yaml
contract:
  task: string              # 任务目标的精确描述
  deliverables:             # 可验证的交付物列表
    - type: artifact | report | state_change
      acceptance_criteria: string
  scope:                    # 约束边界
    allowed_tools: []
    forbidden_actions: []
    time_budget: duration
    token_budget: int
  cost:                     # 预算与计费
    max_cost: float
    billing_model: per_task | per_token | fixed
  reporting:                # 过程汇报要求
    frequency: on_milestone | on_error | on_completion
    format: structured_log | summary
```

## 协商机制

Contract 支持双向协商，Agent 可以在接受前提出修改：

1. **澄清**：Task 描述模糊时，Agent 请求补充约束或示例。
2. **反提议**：Agent 评估后认为 budget 不足或 scope 不合理，返回修改建议。
3. **拒绝**：Agent 判断任务超出能力范围，明确拒绝并说明原因。

协商必须在有限轮次内收敛（建议 ≤ 3 轮），否则升级到人类决策。

## 子合同分解

复杂任务可拆分为子合同，每个子合同独立委派给不同 Agent 或同一 Agent 的不同执行阶段：

```text
主合同 (Contractor A)
  ├── 子合同 1 → Subcontractor B（数据采集）
  ├── 子合同 2 → Subcontractor C（分析处理）
  └── 子合同 3 → Contractor A 自行完成（报告生成）
```

子合同的 scope 不得超出主合同的 scope；deliverables 的并集必须覆盖主合同的 deliverables。

## 与 TaskEnvelope 的映射

| Contract 字段 | TaskEnvelope 对应 | 说明 |
|---|---|---|
| task | `goal` + `constraints` | 目标和约束分离 |
| deliverables | `success_criteria` | 验收条件 |
| scope | `allowed_tools` + `policy_ref` | 权限边界 |
| cost | `budget` | 预算控制 |
| reporting | `trace_config` | 可观测性要求 |

## 适用场景

- 高 stakes 任务需要明确验收标准和责任边界
- 多 Agent 协作中需要清晰的委派和交付协议
- 企业环境中 Agent 行为需要可审计、可追责

相关文件：`contract-agent.md`、`worker-orchestration.md`、`../../paradigms/collaboration-paradigms.md`。
