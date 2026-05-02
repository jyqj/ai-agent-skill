# 已知失败的设计——经验教训档案

> **Evidence Status** — synthesized. 生产环境中的真实失败案例、社区复盘报告、知识库维护过程中反复出现的误解模式。

## 为什么需要这个目录

`anti-patterns/` 是抽象的"不该做什么"——它告诉你某类设计模式有风险，但不告诉你具体是谁、在什么场景下踩了坑。

本目录不同。每一篇都是一个具体的 narrative：谁在什么场景下做了什么设计选择、为什么当时觉得合理、实际发生了什么、根因是什么、我们学到了什么。

Anti-patterns 是规则，lessons-learned 是故事。规则容易被跳过，故事更容易被记住。

## 与 anti-patterns 的区别

| 维度 | Anti-Patterns | Lessons Learned |
|---|---|---|
| 抽象程度 | 高——模式级别 | 低——具体案例 |
| 叙事性 | 弱——列表和规则 | 强——有场景、有转折、有教训 |
| 上下文 | 通用 | 绑定到具体场景和约束 |
| 阅读目的 | 设计评审检查清单 | 理解"为什么那样不行" |
| 更新频率 | 低——模式稳定 | 中——新案例持续积累 |

## 格式模板

每篇经验教训遵循以下结构：

1. **场景**：什么类型的 Agent、什么业务需求、什么约束条件
2. **设计选择**：团队做了什么决定
3. **预期**：为什么觉得这样可行
4. **实际结果**：发生了什么
5. **根因分析**：为什么预期和现实不符
6. **教训**：下次应该怎么做
7. **关联文件**：知识库中哪些文件提供了更系统的分析

## 案例索引

| 案例 | 核心教训 | 关联概念 |
|---|---|---|
| [infinite-context-as-memory.md](infinite-context-as-memory.md) | 上下文窗口再大也不能替代记忆系统 | Working Memory、Memory Plane |
| [tool-success-as-completion.md](tool-success-as-completion.md) | 工具返回成功不等于任务完成 | Effect Verification、Postcondition |
| [single-model-judge.md](single-model-judge.md) | 不能让同一个模型当自己的法官 | Multi-Model、Confidence Aggregation |

---

## 延伸阅读

- `design-space/anti-patterns/` — 抽象层面的反模式汇总
- `evaluation/failure-taxonomy.md` — 失败分类学
- `concepts/representation-and-effects.md` — 表示、接口与效果的核心概念
