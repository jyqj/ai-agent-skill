# 成熟度阶梯对照表

> **Evidence Status** — synthesized. 本知识库中 4 套阶梯体系的交叉引用分析；实际项目中阶梯选择的困惑反馈。

知识库有 4 套阶梯，各自从不同角度刻画 Agent 成熟度。下文厘清它们的关系，帮助在正确场景选择正确阶梯。

---

## 四套阶梯概览

| 阶梯 | 维度 | 核心问题 | 来源文件 |
|---|---|---|---|
| C0-C6 复杂度等级 | 架构复杂度 | 需要启用哪些 plane？ | `architecture/complexity-levels.md` |
| D0-D6 执行深度 | 任务执行深度 | Agent 执行到多深？ | `architecture/controllers/execution-depth/overview.md` |
| MVA-0 到 MVA-6 | 构建起点 | 从哪里开始构建？ | `starter-kit/` |
| Autonomy Level L0-L5 | 自主权 | Agent 有多大的决策自由？ | `concepts/autonomy-levels.md` |

## 对照表

以下将 4 套阶梯按成熟度等级放在一起对照。注意：对照是近似的——每套阶梯的维度不同，边界不完全重合。

| 等级 | C (复杂度) | D (执行深度) | MVA (构建起点) | L (自主权) | 典型 Agent 形态 |
|---|---|---|---|---|---|
| 起步 | C0: 单 prompt | D0: 纯对话 | MVA-0: 裸模型 | L0: 人做所有决策 | ChatGPT wrapper |
| 基础 | C1: + 工具调用 | D1: 单步工具 | MVA-1: + 1 个工具 | L1: Agent 建议，人执行 | 简单 QA Bot |
| 可用 | C2: + 多步规划 | D2: 多步编排 | MVA-2: + 规划 + 多工具 | L2: Agent 执行，人审批 | Copilot 类产品 |
| 稳健 | C3: + memory + context | D3: + 验证 + 重试 | MVA-3: + memory + eval | L3: Agent 自主，人监督 | 自动化工作流 |
| 成熟 | C4: + 多模型 + 安全 | D4: + 效果验证 + 回滚 | MVA-4: + 多模型 + ops | L4: Agent 自主，异常上报 | 生产级 Agent |
| 高级 | C5: + 学习 + 演化 | D5: + 端到端验证 | MVA-5: + 学习循环 | L4.5: 高度自主 | 自适应 Agent |
| 前沿 | C6: 全 plane | D6: + 跨系统协调 | MVA-6: 完整架构 | L5: 完全自主 | 多 Agent 系统 |

## 阶梯的用途区别

### C 阶梯：架构决策

**核心问题**：需要启用哪些 plane？

C0 只需要 LLM 调用，C3 需要 Memory Plane + Context Plane，C6 需要全部 plane。用于架构评审时判断是否真的需要引入新 plane，避免过度工程化。例如 Claude Code 的工具权限系统对应 C3-C4——需要 Context Plane 管理权限状态，但不需要 C5 的学习循环。

**典型问题**："我们需要 Memory Plane 吗？" —— 如果你的 Agent 是 C2 以下，大概率不需要。

### D 阶梯：任务分析

**核心问题**：这个任务需要执行到什么深度？

D1 是"调一个 API 就完事"，D4 是"调 API + read-after-write + 失败重试 + 效果验证"。用于逐任务评估执行深度，避免所有任务都用最高深度（浪费资源）或最低深度（质量不够）。例如 SWE-bench 上的 Coding Agent 通常需要 D4-D5——修改代码后必须运行测试验证，失败后还要重试。

**典型问题**："更新 CRM 需要 D 几？" —— 至少 D4（需要效果验证），如果涉及多系统协调则 D5+。

### MVA 阶梯：项目启动

**核心问题**：从哪个最小可行版本开始构建？

从 MVA-0（裸模型验证需求）开始，逐步增加能力，每一级都是一个可交付的里程碑。避免一开始就瞄准 MVA-6 导致永远交付不了，也避免在 MVA-1 时就引入 MVA-4 才需要的组件。例如大多数内部工具类 Agent 从 MVA-2 起步就够用——一个模型 + 规划 + 几个工具。

**典型问题**："第一个版本应该做到什么程度？" —— 找到你的 MVA 级别，那就是第一个版本。

### Autonomy Level：产品定位

**核心问题**：人和 Agent 怎么分工？

L1 是"Agent 给建议，人来做"，L3 是"Agent 自己做，人来看"。直接影响 UI 设计、审批流程和信任建设策略。例如 GitHub Copilot 是 L1-L2（建议代码，人决定是否采纳），而 Devin 瞄准 L3-L4（自主完成任务，人监督结果）。

**典型问题**："用户需要审批每个操作吗？" —— 取决于 Autonomy Level。L2 需要，L4 不需要（但需要告知）。

## 典型组合示例

| 场景 | C | D | MVA | L | 要点 |
|------|---|---|-----|---|------|
| 企业工单处理 Agent | C3 | D4 | MVA-2 | L2 | 架构能力（C3）可以超前于构建进度（MVA-2）；执行深度和自主权由业务场景决定 |
| FAQ Bot | C1 | D1 | MVA-1 | L1 | 最简组合：一个模型 + 一个检索工具，单步查询，用户自行判断 |
| 生产级代码审查 Agent | C5 | D5 | MVA-4 | L4 | 需要学习代码风格（C5）、端到端验证审查效果（D5）、自主执行只在高风险时上报（L4） |

## 何时使用哪套阶梯——速查表

| 你在做什么 | 用哪套阶梯 | 关键产出 |
|---|---|---|
| 架构设计评审 | C 阶梯 | Plane 启用决策 |
| 任务需求分析 | D 阶梯 | 执行策略选择 |
| 项目规划 / 迭代计划 | MVA 阶梯 | 里程碑定义 |
| 产品定位 / UX 设计 | Autonomy Level | 人机分工方案 |
| 综合评估现有 Agent | 全部 | 四维成熟度画像 |

---

## 延伸阅读

- `architecture/complexity-levels.md` — C0-C6 复杂度等级详细定义
- `architecture/controllers/execution-depth/overview.md` — D0-D6 执行深度详细定义
- `concepts/autonomy-levels.md` — Autonomy Level 详细定义
- `starter-kit/` — MVA 阶梯的构建指南
- `index/design-checklist.md` — 设计检查清单（使用各阶梯的实操入口）
