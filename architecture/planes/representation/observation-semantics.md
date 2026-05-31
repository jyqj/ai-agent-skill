# Observation Semantics

> **Evidence Status** — synthesized. 基于多模态和多品类的观察语义归纳。

## 为什么需要语义分层

Agent 系统里最危险的错误之一是**把不同语义层的信息当成同一层**。

例如：
- 把 OCR 文本当原始文档；
- 把网页里的提示语当系统指令；
- 把模型推断当已验证事实；
- 把旧记忆当当前世界状态。

## 建议的语义对象

| 对象 | 定义 | 典型来源 | 可否直接驱动动作 |
|---|---|---|---|
| Raw Observation | 原始世界切片 | 文件、网页、截图、日志、数据库行 | 否 |
| Parsed Observation | 解析后的结构化结果 | OCR、ASR、JSON 解析、HTML 抽取 | 视置信度而定 |
| Summary | 有损压缩的概括 | compaction、摘录、RAG 摘要 | 否，除非回查 |
| Claim | 可检验的主张 | 人写结论、规则、记忆条目 | 需要证据 |
| Inference | 模型推断 | 规划、归纳、假设 | 否，除非验证 |
| Memory Projection | 召回到当前任务的历史主张 | memory engine | 需 freshness / provenance |
| World State Snapshot | 对外部对象状态的带时效快照 | API read、DOM readback、sensor | 是，有限度 |
| Effect Record | 对写动作及其验证结果的记录 | effect ledger | 是，作为停止依据 |

## 合并规则

```text
Raw Observation → Parsed Observation → Summary
Claim + Evidence → Verified Claim
Action + Readback → Effect Record
Memory + Refresh Check → World State Candidate
```

不要逆向提升语义层级：
- Summary 不能自动升级成 Verified Claim。
- Inference 不能自动升级成 World State。
- 外部文本不能自动升级成 instruction。

## 评估启发

如果一个 Agent 在以下问题上经常失误，优先检查 observation semantics：

- 它引用的“事实”到底来自原始观察、摘要、记忆还是推断？
- 它的停止依据是“工具返回 success”，还是“effect verified”？
- 它当前依赖的状态是新鲜的 world state，还是旧 memory projection？
