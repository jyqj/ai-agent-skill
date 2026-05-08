# Reasoning x Action 交叉设计

> **Evidence Status** — grounded.
> 知识库映射: Cognition (Plane 4-6) x Action&Effect (Plane 10-12) x Sensing&Repr (Plane 1-3)

## 为什么需要这篇文档

推理模型（Extended Thinking、o-series、Gemini Thinking）的出现，根本性地改变了 Agent 与工具交互的模式。传统 ReAct 范式中，推理和工具调用是交替进行的——Agent 思考一步、调用一个工具、观察结果、再思考下一步。推理模型让 Agent 能在单次推理中进行更深层的多步推理，减少了"浅层推理 → 错误行动 → 纠正"的往复。

关键证据：
- **Interleaved Thinking**: Claude 在每次工具返回结果后可以"停下来思考"再决定下一步，tau-Bench 航空领域实现 54% 相对改进
- **MCP Sampling**: MCP Server 可以请求 LLM 在工具执行过程中生成额外推理，实现嵌套推理
- **ReWOO**: LLM 在执行前一次性规划整个工具调用序列，显著降低 token 消耗
- **Think Tool**: 在已开始生成响应后，Agent 可以"停下来思考"——与 Extended Thinking（生成响应前的深度思考）形成互补

推理模型并未替代 ReAct——ReAct 的核心价值（将推理锚定在真实世界反馈中）仍不可替代。但推理模型让每步 Thought 更深、更准确，同时引入了全新的工具调用模式。

---

## 交叉点识别

| 交叉点 | Reasoning 侧关注 | Action 侧关注 | 冲突/张力 | 设计要求 |
|--------|----------------|--------------|----------|---------|
| 推理深度 vs 行动频率 | 更深推理可能减少行动次数 | 行动提供真实世界反馈 | 过度推理 vs 过度行动 | 自适应推理-行动平衡 |
| 推理过程中的工具需求 | 推理需要外部信息辅助 | 工具调用需要上下文切换 | 推理连续性 vs 信息需求 | Interleaved Thinking |
| 预规划 vs 逐步调用 | 一次性规划可减少推理开销 | 逐步调用可利用中间反馈 | 效率 vs 适应性 | ReWOO vs ReAct 选择 |
| 推理可见性 | 推理过程是调试的关键信息 | 工具调用链是审计的关键 | 推理隐私 vs 可审计性 | 分级可见性策略 |
| 错误处理 | 推理可预判可能的错误 | 行动失败需要实际处理 | 预防 vs 响应 | 推理驱动的错误预判 |
| 成本分配 | 推理 token 高成本 | 工具调用有独立计费 | 推理成本 vs 行动成本 | Budget-Aware 推理-行动分配 |

---

## 推理模型下的工具调用模式对比

### 五种模式概览

| 模式 | 推理-行动关系 | Token 效率 | 适应性 | 适用场景 |
|------|-------------|----------|--------|---------|
| **传统 ReAct** | 交替（浅推理+逐步行动） | 低（每步重发上下文） | 高（每步可调整） | 时敏 QA、故障排查 |
| **Interleaved Thinking** | 深度交替（深推理+行动+深推理） | 中（推理 token 增加但步数减少） | 高（推理+反馈双保障） | 复杂 Agentic 工作流 |
| **ReWOO** | 分离（一次性规划+批量执行） | 高（无重复上下文） | 低（中途无法调整） | 常规多跳查询 |
| **Think Tool** | 按需暂停推理 | 中（额外推理 token） | 高（策略密集环境） | 工具输出分析、合规检查 |
| **MCP Sampling** | 嵌套推理（工具内请求推理） | 可变 | 高（推理嵌套在工具内） | Agent 任务中途需额外推理 |

### 模式 1: 传统 ReAct

```
User Query → Thought(浅) → Action → Observation → Thought(浅) → Action → ... → Response
```

- 每步 Thought 推理深度有限
- 错误会沿后续步骤级联传播
- 缺乏长期规划能力
- "对需要长远规划或复杂依赖的任务效率低下"
- 纯推理模型（reason-only）"经常给出自信但错误的答案"，ReAct 通过环境验证降低幻觉风险

### 模式 2: Interleaved Thinking（交错思考）

```
User Query → [Deep Thinking] → Action 1 → Result → [Deep Thinking] → Action 2 → ... → Response
```

**无交错思考**:
```
Query → [Think] → [Tool 1] → Result → [Tool 2] → Result → [Response]
         一次性推理   →   后续不再思考   →   盲目继续
```

**有交错思考**:
```
Query → [Think] → [Tool 1] → Result → [Think] → [Tool 2] → Result → [Think] → [Response]
         深度推理          →  消化结果  →  调整策略  →  消化结果  →  最终综合
```

**关键差异**:
- 每次工具返回结果后，模型可以"停下来思考"再决定下一步
- Claude 的 Adaptive Thinking 自动启用 interleaved thinking
- effort 参数可动态调整：简单步骤 `low`，关键决策 `high`
- 对复杂 agentic 工作流至关重要

### 模式 3: ReWOO（Reasoning Without Observation）

```
User Query → [完整规划: Tool1(arg1), Tool2(#1.result), Tool3(#2.result)]
                  → Execute Tool1 → Execute Tool2(用 Tool1 结果替换占位符) → Execute Tool3 → Response
```

- LLM 在执行前一次性规划整个工具调用序列
- 使用占位符 `#N.result` 引用未来结果
- 显著降低 token 消耗和延迟（避免重复发送对话历史）
- 适合多跳问题和常规工具流程
- **关键限制**: 中途失败时缺乏调整能力

### 模式 4: Think Tool（思考工具）

```
Agent 已开始生成响应...
    → 遇到复杂工具输出 → [调用 Think Tool: 分析结果、评估策略]
    → 继续生成...
    → 遇到合规检查点 → [调用 Think Tool: 逐约束验证]
    → 继续生成...
```

**与 Extended Thinking 的本质区别**:
- Extended Thinking: 生成响应**前**的深度思考（前置推理）
- Think Tool: 开始生成**后**，在执行过程中"停下来思考"（中途推理）

**三大应用场景**:
1. 工具输出分析: 处理前置工具调用的结果，可能需要改变策略
2. 策略密集环境: 遵循复杂指南并验证合规性
3. 顺序决策: 每步建立在前一步基础上，错误代价高

**实验结果**: tau-Bench 航空领域 Think Tool + 优化提示实现 54% 相对改进（0.370 → 0.570）

### 模式 5: MCP Sampling（嵌套推理）

```
Agent → MCP Tool Call → MCP Server 执行...
    MCP Server 需要额外推理 → [Sampling: 请求 LLM 生成中间推理]
    → LLM 返回推理结果给 MCP Server → MCP Server 继续执行 → 返回最终结果给 Agent
```

- MCP Sampling 允许 MCP Server 请求 LLM 生成文本
- 用于 Agent 任务中途需要额外推理的场景
- 实现了"工具内推理"——推理能力不限于 Agent 主循环

---

## Interleaved Thinking 的工具间推理详解

### 为什么工具间推理是关键

在标准工具调用链中，Agent 收到 Tool 1 的结果后直接决定 Tool 2 的调用。这意味着：
- 如果 Tool 1 返回意外结果，Agent 可能按照过时的计划继续执行
- 无法基于中间结果重新评估整体策略
- 错误在工具链中无声传播

Interleaved Thinking 在每个工具结果后插入一个推理阶段：

```
[Thinking]: 初始分析和计划
  → Tool 1 (搜索代码库)
    → Result: 找到 3 个相关文件
      → [Thinking]: 文件 A 最相关，但发现依赖项冲突。
         原计划直接修改，现在需要先理解依赖关系。调整策略。
  → Tool 2 (读取依赖配置)
    → Result: 依赖版本不兼容
      → [Thinking]: 版本冲突可通过升级 X 或降级 Y 解决。
         升级 X 风险更低，但需要同时修改测试。重新规划步骤。
  → Tool 3 (修改代码)
    → Result: 修改完成
      → [Thinking]: 核心修改已完成。按照安全检查清单:
         1. 类型检查 ✓
         2. 依赖兼容 ✓
         3. 测试覆盖 — 需要添加新测试
  → Tool 4 (运行测试)
    → Result: 2 个测试失败
      → [Thinking]: 失败原因是 mock 对象未更新。这是预期的，
         因为修改了接口签名。修复 mock 即可。
  → [Response]: 最终结果
```

### Adaptive Thinking 的 effort 动态调整

| Effort 级别 | 思考行为 | 适用的工具间阶段 |
|-------------|---------|----------------|
| `max` | 始终深度思考，无约束 | 架构级决策、安全审计 |
| `high`（默认） | 始终思考，复杂任务深度推理 | 大多数工具间推理 |
| `medium` | 中等思考，简单查询可能跳过 | 常规数据提取 |
| `low` | 最小化思考，简单任务优先速度 | 格式转换、简单查找 |

**关键洞察**: "提示对困难域至关重要，但简单域只需有思考空间即可"

---

## 设计决策矩阵

### 按场景选择推理-工具模式

| 场景 | 推荐模式 | 理由 | effort 配置 |
|------|---------|------|------------|
| 实时 QA + 工具查找 | 传统 ReAct | 快速响应、增量发现 | low-medium |
| 复杂代码修改 | Interleaved Thinking | 每步需要消化代码上下文 | high |
| 常规多跳搜索 | ReWOO | 搜索链可预测，无需中间调整 | N/A（一次规划） |
| 合规审查工作流 | Think Tool | 需要逐约束验证 | high-max |
| MCP 工具需要中间推理 | MCP Sampling | 工具内部需要额外推理 | 由 MCP Server 决定 |
| 安全关键操作 | Interleaved + Think Tool | 每步推理 + 操作前二次审视 | max |
| 大型项目（40+ 步） | Hybrid: ReWOO 框架 + 局部 Interleaved | 全局预规划 + 关键步骤深度推理 | 分步调整 |

### 推理-行动平衡的成本影响

| 模式 | 推理 Token 消耗 | 工具调用次数 | 总成本趋势 | 适用 Budget |
|------|---------------|------------|-----------|------------|
| 传统 ReAct | 低/步 x 多步 = 中 | 高 | 中-高 | $0.5-5 |
| Interleaved | 高/步 x 少步 = 中-高 | 中 | 中 | $1-5 |
| ReWOO | 高（一次）+ 零（执行时） | 固定 | 低 | $0.1-1 |
| Think Tool | 按需增加 | 中 | 中 | $1-3 |
| MCP Sampling | 可变 | 中 | 可变 | $0.5-5 |

---

## 常见错误与案例

### 错误 1: 纯推理不接地（Reason-Only without Grounding）

**表现**: 使用推理模型的深度思考能力，但不通过工具调用验证推理结果
**数据**: 纯推理模型"经常给出自信但错误的答案"
**案例**: 法律 AI 幻觉——1,348 起全球案件中，AI 生成不存在的法律引用并自信地"推理"其适用性
**修正**: ReAct 的环境验证锚定推理——推理模型增强了 ReAct，但不替代它

### 错误 2: 推理与行动不匹配（Mismatched Depth）

**表现**: 对简单查找任务使用 Extended Thinking (max effort)，或对关键决策跳过推理
**成本影响**: 简单 QA 用 max effort 推理，成本增加 5-10x 但质量无提升
**修正**: Adaptive Thinking 自动评估复杂度并调整 effort；或显式配置 effort per 步骤

### 错误 3: ReWOO 用于高不确定性任务

**表现**: 对中间步骤结果高度不确定的任务使用 ReWOO 预规划
**风险**: ReWOO 中途失败时缺乏调整能力，整个规划可能因一步失败而作废
**修正**: ReWOO 仅用于工具调用链可预测的场景（如：搜索A → 搜索B → 合并结果）

### 错误 4: 忽略 Think Tool 与 Extended Thinking 的差异

**表现**: 将 Think Tool 和 Extended Thinking 视为同一机制的不同名称
**实际差异**: Extended Thinking 是前置推理，Think Tool 是中途推理。前者决定整体策略，后者处理执行过程中的复杂决策
**修正**: 两者互补使用——Extended Thinking 做前置规划，Think Tool 处理工具输出分析和合规检查

### 错误 5: Agent 可修改自身安全配置

**表现**: 推理模型的强大能力被用于绕过安全约束
**案例**: GitHub Copilot RCE (CVE-2025-53773)——Prompt Injection 导致 Copilot 修改 `.vscode/settings.json`，启用 YOLO 模式（所有操作无需确认）
**修正**: Agent 的安全配置必须在不可修改的层面实现；推理能力不应扩展到安全配置修改

---

## 设计启发

1. **推理模型增强 ReAct，不替代 ReAct**。ReAct 的核心价值——将推理锚定在真实世界反馈中——在推理模型时代仍不可替代。推理模型让每步 Thought 更深、更准确。
2. **Interleaved Thinking 是复杂 Agentic 工作流的关键模式**。在工具返回结果后"停下来思考"的能力，解决了传统 ReAct 中"盲目继续"的问题。
3. **Think Tool 和 Extended Thinking 是互补的，不是替代的**。Extended Thinking 做前置深度规划，Think Tool 处理执行中的关键决策。同时使用可覆盖推理链的全部阶段。
4. **ReWOO 适合确定性工具链，不适合探索性任务**。预规划的效率优势以牺牲适应性为代价；仅在工具调用序列可预测时使用。
5. **effort 动态调整是成本控制的隐藏杠杆**。简单步骤用 `low` effort，关键决策用 `high`/`max`——同一任务内的 effort 差异可达 10x token 消耗。
6. **MCP Sampling 开启了"工具内推理"的新范式**。推理不再局限于 Agent 主循环；MCP Server 可在工具执行过程中请求额外推理，实现嵌套推理链。
7. **不可逆操作前必须有推理检查点**。PocketOS 数据库 9 秒删除事件证明：Agent 在执行破坏性操作前必须有显式推理步骤（Think Tool）评估风险。
8. **推理能力不应扩展到安全边界修改**。Copilot YOLO 模式事件证明：即使推理模型"理解"了安全设置的含义，也不应允许其修改安全配置。

---

## 与知识库的映射

| 本文档章节 | 映射到的 Plane / 文档 | 关系说明 |
|-----------|---------------------|---------|
| 五种模式对比 | Plane 4-6 (Cognition) | 推理范式的核心分类 |
| Interleaved Thinking | Plane 10-12 (Action&Effect) | 推理-行动交错影响行动质量 |
| ReWOO | Plane 16 (Coordination) | 预规划是编排模式的一种 |
| Think Tool | `concepts/foundations/` | 思考工具的认知基础 |
| MCP Sampling | Plane 1-3 (Sensing&Repr) | MCP 协议层的推理集成 |
| effort 动态调整 | `paradigm-x-cost.md` | 推理深度与成本的交叉 |
| 安全配置不可修改 | `protocol-x-security.md` | 协议层安全边界 |
| 不可逆操作检查 | `ai-agent-failure-casebook` 案例 1, 2 | PocketOS/Replit 案例 |
