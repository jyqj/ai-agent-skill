# Autonomy and Execution Depth

> **Evidence Status** — synthesized. `concepts/autonomy-levels.md`、`architecture/controllers/execution-depth/overview.md`、Control/Interaction/Evaluation 模块。


## 自治等级 L0-L5

| 等级 | 名称 | Agent 行为 | 人类角色 | 适合 |
|---|---|---|---|---|
| L0 | Answer | 只解释、回答、总结 | 提问者 | 问答、概念解释 |
| L1 | Recommend | 给建议和可选方案 | 决策者 | 高风险前期分析 |
| L2 | Draft | 生成可编辑草稿 | 编辑者 | 文案、代码草稿、流程方案 |
| L3 | Execute with Approval | 提出动作，审批后执行 | 审批者 | 写文件、发消息、企业流程 |
| L4 | Bounded Autonomy | 在规则内自动执行 | 监督者 | 低风险批量任务、研究、代码局部修改 |
| L5 | Delegated Workflow | 长时自主推进，定期汇报 | 委托者 | 成熟平台、持续运营 |

自治等级取决于：

```text
动作风险 × 可逆性 × 用户信任 × 验证能力 × 失败成本 × 运维兜底
```

## 执行深度 D0-D6

| 深度 | 名称 | 完成定义 | 必备能力 |
|---|---|---|---|
| D0 | Answer | 给出解释或回答 | claim caution |
| D1 | Plan | 给出可执行计划 | success criteria |
| D2 | Assisted Action | 准备动作或草稿 | tool schema / artifact |
| D3 | Tool Execution | 执行单步或短链工具 | execution result |
| D4 | Verified Execution | 执行并验证结果 | test/readback/evidence |
| D5 | Stateful Workflow | 长任务、多阶段、可恢复 | checkpoint/world state/effect ledger |
| D6 | Continuous Operation | 持续流、监控、自治运营 | dataflow/incident/cost/ops gate |

执行深度取决于：

```text
Goal Persistence × Representation Quality × State Continuity × Tool Chain Reliability × Effect Verification × Recovery
```

## 二者的区别

| 维度 | 问题 | 示例 |
|---|---|---|
| Autonomy | Agent 能不能自己做？ | 是否允许自动提交 PR |
| Depth | Agent 要做到哪一步？ | 是否必须跑测试并修复失败 |

一个 Agent 可以是 **低自治高深度**：例如 D5 coding agent 需要完整修复和测试，但所有写动作前都 L3 审批。也可以是 **高自治低深度**：例如自动生成每日摘要，L4 执行但只到 D2。

## 默认组合建议

| 产品类型 | 默认 Autonomy | 默认 Depth | 说明 |
|---|---|---|---|
| Chatbot | L0-L1 | D0-D1 | 不产生外部效果 |
| Research Agent | L3-L4 | D3-D4 | 可自动检索，但结论需证据 |
| Coding Agent | L3-L4 | D4-D5 | 本地改动可 bounded autonomy，高风险需审批 |
| Enterprise Workflow | L2-L4 | D4-D5 | 权限和审计决定自治范围 |
| Browser/Desktop | L2-L3 | D4-D5 | 点击和购买等动作风险高 |
| Ops/SRE | L1-L3 | D5-D6 | 生产操作默认低自治高验证 |
| Agent Platform | L3-L5 | D5-D6 | 需要 operations、observability、incident response |

## 升级触发器

| 从 | 到 | 触发器 |
|---|---|---|
| L1 → L2 | 建议变草稿 | 用户反复要求“直接帮我写出来” |
| L2 → L3 | 草稿变执行 | 工具链稳定且动作可回滚 |
| L3 → L4 | 审批变监督 | 低风险、验证稳定、用户信任提升 |
| D2 → D3 | 草稿变执行 | 有 typed tool 和执行宿主 |
| D3 → D4 | 执行变验证 | 有 postcondition 和 readback/test |
| D4 → D5 | 验证变长流程 | 需要 checkpoint、world state、恢复循环 |
| D5 → D6 | 长流程变持续运营 | 有事件流、运维、回归和事故响应 |

相关文件：`../../architecture/controllers/execution-depth/overview.md`、`../../architecture/planes/interaction/trust-escalation.md`、`../../architecture/planes/control/overview.md`。
