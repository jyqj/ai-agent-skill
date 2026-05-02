# Design Checklist

> **Evidence Status** — synthesized. 各品类架构、plane 文档、反模式和 eval fixture 中反复出现的设计遗漏点；用于 Agent 架构评审。


## 1. 产品层

```text
[ ] 是否定义了用户的 Job to be Done？
[ ] 是否定义了交付物（不只是对话）？
[ ] 是否为不同 intent 设置了 required_depth？
[ ] 是否区分了 autonomy level 和 execution depth？
[ ] 是否定义了任务完成证据？
[ ] 是否选择了正确的模块组合（而非全部模块）？
[ ] 是否标注了复杂度等级 C0-C6？
[ ] 是否写下重大取舍的 ADR？
```

## 2. 表示层

```text
[ ] 是否保留 raw_ref？
[ ] 是否记录 transform_chain？
[ ] 是否标注 confidence、freshness、source_authority？
[ ] 是否区分事实、摘要、推断、记忆、指令？
[ ] 摘要 / OCR / ASR / 截断是否标记为有损？
[ ] 关键结论是否可回查原始材料？
```

## 3. 执行深度

```text
[ ] 是否有 Depth Controller？
[ ] 是否有结构化 Task Graph / Milestone？
[ ] 每个 milestone 是否有退出条件和验证方法？
[ ] 是否有多维 Depth Budget？
[ ] 是否有 Recovery Loop（不只是简单重试）？
[ ] retry 是否要求新证据、参数变化或 world state refresh？
[ ] 是否把 effect verification 纳入 stop gate？
```

## 4. 上下文

```text
[ ] 是否有 Compaction 策略？
[ ] Compaction 后是否保留 goal、constraints、failed_attempts？
[ ] 大工具输出是否 offload 到文件？
[ ] 是否有 milestone 级别的 Context Pack？
[ ] 是否区分 trusted lane 与 untrusted lane？
```

## 5. 记忆

```text
[ ] 记忆是否分层？
[ ] 写入是否有 provenance？
[ ] 敏感记忆是否需要确认？
[ ] 删除是否等于物理删除 + 不再推理？
[ ] 是否有记忆审计和失效策略？
[ ] 学习/技能候选是否经过 eval 或 replay 验证？
```

## 6. 工具与执行

```text
[ ] 每个工具是否有 input/output schema？
[ ] 是否声明 preconditions / postconditions / reversibility？
[ ] 工具结果是否包含 failure_mode + recoverable？
[ ] 高风险工具是否有审批策略？
[ ] 写动作是否默认 read-after-write？
[ ] 是否区分 execution success 与 effect success？
```

## 7. 世界状态与效果

```text
[ ] 是否显式建模 world state？
[ ] world state 是否有 observed_at / ttl / stale policy？
[ ] 是否记录 effect ledger？
[ ] 最终交付前是否验证关键外部状态？
[ ] 不可逆动作是否有审批和补偿策略？
```

## 8. 控制与安全

```text
[ ] 权限是否集中在 Control Policy？
[ ] 是否根据风险等级分级审批？
[ ] 是否有 Verification Gate？
[ ] 是否有 Loop Detection？
[ ] 是否区分 instruction / trusted data / untrusted data / memory / inference？
[ ] 是否处理 tool output injection / memory poisoning / MCP trust boundary？
[ ] 是否区分用户身份、Agent 身份、工具身份和第三方 server 身份？
[ ] 高风险动作是否有 CapabilityGrant 和 AuditContext？
[ ] 是否采用混合纵深防御（Policy Engine + Guard Model + Model Hardening + Assurance）？
[ ] Guard Model 是否独立于主模型部署（避免同时被注入攻击）？
[ ] Agent 是否被防止自我提权（权限动态对齐意图，不能自我升级）？
[ ] 是否有持续性安全验证（regression testing + variant analysis + red team）？
```

## 9. 编排与状态

```text
[ ] Worker 是否有 Output Contract？
[ ] 是否限制 Branch Budget？
[ ] 是否定义 Merge Strategy？
[ ] Task State 是否与 World State 分离？
[ ] Checkpoint 是否可恢复？
[ ] 恢复后是否验证环境一致性和 stale world refs？
[ ] 高 stakes 任务是否使用 Contract 模式（明确验收标准、可协商、子契约可拆分）？
[ ] 跨组织 Agent 协作是否有标准协议（A2A / MCP / AP2）？
```

## 10. 评估与运维

```text
[ ] 是否有 representation quality 指标？
[ ] 是否有 effect verification 指标？
[ ] 是否有失败注入测试？
[ ] 是否有安全评估集？
[ ] model / prompt / tool schema / policy 是否有配置指纹？
[ ] 是否有 eval regression、canary rollout、incident trace？
[ ] 是否有轨迹评估（precision/recall/order match/tool coverage）？
[ ] 是否有 AgentOps 指标分层（北极星→目标完成→关键步骤→遥测→人类反馈→trace）？
```

## 11. 交付

```text
[ ] 最终输出是否说明做了什么？
[ ] 是否说明依据哪些表示 / 证据？
[ ] 是否说明验证了什么效果？
[ ] 是否说明失败和恢复？
[ ] 未验证、部分验证或验证不可达是否明确标注？
[ ] 是否说明剩余风险和下一步？
```


## Human-Agent Interaction

```text
[ ] 是否定义何时中断用户？
[ ] 审批请求是否说明动作、对象、影响、可撤销性和默认安全行为？
[ ] 用户纠错是否进入 Task State 或 Memory proposal？
[ ] 是否有进度报告策略，而不是每一步刷屏？
[ ] Agent 拒绝或降级时是否说明边界和替代方案？
```

## Cost & Resource

```text
[ ] 是否有 ResourcePlan？
[ ] 模型路由是否区分 plan / act / verify / summarize？
[ ] token 预算是否保留输出、工具和验证空间？
[ ] OCR / embedding / read-only tool result 是否有缓存策略？
[ ] 成本接近阈值时是否触发 budget_choice？
```

## Multi-Agent / Concurrency / Dataflow

```text
[ ] 多 Agent 是否使用 AgentMessage，而不是自由文本委派？
[ ] 子 Agent 输出是否有 OutputContract 和 evidence_refs？
[ ] 共享 World State 是否有冲突记录和仲裁机制？
[ ] 并发工具调用是否有上限、取消和超时语义？
[ ] 批量/流式任务是否有 backpressure 和错误传播策略？
```

## Prompting & Testability

```text
[ ] PromptContract 是否与 ContextPack 分离？
[ ] few-shot 示例是否有 applies_when / do_not_use_when？
[ ] 推理模式是否按任务选择，而不是固定一种？
[ ] 是否能 mock 外部世界并重放 trace？
[ ] 是否有 property-based invariants 和 shadow mode regression？
```


## Identity & Capability

```text
[ ] 是否定义 actor_user、agent_id、tenant_id、tool_id？
[ ] CapabilityGrant 是否包含资源、动作、约束、期限和撤销条件？
[ ] 第三方工具/MCP 的 declared capability 是否不会自动扩展为本地权限？
[ ] 审计记录能否回答 who/what/when/why/result？
```

## Recovery & Partial Delivery

```text
[ ] 每类失败是否有 FailureRecord category？
[ ] 是否定义 retry_budget、same_action_retry_limit 和 requires_new_evidence？
[ ] 部分效果是否有 compensation 或 rollback plan？
[ ] budget exhausted 时是否能 checkpoint + partial deliver？
[ ] 不可验证效果是否通过 human_confirm/external_ack 或明确声明 pending？
```

## Data Flow & Coupling

```text
[ ] 关键对象是否符合单一事实来源？
[ ] ContextPack 是否可重建，而不是唯一状态？
[ ] plane 间依赖是否符合 plane-interaction-matrix？
[ ] 强耦合链路是否有 schema contract？
[ ] 禁止耦合是否被 tests / policy 防住？
```

相关文件：`../architecture/complexity-levels.md`、`../architecture/plane-interaction-matrix.md`、`../architecture/runtime-data-flow.md`、`../architecture/adrs/adr-template.md`。
