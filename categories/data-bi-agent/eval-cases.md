# Data / BI Agent Evaluation Cases

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

## 维度

| 维度 | 指标 | Benchmark |
|---|---|---|
| SQL 准确率 | 语义正确/总查询 | BIRD ~92% |
| 口径一致性 | 与定义一致/涉及指标 | 100% |
| 时效声明率 | 有声明/总结果 | 100% |

## Cases

### Case 1: 跨表 join
```yaml
scenario: "上月华东 VIP 客户平均订单金额"
assertions: join 正确、区域定义一致、VIP 定义一致、时间正确
```

### Case 2: 口径歧义
```yaml
scenario: "转化率是多少"（有多个定义）
assertions: 识别歧义、使用默认+声明口径
```

### Case 3: 数据时效
```yaml
scenario: "今天销售额"（数据 T+1）
assertions: 告知数据截止时间、不编造
```
