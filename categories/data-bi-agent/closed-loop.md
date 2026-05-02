# Data / BI Agent Closed Loop

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

## 核心循环

```text
1. Observe: 接收自然语言问题
2. Represent: 加载 schema + metric + glossary
3. Decide: 识别表/列 → 生成 SQL → 自检
4. Act: 执行 SQL（只读）
5. Verify: 合理性检查 + 时效声明 + 可选交叉验证
6. Deliver: 结果 + SQL + 口径 + 时效
```

## SQL 自检

```text
生成 → EXPLAIN（无全表扫描）→ WHERE 匹配意图
→ GROUP BY 与聚合一致 → JOIN 条件正确
```

## 结果合理性

```text
行数在预期范围 → 数值在业务范围 → 汇总=明细之和 → 时间范围匹配
```
