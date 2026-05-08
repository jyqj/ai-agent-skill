> **已合并**：本反模式的完整内容已合并至 `top-10.md`。以下内容保留为存档。

# Eval Theater

> **Evidence Status** — synthesized. Agent 项目常把 rubric、人工主观评分或 demo success 当成评估闭环，但缺少 mock world、trace replay、failure fixture 和可执行断言。

## 定义

看起来有评估，实际上无法捕捉关键失败：工具是否越权、效果是否验证、引用是否可回查、失败是否恢复、成本是否失控。

## 典型表现

- 只有“回答质量 1-5 分”，没有外部效果断言；
- 没有失败注入和 replay；
- eval 不读取 trace，只看最终文本；
- 安全、成本、恢复没有指标；
- demo 通过后进入生产。

## 风险

Agent 最危险的失败常发生在最终回答之外：工具链、权限、world state、effect verification、memory write、recovery。Eval Theater 会让系统在上线后才暴露这些问题。

## 修复

- 建 `evaluation/fixtures/`，覆盖正常、失败、攻击和过期状态；
- 使用 trace comparator 检查必备事件；
- 对写动作检查 EffectRecord；
- 对高风险动作检查 policy / approval / blocked；
- 对失败检查 RecoveryAction；
- 从真实失败提炼 regression fixture。

## 评审问题

```text
这个 eval 是否能在没有真实外部系统时运行？
它检查的是最终文本，还是完整 trace？
它能否捕捉工具成功但效果失败？
```
