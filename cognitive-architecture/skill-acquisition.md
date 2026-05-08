# 技能习得——Agent 如何从新手到专家

> **Evidence Status** — mixed | **类比边界** — ACT-R 知识编译有结构性对应（Skill Crystallization 直接映射）；Dreyfus 五阶段为启发性类比，生产系统很少严格按此设计。

## 核心问题

Agent 面对新任务类型时依赖显式规则逐步摸索；反复执行后应能识别模式并高效执行。核心问题：**知识如何从显式规则变为自动化技能？**

## Dreyfus 五阶段速查

| 阶段 | Agent 行为 | 工程对应 |
|---|---|---|
| 新手 | 严格按 System Prompt 规则执行，无上下文判断 | few-shot + 显式指令 |
| 高级初学者 | 开始识别项目约定，处理常见变体 | Convention Discovery |
| 胜任者 | 有目标意识，能做计划和 trade-off | Skill Candidate 识别 |
| 精通者 | 快速识别问题类型，自动检索 Skill | Skill Memory 检索 |
| 专家 | 模式识别后直接执行，极低推理开销 | Crystallized Skill 调用 |

注意：Agent 在特定域内是专家，遇到全新域时会退回新手阶段。

## ACT-R 知识编译 -> Skill Crystallization

ACT-R 的三阶段（认知 -> 联结 -> 自主）直接映射到 Agent 工程实现：

| 习得阶段 | Agent 工程实现 | 知识存储 |
|---|---|---|
| 认知阶段 | System Prompt 中的显式规则 + few-shot | Prompting Plane |
| 联结阶段 | Convention Learning + 初步 Skill Candidate | Memory Plane（Project Memory） |
| 自主阶段 | Crystallized Skill + 自动化工具链 | Learning-Adaptation Plane |

**知识编译**的本质：将多步推理压缩为一步操作。原来需要 5 步推理完成的操作，编译后变成一步自动执行。这是 Skill Crystallization 的认知基础。

## Convention Discovery 作为隐性知识获取

Convention 不是显式教给 Agent 的规则，而是 Agent 从环境中自主提取的模式（缩进风格、测试命名约定、CI 流程等）。这对应从"只看规则"到"识别环境模式"的转变。

## 设计启发

1. **支持渐进式发展**：不要设计"无技能 / 有技能"的二态系统。Skill Crystallization 需要足够的执行次数和成功率作为阈值。
2. **Prompt 规则应随技能发展动态调整**：技能固化后，对应的显式规则可简化或移除，释放 Context 空间。
3. **Skill 固化不是终点**：需要退化检测（最近 N 次成功率下降）、版本管理、退役机制。
4. **平衡利用与探索**：高风险任务优先利用已验证 Skill；低风险任务允许探索新方法。
5. **Skill 检索应基于任务模式匹配**，而非仅语义相似度。

## 交叉引用

- `procedural-vs-declarative.md` — 程序性 vs 陈述性知识
- `metacognitive-control.md` — 元认知控制
- `../architecture/learning/overview.md` — Learning 模块工程实现
- `../design-space/patterns/skill-crystallization.md` — Skill Crystallization 模式
- `../index/maturity-ladders.md` — MVA 成熟度阶梯
