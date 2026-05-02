# Agent Capability Map

> **Evidence Status** — synthesized. 跨项目观察归纳。

| 能力域 | 能力 | 对应模块 |
|---|---|---|
| 感知 | 用户输入、外部事件、文件、网页、API、传感器 | Interface, Representation, Tools |
| 表示 | 解析、结构化、压缩、置信度、freshness、trust tier | Representation, Context |
| 推理 | 意图识别、计划、风险判断、反思、综合 | Kernel, Control, Context |
| 执行深度 | 深度选择、里程碑门控、预算控制、恢复路由 | Execution Depth, State, Recovery |
| 行动 | 工具调用、文件编辑、代码执行、外部写入 | Tools, Execution, Control, Identity |
| 世界建模 | 外部对象快照、冲突检测、时效管理 | World State, Effects |
| 效果闭环 | postcondition、read-after-write、补偿 | Effects, Control |
| 记忆 | 工作 / 会话 / 长期 / 技能记忆、审计 | Context, Memory, State |
| 安全 | 混合纵深防御、Policy Engine、Guard Model、注入防护、租户隔离、身份边界 | Security, Control, Identity & Capability |
| 协作 | 子代理、Worker、Contract Agent、A2A/MCP 协议、多窗口、合并 | Orchestration, State |
| 学习 | 技能提炼、eval 反馈、记忆整合（Formation/Evolution/Retrieval）、失效治理 | Learning & Adaptation, Memory, Evaluation |
| 运维 | 配置追踪、回归、灰度、事故处理、AgentOps 指标分层 | Operations, Observability |
| 评估 | 轨迹评估（6维）、最终结果评估、Agent-as-Judge、trajectory replay | Evaluation, Observability |

## 深执行能力链

```text
Observe → Represent → Plan → Gate Identity/Policy → Execute → Verify Effect → Recover / Deliver
```
