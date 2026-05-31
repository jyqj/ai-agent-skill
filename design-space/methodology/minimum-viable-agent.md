# Minimum Viable Agent Ladder

> **Evidence Status** — synthesized. 给轻量级 Agent 留出起步空间；同时给出何时升级复杂度的证据触发器。


## 核心原则

```text
先构建最小闭环，再根据真实失败补模块。
不要因为框架有 25 个 plane，就要求每个 Agent 从第一天全部实现。
```

## MVA 阶梯

| 阶段 | 能力 | 必备组件 | 适合 | 升级触发器 |
|---|---|---|---|---|
| MVA-0 Answer | 只回答/解释 | Prompt + basic context | 概念问答、总结 | 用户要求行动或证据 |
| MVA-1 Assisted Artifact | 生成可编辑草稿或计划 | Output contract + success criteria | 文案、代码片段、流程建议 | 用户反复复制执行 |
| MVA-2 Tool-assisted | 单步/短链工具调用 | Tool schema + observation | 查询、搜索、计算 | 工具结果影响下一步 |
| MVA-3 Verified Tool Agent | 执行并验证 | postcondition + readback/test | D4 任务、代码修改、业务写入 | 任务跨阶段或会中断 |
| MVA-4 Stateful Agent | 长任务、可恢复 | TaskState + checkpoint + world state | migration、研究、workflow | 需要跨会话/团队协作 |
| MVA-5 Production Agent | 可观测、可回归、可运维 | trace + eval + config fingerprint + incident | 企业/平台/高风险流程 | 进入持续运营 |
| MVA-6 Continuous Agent | 持续监控和自治 | dataflow + heartbeat + cost gate + rollback | Ops/SRE、agent platform | 需要组织级治理 |

## 每阶段最低验收标准

| 阶段 | 最低验收 |
|---|---|
| MVA-0 | 明确回答范围、声明不确定性、不假装已执行外部动作 |
| MVA-1 | 有交付物格式、有用户可检查的成功标准、不把草稿说成已完成 |
| MVA-2 | 工具有 schema、工具输出标准化为 observation、外部文本默认 data lane |
| MVA-3 | 写动作有 pre/postcondition，done 前有 read-after-write/test/外部确认 |
| MVA-4 | TaskState 可保存和恢复，WorldStateSnapshot 有 TTL 和 refresh 策略 |
| MVA-5 | 关键行为变化有 ConfigFingerprint，有 trace replay 或 fixture eval |

## 从失败补模块

| 观察到的失败 | 补哪个模块 |
|---|---|
| 输入被误解 | Representation |
| 上下文满后质量下降 | Context + Compaction |
| 记不住项目约定 | Project Memory |
| 工具结果被误读 | Standard Observation |
| 修改后没验证 | Effects + Verification Gate |
| 长任务中断 | State + Checkpoint |
| 外部状态过期 | World State |
| 用户觉得不可控 | Interaction + Control |
| 成本飙升 | Cost + Routing + Cache |
| 上线后退化 | Observability + Operations + Eval |

## 与生产级架构的关系

MVA 阶梯给出**何时增加复杂度的判据**：

```text
MVA-0/1 证明需求
MVA-2/3 证明工具闭环
MVA-4   证明长任务能力
MVA-5/6 证明组织级可靠性
```

相关文件：`../../architecture/reference-topologies.md`、`../../design-space/principles/core-design-principles.md`、`../../evaluation/eval-framework.md`。
