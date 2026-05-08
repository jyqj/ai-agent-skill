# Categories x Multi-Model 交叉设计

> **Evidence Status** — synthesized.
> 知识库映射: L3 品类 x L4 运行时 (Multi-Model) x Coordination (Plane 16)

## 为什么需要这篇文档

Agent 品类（Coding / Research / Browser / Companion / Financial 等）定义了"Agent 要做什么"，多模型架构定义了"用什么模型做"。在实际生产系统中，这两个维度必须联合设计：不同品类的任务特征决定了多模型架构中每个角色应选用何种能力级别的模型。

关键数据支撑：
- Planner-Executor 分离可减少推理成本达 **45%**，但前提是正确匹配品类需求与模型角色
- 三层推理层级（Fast → Standard → Extended Reasoning）的路由粒度取决于品类的任务复杂度分布
- Claude Code、Cursor、Devin 等生产系统均采用"单核心 Agent + 模块化子 Agent"模式，但各品类的子 Agent 组合截然不同

忽视品类与模型角色的匹配，会导致两种典型失败：用推理模型处理简单执行任务（浪费成本）或用轻量模型处理复杂规划任务（质量崩溃）。

---

## 交叉点识别

| 交叉点 | Categories 侧关注 | Multi-Model 侧关注 | 冲突/张力 | 设计要求 |
|--------|------------------|-------------------|----------|---------|
| 规划复杂度 | 各品类任务分解的难度差异大 | Planner 模型选择 | 统一 vs 专用 Planner | 品类感知的规划模型配置 |
| 执行精度 | 编码需精确、研究需广度、对话需自然 | Executor 模型选择 | 精度 vs 效率 vs 风格 | 品类特化的 Executor 配置 |
| 验证方式 | 编码可自动测试、研究需事实核查、对话需主观评估 | Verifier 模型/方法选择 | 确定性验证 vs 主观判断 | 品类匹配的验证链 |
| 工具生态 | 各品类依赖的工具集完全不同 | 工具调用模型需求 | 工具专精 vs 通用 | 品类工具-模型绑定 |
| 上下文窗口 | 研究需长上下文、编码需代码库、对话需历史 | 上下文管理策略 | 窗口大小 vs 成本 | 品类驱动的上下文策略 |
| 安全边界 | 金融需严格审批、编码需沙箱、浏览需隔离 | 安全模型配置 | 安全级别 vs 自主度 | 品类安全矩阵 |

---

## 品类 x 模型角色矩阵

### 核心模型角色定义

| 模型角色 | 职责 | 能力要求 | 典型模型 |
|---------|------|---------|---------|
| **Planner** | 任务分解、依赖识别、DAG 生成 | 强推理、长程规划 | Opus/o3-pro（含 Extended Thinking） |
| **Executor** | 工具调用执行、代码生成、内容产出 | 工具使用、领域知识 | Sonnet/GPT-4o/Gemini Pro |
| **Router** | 复杂度评估、模型/范式选择 | 快速分类 | Haiku/Flash/o4-mini |
| **Verifier** | 结果验证、质量检查、合规审查 | 批判性推理 | Opus（含 Think Tool）/ 代码工具 |
| **Summarizer** | 上下文压缩、摘要生成 | 信息保留、压缩能力 | Sonnet/Haiku |
| **Retriever** | 知识检索、RAG 查询构建 | 语义理解、查询优化 | Embedding 模型 + Haiku |

### 四大品类的多模型配置

#### 1. Coding Agent（编码 Agent）

| 模型角色 | 配置 | 理由 |
|---------|------|------|
| Planner | Opus + Extended Thinking | 代码架构决策需要深度推理；SWE-bench 最佳 87.6% |
| Executor (Code Gen) | Sonnet | 代码生成质量与成本的最佳平衡 |
| Executor (Simple Edit) | Haiku | 简单重构/格式化不需要高端模型 |
| Verifier | 代码工具（测试/lint）+ Opus Think Tool | 优先确定性验证；主观质量用 Think Tool |
| Router | Haiku | 任务复杂度分类（新功能 vs 改 bug vs 重构） |
| Summarizer | Sonnet | 代码上下文压缩需保留架构决策 |

**品类特有模式**:
- 自测循环: Executor 生成 → 测试运行 → Verifier 分析失败 → Executor 修复
- 成本控制: SWE-bench 级任务用 Opus；日常编辑用 Haiku；平均成本 $0.72/PR
- 沙箱执行: 代码在隔离沙箱中运行，冷启动 <90ms（Daytona 级别）

#### 2. Research Agent（研究 Agent）

| 模型角色 | 配置 | 理由 |
|---------|------|------|
| Planner | Opus + Extended Thinking | 研究方向规划需要多跳推理 |
| Executor (Search) | Sonnet + 搜索工具 | 查询构建需要语义理解 |
| Executor (Synthesis) | Opus | 多源信息综合需要高推理能力 |
| Verifier | 多 Agent 辩论（Sonnet x3） | 事实性验证需要多视角交叉检查 |
| Router | Haiku | 简单查找 vs 深度研究 vs 多跳推理分流 |
| Summarizer | Sonnet | 研究摘要需保留来源归因 |

**品类特有模式**:
- 深度-广度平衡: BATS 框架在 BrowseComp 上 24.6%（标准 ReAct 仅 12.6%）
- 并行采集: Budget-Constrained Parallel Scaling——N 个并行搜索 + 多数投票
- 来源质量评估: Verifier 同时验证事实准确性和来源可信度

#### 3. Browser Agent（浏览器 Agent）

| 模型角色 | 配置 | 理由 |
|---------|------|------|
| Planner | Sonnet + Adaptive Thinking | 网页导航规划复杂度中等 |
| Executor (Navigation) | Sonnet + DOM/截图工具 | 需要多模态理解（文本+视觉） |
| Executor (Data Extract) | Haiku | 结构化数据提取是轻量任务 |
| Verifier | 截图比对 + Haiku | 视觉验证页面状态正确性 |
| Router | Flash | 导航 vs 提取 vs 交互分流 |
| Summarizer | Haiku | 网页内容摘要相对简单 |

**品类特有模式**:
- GUI 交互链: WebArena 最佳 68.7%，但人类基线 78.24%——差距主要在长程规划
- 延迟敏感: 网页交互有实时性要求，优先低延迟模型
- 安全隔离: 浏览器环境是高风险输入源（Prompt Injection via 网页内容）

#### 4. Companion Agent（伴侣/对话 Agent）

| 模型角色 | 配置 | 理由 |
|---------|------|------|
| Planner | 通常不需独立 Planner | 对话驱动，非任务驱动 |
| Executor (Conversation) | Sonnet + 人格 Prompt | 对话自然度和情感理解 |
| Executor (Task) | Haiku | 简单工具调用（日历/提醒） |
| Verifier | 规则引擎 + Haiku | 安全边界检查（内容政策） |
| Router | Haiku | 闲聊 vs 任务请求 vs 情感支持分流 |
| Summarizer | Haiku | 对话历史压缩 |

**品类特有模式**:
- 个性化记忆: 长期用户偏好 + 对话风格适应（记忆安全尤为重要）
- 低延迟优先: 对话响应需在 1-2 秒内，推理深度让位于响应速度
- 主观评估: 对话质量无法用确定性方法评估，需 LLM-as-Judge + 用户满意度

---

## 设计决策矩阵

### 品类 x 关键设计维度

| 设计维度 | Coding | Research | Browser | Companion |
|---------|--------|----------|---------|-----------|
| 主推理范式 | Hybrid (Plan+ReAct) | Plan-and-Execute | ReAct | 单步/浅 ReAct |
| Planner 模型层 | Opus (Extended Thinking) | Opus (Extended Thinking) | Sonnet (Adaptive) | 无独立 Planner |
| Executor 模型层 | Sonnet / Haiku | Sonnet / Opus | Sonnet / Haiku | Sonnet / Haiku |
| 验证方式 | 确定性优先（测试） | 多 Agent 辩论 | 截图比对 | 规则+主观 |
| 典型步骤数 | 10-30 步 | 15-50 步 | 5-20 步 | 1-3 步 |
| 上下文策略 | 代码库索引+JIT 检索 | 长上下文+Compaction | 页面 DOM+截图 | 对话历史+记忆 |
| 成本中位数 | $0.72/PR | $1-5/研究 | $0.1-1/任务 | $0.01-0.05/对话 |
| 关键安全需求 | 沙箱执行 | 来源验证 | 输入隔离 | 内容政策 |
| 评估基准 | SWE-bench Verified | GAIA | WebArena | 主观 Rubric |

### 模型路由决策树（品类感知）

```
用户请求到达
  → 品类识别（Router: Haiku/Flash）
     → Coding: 复杂度评估
          简单编辑 → Haiku 直接执行
          标准功能 → Sonnet ReAct Loop
          架构级变更 → Opus 规划 + Sonnet 执行
     → Research: 深度评估
          简单查找 → Haiku + 单次搜索
          标准研究 → Sonnet 搜索 + Sonnet 综合
          深度多跳 → Opus 规划 + 并行 Sonnet 搜索 + Opus 综合
     → Browser: 交互评估
          数据提取 → Haiku + DOM 解析
          导航任务 → Sonnet ReAct + 截图
          复杂交互 → Sonnet 规划 + Sonnet 执行
     → Companion: 意图评估
          闲聊 → Haiku 直接回复
          简单任务 → Haiku + 工具调用
          深度对话 → Sonnet 对话
```

---

## 常见错误与案例

### 错误 1: 用同一模型配置处理所有品类

**表现**: 在 Coding Agent 和 Companion Agent 中使用相同的 Opus + 完整 ReAct 循环
**成本影响**: Companion 对话成本膨胀 50-100x（$0.01→$1/对话轮）
**修正**: 建立品类感知的模型路由，不同品类有不同的默认模型层级

### 错误 2: Planner 和 Executor 使用同一模型

**表现**: 规划和执行都用 Opus/o3-pro
**成本影响**: 浪费 45% 的推理成本，Executor 不需要深度推理能力
**数据**: Planner-Executor 分离可减少推理成本达 45%
**修正**: Planner 用推理模型，Executor 用快速模型

### 错误 3: 研究 Agent 用单一模型做验证

**表现**: 用同一个 LLM 实例既生成又验证研究结果
**质量影响**: 自我验证的偏见导致幻觉漏检
**数据**: Agent-as-a-Judge vs 人类专家共识不一致率 0.3%（单 LLM judge 为 31%）
**修正**: 研究品类必须用独立模型或多 Agent 辩论做验证

### 错误 4: 编码 Agent 忽略确定性验证

**表现**: 用 LLM-as-Judge 评估代码正确性，而非运行测试
**质量影响**: 代码幻觉未被检测（SWE-bench 100% 可被 pytest hooks 绕过）
**修正**: 编码品类优先使用确定性验证（单元测试、lint、类型检查），LLM 仅用于主观质量

### 错误 5: 浏览器 Agent 忽略输入信任边界

**表现**: 将网页内容直接注入模型上下文，不做信任分级
**安全影响**: GitHub Copilot RCE (CVE-2025-53773) 通过网页内容 Prompt Injection 实现远程代码执行
**修正**: 网页内容在品类安全模型中属于 Untrusted 来源，必须经过输入净化

---

## 设计启发

1. **品类决定模型角色的最低能力线**。编码品类的 Planner 需要 Opus 级推理能力（SWE-bench 数据支撑），但 Companion 品类通常根本不需要独立 Planner。
2. **验证方式是品类最大的分化点**。编码品类可用确定性方法（测试），研究品类需要多 Agent 辩论，对话品类依赖主观评估。验证方式决定了 Verifier 模型的配置。
3. **品类内部仍需复杂度分流**。即使在编码品类中，简单重命名和架构级重构的模型需求也相差 10x 以上。Router 必须是品类内的第一道门。
4. **工具生态与模型角色绑定**。不同品类的工具集完全不同（IDE 工具 vs 搜索 API vs DOM 操作 vs 日历 API），模型需要与其操作的工具集匹配。
5. **安全配置是品类特定的**。金融品类需要逐笔审批，编码品类需要沙箱执行，浏览器品类需要输入隔离。不存在通用的安全配置。
6. **评估基准必须匹配品类**。用 SWE-bench 评估 Browser Agent 没有意义；用 WebArena 评估 Coding Agent 同样如此。品类-基准对齐是评估有效性的前提。
7. **"单核心 Agent + 模块化子 Agent"是跨品类的共同模式**。Claude Code、Cursor、Devin 均采用此模式，区别在于子 Agent 的角色组合和模型配置。
8. **成本结构因品类而异**。Coding Agent $0.72/PR，Research Agent $1-5，Companion Agent $0.01-0.05。统一的成本预算对所有品类都不合适。

---

## 与知识库的映射

| 本文档章节 | 映射到的 Plane / 文档 | 关系说明 |
|-----------|---------------------|---------|
| 品类 x 模型角色矩阵 | L3 品类层 + L4 运行时层 | 品类与运行时模型配置的联合设计 |
| Planner-Executor 分离 | `architecture/multi-model/` | 多模型架构的核心模式 |
| 三层推理层级 | Plane 4-6 (Cognition) | 推理深度与模型层级映射 |
| 品类验证方式 | `evaluation/subjective-eval.md` | 主观评估方法论 |
| 品类安全矩阵 | Plane 13-15 (Trust&Identity) | 品类特定的安全需求 |
| 评估基准匹配 | `agent-evaluation-cost-corpus` | 50+ 基准的品类分类 |
| 模型路由决策树 | `paradigm-x-cost.md` | 范式选择与成本的交叉 |
| 工具生态绑定 | `reasoning-model-x-tool-use.md` | 推理模型与工具调用的交叉 |
