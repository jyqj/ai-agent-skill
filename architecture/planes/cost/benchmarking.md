# Cost Benchmarking

> **Evidence Status** — synthesized. model routing、tool预算、cache、verification 深度等成本控制需求，以及 evaluation 中的回归目标。

## 目标

Cost Plane 只有框架还不够，还需要 benchmark 方法，回答：

```text
哪种 routing / retrieval / verification 组合，在这个品类下最划算？
```

## Benchmark 维度

| 维度 | 说明 |
|---|---|
| Task Success | 是否完成目标 |
| Verified Success | 是否带验证证据完成 |
| Cost | 模型、工具、执行环境成本 |
| Latency | 总时延与关键路径时延 |
| Trace Size | 上下文和 artifact 规模 |
| Recovery Cost | 失败后补救成本 |

## 设计变量

| 变量 | 示例 |
|---|---|
| Model Routing | single-tier / tiered / difficulty-aware |
| Retrieval Budget | source fanout、read depth、refresh count |
| Verification Depth | lightweight vs full readback/test |
| Caching | observation / embedding / tool result cache |
| Orchestration | 单 agent、worker fanout、阶段合并 |

## 基准方法

```text
固定任务集
→ 固定 fixture / mock world /工具成本模型
→ 只改变一个控制变量
→ 同时记录 success、verified success、cost、latency
→ 绘制 quality-cost frontier
```

## 推荐输出

- 任务完成率曲线
- verified completion 率曲线
- 单任务平均成本和尾部成本
- retrieval / verification 的边际收益
- 失败类别分布

## 关联文档

- `overview.md`
- `../../../../evaluation/cost-evals.md`
- `../../../../design-space/anti-patterns/hidden-cost-explosion.md`
