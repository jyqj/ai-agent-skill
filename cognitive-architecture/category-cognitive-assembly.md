> **已迁移**：本文件已迁移至 `../categories/category-cognitive-assembly.md`。以下内容保留为存档，权威版本请查阅迁移目标。

# 品类认知组装指南

> **Evidence Status** — synthesized. 基于 `category-cognitive-profiles.md` 的品类认知热力图；SoK Agentic Skills (arXiv 2602.20867) 提供了 Skill 形式化定义和 SkillsBench 数据；Nurture-First (arXiv 2603.10808) 提供了三层认知架构的设计思路。本文为针对各品类的认知模块组装推导。

## 1. 为什么需要这篇

`category-cognitive-profiles.md` 提供了品类 x 认知维度的热力图（H/M/L），告诉你"Coding Agent 的工作记忆需求是 H"。但 H 意味着什么？具体应该组装哪些认知模块、如何配置双过程分配、监控什么元认知指标？

本文为每个主要品类提供可操作的认知组装方案——从热力图到工程蓝图。

## 2. Skill 形式化定义

在讨论品类组装前，先明确 skill 的形式化定义（SoK Agentic Skills, arXiv 2602.20867）：

```text
Skill = (C, π, T, R)

C — 适用条件（Applicability Conditions）
    何时触发此 skill？需要什么前置状态？
π — 可执行策略（Executable Policy）
    具体的行动序列或决策逻辑
T — 终止条件（Termination Conditions）
    何时认为 skill 执行完成？成功/失败判据
R — 可复用接口（Reusable Interface）
    如何被其他 skill 或上层控制调用？输入/输出合约
```

**SkillsBench 关键发现**：经过人工筛选的 curated skills 使 Agent 通过率提升 16.2 个百分点。更重要的是，**小模型 + curated skills > 大模型 + 无 skills**——这意味着 skill 质量可以部分补偿模型能力的不足。

## 3. 三层认知架构：按波动性分层

来自 Nurture-First (arXiv 2603.10808) 的设计原则——认知资产按变化频率分为三层：

| 层 | 波动性 | 内容 | 修改频率 | 审批要求 |
|---|---|---|---|---|
| Constitutional | 低 | 身份、价值观、安全约束、核心行为准则 | 极少修改 | 需人工审批 |
| Skill | 中 | 领域技能、工具使用模式、任务解决策略 | 随经验积累逐步更新 | 需评估通过 |
| Experiential | 高 | 操作记忆、会话上下文、临时状态 | 持续变化 | 自动管理 |

**设计原则**：高波动层不应修改低波动层。Experiential 层的经验积累到一定程度后，经过评估可以"沉淀"到 Skill 层；但 Skill 层不应自行修改 Constitutional 层。

```text
Constitutional ──────────────── 稳定锚点，极少改变
     │
     ▼ 约束
Skill ───────────────────────── 领域能力，渐进积累
     │
     ▼ 约束
Experiential ────────────────── 运行时记忆，持续流转
     │
     ▲ 沉淀（需评估）
```

## 4. 品类认知组装方案

### 4.1 Coding Agent

**认知重心**：工作记忆（H）、目标层级（H）、推理模式（H: 演绎/溯因）、注意力（H）、元认知（H）。

| 认知模块 | 需求 | 工程实现要点 |
|---|---|---|
| 工作记忆 | H | 大上下文窗口 + 积极 compaction；代码文件作为组块单位；scratchpad 外化中间状态 |
| 目标层级 | H | 需求 → 方案 → 文件级修改 → 验证；goal stack 支持 3-4 层嵌套 |
| 推理模式 | H | 演绎（规则应用）+ 溯因（Debug 核心）；prompt 需支持多假设追踪 |
| 注意力 | H | search → symbol → targeted read 策略；避免全量读取 |
| 元认知 | H | 修改前预判影响范围；测试失败时反思而非盲目重试 |

**推荐认知组装模式**：

```text
Plan-Verify-Execute-Verify 循环
  1. Plan: 分析需求 → 分解为文件级修改计划
  2. Verify-Plan: 计划是否覆盖所有需求？是否有遗漏？
  3. Execute: 逐步实施修改
  4. Verify-Exec: 运行测试 + diff 审查
  5. 失败 → Reflection → 回到 Plan 或 Execute
```

**双过程配置**：

| 决策类型 | System 1 (自动) | System 2 (审慎) |
|---|---|---|
| 文件搜索策略 | 已知项目结构时直接定位 | 新项目首次探索 |
| 工具选择 | 常见操作（read/grep/edit） | 复杂 bash 命令、外部 API |
| 代码修改 | 格式调整、import 添加 | 逻辑变更、架构改动 |
| 测试判断 | 明确的 pass/fail | 测试覆盖率是否足够 |

**元认知监控维度**：
- 修改范围是否在计划内？（scope creep 检测）
- 测试是否覆盖了关键路径？（验证充分性）
- 连续修改-测试失败次数？（impasse 检测 → 阈值 3 次）
- 当前对代码库的理解置信度？（低置信 → 扩大搜索范围）

**Skill 习得策略**：
- C: 项目类型 + 语言 + 框架版本匹配
- π: 项目约定（命名、目录结构、测试规范）→ 编译为 project instruction
- T: 测试通过 + lint 通过 + diff 范围合理
- R: 可被 sub-agent 调用的修改-验证原语

### 4.2 Research Agent

**认知重心**：工作记忆（H）、推理模式（H: 归纳/溯因）、注意力（H）、元认知（H）。

| 认知模块 | 需求 | 工程实现要点 |
|---|---|---|
| 工作记忆 | H | 多源信息并行追踪；引用链管理；中间结论需持久化到 scratchpad |
| 推理模式 | H | 归纳（从多个来源提取模式）+ 溯因（寻找最佳解释）；证据质量分级 |
| 注意力 | H | 海量检索结果中筛选相关信息；避免被高曝光但低质量来源误导 |
| 元认知 | H | 评估结论可靠性；识别证据不足的区域；知道何时"够了" |

**推荐认知组装模式**：

```text
Hypothesize-Gather-Synthesize-Evaluate 循环
  1. Hypothesize: 形成初始假设或研究问题分解
  2. Gather: 多源信息收集（搜索、阅读、API）
  3. Synthesize: 归纳整合，更新信念
  4. Evaluate: 证据是否充分？结论是否可靠？
  5. 不足 → 回到 Gather 补充；充分 → 输出报告
```

**双过程配置**：

| 决策类型 | System 1 | System 2 |
|---|---|---|
| 搜索关键词选择 | 常见领域术语 | 跨学科搜索策略 |
| 来源可信度判断 | 已知权威来源 | 新来源的可信度评估 |
| 信息相关性筛选 | 明显相关/不相关 | 边界情况的相关性判断 |
| 结论形成 | — | 所有结论都应经过 System 2 |

**元认知监控维度**：
- 证据覆盖了多少个独立来源？（≥3 为基线）
- 是否存在相互矛盾的证据？（矛盾 → 深入分析）
- 当前结论与初始假设的偏离程度？（防止 confirmation bias）
- 信息饱和度？（新来源不再提供新信息 → 可以停止收集）

### 4.3 Browser/Desktop Agent

**认知重心**：工作记忆（H）、注意力（H: 视觉）、心智理论（M）、元认知（M）。

| 认知模块 | 需求 | 工程实现要点 |
|---|---|---|
| 工作记忆 | H | 页面状态 + 操作历史 + 目标追踪；截图的 token 成本需管理 |
| 注意力（视觉） | H | GUI 元素识别和定位；视觉信息 → 结构化文字描述的转换 |
| 心智理论 | M | 理解用户的操作意图；推理网站的交互逻辑 |
| 元认知 | M | 操作成功/失败的判断；页面是否加载完成 |

**推荐认知组装模式**：

```text
Observe-Orient-Act-Confirm 循环
  1. Observe: 截图/DOM → 结构化状态描述
  2. Orient: 当前状态与目标的距离评估
  3. Act: 选择并执行操作（点击/输入/滚动）
  4. Confirm: 验证操作效果（页面变化是否符合预期）
  5. 失败 → 重试或调整策略
```

**双过程配置**：

| 决策类型 | System 1 | System 2 |
|---|---|---|
| 元素定位 | 明确的 selector/label | 模糊匹配、视觉推理 |
| 操作选择 | 标准交互（click, type） | 复杂交互（drag, multi-step） |
| 等待策略 | 固定超时 | 动态判断页面是否就绪 |
| 导航决策 | 线性流程中的下一步 | 多路径选择、弹窗处理 |

### 4.4 Companion Agent

**认知重心**：工作记忆（H）、心智理论（H）、情绪/动机（H）、元认知（M）、创意认知（M）。

| 认知模块 | 需求 | 工程实现要点 |
|---|---|---|
| 工作记忆 | H | 对话历史中的关系线索；用户偏好和情绪状态追踪 |
| 心智理论 | H | 用户情绪识别；意图推理；知识水平估计 |
| 情绪/动机 | H | 情感响应策略；共情表达；边界维护 |
| 元认知 | M | 回应是否恰当？是否越界？何时该沉默？ |
| 创意认知 | M | 对话中的趣味性和新鲜感 |

**推荐认知组装模式**：

```text
Perceive-Understand-Respond 循环
  1. Perceive: 用户输入 + 情绪信号 + 对话上下文
  2. Understand: 意图推理 + 情绪状态更新 + 关系阶段评估
  3. Respond: 选择响应策略（支持/建议/陪伴/幽默）
  4. 元监控: 回应是否符合用户当前需要？
```

**双过程配置**：

| 决策类型 | System 1 | System 2 |
|---|---|---|
| 情绪识别 | 明确的情绪表达 | 隐含情绪、混合情绪 |
| 响应风格 | 日常问候、简单回应 | 敏感话题、情绪危机 |
| 关系边界 | 标准交互模式 | 越界请求、依赖风险 |

### 4.5 Ops/SRE Agent

**认知重心**：工作记忆（H）、目标层级（H）、推理模式（H: 溯因/因果）、注意力（H）。

| 认知模块 | 需求 | 工程实现要点 |
|---|---|---|
| 工作记忆 | H | 多系统状态并行追踪；告警时间线；历史事件关联 |
| 目标层级 | H | 恢复 > 定位 > 预防；多层目标并行管理 |
| 推理模式 | H | 溯因（从告警回溯根因）+ 因果（追踪故障传播链） |
| 注意力 | H | 多源告警中的优先级排序；噪声过滤 |

**推荐认知组装模式**：

```text
Triage-Hypothesize-Investigate-Mitigate 循环
  1. Triage: 告警优先级评估 + 影响范围估计
  2. Hypothesize: 列出可能根因（≥3 个候选）
  3. Investigate: 日志/指标/拓扑检查 → 排除/确认假设
  4. Mitigate: 执行恢复操作 + 验证恢复效果
  5. Postmortem: 记录根因和预防措施
```

**双过程配置**：

| 决策类型 | System 1 | System 2 |
|---|---|---|
| 告警优先级 | 已知告警模式的严重性 | 新类型告警的评估 |
| 恢复操作 | 标准 runbook 操作 | 非标准故障的恢复策略 |
| 根因分析 | — | 所有根因分析都应经过 System 2 |
| 变更风险 | 已知安全操作 | 首次执行的恢复操作 |

### 4.6 Creative Agent

**认知重心**：创意认知（H）、元认知（H）、推理模式（M: 类比）、情绪/动机（M）。

| 认知模块 | 需求 | 工程实现要点 |
|---|---|---|
| 创意认知 | H | 跨域类比检索；约束放松机制；多样性采样（temperature 调整） |
| 元认知 | H | "这个方案有趣吗？"——主观质量评估；风格一致性检查 |
| 推理模式 | M | 类比推理为主（跨域迁移和组合） |
| 情绪/动机 | M | 创作的内在驱动力；风格的情感色彩 |

**推荐认知组装模式**：

```text
Diverge-Explore-Converge-Refine 循环
  1. Diverge: 生成多个候选方案（宽松约束、高多样性）
  2. Explore: 对候选方案进行初步发展
  3. Converge: 基于质量标准筛选 top 方案
  4. Refine: 精细化打磨选定方案
  5. 评估: 风格一致性 + 创新性 + 可用性
```

**双过程配置**：

| 决策类型 | System 1 | System 2 |
|---|---|---|
| 灵感联想 | 直觉性联想、模式迁移 | — (System 1 为主) |
| 质量评估 | — | 所有质量判断都应经过 System 2 |
| 风格保持 | 已建立的风格模板 | 风格适配新场景 |
| 约束处理 | 标准格式要求 | 创意约束与自由度的平衡 |

## 5. 跨品类共性

尽管品类差异显著，以下认知组装原则具有通用性：

| 原则 | 说明 | 来源 |
|---|---|---|
| 元认知必须存在 | 即使需求是 M，也不能完全没有元认知——所有品类都需要某种形式的自我监控 | 热力图中没有 L 的元认知 |
| 工作记忆是瓶颈 | 所有 H 工作记忆品类都需要显式的 compaction 和外化策略 | working-memory-dynamics.md |
| Skill 质量 > 模型大小 | 16.2pp 的提升来自 skill 质量，不是模型参数 | SkillsBench |
| 三层分离 | Constitutional / Skill / Experiential 的分层适用于所有品类 | Nurture-First |
| System 2 是默认 | LLM Agent 的所有行为默认都是 System 2；System 1 需要通过 skill 固化来实现 | cognitive-to-paradigm-routing.md |

## 6. 从热力图到组装清单

使用本文的步骤：

```text
1. 确定品类 → 查 §4 对应小节
2. 识别 H 维度 → 这些是必须投入的认知模块
3. 选择组装模式 → 品类推荐的循环结构
4. 配置双过程 → 哪些决策走 System 1，哪些走 System 2
5. 设置元认知监控 → 监控哪些指标，阈值是多少
6. 规划 Skill 习得 → 用 (C, π, T, R) 形式化描述 skill 候选
7. 落实三层架构 → Constitutional / Skill / Experiential 各放什么
```

## 7. 延伸阅读

- `category-cognitive-profiles.md` — 品类认知需求热力图（本文的输入）
- `cognitive-to-paradigm-routing.md` — 认知需求如何驱动范式选择
- `cognitive-to-plane-mapping.md` — 认知模块到架构 Plane 的反向索引
- `skill-acquisition.md` — Dreyfus 阶段与 skill 生命周期
- `metacognitive-control.md` — 元认知监控的详细设计
- `../categories/coding-agent/design-decisions.md` — Coding Agent 工程决策
- `../categories/companion-agent/` — Companion Agent 品类详情
- `../categories/ops-sre-agent/design-decisions.md` — Ops/SRE Agent 工程决策
- `../categories/creative-agent/design-decisions.md` — Creative Agent 工程决策
- SoK Agentic Skills (arXiv 2602.20867) — Skill 形式化与 SkillsBench
- Nurture-First (arXiv 2603.10808) — 三层认知架构
