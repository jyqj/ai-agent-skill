# Decision Frameworks

> **Evidence Status** — synthesized. Autonomy Level、Execution Depth、范式层、Context/Memory/State、Orchestration、Verification 等既有框架。


## 先问五个问题

```text
1. 交付物是什么？只是答案，还是外部效果？
2. 外部对象是什么？是否可刷新、可验证、可回滚？
3. 动作风险是什么？可逆性、影响范围、失败成本？
4. 需要多深？D0-D6 哪一级才算完成？
5. 用户信任到哪？L0-L5 哪一级可接受？
```

## 范式选择

| 场景 | 推荐范式 | 看哪里 |
|---|---|---|
| 单轮解释 | Direct | `../reasoning-paradigms.md` |
| 需要工具边做边看 | ReAct | `../reasoning-paradigms.md` |
| 多步骤可拆解任务 | Plan-and-Execute + ORDA-VU | `../reasoning-paradigms.md` |
| 长期偏好/项目约定 | Layered Memory | `../memory-paradigms.md` |
| 文档知识库问答 | RAG + Source Trust | `../memory-paradigms.md` |
| 外部工具生态 | MCP + Tool Registry | `../tool-paradigms.md` |
| 可并行子任务 | Coordinator-Worker | `../collaboration-paradigms.md` |
| 高风险动作 | Rule + Approval + Verification | `../control-paradigms.md` |

## 何时选择自治等级

| 选择 | 使用条件 | 不要使用在 |
|---|---|---|
| L0-L1 | 高风险、无验证、用户只要建议 | 需要快速批量执行 |
| L2 | 输出可编辑、用户愿意接管 | 用户期望自动闭环 |
| L3 | 动作清楚但风险需确认 | 低风险重复任务，会造成审批疲劳 |
| L4 | 有规则、有验证、有 checkpoint | 用户尚未建立信任、动作不可逆 |
| L5 | 有监控、eval、incident response、人工接管 | 缺持续观测和资源上限 |

## 何时选择执行深度

| 深度 | 适合 | 必备能力 |
|---|---|---|
| D0 | 解释、问答 | claim caution |
| D1 | 给步骤 | success criteria |
| D2 | 帮用户准备动作 | artifact / tool schema |
| D3 | 单步或短链执行 | execution result |
| D4 | 需要证明结果 | tests/readback/citation |
| D5 | 长任务、多阶段、可恢复 | checkpoint/world state/effect ledger |
| D6 | 持续流、监控、自治 | dataflow/incident/cost gate |

## 何时用 Subagent、Worker、Multi-window

| 机制 | 用在 | 不用在 |
|---|---|---|
| Subagent | 子任务需要独立上下文、角色或证据收集 | 只是普通函数调用 |
| Worker | 可并行、输出可合并、低共享状态 | 需要强一致共享状态 |
| Multi-window | 上下文隔离、长研究、阶段切换 | 需要实时一致状态 |
| Multi-agent Protocol | 3 个以上角色长期协作 | 简单顺序流程 |

## 何时信任 Memory vs 刷新 World State

```text
如果要写外部对象：刷新 World State。
如果只是偏好、习惯、历史约定：查 Memory。
如果 Memory 与 Observation 冲突：优先新鲜可信 Observation，并暴露冲突。
如果 Observation 低置信度：回查 raw ref 或请求用户确认。
```

## 何时中断用户

| 触发器 | 推荐交互 |
|---|---|
| 不可逆动作 | approval_request |
| 关键歧义 | clarification |
| 低置信度但高影响 | confirm_uncertainty |
| 长任务 milestone | progress_report |
| 用户纠错机会 | teaching_prompt |
| 超出预算 | budget_choice |
| 安全风险 | refusal_or_escalation |

相关文件：`minimum-viable-agent.md`、`../../architecture/reference-topologies.md`、`../../index/design-checklist.md`。
