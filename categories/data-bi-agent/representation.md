# Data / BI Agent Representation Model

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

## 核心表示对象

| 对象 | 含义 | Freshness | Trust |
|---|---|---|---|
| SchemaSnapshot | 表/列/类型/关系 | 每日更新 | high |
| ColumnDescription | 列业务含义 | 版本化 | config |
| MetricDefinition | 指标公式/口径/分母 | 版本化 | config（关键） |
| BusinessGlossary | 术语→schema 映射 | 版本化 | config |
| QueryResult | 查询结果 | 一次性 | 取决于源 |
| FreshnessTimestamp | 数据最后更新时间 | 每次查询 | high |

## 关键原则

- **Semantic Layer 是核心。** 没有 metric definition，LLM 就是在猜。
- **Schema 理解 > SQL 生成。** 80% 错误来自 schema 理解。
- **数据时效必须声明。**
- **结果可追溯到 SQL → 表 → 列 → 刷新时间。**
