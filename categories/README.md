# Agent Categories

> **Evidence Status** — synthesized. 品类索引，覆盖 14 个 Agent 品类。

## 品类层在主干中的位置

```text
concepts/       Agent 是什么
paradigms/      有哪些根本不同的做法
categories/     某类 Agent 的完整设计
architecture/   通用模块怎么设计
projects/       真实项目怎么实现
```

品类文档不应该只是"模块配方清单"。一个成熟的品类架构至少回答：

```text
1. 用户模型：谁用、信任如何建立、交互心智是什么
2. 任务模型：任务类型、成功定义、失败分类
3. 表示模型：这个品类的关键对象、freshness、trust
4. 行动模型：读/写/验证动作、前置/后置条件
5. 闭环模型：happy path、failure path、stop gate、verification
6. 设计决策：沙箱、并发、上下文、记忆、控制、运维
7. 评估用例：品类专属 eval cases 和指标
8. 实现映射：参考项目中每个模块怎么落地
```

## 当前成熟度

> **CC = Category Coverage**，衡量品类文档的完整程度（CC0-CC4）。与 `architecture/blueprint.md` 中的运行时成熟度 A0-A5 是不同维度。

| 品类 | 入口 | 成熟度 | 说明 |
|---|---|---|---|
| Coding Agent | `coding-agent/README.md` | CC4 | 完整样板 |
| Research Agent | `research-agent/README.md` | CC4 | 完整样板 |
| Enterprise Workflow Agent | `enterprise-workflow-agent/README.md` | CC3-CC4 | 已升级：任务/表示/行动/闭环/决策/eval/实现 |
| Browser/Desktop Agent | `browser-desktop-agent/README.md` | CC3-CC4 | 已升级：双通道验证/安全/benchmark 映射 |
| Ops/SRE Agent | `ops-sre-agent/README.md` | CC3 | 已升级：多 Agent 诊断/信号关联/缓解闭环 |
| Data/BI Agent | `data-bi-agent/README.md` | CC3 | 已升级：Text-to-SQL/语义层/SQL 安全 |
| Companion Agent | `companion-agent/README.md` | CC3 | 已升级：三层记忆/人格一致性/安全边界 |
| Security Agent | `security-agent/README.md` | CC3 | 已升级：自身安全/证据链/MITRE 映射 |
| Personal Memory Agent | `personal-memory-agent/README.md` | CC3 | 已升级：三层存储/矛盾检测/隐私控制 |
| Embodied Robot Agent | `embodied-robot-agent/README.md` | CC2-CC3 | 已升级：安全层级/LLM+控制分离/Sim-to-Real |
| Agent Platform | `agent-platform/README.md` | CC3 | 已升级：协议栈/多租户/版本管理 |
| Creative Agent | `creative-agent/README.md` | CC3 | 新增：风格一致性/创意评估/版权边界/多模态工作流 |
| Financial Agent | `financial-agent/README.md` | CC2 | 金融交易、风险管理和合规监控 |
| Education Agent | `education-agent/README.md` | CC2 | 个性化教学、练习、评估和学习路径规划 |

## 品类的默认范式组合

每个品类有推荐的范式起点，作为基于品类特征的合理默认值。运行时可按 `../paradigms/decision-trees.md` 动态调整。

范式名与 `../paradigms/` 中的定义一致。

| 品类 | 推理范式 | 记忆范式 | 工具范式 | 协作范式 | 控制范式 | 说明 |
|---|---|---|---|---|---|---|
| Coding Agent | ReAct + Plan-and-Execute | Layered (Project + Skill) + World State | Atomic (read/edit/search/shell) + Rich (git/test) | Single + Subagent (隔离上下文) | Rule/Permission Tree + Hook + Verification Gate | 代码修改需 read-after-write 验证；diff 是核心交付物 |
| Research Agent | Plan-and-Execute + Reflection | RAG + Episodic (Citation Chain) | Search + Extraction + Cite 工具 | Single / Subagent (多源并行) | Rule + LLM-as-Judge | 引用链完整性是核心约束；claim 必须绑定 evidence |
| Browser/Desktop Agent | ReAct | In-context + World State (PageState) | Rich Domain (GUI Action: click/type/navigate) | Single | Rule + Sandbox + Approval Gate | GUI 验证需双通道（DOM + 截图视觉）；Submit 类动作需确认 |
| Security Agent | ReAct + Reflection | World State (Threat KB + SIEM) + Graph (实体关联) | Atomic + Rich Domain (SIEM/EDR/MITRE) | Single / Coordinator-Worker (metrics/logs/topology 子 Agent) | Rule + Sandbox + Approval Gate | 高风险操作需人工审批；自身安全是额外攻击面 |
| Companion Agent | Reflection + Direct | Layered (Episodic + Persona Anchor) + Disclosure | Atomic (对话为主，工具为辅) | Single | Rule (Persona Boundary) + LLM-as-Judge | 人格一致性优先于任务完成度；安全边界不可被对话绕过 |
| Data/BI Agent | Plan-and-Execute | World State (Schema Snapshot) + In-context (Query History) | Code-as-Tool (SQL) + Rich Domain (Semantic Layer) | Single | Rule + Verification Gate | 数据准确性需 double-check；SQL 必须只读 + 超时控制 |
| Enterprise Workflow Agent | Plan-and-Execute + ORDA-VU | World State (WorkflowInstance/EntityRecord) + Layered (审计链) | Rich Domain + Workflow Tool | Event-driven + Human-in-the-loop | Rule + Approval Gate + Verification Gate | 审计留痕是硬性要求；异常必须升级 |
| Ops/SRE Agent | ReAct + Reflection | World State (Alert/Metrics/Traces) + Episodic (IncidentTimeline) | Rich Domain (监控/日志/拓扑) + Workflow (Runbook) | Coordinator-Worker (metrics/logs/topology/runbook 子 Agent) | Rule + Approval Gate + Canary | 诊断自主，缓解需确认；高风险变更需审批 |
| Financial Agent | Plan-and-Execute + ORDA-VU | World State (MarketData/Portfolio) + Layered (TradeRecord) | Rich Domain (OMS/EMS/风控) | Single + Human-in-the-loop | Rule + Approval Gate + Sandbox + Canary | 毫秒级延迟约束；单错误可致灾难性损失；合规是硬约束 |
| Personal Memory Agent | Direct + Reflection | Layered (Factual/Preference/Episodic/Procedural) + Disclosure | Atomic (存储/检索 API) | Single (可作为下游服务被调用) | Rule + Disclosure Policy | 记忆是 claim 不是 truth；用户可纠错/删除 |
| Embodied Robot Agent | Plan-and-Execute (高层) + ReAct (感知-动作) | World State (传感器) + In-context | Rich Domain (运动控制/感知) | Single / Coordinator-Worker (LLM + 控制器) | Rule (硬件安全边界) + Sandbox (Sim-to-Real) | 安全绝对优先；硬件边界不可被 LLM 覆盖；骨架级，待补充 |
| Agent Platform | — (平台层，不直接推理) | — (提供记忆基础设施) | MCP + Tool Registry | Event-driven + Blackboard | Rule + Sandbox + Canary | 平台为其他 Agent 提供基础设施；多租户隔离是核心；骨架级，待补充 |
| Creative Agent | Reflection + Tree/Graph Search | Layered (StyleGuide + ReferenceWork) + Episodic (版本历史) | Rich Domain (LLM/图像/视频生成模型) + Workflow (批量管线) | Single / Peer (多视角审查) | Rule (品牌/版权边界) + LLM-as-Judge (风格一致性) | 评估超越客观 postcondition；风格漂移是主要失败模式 |
| Education Agent | Reflection + Plan-and-Execute | Layered (学习者模型/知识状态) + Episodic (学习轨迹) | Rich Domain (题库/内容库) + Atomic | Single + Human-in-the-loop (教师监督) | Rule + Verification Gate (理解度检验) | 教错内容是最严重失败；难度适配需持续校准 |

**使用方式**：找到目标品类行 → 以该行范式组合为起点 → 根据具体任务的深度、风险和复杂度，用 `../paradigms/decision-trees.md` 微调。

## 品类模板

新建或升级品类时使用：

- `../meta/templates/category-architecture-template.md`
- `coding-agent/` 和 `research-agent/` 作为 CC4 样板
- 其他品类作为 CC3 样板

## 验证类型说明

不同品类的效果验证方式不同。工程型品类（Coding、Ops/SRE）主要使用客观 postcondition 验证；关系/创造型品类（Companion、Creative）需要扩展验证语义。详见：

- `../concepts/beyond-verification.md` — 超越验证：审美、情感、创造性任务
- `../evaluation/subjective-eval.md` — 主观性任务评估框架

## 旧单页入口

目录化品类文档是权威源：`categories/<type>/README.md` 负责完整设计；历史单页 `categories/<type>.md` 仅作兼容入口或摘要，不承载新的架构判断。


历史单页文件保留为兼容入口，指向对应目录。
