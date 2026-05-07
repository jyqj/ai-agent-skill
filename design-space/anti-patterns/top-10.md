# Top 10 Agent Architecture Anti-Patterns

> **Evidence Status** — synthesized. 本目录反模式、failure taxonomy、module boundaries、security/effects/memory/context 文档，以及 coding/research/workflow/browser 等品类中的失败模式综合。

## 总览

| # | 反模式 | 核心误区 | 真实案例 | 修复入口 |
|---:|---|---|---|---|
| 1 | God Prompt | 用一个巨大 prompt 承担所有架构责任 | — | `god-prompt.md` |
| 2 | Tool Soup | 工具很多但没有风险、权限、postcondition | Step Finance 4,000 万美元损失（Agent 过度授权工具访问）；PocketOS 9 秒删库（未限制破坏性工具权限） | `tool-soup.md` |
| 3 | Tool Success = Done / Depth Without Verification | 工具成功或步骤很多就声称完成 | PocketOS（`rm` 返回成功 = Agent 认为任务完成，实际删除了生产数据库和备份） | `depth-without-verification.md` |
| 4 | Memory as Database | 用长期记忆当当前现实 | Agent 记忆投毒 84.3% 成功率（MINJA/MemoryGraft 攻击：污染长期记忆后 Agent 持续做出错误决策） | `memory-as-database.md` |
| 5 | Context as State | 用当前上下文当任务状态 | — | `context-as-state.md` |
| 6 | Trust Everything | 外部数据、工具输出、记忆和指令混 lane | Copilot RCE（CVE-2025-53773：Prompt Injection 实现远程代码执行）；Cursor 大小写绕过（CVE-2025-59944：.ts/.TS 路径大小写绕过文件保护） | `trust-everything.md` |
| 7 | Infinite Retry | 失败后无新证据地重复 | $47K 多 Agent 循环失控（token 预算告警未阻断执行，Agent 无新证据持续重试直到耗尽 $47,000） | `infinite-retry.md` |
| 8 | Approval-only Interaction | 把人机交互简化为同意/拒绝 | — | `approval-only-interaction.md` |
| 9 | Hidden Cost Explosion | 长上下文、多 worker、重复检索导致成本失控 | $47K 多 Agent 循环失控（多 Agent 互相触发导致 token 消耗失控） | `hidden-cost-explosion.md` |
| 10 | Eval Theater | 有 rubric 但没有可执行 trace/effect eval | — | `eval-theater.md` |

## 使用方式

设计评审时，先问三件事：

```text
这个 Agent 的完成定义是什么？
哪些状态是可回查、可验证、可恢复的？
如果失败，trace 能不能说明失败发生在哪里？
```

如果答案依赖“模型应该会理解”“用户可以自己检查”“工具返回成功”，通常已经落入反模式。

## 对应的正向结构

| 反模式 | 正向结构 |
|---|---|
| God Prompt | PromptContract + Policy + ToolSpec + ContextPack |
| Tool Soup | Tool Registry + CapabilityGrant + EffectRecord |
| Depth Without Verification | Verification Gate + Stop Gate |
| Memory as Database | Memory / WorldState / TaskState 分离 |
| Context as State | Checkpoint + Trace + ContextPack 可重建 |
| Trust Everything | Trust lanes + sanitization + untrusted context boundary |
| Infinite Retry | FailureRecord + recovery budget |
| Approval-only Interaction | Interaction Plane + progressive disclosure |
| Hidden Cost Explosion | ResourcePlan + routing + cache + budget gate |
| Eval Theater | executable fixtures + trace comparator + mock world |
