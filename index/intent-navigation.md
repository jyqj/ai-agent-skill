# 按意图导航（完整版）

> **Evidence Status** — synthesized. 知识库全量文件的意图分类与入口映射；基于用户导航反馈持续迭代。

> 从 SKILL.md 迁出的完整意图导航表。按"想做什么"直接给出入口。

## 理解与学习

| 想做什么 | 入口 |
|---|---|
| 理解整体架构 | `ARCHITECTURE.md` → `architecture/blueprint.md` → `architecture/lifecycle.md` |
| 理解 Agent 基本概念 | `concepts/README.md` → `concepts/what-is-agent.md` → `concepts/representation-and-effects.md` |
| 理解哲学基础（为什么 Agent 必须这样设计） | `concepts/foundations/README.md` |
| 理解认知架构（Agent 的认知如何组织） | `cognitive-architecture/README.md` |
| 判断需要启用多少架构复杂度 | `architecture/complexity-levels.md` → `architecture/reference-topologies.md` |
| 对照 4 套成熟度阶梯 | `index/maturity-ladders.md` |
| 查看模块依赖和数据流 | `architecture/plane-interaction-matrix.md` → `architecture/runtime-data-flow.md` |
| 查术语 | `concepts/glossary.md` |

## 范式选择

| 想做什么 | 入口 |
|---|---|
| 选择 Agent 构建范式 | `paradigms/README.md` → `paradigms/reasoning-paradigms.md` |
| 理解运行时范式切换 | `paradigms/paradigm-routing.md` |
| 选择记忆/RAG/Disclosure/图记忆 | `paradigms/memory-paradigms.md` → `architecture/planes/memory/overview.md` |
| 选择工具集、MCP、code-as-tool | `paradigms/tool-paradigms.md` → `architecture/planes/tools/overview.md` |
| 选择单 Agent / Subagent / Worker / 多 Agent | `paradigms/collaboration-paradigms.md` → `architecture/planes/orchestration/overview.md` |
| 选择 rule / judge / hook / sandbox / approval | `paradigms/control-paradigms.md` → `architecture/planes/control/overview.md` |
| 判断 Agent 该怎么设计 | `paradigms/methodology/agent-product-model.md` → `paradigms/methodology/decision-frameworks.md` |
| 评估 Agent 经济学与 ROI | `paradigms/methodology/agent-economics.md` |
| 从最小闭环开始 | `paradigms/methodology/minimum-viable-agent.md` → `architecture/reference-topologies.md` |

## 品类设计

| 想做什么 | 入口 |
|---|---|
| 从零设计某类 Agent | `categories/README.md` → `categories/<type>/README.md` |
| 设计 Coding Agent | `categories/coding-agent/README.md` → `categories/coding-agent/implementation-map.md` |
| 设计 Research Agent | `categories/research-agent/README.md` → `categories/research-agent/implementation-map.md` |
| 设计 Enterprise Workflow Agent | `categories/enterprise-workflow-agent/README.md` |
| 设计 Browser/Desktop Agent | `categories/browser-desktop-agent/README.md` |
| 设计 Ops/SRE Agent | `categories/ops-sre-agent/README.md` |
| 设计 Data/BI Agent | `categories/data-bi-agent/README.md` |
| 设计 Security Agent | `categories/security-agent/README.md` |
| 设计 Companion Agent | `categories/companion-agent/README.md` |
| 设计 Personal Memory Agent | `categories/personal-memory-agent/README.md` |
| 设计 Embodied Robot Agent | `categories/embodied-robot-agent/README.md` |
| 设计 Agent Platform | `categories/agent-platform/README.md` |

## 模块深入设计

| 想做什么 | 入口 |
|---|---|
| 建模输入如何进入系统 | `architecture/planes/interface/overview.md` → `architecture/planes/representation/overview.md` |
| 设计 Prompt 与 Harness | `architecture/planes/prompting/overview.md` → `paradigms/methodology/harness-engineering.md` |
| 设计外部世界状态与效果闭环 | `architecture/planes/world-state/overview.md` → `architecture/planes/effects/overview.md` |
| 理解因果世界模型 | `architecture/planes/world-state/causal-model.md` → `architecture/multi-model/world-models.md` |
| 设计 Human-Agent 交互 | `architecture/planes/interaction/overview.md` |
| 设计意图对齐与认知负载管理 | `architecture/planes/interaction/intent-alignment.md` |
| 设计可解释性 | `architecture/planes/explainability/overview.md` |
| 设计成本与资源策略 | `architecture/planes/cost/overview.md` |
| 设计租户经济学、SLO/SLA 与配额 | `architecture/planes/economics/overview.md` |
| 设计时间约束与有效期管理 | `architecture/planes/time/overview.md` |
| 设计多 Agent 协作 | `paradigms/collaboration-paradigms.md` → `architecture/planes/orchestration/communication.md` |
| 设计并发、取消、流式任务 | `architecture/planes/concurrency/overview.md` → `architecture/planes/dataflow/overview.md` |
| 设计安全边界 | `architecture/planes/security/overview.md` |
| 设计身份、租户和能力授权 | `architecture/planes/identity-capability/overview.md` |
| 设计错误恢复、补偿和部分交付 | `architecture/planes/recovery/overview.md` |
| 设计上线、回归与事故响应 | `architecture/planes/operations/overview.md` |
| 设计从经验中学习和失效治理 | `architecture/planes/learning-adaptation/overview.md` → `architecture/learning/overview.md` |
| 设计多模型/异构 Agent 架构 | `architecture/multi-model/README.md` |
| 设计长期演化与退役 | `architecture/evolution/README.md` |

## 设计空间与参考

| 想做什么 | 入口 |
|---|---|
| 查找设计模式 | `design-space/patterns/` → `index/category-pattern-matrix.md` |
| 查找反模式 | `design-space/anti-patterns/` |
| 看已知失败的设计教训 | `design-space/lessons-learned/` |
| 看真实项目怎么做 | `projects/` 下按品类选项目 |
| 跨项目对比分析 | `synthesis/` |
| 对照根目录真实项目反思架构 | `synthesis/local-reference-systems-reflection.md` → `index/project-module-map.md` |
| 对照主流框架 | `synthesis/framework-comparison.md` |
| 看前沿协议 / agentic RAG / computer use | `design-space/frontier/README.md` |
| 从参考代码骨架开始 | `starter-kit/verified-tool-agent/README.md` |
| 从有状态骨架开始 | `starter-kit/stateful-agent/README.md` |

## 评估与运维

| 想做什么 | 入口 |
|---|---|
| 评估和验收 | `evaluation/eval-framework.md` → `evaluation/eval-runner/README.md` |
| 评估主观性任务（审美/情感/创造） | `evaluation/subjective-eval.md` |
| 评估体系的元评估 | `evaluation/eval-meta/README.md` |
| 做设计评审 | `index/design-checklist.md` |
| 理解超越验证的任务类型 | `concepts/beyond-verification.md` |

## 实践与反馈

| 想做什么 | 入口 |
|---|---|
| 跟着做一个完整 Agent | `guides/build-research-agent.md` |
| 提交知识库反馈 | `meta/feedback/feedback-template.md` |
| 了解 Evidence Status 升降级标准 | `meta/feedback/evidence-upgrade-criteria.md` |

## 治理与信任

| 想做什么 | 入口 |
|---|---|
| 设计多 Agent 治理 | `architecture/planes/orchestration/governance.md` |
| 理解 Agent 间信任 | `architecture/planes/orchestration/trust-and-attribution.md` |

## 认知架构（补充）

| 想做什么 | 入口 |
|---|---|
| 了解 Agent 注意力和显著性 | `cognitive-architecture/attention-and-salience.md` |
| 了解技能习得路径 | `cognitive-architecture/skill-acquisition.md` |

## 元信息

| 想做什么 | 入口 |
|---|---|
| 了解这个 skill 怎么用、怎么添加新内容 | `meta/guide.md` |
