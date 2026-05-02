# Token Budgeting

> **Evidence Status** — synthesized. Context compaction、tool-output offloading、progressive disclosure 等模式。

## 1. 预算分区

```text
System / Policy Instructions
Task Goal
Relevant Observations
Memory
World State
Tool Specs
Scratchpad / Working State
Output Budget
```

不要把所有 token 都给历史上下文。输出、工具参数和验证也需要预算。

## 2. 动态分配

| 场景 | 分配策略 |
|---|---|
| 规划阶段 | 更多 goal、constraints、world state |
| 执行阶段 | 更多 tool spec、current state、pre/postconditions |
| 验证阶段 | 更多 evidence、effect record、tests |
| 交互阶段 | 更多用户约束、风险说明、选项 |
| 恢复阶段 | 更多 failure history、新观察、retry constraints |

## 3. 预算失败处理

```text
context too large
  → offload raw tool output
  → compact non-critical history
  → keep raw refs
  → preserve constraints and open risks
  → disclose omitted_refs when relevant
```
