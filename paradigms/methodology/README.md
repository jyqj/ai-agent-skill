# Methodology

> **Evidence Status** — synthesized. 汇总 Agent 设计方法论，作为从抽象范式落到具体产品/架构的工作台。


## 方法论入口

| 文档 | 作用 |
|---|---|
| `harness-engineering.md` | 解释 Model 之外的一切如何成为 Agent 能力上限 |
| `agent-product-model.md` | 用产品画布定义用户、交付物、外部对象、效果、评估 |
| `autonomy-and-depth.md` | 统一使用 L0-L5 自治等级与 D0-D6 执行深度 |
| `decision-frameworks.md` | 常见架构选择矩阵：何时用什么 |
| `minimum-viable-agent.md` | 从最小可用 Agent 到生产 Agent 的阶梯式路径 |
| `agent-economics.md` | Agent 经济学：采纳成本、价值公式、定价 |
| `performance-optimization.md` | 性能优化决策树、技术组合矩阵、AgentOps 体系 |

## 推荐使用顺序

```text
1. agent-product-model.md      定义 Agent 要完成什么 job
2. autonomy-and-depth.md       定义能自己做多少、要做到哪一步
3. reasoning/memory/tool/...   选择范式
4. decision-frameworks.md      检查模块组合和风险控制
5. minimum-viable-agent.md     决定最小起步版本和升级触发器
```
