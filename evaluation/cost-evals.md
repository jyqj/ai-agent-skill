# Cost Evaluations

> **Evidence Status** — synthesized. Cost Plane、benchmarking、model routing 与可执行 eval 的需求。

## 目标

把成本工程从“账单复盘”变成可回归的评估对象。

## 评估问题

```text
1. 哪种 routing 更省，但不明显伤害 verified success？
2. retrieval/verification 的边际收益在哪里开始递减？
3. 缓存是否真的带来成本和延迟优势？
4. 多 agent / worker fanout 什么时候开始不划算？
```

## 指标

| 指标 | 含义 |
|---|---|
| Cost per Completed Task | 完成任务的平均成本 |
| Cost per Verified Task | 带验证完成的平均成本 |
| Tail Cost | 成本尾部风险 |
| Latency | 平均与尾时延 |
| Token Efficiency | 每单位 token 带来的 verified gain |
| Tool Efficiency | 每个 tool call 的边际收益 |

## 推荐实验

### Model Routing

- single-tier
- tiered routing
- difficulty-aware routing

### Retrieval Budget

- low fanout
- medium fanout
- high fanout

### Verification Depth

- minimal
- standard
- critical

## 读法

成本图最好和 success / verified success 一起看：

```text
便宜但经常假完成
≠
真正更优
```

## 关联文档

- `../architecture/planes/cost/benchmarking.md`
- `execution-depth-evals.md`
- `tool-use-evals.md`
