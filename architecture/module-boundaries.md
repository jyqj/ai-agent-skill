# Module Boundaries

> **Evidence Status** — synthesized. 参考项目中 context、memory、tools、execution、control、state、observability 等职责分离的实现经验；本知识库对常见 Agent 架构混淆点的统一边界定义。

## 1. 为什么边界重要

Agent 失败的常见根因是边界混乱：

```text
摘要被当成事实
工具返回被当成效果
上下文被当成记忆
任务状态被当成世界状态
审批被当成交互全部
多 Agent 消息被当作可信事实
成本日志被当作成本控制
外部网页文本被当成系统指令
第三方 capability 被当成本地授权
工具失败后靠无限 retry 伪装恢复
```

## 2. 核心边界表

| 边界 | A 是什么 | B 是什么 | 常见错误 | 修复 |
|---|---|---|---|---|
| Interface vs Representation | 接收事件和原始输入 | 解释、转换、标注输入 | 入口直接塞 prompt | 先生成 Observation |
| Representation vs Context | 稳定表示资产 | 当前模型窗口 | 把 Context 当事实库 | ContextPack 引用 Observation |
| Prompting vs Context | 指令结构和输出契约 | 当前可见数据 | 把所有规则塞上下文 | PromptContract 与 ContextPack 分离 |
| Context vs Memory | 当前注意力预算 | 跨任务持久知识 | 把全部记忆塞进上下文 | 检索、分层、披露 |
| Memory vs World State | 长期知识/偏好 | 外部对象当前快照 | 用旧记忆判断当前现实 | 写前刷新 World State |
| Task State vs World State | 任务进度 | 外部对象状态 | checkpoint 说完成就认为外部完成 | readback 验证 |
| Tool Runtime vs Execution Host | 工具 schema/路由/权限 | 实际命令/API/进程 | 工具层直接拼命令 | Execution Host 隔离 |
| Execution Result vs Effect Record | 执行返回 | 现实效果验证 | success 直接 final | 记录 intended/actual/postcondition |
| Approval vs Interaction | 高风险授权 | 全部人机协作 | 只在危险时打扰用户 | 设计进度、纠错、教学、拒绝解释 |
| Orchestration vs Concurrency | 任务分工和协议 | 并发调度与取消 | spawn 多 worker 但无取消语义 | 分离 AgentMessage 与 CancellationToken |
| Control vs Security | 授权、审批、停止门 | 信任边界、注入、秘密 | 权限通过就忽略注入 | 双重 gate |
| Identity vs Capability | 谁发起 / 谁被代理 | 被授权做什么 | 用户消息直接等于授权 | CapabilityGrant + AuditContext |
| Failure vs Recovery | 失败事实 | 恢复策略 | 错误后原样重试 | FailureRecord + recovery budget |
| Observability vs Operations | 记录和看见 | 发布、回归、事故 | 只有日志没有行动 | trace 驱动运维流程 |
| Eval vs Testability | 评分标准 | mock、replay、shadow、property tests | 有 rubric 无自动化 | 建 eval runner 和 fixture |
| Learning vs Memory | 提炼可复用能力 | 存储事实/偏好/技能 | 自动固化偶然成功 | skill eval + rollback |

## 3. 模块职责矩阵

| 模块 | 负责 | 不负责 | 写入对象 |
|---|---|---|---|
| Interface | 接入渠道、身份、权限上下文、raw refs | 解释事实、决策动作 | RawInputRef、PerceptionEvent |
| Representation | 解析、规范化、置信度、时效、trust lane | 选择行动、写外部系统 | Observation |
| Prompting | 指令结构、few-shot、推理模式、输出契约 | 装载全部事实 | PromptContract |
| Context | 装配当前模型输入、压缩、披露 | 长期存储事实 | ContextPack |
| Memory | 跨任务记忆、provenance、失效 | 当前世界真相 | MemoryRecord |
| Kernel | 决策下一步、规划、恢复 | 绕过工具执行 | Decision |
| Tools | 工具 schema、路由、结果标准化 | 高风险审批最终决定 | ToolCall |
| Execution | 沙箱、进程、API 调用、超时 | 解释任务是否完成 | ExecutionResult |
| Effects | intended/actual/postcondition、补偿 | 选择业务目标 | EffectRecord |
| Interaction | 中断、审批、进度、教学、纠错、拒绝解释 | 代替策略判断 | InteractionEvent |
| Orchestration | Agent 间协议、拓扑、共享状态、仲裁 | 底层并发实现 | AgentMessage、ArbitrationDecision |
| Concurrency | 并发限制、取消、超时、事件排序 | 业务分工 | CancellationToken、ConcurrencyEvent |
| Dataflow | 批量、流式、管道、回压 | 单步决策 | FlowRun、BatchRecord |
| Control | policy、approval、verification、stop gate | 防所有信息攻击 | PolicyVerdict、VerificationResult |
| Security | trust lane、注入防护、secret、隔离 | 业务审批 | SecurityVerdict |
| Identity & Capability | 身份、租户、委托链、能力范围 | 判定所有安全攻击 | CapabilityGrant、AuditContext |
| Recovery | 错误分类、恢复、补偿、部分交付 | 掩盖失败或伪造成功 | FailureRecord、RecoveryAction |
| Cost | 模型路由、预算、缓存、成本质量 tradeoff | 评判业务正确性 | ResourcePlan、CostTrace |
| State | checkpoint、plan、失败记录 | 外部对象事实 | TaskCheckpoint |
| World State | 外部对象快照、freshness、冲突 | 任务计划 | WorldStateSnapshot |
| Observability | trace、指标、成本、eval event | 修改业务流程 | TraceEvent |
| Operations | 配置指纹、canary、rollback、incident | 单步推理 | ConfigFingerprint、IncidentReport |
| Learning | skill 提炼、经验固化、反馈 | 未验证自动激活 | CandidateRecord |

## 4. 边界评审问题

```text
这个模块写入的对象是什么？
这个对象是否 append-only 或可重建？
消费者是否能回查生产者和原始证据？
高风险动作经过了哪几个 gate？
谁授权 Agent 做这个动作，授权范围是什么？
失败后是 retry、refresh、compensate、ask user 还是 stop？
工具成功和效果成功在哪里分离？
用户交互何时改变任务状态或长期记忆？
多 Agent 消息是否有 evidence_refs 和 authority_scope？
并发任务是否有取消、超时、回压和事件排序？
成本预算是否影响策略，而不只是事后统计？
最终回答中的 claim 指向哪些 observation / effect record？
```


更多 plane 读写关系见 `plane-interaction-matrix.md`。
