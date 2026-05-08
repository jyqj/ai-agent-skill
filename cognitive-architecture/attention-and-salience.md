# 注意力与显著性——Agent 如何在信息洪流中分配权重

> **Evidence Status** — mixed | **类比边界** — Broadbent 过滤模型和 Kahneman 容量模型有结构性对应（直接映射到 Context 组装策略）；Treisman 衰减模型为启发性类比。

> **相关视角**：工程实现见 [上下文工程](../concepts/context-engineering.md)，容量与衰减见 [工作记忆动态](working-memory-dynamics.md)。本文聚焦显著性权重。

## 核心问题

Agent 每一步面临大量信息（工具输出、对话历史、检索记忆、世界状态）。Context Window 容量有限，注意力权重非均匀分布。核心问题：**什么应该进入当前窗口？进入后什么值得更多注意力？**

## 对 Agent 的直接启发

### Broadbent 过滤模型 -> 信息进入前过滤

信息在进入深度加工之前就应被过滤——不是所有工具输出都需要进入 Context Window。

```text
工具输出 -> [显著性评估]
  -> 高显著性：原样保留或结构化提取
  -> 中显著性：摘要 + raw ref
  -> 低显著性：仅保留 raw ref，不进入窗口
```

### Kahneman 容量模型 -> Context 预算分配

Context Window 的 token 预算就是注意力资源池。分配策略：

```text
1. 固定分配（pin）：System Prompt、Goal、Constraints     — 持久倾向
2. 目标驱动分配：与当前 milestone 相关的 observations    — 即时意图
3. 显著性驱动分配：异常信号、错误、冲突                  — 自动注意
4. 预算余量（10-15%）：处理意外发现和方向调整            — 剩余资源
```

### Treisman 衰减模型 -> 压缩信息的回查

被压缩或摘要化的信息不是完全不可用。如果摘要中出现异常信号（错误码、unexpected 关键词），应触发"回查原文"。这是 Tool Output Offloading 中保留 raw ref 的认知基础。

## Context Pack 组装优先级

| 选择因素 | 策略 | 冲突时优先级 |
|---|---|---|
| 结构优先级 | System Prompt > Goal > Recent > Background | 最高——不可缺省的基线 |
| 显著性 | 异常信号优先（可能推翻假设） | 高 |
| 目标相关性 | 按 goal alignment 排序 | 中 |
| 新鲜度 | 最近的观察优先 | 中 |
| 可靠性 | 高 trust 来源优先 | 默认即可 |

对任务交付型 Agent，**目标相关性**和**新鲜度**通常是最需要调优的两个因素。

## 显著性信号类型

| 信号类型 | 示例 | 处理策略 |
|---|---|---|
| 错误和异常 | exit code != 0、stack trace | 自动提升优先级 |
| 与预期不符 | 搜索预期有结果但为空 | 触发反思 |
| 模式打破 | 前 9 个测试通过、第 10 个异常失败 | 可能暴露边界条件 |
| 安全信号 | 权限错误、认证失败 | 强制注意 + 告警 |

**设计原则**：异常信号的优先级应高于正常的任务相关信息。正常信息确认假设，异常信息可能推翻假设——推翻假设的信息价值更高。

## Compaction 与注意力的关系

| Compaction 策略 | 注意力模型 |
|---|---|
| Snip（裁剪工具输出） | Broadbent 过滤——直接丢弃低显著性输出 |
| Micro-summary（微摘要） | Treisman 衰减——保留关键信号，衰减细节 |
| Collapse（折叠历史） | 容量模型的资源回收 |

压缩原则：高显著性信息最后压缩；压缩应保留异常信号摘要；保留 raw ref 允许回查。

## 常见反模式

| 反模式 | 修正 |
|---|---|
| 注意力均匀分布（关键信号被淹没） | 引入显著性评估和优先级分配 |
| 纯目标驱动（忽略异常） | 为异常信号保留自动注意力通道 |
| 注意力僵化（阶段变了关注没变） | 阶段转换时重新评估分配 |
| 预算耗尽（无法处理新信息） | 保留 10-15% token 余量 |
| 摘要丢失异常 | 压缩策略显式保留异常信号 |

## 交叉引用

- `working-memory-dynamics.md` — 工作记忆动力学
- `metacognitive-control.md` — 反思决策中的注意力
- `../concepts/context-engineering.md` — 上下文工程
- `../design-space/patterns/compaction.md` — Compaction 策略
- `../design-space/patterns/tool-output-offloading.md` — 工具输出卸载
