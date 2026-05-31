# Data / BI Agent Architecture

> **Evidence Status** — grounded. Text-to-SQL 研究 (ReViSQL/BIRD)、Databricks AI/BI Genie、Snowflake Cortex Analyst、ThoughtSpot、LinkedIn chatbot。

## Core Job

让非技术用户用自然语言获取可追溯、可信赖的数据分析结果：

```text
理解问题 → 识别数据源和指标 → 构建查询 → 执行校验 → 解释结果 → 追溯来源
```

核心挑战：AI 生成的 SQL 看起来对但语义错，例如用错 join、混淆口径、忽略时效。

## 用户模型

| 用户 | 心智模型 | 信任建立方式 | 默认交互 |
|---|---|---|---|
| 业务分析师 | SQL 助手 | SQL 可审、结果可验证 | NL → SQL + 结果 + 解释 |
| 管理层 | 数据问答 | 结论清晰、来源透明 | NL → 图表 + 摘要 |
| 数据工程师 | 查询优化器 | SQL 质量高 | SQL 生成 + 优化建议 |

## 任务模型

| 任务 | 深度 | 完成定义 |
|---|---|---|
| 事实查询 | D3-D4 | 准确数字 + SQL + 时效声明 |
| 趋势分析 | D4 | 时间序列 + 可视化 + 解释 |
| 交叉分析 | D4-D5 | 正确 join + 聚合 + 解释 |
| 报表生成 | D4-D5 | 格式合规 + 数据准确 |

## 表示模型

```text
SchemaSnapshot、ColumnDescription、MetricDefinition、
BusinessGlossary、QueryResult、DataLineage、FreshnessTimestamp
```

核心原则：**Semantic Layer 是核心**。没有 metric definition，LLM 就是在猜 SQL。

## 品类特有设计决策

| 决策 | 默认 |
|---|---|
| 语义层 | 必须有 semantic layer / metric definition |
| SQL 安全 | 只读；大结果集限制；超时控制 |
| 可追溯 | 每个数字 → SQL → 表 → 列 → 刷新时间 |
| 成本 | 大查询预估成本；缓存常见结果 |

## 参考实现

| 参考 | 学习点 |
|---|---|
| Databricks AI/BI Genie | 企业级 agentic analytics |
| Snowflake Cortex Analyst | semantic model + 90% 准确率 |
| LinkedIn Text-to-SQL | 百万表级 knowledge graph |
| Vanna AI | 开源 RAG Text-to-SQL |

## 延伸：主观性任务的验证

本品类的部分任务涉及主观判断，标准效果验证可能不够：

- `../../concepts/beyond-verification.md` — 超越 postcondition 的验证方式
- `../../evaluation/subjective-eval.md` — 主观性任务的评估框架
