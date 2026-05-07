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
| Creative Agent | Representation, Context, Memory, Interface, Control, Interaction | Tools, Orchestration, Learning | D2-D4 | 风格漂移、版权侵权、创意枯竭、审美偏差、多模态不一致 | `../categories/creative-agent/README.md` |
| Data/BI Agent | Representation, Context, Tools, Control, World State, Observability, Cost | Memory, Orchestration, Operations | D4-D5 | SQL 注入、数据泄露、统计误导、语义歧义、查询失控 | `../categories/data-bi-agent/README.md` |
| Embodied Robot Agent | Representation, Tools, Control, State, World State, Effects, Observability, Depth Controller | Memory, Orchestration, Learning, Operations | D5-D6 | 物理伤害、传感器失效、Sim-to-Real 漂移、紧急停止失败、环境误判 | `../categories/embodied-robot-agent/README.md` |
| Financial Agent | Representation, Tools, Control, State, World State, Effects, Observability, Cost, Recovery, Depth Controller | Memory, Orchestration, Operations | D5-D6 | 未授权交易、滑点失控、合规违规、闪崩、肥手指 | `../categories/financial-agent/README.md` |
| Education Agent | Representation, Context, Memory, Interface, Control, Interaction | Tools, State, Orchestration, Learning | D2-D4 | 教授错误内容、难度不匹配、失去学习动力、评估偏差、隐私泄露 | `../categories/education-agent/README.md` |

## 使用方式

1. 先用 `../design-space/methodology/agent-product-model.md` 定义产品画布。
2. 再用本表确定默认模块组合。
3. 再进入品类入口补齐任务模型、表示模型、行动模型、闭环模型。
4. 最后用 `category-pattern-matrix.md` 选择横切模式。
