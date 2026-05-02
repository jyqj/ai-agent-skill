# Trust Escalation

> **Evidence Status** — synthesized. Autonomy Level、approval policy、memory feedback 的共同需求。

## 1. 渐进信任模型

Agent 不应一开始就拿到最高自治。信任应基于历史效果、验证能力、用户纠错和风险范围逐步升级。

| 阶段 | 能力 | 升级条件 |
|---|---|---|
| Observe | 只读、建议 | 用户接受建议、claim 准确 |
| Prepare | 准备动作但不执行 | 参数正确、风险说明清楚 |
| Execute with Approval | 每个高风险动作审批 | 多次 verified effect，无越权 |
| Execute within Policy | 策略内自动执行 | policy 明确、rollback 可用、trace 稳定 |
| Continuous Autonomy | 持续运行 | 有监控、预算、事故接管、回归测试 |

## 2. 信任下降

| 事件 | 降级 |
|---|---|
| 错误对象写入 | 降到逐步审批 |
| 未验证却声称完成 | 强制 verification gate |
| 用户多次纠错同类问题 | 触发 teaching / memory review |
| 成本超支 | 强制 budget_choice |
| 安全边界触发 | 暂停相关工具 |

## 3. 授权范围

授权必须绑定：

```text
工具范围
对象范围
动作类型
时间范围
成本范围
撤销能力
验证方式
```
