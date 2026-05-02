# Data / BI Agent Action Model

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

| 动作 | 风险 | Precondition | Verification |
|---|---|---|---|
| Schema 检索 | safe | DB 可达 | 非空 |
| SQL 生成 | check | schema+metric 已加载 | EXPLAIN dry-run |
| SQL 执行 | check | 只读+超时 | 行数合理 |
| 结果解释 | safe | 非空结果 | 解释与数据一致 |
| 可视化 | safe | 数据适合 | 渲染正确 |

## SQL 安全

- **只读。** 无 INSERT/UPDATE/DELETE。
- **LIMIT 1000 默认。** 大结果需确认。
- **30s 超时。** 大查询预估成本。
- **禁止动态拼接。** 防 SQL 注入。
- **PII 自动脱敏。**
