> **已合并**：本反模式的完整内容已合并至 `top-10.md`。以下内容保留为存档。

# Hidden Cost Explosion

> **Evidence Status** — synthesized. 本知识库中相关模块的失败模式总结。


## 定义

多 worker、长 context、重复检索、重复 OCR、强模型验证导致成本隐性爆炸。

## 典型表现

- 单次任务实际消耗 token 数是预期的 5-10 倍，但调用方无感知；
- 多个 worker 各自携带完整上下文并行运行，重复检索相同文档；
- 用 GPT-4 级别模型做格式校验、JSON 解析等低复杂度任务；
- 没有 token 计数或费用统计，月底账单才发现成本失控。

## 风险

- 单次任务费用不可预测，无法为用户或业务设置预算上限。
- 上下文膨胀和重复检索的成本随任务复杂度指数增长，而非线性增长。
- 成本反馈滞后（通常是月结账单），无法在运行时做出降级决策。
- 强模型被用于低价值子任务，性价比极低且占用 rate limit 配额。

## 修复

ResourcePlan + model routing + cache + cost gate。

## 评审问题

```text
这个设计的单一事实来源是什么？
失败时能否重放？
是否有明确的 gate、trace 和 stop condition？
```
