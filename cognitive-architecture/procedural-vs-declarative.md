# 程序性知识与陈述性知识——Skill Memory vs Knowledge Memory

> **Evidence Status** — mixed. 知识分类来自认知心理学（Tulving、Anderson），LLM Agent 中的映射为工程实践推导。

## 1. 为什么需要这篇

当 Agent 需要"记住"某些东西时，"记忆"这个词掩盖了一个关键区分：记住一个事实（"Python 3.12 引入了 type parameter 语法"）和记住一个技能（"如何调试 OOM 错误"）是完全不同的认知操作。它们的存储方式、检索策略、验证方法和失效条件都不同。混淆两者会导致：

- 用 semantic search 检索技能——找到了描述但不是可执行步骤
- 用 fact-check 验证技能——事实正确但方法可能已不适用
- 用相同的治理策略管理两类知识——过度约束事实或放松了对技能的管控

## 2. 经典区分

### 2.1 陈述性知识（Declarative / "Knowing that"）

关于事实、概念和关系的知识。

```text
- Python 的 list comprehension 语法是 [x for x in iterable]
- PostgreSQL 的默认端口是 5432
- 项目 X 使用 monorepo 结构，CI 在 GitHub Actions 上运行
- 用户 A 偏好简洁的代码风格
```

特征：

- 可以直接陈述
- 有明确的真/假值
- 可能随时间过期（stale）
- 验证方式：fact-check，与权威来源比对

### 2.2 程序性知识（Procedural / "Knowing how"）

关于操作步骤、技能和方法的知识。

```text
- 如何调试一个 OOM 错误：先查内存 profile，再找泄漏点，再修复
- 如何在这个项目中添加新 API endpoint：创建 route → 写 handler → 加测试 → 更新文档
- 如何处理用户的模糊需求：先确认范围，再给出选项，等用户选择后执行
- 如何从 CI 失败日志中定位问题：先看 exit code，再看最后 50 行输出，再搜索错误信息
```

特征：

- 描述的是过程，不是单个事实
- 没有简单的真/假值——"有效/无效"取决于上下文
- 可能因环境变化而不再适用
- 验证方式：replay + eval，在实际场景中执行并评估结果

## 3. 在 LLM Agent 中的映射

| 认知分类 | Agent 中的存在形式 | 存储位置 |
|---|---|---|
| 陈述性 | 模型权重中的知识 | LLM 参数（不可直接修改） |
| 陈述性 | RAG 检索的文档 | 外部知识库、向量数据库 |
| 陈述性 | World State 的事实 | State Plane |
| 陈述性 | 用户偏好和历史 | Memory Plane（episodic / semantic） |
| 程序性 | Skill Memory | Learning & Adaptation Plane |
| 程序性 | 学习到的 SOP | Memory Plane（procedural） |
| 程序性 | 固化的工具链组合 | Skill 定义、Workflow 模板 |
| 程序性 | 模型内化的编程模式 | LLM 参数（通过训练习得） |

### 3.1 边界情况

有些知识兼具两种性质：

- "如何使用 git rebase"——语法是陈述性的，何时用、怎么处理冲突是程序性的
- "项目的部署流程"——步骤列表是陈述性的，每步的判断和处理是程序性的
- "代码风格规范"——规则是陈述性的，如何优雅地遵守规则是程序性的

设计建议：按**检索和使用场景**分类，而不是试图精确分割。查"git rebase 语法"时走陈述性检索，查"如何安全地 rebase 一个已推送的分支"时走程序性检索。

## 4. 为什么这个区分重要

### 4.1 检索策略不同

| 知识类型 | 检索方式 | 查询形式 |
|---|---|---|
| 陈述性 | Semantic search、关键词匹配 | "Python 3.12 type parameter 语法" |
| 程序性 | Task-pattern matching、场景匹配 | "处理 OOM 错误" "添加新 endpoint" |

程序性知识的检索需要理解**任务上下文**，而不仅仅是语义相似度。"调试 OOM"和"内存泄漏分析"语义相似，但"调试 OOM"和"如何在生产环境安全重启服务"可能在同一个 SOP 中出现，语义距离却很远。

### 4.2 验证方式不同

| 知识类型 | 验证方法 | 验证成本 |
|---|---|---|
| 陈述性 | 与权威来源比对、交叉验证 | 低——查文档即可 |
| 程序性 | Replay + eval，在实际或模拟环境中执行 | 高——需要执行环境和评估标准 |

一个事实可以快速验证："PostgreSQL 默认端口是 5432"——查官方文档。但一个技能的验证需要实际执行："这个调试流程在当前版本的工具链上是否仍然有效？"

### 4.3 失效条件不同

| 知识类型 | 失效原因 | 检测方式 |
|---|---|---|
| 陈述性 | 事实过期（版本更新、配置变更） | freshness check、TTL |
| 程序性 | 环境变化使步骤不再适用 | 执行失败、结果偏离预期 |

事实过期通常是突变的（版本从 3.11 升到 3.12，语法变了）。技能失效通常是渐变的（工具链逐渐更新，SOP 中的某些步骤变得低效或无效）。

### 4.4 学习机制不同

| 知识类型 | 学习方式 | 治理要求 |
|---|---|---|
| 陈述性 | 写入 memory（indexing） | 来源标注、freshness 管理 |
| 程序性 | Crystallization + governance | 需要 eval、审批、版本管理 |

把一个事实写入知识库风险较低。但把一个 SOP 固化为 Skill 需要更严格的治理——错误的 Skill 会被反复执行，影响面远大于一条错误的事实。

## 5. 与知识库的映射

| 知识库组件 | 知识类型角色 | 设计影响 |
|---|---|---|
| Memory Plane | 主要存储陈述性知识 | 检索策略应区分事实查询和技能查询 |
| Learning & Adaptation Plane | 程序性知识的固化 | Skill crystallization 需要 eval gate |
| Skill Governance | 程序性知识的治理 | 版本管理、审批流程、失效检测 |
| memory-paradigms.md | 记忆范式选择 | 不同范式对两类知识的支持不同 |
| World State Plane | 环境事实（陈述性） | freshness 和 TTL 管理 |
| Prompting Plane | 混合（规则 = 陈述性，指令 = 程序性） | System Prompt 中的规则和流程应分别管理 |

## 6. 设计启发

### 6.1 Memory Plane 应支持双通道检索

```text
陈述性通道：
  query: "PostgreSQL 默认端口"
  method: semantic search / keyword match
  result: 5432

程序性通道：
  query: "如何处理数据库连接超时"
  method: task-pattern match / SOP lookup
  result: [step1: 检查连接池配置, step2: 查看网络延迟, step3: ...]
```

### 6.2 Skill 固化需要比事实写入更严格的门槛

```text
事实写入流程：
  观察 → 提取 → 标注来源 → 存储

Skill 固化流程：
  观察模式 → 抽象为 SOP → 在多个场景中 eval → 审批 → 存储 → 持续监控
```

### 6.3 System Prompt 中的两类知识应分别管理

System Prompt 通常混合了两类知识：

- 规则（陈述性）："代码风格使用 4 空格缩进"
- 流程（程序性）："修改文件前先读取当前内容，修改后运行测试"

分别管理的好处：规则可以通过配置更新，流程需要通过 eval 验证更新后仍然有效。

### 6.4 检查清单

```text
Memory 系统是否区分了陈述性和程序性知识的检索路径？
Skill 固化是否有独立于事实写入的 eval 和审批流程？
程序性知识是否有失效检测机制（不只是 freshness TTL）？
System Prompt 中的规则和流程是否分别管理？
知识过期时的处理策略是否区分了两种类型？
```

## 7. 延伸阅读

- Tulving, E. (1972). "Episodic and Semantic Memory" -- 记忆类型的经典分类
- Anderson, J. R. (1982). "Acquisition of Cognitive Skill" *Psychological Review* -- 程序性知识的习得
- Ryle, G. (1949). *The Concept of Mind* -- "knowing how" vs "knowing that" 的哲学基础
- `paradigms/memory-paradigms.md` -- 记忆范式选择
- `architecture/planes/learning-adaptation/overview.md` -- 学习与适应
- `architecture/learning/skill-governance.md` -- Skill 治理
