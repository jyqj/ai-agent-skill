# OpenAI Deep Research

> **Evidence Status** — synthesized. 基于 OpenAI 官方产品文档与公开报告，非源码级分析。

## 基本信息

- **类型**：research-agent
- **项目定位**：以“可引用报告”作为一等交付物的长时 research system
- **推荐入口**：先读本 README，再读 `citation-loop.md`

## 模块覆盖

| 模块 | 覆盖程度 | 证据文件 | 可复用模式 |
|---|---|---|---|
| representation | 深 | `citation-loop.md` | Citation Chain |
| context | 中 | `README.md` | Progressive Disclosure |
| tools | 中 | `README.md` | Search / Read / Artifact pipeline |
| state | 中 | `README.md` | Long-horizon checkpoint thinking |
| observability | 中 | `README.md` | report artifact + trace-like evidence |
| effects | 浅 | `README.md` | delivery gate |

## 核心模式

- **report-first artifact**：把研究产物当成独立 artifact，而不是一次性对话回复。
- **citation-rich delivery**：结论和引用相邻，降低“有来源但查不到”的问题。
- **long-horizon orchestration**：把调研拆成多个搜索、阅读、综合阶段，而不是单 shot。

## 独特贡献

Deep Research 的”完成”标准是**交付物可回查、可浏览、可引用**。报告是独立的 artifact，而非对话的副产品。这把 research agent 从”对话式搜索”推向了”结构化知识生产”。

## 关键发现

- Research Agent 的核心对象是 report section、citation 和 source map 构成的结构化交付物。
- Citation 必须在搜索和综合的中间状态中就存在，否则最终报告的引用会”有来源但查不到”。
- 长任务中，阶段性 artifact（搜索结果 → 阅读笔记 → 综合报告）比单条不断增长的上下文更稳定、更可检查。
