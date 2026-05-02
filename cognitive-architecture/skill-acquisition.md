# 技能习得——Agent 如何从新手到专家

> **Evidence Status** — mixed. 技能习得理论来自认知心理学（Dreyfus、Anderson ACT-R），LLM Agent 中的映射为工程实践推导，部分阶段在 Skill Crystallization 和 Convention Learning 实现中有对应。

## 1. 核心问题

Agent 在面对新任务类型时，行为模式与熟练执行同类任务时截然不同。第一次调试 OOM 错误时，Agent 依赖显式规则和 few-shot 示例逐步摸索；第 100 次调试时，Agent 应该能直接识别模式并高效执行。核心问题是：

```text
"Agent 如何从依赖外部支架的新手，进化为自主高效的专家？
技能发展的路径如何映射到 Learning Plane 的工程实现？"
```

这不是简单的"记住做过的事"——而是知识从显式到隐式、从规则到直觉、从慢速到自动化的质变过程。

## 2. 经典认知科学中的技能习得模型

### 2.1 Dreyfus 五阶段模型

Dreyfus & Dreyfus（1980）提出技能习得经历五个阶段：

| 阶段 | 特征 | 行为模式 |
|---|---|---|
| 新手（Novice） | 依赖显式规则，无上下文判断 | 严格按规则执行，不能处理例外 |
| 高级初学者（Advanced Beginner） | 开始识别情境特征 | 能处理常见变体，但不能排优先级 |
| 胜任者（Competent） | 有目标意识，能做有意识的规划 | 能制定计划、处理复杂情况，但需要刻意思考 |
| 精通者（Proficient） | 直觉识别情境，分析性决策 | 自动识别"这是什么情况"，但仍需思考"该怎么做" |
| 专家（Expert） | 直觉识别 + 直觉决策 | 看到情况直接知道怎么做，无需刻意分析 |

关键洞察：从新手到专家，最大的变化不是知识量增加，而是**知识的组织方式**从"规则集合"变为"模式识别 + 情境响应"。

### 2.2 Anderson ACT-R 技能编译

Anderson（1982, 1993）的 ACT-R 理论提出技能习得的三个阶段：

**认知阶段（Cognitive Stage）**

```text
知识形式：陈述性规则（"如果 X 则做 Y"）
执行方式：逐条解释规则 → 逐步执行
速度：慢
错误率：高（规则理解错误、遗漏步骤）
```

**联结阶段（Associative Stage）**

```text
知识形式：从陈述性规则向程序性知识过渡
执行方式：规则开始被编译（compiled）为更大的操作单元
速度：中
错误率：降低（常见错误被修正）
```

**自主阶段（Autonomous Stage）**

```text
知识形式：程序性知识（自动化执行）
执行方式：模式识别 → 直接响应，无需逐步推理
速度：快
错误率：低（对常见情况），但可能对新变体缺乏灵活性
```

关键概念——**知识编译（Knowledge Compilation）**：将多个小步骤合并为一个大步骤的过程。原来需要 5 步推理完成的操作，编译后变成一步自动执行。这就是 Skill Crystallization 的认知基础。

## 3. LLM Agent 的技能习得映射

### 3.1 显式规则 → 编译技能 → 自动化执行

| 习得阶段 | Agent 工程实现 | 知识存储 | 执行效率 |
|---|---|---|---|
| 认知阶段 | System Prompt 中的显式规则 + few-shot 示例 | Prompting Plane | 低——每次都在窗口中重新推理 |
| 联结阶段 | Convention Learning + 初步 Skill Candidate | Memory Plane（Project Memory） | 中——检索到相关规则后简化推理 |
| 自主阶段 | Crystallized Skill + 自动化工具链 | Learning-Adaptation Plane（Skill Memory） | 高——模式识别后直接执行 |

### 3.2 Few-shot 示例作为"新手"阶段的外部支架

在 Dreyfus 模型中，新手依赖外部提供的显式规则。在 LLM Agent 中，few-shot 示例就是这种外部支架：

```text
新手阶段的 Agent：
  System Prompt: "当用户要求修改代码时，按以下步骤执行：
    1. 先读取目标文件
    2. 理解当前实现
    3. 做最小必要改动
    4. 运行相关测试
    5. 报告结果"

  Few-shot 示例:
    User: "修复 login 函数的 NPE"
    Agent: [读文件] → [定位 NPE] → [添加 null check] → [运行测试] → [报告]
```

问题：few-shot 示例是静态的。它告诉 Agent "按这个模式做"，但不帮助 Agent 理解"为什么这么做"或"什么时候不该这么做"。这正是 Dreyfus 新手阶段的特征——有规则但没有上下文判断能力。

### 3.3 Skill Crystallization 作为"精通/专家"阶段的工程实现

Skill Crystallization（技能结晶）对应 ACT-R 中的知识编译和 Dreyfus 模型中的精通→专家过渡：

```text
多次成功执行 trace
  → 识别共同模式
  → 抽象为可复用的 Skill Candidate
  → 验证（eval / replay）
  → 固化为 Crystallized Skill
  → 后续遇到相似场景时直接调用
```

从认知角度看，Skill Crystallization 做了两件事：

1. **知识编译**：把多步推理压缩为一步操作（对应 ACT-R 的 compilation）
2. **模式固化**：把"每次都在 Context Window 中重新推导"变为"识别模式后直接检索执行方案"（对应 Dreyfus 的直觉识别）

### 3.4 Convention Discovery 作为隐性知识获取

专家的大量知识是隐性的（tacit knowledge）——他们知道怎么做但难以明确表述。在 Agent 系统中，Convention Discovery 对应这种隐性知识的获取：

```text
Convention Discovery 过程：
  Agent 执行项目中的第一个任务
    → 观察到项目使用 4 空格缩进
    → 观察到测试文件以 test_ 开头
    → 观察到 CI 在 push 时自动运行
    → 将这些观察编码为 Project Convention
    → 后续任务自动遵循，无需每次重新发现
```

Convention 不是显式教给 Agent 的规则，而是 Agent 从环境中自主提取的模式。这对应 Dreyfus 高级初学者阶段的"情境特征识别"——不再只看规则，开始看环境中的模式。

## 4. Dreyfus 阶段与 Agent 架构的详细映射

### 4.1 新手阶段

```text
Agent 特征：
  - 完全依赖 System Prompt 和 few-shot 示例
  - 不能处理示例未覆盖的变体
  - 没有项目特定的知识

工程表现：
  - Memory 为空（无历史经验）
  - Skill Memory 为空（无已固化技能）
  - 所有推理在 Context Window 内从头开始
  - Token 消耗高，执行效率低

改进方向：
  → 积累成功和失败的 trace
  → 开始 Convention Discovery
```

### 4.2 高级初学者阶段

```text
Agent 特征：
  - 开始识别项目约定和环境特征
  - 能处理常见任务变体
  - 但不能自主判断优先级

工程表现：
  - Project Memory 中有初步的 Convention
  - 部分 Skill Candidate 被识别但未固化
  - 检索到 Convention 后可以简化推理

改进方向：
  → 验证和固化 Skill Candidate
  → 发展任务优先级判断能力
```

### 4.3 胜任者阶段

```text
Agent 特征：
  - 能自主制定执行计划
  - 能处理复杂任务但需要刻意思考
  - 有目标意识，能做 trade-off

工程表现：
  - Memory 中有稳定的 Convention 和部分 Skill
  - 能根据任务类型选择合适的范式（paradigm-routing）
  - 规划和推理仍主要发生在 Context Window 中

改进方向：
  → 更多技能固化，减少 Context 中的推理开销
  → 发展模式识别能力
```

### 4.4 精通者阶段

```text
Agent 特征：
  - 快速识别"这是什么类型的问题"
  - 自动检索相关 Skill
  - 仍需要分析性思考来处理细节

工程表现：
  - Skill Memory 丰富，覆盖大多数常见场景
  - 任务分类和 Skill 检索接近自动化
  - Context 主要用于处理问题细节而非基本方法

改进方向：
  → 处理边界情况和新变体的能力
  → 优化 Skill 的泛化性
```

### 4.5 专家阶段

```text
Agent 特征：
  - 见到问题直接知道方案
  - 极少的推理开销
  - 能优雅地处理例外和新变体

工程表现：
  - 多数常见任务通过 Skill 直接执行
  - Context 开销极低——模式识别 → Skill 调用 → 验证
  - 能从失败中快速调整（因为有大量替代策略）
  - 新任务类型仍可能退回到早期阶段

注意：Agent 的"专家"不是全能的——它在特定任务域内是专家，
遇到全新域时会退回新手阶段。这与人类专家一样。
```

## 5. MVA 阶梯作为系统级技能习得

Maturity-Value Alignment（MVA）阶梯可以被视为系统级别的技能习得过程：

| MVA 级别 | Dreyfus 对应 | 系统特征 |
|---|---|---|
| MVA-0: Prompt-Only | 新手 | 纯规则驱动，无学习 |
| MVA-1: Tool-Augmented | 高级初学者 | 有工具但不会自主选择 |
| MVA-2: Memory-Enhanced | 胜任者 | 跨会话学习，有计划能力 |
| MVA-3: Self-Improving | 精通者 | 自主提炼 Skill，自我改进 |
| MVA-4: Ecosystem-Integrated | 专家 | 与环境深度集成，近乎自动化 |

每个 MVA 级别的提升，本质上是 Agent 系统在更大尺度上完成了"从显式规则到自动化执行"的转化。

## 6. 与 Procedural-vs-Declarative 的关系

技能习得的过程本质上是**陈述性知识向程序性知识转化**的过程：

```text
陈述性（规则、事实）
  → [反复执行 + 反馈]
  → 联结（规则与执行的绑定）
  → [编译 + 优化]
  → 程序性（自动化技能）
```

| 知识转化 | 在 Agent 中的对应 | 涉及的 Plane |
|---|---|---|
| 陈述性规则 | System Prompt 中的显式指令 | Prompting Plane |
| 规则 → 执行绑定 | 成功 trace 与规则的关联 | Context + Memory |
| 执行 → 技能编译 | Skill Crystallization | Learning-Adaptation Plane |
| 技能 → 自动化 | Crystallized Skill 的自动检索和调用 | Memory + Context |

关键设计约束：不是所有陈述性知识都应该变成程序性知识。有些知识应该保持陈述性形式（如"PostgreSQL 默认端口是 5432"），因为它的价值在于准确性而非执行效率。只有**反复执行且稳定的操作序列**才值得编译为技能。

## 7. 与 Learning 目录的连接

`architecture/learning/` 提供了技能习得的工程机制，认知架构层提供了理论框架：

| Learning 组件 | 认知基础 | 设计影响 |
|---|---|---|
| Skill Crystallization | ACT-R 的知识编译 | 结晶的阈值应基于执行次数和成功率 |
| Skill Governance | Dreyfus 专家阶段的"例外处理" | 专家级技能也可能过时，需要退役机制 |
| Convention Learning | 隐性知识获取 | Convention 是情境特征识别，不是通用规则 |
| Knowledge Distillation | 长 trace 到精炼 skill 的压缩 | 蒸馏应保留决策逻辑而非仅保留步骤序列 |
| Failure-driven Improvement | Dreyfus 胜任者阶段的刻意学习 | 失败反馈应修正 Skill 而非仅修正规则 |
| Online Adaptation | 从胜任到精通的过渡 | 在线适应需要平衡"利用已有技能"和"探索新方法" |

## 8. Plane Mapping

| Plane | 技能习得的影响 | 设计影响 |
|---|---|---|
| Learning-Adaptation Plane | 技能的提炼、验证、固化、退役的全生命周期 | 应支持 Dreyfus 阶段的渐进式演进，而非一步到位 |
| Memory Plane | Skill Memory 和 Convention 的存储和检索 | 程序性记忆的检索应基于任务模式匹配，而非语义相似 |
| Prompting Plane | 从 few-shot 支架到 Skill 调用的演进 | 随着技能固化，Prompt 中的显式规则应逐步减少 |
| Context Plane | 技能固化后减少 Context 中的推理开销 | 专家级执行应消耗更少的 Context 预算 |
| Evaluation Plane | 技能验证和阶段判断 | Eval 应能区分"新手正确执行规则"和"专家高效执行" |

## 9. 设计启发

### 9.1 支持渐进式技能发展

不要试图让 Agent 一步从新手跳到专家。设计应支持渐进式发展：

```text
第 1 次执行：完全依赖 Prompt 规则（新手）
第 2-5 次执行：积累 trace，开始识别模式（高级初学者）
第 5-10 次执行：Skill Candidate 被识别，开始验证（胜任者）
第 10+ 次执行：Skill 被固化，执行效率显著提升（精通）
持续执行：Skill 持续优化，边界情况被覆盖（专家）
```

### 9.2 Prompt 规则应随技能发展动态调整

新手阶段需要详细的规则；专家阶段不需要。如果 Skill 已经固化了某个操作序列，对应的 Prompt 规则可以简化或移除，释放 Context 空间。

```text
新手阶段的 Prompt：
  "修改文件的步骤：1. 读取文件 2. 理解结构 3. 做最小改动
   4. 运行测试 5. 检查结果 6. 如果失败则修正"

专家阶段的 Prompt：
  "修改文件时遵循项目约定"
  + Skill Memory 中有 "code-modification" Skill 可检索
```

### 9.3 Skill 固化不是终点

固化的 Skill 会随环境变化而过时。设计应支持：

- **Skill 的退化检测**：固化的 Skill 在最近 N 次使用中成功率下降
- **Skill 的版本管理**：同一 Skill 可能有多个版本，适用于不同环境
- **Skill 的退役**：不再适用的 Skill 应被停用而非继续使用
- **从专家回到新手**：面对全新领域时，应优雅地退回到规则驱动模式

### 9.4 区分"利用"和"探索"

精通阶段的 Agent 面临一个经典 trade-off：

```text
利用（Exploitation）：使用已有的固化 Skill，效率高但可能错过更好的方法
探索（Exploration）：尝试新方法，可能发现更优路径但有失败风险
```

设计建议：

- 对高风险任务优先利用已验证的 Skill
- 对低风险任务允许一定比例的探索
- 定期在 eval 环境中对 Skill 进行"再探索"，检验是否有更优路径

### 9.5 检查清单

```text
Agent 系统是否支持技能的渐进式发展（而非只有"无技能"和"有技能"两态）？
Skill Crystallization 是否有足够的验证门槛（不是执行一次就固化）？
固化的 Skill 是否有退化检测和退役机制？
Prompt 规则是否随技能发展动态调整（避免冗余指令）？
新领域是否支持优雅地退回到规则驱动模式？
Skill 检索是否基于任务模式匹配（而非仅语义相似度）？
是否有"利用 vs 探索"的平衡策略？
Convention Discovery 是否与 Skill Crystallization 区分管理？
```

## 10. 延伸阅读

- Dreyfus, H. L. & Dreyfus, S. E. (1980). "A Five-Stage Model of the Mental Activities Involved in Directed Skill Acquisition" -- 五阶段模型
- Anderson, J. R. (1982). "Acquisition of Cognitive Skill" *Psychological Review* -- ACT-R 技能编译
- Anderson, J. R. (1993). *Rules of the Mind* -- ACT-R 理论的完整阐述
- Ericsson, K. A. & Charness, N. (1994). "Expert Performance" *American Psychologist* -- 刻意练习和专家表现
- `procedural-vs-declarative.md` -- 程序性知识与陈述性知识的区分
- `metacognitive-control.md` -- 元认知控制（含学习意识）
- `architecture/learning/overview.md` -- Learning 模块的工程实现
- `architecture/learning/skill-governance.md` -- Skill 治理
- `design-space/patterns/skill-crystallization.md` -- Skill Crystallization 模式
- `index/maturity-ladders.md` -- MVA 成熟度阶梯
