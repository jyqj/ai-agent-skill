# Representation and Effect Boundaries

> **Evidence Status** — synthesized. 从 coding、research、workflow、browser、ops、memory 等品类的项目中归纳的输入表示、动作接口和验证方式差异。

## 核心观察

不同品类的 Agent 之间，关键差异在于三个东西：

1. **它依赖什么表示进入系统** — 代码文件、网页 DOM、CRM 记录、告警日志？
2. **它通过什么接口作用于世界** — 编辑代码、点击按钮、调用 API、回滚部署？
3. **它如何验证效果** — 跑测试、回读截图、检查健康状态、核对引用链？

这三个方面决定了品类的难点分布。理解它们，比列举工具清单更能指导架构选择。

## 跨品类对比

| 品类 | 关键输入表示 | 关键动作 | 关键验证 |
|---|---|---|---|
| Coding Agent | 代码、测试日志、git 状态 | edit / run / diff | test + diff + readback |
| Research Agent | 网页、PDF、表格、来源评级 | 搜索 / 阅读 / 报告 | claim verification（断言可溯源） |
| Enterprise Workflow | ticket、CRM、审批状态 | update / notify / advance flow | read-after-write + audit |
| Browser/Desktop Agent | DOM、截图、UI state | click / type / navigate | DOM + screenshot + backend |
| Ops/SRE Agent | alert、metric、log、deploy state | ack / rollout / rollback | health check + metric recovery |

## 难点分布

从这张表可以看出一个规律：难点随品类集中在不同方面。

**Research Agent** 几乎不改变外部世界，effect verification 的压力很小；核心挑战落在表示质量和断言验证上——来源是否可信、摘要是否忠于原文、结论是否有证据支撑。典型场景：Agent 引用了一篇论文的结论，但原文实际说的是"在特定条件下成立"，摘要丢失了限定条件。

相比之下，**Workflow / Ops / Browser Agent** 的表示层相对标准化（ticket、DOM、metric 都有明确 schema），真正的难点在于效果验证和世界状态新鲜度：动作执行了，外部世界是否真的变了？状态是否已经被别人改了？典型场景：Ops Agent 执行了 rollback 命令并收到 200，但上游 load balancer 缓存了旧版本，实际流量仍然打到故障实例。这些品类需要可靠的 read-after-write 和 stale state 防护。

**Coding Agent** 同时承受两端的压力——既要在庞大的 repo 中正确读取上下文（表示层），又要通过测试和 diff 验证修改效果（效果层）。典型场景：Agent 修复了一个函数的 bug，测试通过，但没有发现另一个模块通过 monkey-patch 依赖了旧行为，集成测试才暴露问题。这也是生产级 Coding Agent 架构复杂度通常最高的原因。

理解这个分布，可以避免一个常见错误：用 Research Agent 的架构去做 Workflow Agent，或者用 Coding Agent 的架构去做 Research Agent——它们的难点在不同的地方。
