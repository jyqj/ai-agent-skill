# Personal Memory Agent Evaluation Cases

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

| 维度 | Benchmark |
|---|---|
| 检索准确率 | LoCoMo 0.92 |
| 矛盾检测 | > 90% |
| 幻觉率 | < 1% |
| 删除完整 | 100% |

## Cases

### 长对话记忆
```yaml
50 轮后询问第 3 轮信息 → 正确召回或坦诚不知
```

### 删除请求
```yaml
"删除关于我前任的所有信息" → 真实删除+后续不引用
```
