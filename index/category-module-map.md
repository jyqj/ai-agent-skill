# Product to Module Map

> **Evidence Status** — synthesized. 跨项目观察归纳。

| 产品 | 必备模块 | 可选模块 | 默认深度 | 重点风险 | 品类入口 |
|---|---|---|---|---|---|
| Coding Agent | Representation, Context, Tools, Execution, Control, State, World State, Effects, Observability, Depth Controller | Memory, Orchestration, Learning, Operations (Warp 证明 Operations 对 agent-driven 项目很关键) | D5 | 误改代码、危险命令、未验证效果 | `../categories/coding-agent/README.md` |
| Research Agent | Representation, Context, Tools, Control, Observability, Cost, Interaction | Memory, Orchestration, State, Operations | D4-D5 | citation drift、来源不可信、freshness blindness、冲突被抹平 | `../categories/research-agent/README.md` |
| Personal Memory Agent | Representation, Memory, Context, Control, Observability, State | Tools, World State, Learning | D3-D4 | 记忆污染、隐私、错误用户建模 | `../categories/personal-memory-agent.md` |
| Enterprise Workflow Agent | Interface, Representation, Tools, Control, State, World State, Effects, Observability, Depth Controller | Orchestration, Memory, Operations | D4-D5 | 越权、错误执行、审计缺失、状态过期 | `../categories/enterprise-workflow-agent.md` |
| Browser/Desktop Agent | Interface, Representation, Tools, Control, World State, Effects, Observability | Memory, Orchestration, Operations | D5 | DOM/截图不一致、坐标漂移、点击成功但任务失败 | `../categories/browser-desktop-agent.md` |
| Ops/SRE Agent | Interface, Representation, Tools, Control, State, World State, Effects, Observability, Operations | Orchestration, Memory | D5-D6 | 误报、误操作、回滚失败 | `../categories/ops-sre-agent.md` |
| Security Agent | Representation, Tools, Control, Observability, Operations | Memory, Orchestration | D4-D5 | 漏洞误判、越权扫描、secret 泄露 | `../categories/security-agent.md` |
| Companion Agent | Representation, Context, Memory, Interface, Control | Tools, State, Orchestration | D2-D4 | 角色漂移、越界建议、记忆泄露 | `../categories/companion-agent.md` |
| Agent Platform | 全部模块 | Marketplace, Distributed Execution | D5-D6 | 插件安全、权限、稳定性、回归 | `../categories/agent-platform.md` |

## 使用方式

1. 先用 `../paradigms/methodology/agent-product-model.md` 定义产品画布。
2. 再用本表确定默认模块组合。
3. 再进入品类入口补齐任务模型、表示模型、行动模型、闭环模型。
4. 最后用 `category-pattern-matrix.md` 选择横切模式。
