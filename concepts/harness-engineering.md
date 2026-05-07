# Harness Engineering

> **Evidence Status** — synthesized. 核心概念归纳与跨模块一致性整理。

> **完整版**见 `../design-space/methodology/harness-engineering.md`。本文保留核心概念供快速查阅。

## 定义

**Harness 是 Agent 系统中除了 Model 之外的一切。**

Harness 这个词来自马具（缰绳、马鞍），用于引导强大但不可预测的力量：
- 马 = AI 模型：强大但不知道该往哪走
- Harness = 控制系统：约束、引导、赋能

## Model vs Harness 边界

| Model 的职责 | Harness 的职责 |
|-------------|---------------|
| 理解、推理、生成 | 执行、存储、验证 |
| 决定做什么 | 提供能做什么 |
| 输出文本 | 解析文本、执行动作 |
| 短期记忆（上下文） | 长期记忆（文件、数据库） |

> LLM-as-CPU 类比（Beren Millidge）：原始 LLM 是一个没有 RAM、没有磁盘、没有 I/O 的 CPU。上下文窗口 = RAM，外部数据库 = 磁盘，工具集成 = 设备驱动，Harness = 操作系统。

## 三层工程关系

```text
Harness Engineering（最广）
└── 设计 Agent 运行的整个环境
    ├── Context Engineering（子集）
    │   └── 管理 Model 看到什么
    │       └── Prompt Engineering（子集）
    │           └── 优化单次交互的措辞
    └── 执行环境、工具、约束、验证、编排
```

| 层次 | 优化目标 | 时间范围 |
|-----|---------|---------| 
| Prompt Engineering | 单次输出质量 | 一次交互 |
| Context Engineering | Model 看到的信息 | 一个上下文窗口 |
| Harness Engineering | 整个 Agent 系统 | 跨多个上下文窗口 |

随着任务复杂度增加，团队自然从 Prompt → Context → Harness 演进。

## 设计哲学

### 从期望行为反推设计

| 期望行为 | Model 局限 | Harness 设计 |
|---------|-----------|-------------|
| 记住之前的对话 | 无持久记忆 | Memory 文件 + 注入 |
| 访问最新信息 | 知识截止 | 搜索工具 |
| 验证代码正确 | 无法执行 | 沙箱 + 测试 |
| 长时间工作 | 上下文限制 | 多窗口 + 进度文件 |

### 约束往往提升可靠性

约束解空间反而让 Agent 更高效：无约束时，Agent 浪费 tokens 探索死胡同；机械化约束（linters、结构测试）比提示更可靠；架构边界让 Agent 更快理解代码库。

### 错误驱动的 Harness 进化

> "每次 Agent 犯错，就工程化一个解决方案，让它永远不再犯。" — Mitchell Hashimoto

循环：观察失败 → 分析根因 → 添加 Harness 特性 → 验证 → 重复

### 文件系统是协作界面

多 Agent 通过文件协调；进度用 git 追踪；状态改变写文件，不只放上下文。

## 关键证据

> LangChain 证明，仅改变 Harness（不改 Model），在 TerminalBench 2.0 上从 Top 30 外跃升至 Top 5。

Harness 工程是 Agent 性能的最大杠杆。

## Harness 的组成模块

Harness 的具体模块架构见 `architecture/overview.md`。
