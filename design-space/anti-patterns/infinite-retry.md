> **已合并**：本反模式的完整内容已合并至 `top-10.md`。以下内容保留为存档。

# Infinite Retry

> **Evidence Status** — synthesized. 本知识库中相关模块的失败模式总结。


## 定义

工具失败后重复相同动作，没有新证据、没有退避、没有终止条件。

## 典型表现

- 同一工具调用连续失败 3 次以上，每次参数完全相同；
- 日志中出现长串重复的 tool call → error → tool call 循环；
- Agent 没有尝试替代方案或降级策略，只是机械重试；
- 任务耗时远超预期但最终仍然失败。

## 风险

- token 成本随重试次数线性增长，单次任务费用不可预测。
- 相同错误反复触发，可能对外部系统产生副作用（如重复写入、重复请求触发限流）。
- 重试占满 context window，挤压后续有效推理空间。
- 用户等待时间无上限，体验严重退化。

## 修复

失败分类、retry budget、requires_new_evidence、human escalation。

## 评审问题

```text
这个设计的单一事实来源是什么？
失败时能否重放？
是否有明确的 gate、trace 和 stop condition？
```
