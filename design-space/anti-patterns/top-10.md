# Top 10 Agent Architecture Anti-Patterns

> **Evidence Status** — synthesized. 本目录反模式、failure taxonomy、module boundaries、security/effects/memory/context 文档，以及 coding/research/workflow/browser 等品类中的失败模式综合。

## 总览

| # | 反模式 | 核心误区 | 真实案例 | 修复入口 |
|---:|---|---|---|---|
| 1 | God Prompt | 用一个巨大 prompt 承担所有架构责任 | — | [#1](#1-god-prompt) |
| 2 | Tool Soup | 工具很多但没有风险、权限、postcondition | Step Finance 4,000 万美元损失（Agent 过度授权工具访问）；PocketOS 9 秒删库（未限制破坏性工具权限） | [#2](#2-tool-soup) |
| 3 | Depth Without Verification | 工具成功或步骤很多就声称完成 | PocketOS（`rm` 返回成功 = Agent 认为任务完成，实际删除了生产数据库和备份） | [#3](#3-depth-without-verification) |
| 4 | Memory as Database | 用长期记忆当当前现实 | Agent 记忆投毒 84.3% 成功率（MINJA/MemoryGraft 攻击：污染长期记忆后 Agent 持续做出错误决策） | [#4](#4-memory-as-database) |
| 5 | Context as State | 用当前上下文当任务状态 | — | [#5](#5-context-as-state) |
| 6 | Trust Everything | 外部数据、工具输出、记忆和指令混 lane | Copilot RCE（CVE-2025-53773：Prompt Injection 实现远程代码执行）；Cursor 大小写绕过（CVE-2025-59944：.ts/.TS 路径大小写绕过文件保护） | [#6](#6-trust-everything) |
| 7 | Infinite Retry | 失败后无新证据地重复 | $47K 多 Agent 循环失控（token 预算告警未阻断执行，Agent 无新证据持续重试直到耗尽 $47,000） | [#7](#7-infinite-retry) |
| 8 | Approval-only Interaction | 把人机交互简化为同意/拒绝 | — | [#8](#8-approval-only-interaction) |
| 9 | Hidden Cost Explosion | 长上下文、多 worker、重复检索导致成本失控 | $47K 多 Agent 循环失控（多 Agent 互相触发导致 token 消耗失控） | [#9](#9-hidden-cost-explosion) |
| 10 | Eval Theater | 有 rubric 但没有可执行 trace/effect eval | — | [#10](#10-eval-theater) |

## 使用方式

设计评审时，先问三件事：

```text
这个 Agent 的完成定义是什么？
哪些状态是可回查、可验证、可恢复的？
如果失败，trace 能不能说明失败发生在哪里？
```

如果答案依赖"模型应该会理解""用户可以自己检查""工具返回成功"，通常已经落入反模式。

---

## 1. God Prompt

**定义**：把所有系统规则、工具说明、策略、安全边界、输出格式都塞进一个巨大 system prompt。

**症状**：
- system prompt 超过数千 token，包含角色设定、工具列表、输出格式、安全规则、业务逻辑等所有内容
- 修改一条安全策略需要在一整段文本中定位并手动编辑
- 不同规则之间出现矛盾（如"永远不要拒绝用户"与"禁止执行危险操作"同时存在）
- 新增功能只能往 prompt 末尾追加段落

**风险**：
- prompt 膨胀导致指令之间相互冲突，模型选择性遗忘尾部或中部规则
- 行为异常时无法定位是哪条规则被忽略或被覆盖，调试成本极高
- 单一 prompt 无法按场景动态加载，所有任务都承担全量指令的上下文开销
- 版本管理困难：一次改动可能无意间影响多个不相关的行为

**修复入口**：PromptContract + Policy + Tool Spec + ContextPack + Security Gate 分离。

**评审问题**：
```text
这个设计的单一事实来源是什么？
失败时能否重放？
是否有明确的 gate、trace 和 stop condition？
```

---

## 2. Tool Soup

**定义**：接入大量工具，但没有路由、权限、风险、precondition、postcondition。

**症状**：
- 工具列表超过 20 个且全部在每次请求中注入 system prompt
- 工具描述之间存在功能重叠（如同时有 `search_web` 和 `google_search`），模型随机选择
- 没有根据任务类型动态加载工具子集
- 高风险工具（如 `execute_shell`）与低风险工具（如 `get_time`）共享同一权限级别

**风险**：
- 工具描述占满上下文窗口，挤压用户指令和推理空间
- 模型选错工具的概率随工具数量增加，尤其在功能描述相近时
- 无差别暴露所有工具导致攻击面扩大，低权限任务也能触发高危操作
- 工具间缺少 precondition/postcondition 约束，组合调用产生非预期副作用

**修复入口**：Tool Registry + Tool Router + Control Gate + Effect Ledger。

**评审问题**：
```text
这个设计的单一事实来源是什么？
失败时能否重放？
是否有明确的 gate、trace 和 stop condition？
```

---

## 3. Depth Without Verification

**定义**：执行很深、步骤很多，但没有测试、readback、postcondition。

**症状**：
- Agent 连续执行 10+ 步工具调用，中间没有任何断言或 readback
- 前序步骤返回空结果或错误码，后续步骤仍基于假设继续执行
- 最终输出看起来完整，但中间关键步骤实际已失败
- 调试时需要逐步回放整条链路才能定位首个出错点

**风险**：
- 多步执行中前序步骤的失败被后续步骤掩盖，最终错误与根因相距甚远
- 错误在链路中逐步放大：一个错误的中间结果被后续步骤当作正确输入反复引用
- 无法做部分重试，缺少 checkpoint 意味着任何修复都需要从头重跑
- 长链路的最终输出置信度无法评估，因为没有中间验证点提供证据

**修复入口**：把 execution depth 与 verification depth 绑定；Verification Gate + Stop Gate。

**评审问题**：
```text
这个设计的单一事实来源是什么？
失败时能否重放？
是否有明确的 gate、trace 和 stop condition？
```

---

## 4. Memory as Database

**定义**：把长期记忆当作当前事实库或强一致数据库使用。

**症状**：
- Agent 从记忆中读取"用户的 API key"或"当前服务器 IP"等实时数据
- 记忆条目没有时间戳或过期机制，三个月前的事实仍被当作当前状态
- 记忆写入没有去重，同一事实存在多个互相矛盾的版本
- 用记忆替代数据库查询来获取订单状态、账户余额等强一致性数据

**风险**：
- 过时信息污染决策：记忆中的旧数据被当作当前事实，导致行动基于错误前提
- 记忆无 ACID 保证，并发写入或部分写入导致不一致，且无法回滚
- 记忆检索依赖向量相似度，关键事实可能因 embedding 漂移而检索不到
- 数据量增长后记忆召回精度下降，错误条目被高置信度返回

**修复入口**：Memory 只存偏好/知识/经验；当前外部事实使用 World State。Memory / WorldState / TaskState 分离。

**评审问题**：
```text
这个设计的单一事实来源是什么？
失败时能否重放？
是否有明确的 gate、trace 和 stop condition？
```

---

## 5. Context as State

**定义**：把当前模型上下文当作任务状态库使用。计划、已完成步骤、用户约束、失败原因和外部对象状态只存在 prompt 或聊天历史里，没有 TaskCheckpoint、WorldStateSnapshot 或 TraceEvent。

**症状**：
- 上下文压缩后忘记已做过的步骤
- 中断恢复时从头开始
- 多 Agent 合并时不知道哪个步骤已验证
- 最终回答无法引用真实 checkpoint

**风险**：Context 是可丢弃、可压缩、可重建的注意力窗口。把它当 state，会让长任务不可恢复、不可审计、不可评估。

**修复入口**：
- 任务进度写入 `TaskCheckpoint`
- 外部对象状态写入 `WorldStateSnapshot`
- 写动作写入 `EffectRecord`
- 失败写入 `FailureRecord`
- ContextPack 只引用这些对象，不成为唯一事实来源

**评审问题**：
```text
如果当前 context 被清空，Agent 能否从 checkpoint 恢复？
最终回答中的"已完成"是否能回到 EffectRecord？
哪些信息只是当前注意力，哪些是持久状态？
```

---

## 6. Trust Everything

**定义**：网页、邮件、issue、tool output、memory、summary 全都放在同一可信上下文。

**症状**：
- 用户输入、网页内容、工具返回值、邮件正文共享同一信任级别
- 没有对 tool output 做 schema 校验或内容过滤
- prompt injection 载荷可以通过 issue 标题、网页摘要等路径进入决策流程
- Agent 直接执行从不可信来源提取的指令（如"请运行以下命令"）

**风险**：
- 不可信来源的指令被当作系统指令执行，prompt injection 无法防御
- 攻击面随接入数据源数量线性增长，任一来源被污染即可劫持 Agent 行为
- 无法区分"模型自己的判断"和"被外部内容诱导的判断"，事后审计无从入手
- 工具返回的恶意或畸形数据直接参与后续推理，导致级联错误

**修复入口**：Trust lanes + tool-output sanitization + untrusted context boundary。

**评审问题**：
```text
这个设计的单一事实来源是什么？
失败时能否重放？
是否有明确的 gate、trace 和 stop condition？
```

---

## 7. Infinite Retry

**定义**：工具失败后重复相同动作，没有新证据、没有退避、没有终止条件。

**症状**：
- 同一工具调用连续失败 3 次以上，每次参数完全相同
- 日志中出现长串重复的 tool call → error → tool call 循环
- Agent 没有尝试替代方案或降级策略，只是机械重试
- 任务耗时远超预期但最终仍然失败

**风险**：
- token 成本随重试次数线性增长，单次任务费用不可预测
- 相同错误反复触发，可能对外部系统产生副作用（如重复写入、重复请求触发限流）
- 重试占满 context window，挤压后续有效推理空间
- 用户等待时间无上限，体验严重退化

**修复入口**：失败分类、retry budget、requires_new_evidence、human escalation。FailureRecord + recovery budget。

**评审问题**：
```text
这个设计的单一事实来源是什么？
失败时能否重放？
是否有明确的 gate、trace 和 stop condition？
```

---

## 8. Approval-only Interaction

**定义**：只把用户当审批按钮，缺少进度、教学、纠错、预算选择和拒绝解释。

**症状**：
- 每个工具调用都弹出"是否允许？"，用户只能点"是"或"否"
- 用户无法看到 Agent 的推理过程、当前进度或预计剩余步骤
- 拒绝某个操作后 Agent 无法解释为什么要做这个操作，也不提供替代方案
- 没有批量授权或信任区间机制，低风险操作也需要逐一确认

**风险**：
- 用户被迫逐步审批导致总耗时超过手动操作，自动化收益归零
- 缺少上下文的审批等同于盲审，用户无法判断操作是否合理，只能习惯性点"允许"
- 审批疲劳导致用户对高风险操作也不加思考地放行，安全机制形同虚设
- 用户无法在中途调整策略或补充约束，交互退化为单向确认流

**修复入口**：Interaction Plane + InteractionEvent + progressive disclosure。

**评审问题**：
```text
这个设计的单一事实来源是什么？
失败时能否重放？
是否有明确的 gate、trace 和 stop condition？
```

---

## 9. Hidden Cost Explosion

**定义**：多 worker、长 context、重复检索、重复 OCR、强模型验证导致成本隐性爆炸。

**症状**：
- 单次任务实际消耗 token 数是预期的 5-10 倍，但调用方无感知
- 多个 worker 各自携带完整上下文并行运行，重复检索相同文档
- 用 GPT-4 级别模型做格式校验、JSON 解析等低复杂度任务
- 没有 token 计数或费用统计，月底账单才发现成本失控

**风险**：
- 单次任务费用不可预测，无法为用户或业务设置预算上限
- 上下文膨胀和重复检索的成本随任务复杂度指数增长，而非线性增长
- 成本反馈滞后（通常是月结账单），无法在运行时做出降级决策
- 强模型被用于低价值子任务，性价比极低且占用 rate limit 配额

**修复入口**：ResourcePlan + model routing + cache + cost gate + budget gate。

**评审问题**：
```text
这个设计的单一事实来源是什么？
失败时能否重放？
是否有明确的 gate、trace 和 stop condition？
```

---

## 10. Eval Theater

**定义**：看起来有评估，实际上无法捕捉关键失败：工具是否越权、效果是否验证、引用是否可回查、失败是否恢复、成本是否失控。

**症状**：
- 只有"回答质量 1-5 分"，没有外部效果断言
- 没有失败注入和 replay
- eval 不读取 trace，只看最终文本
- 安全、成本、恢复没有指标
- demo 通过后进入生产

**风险**：Agent 最危险的失败常发生在最终回答之外：工具链、权限、world state、effect verification、memory write、recovery。Eval Theater 会让系统在上线后才暴露这些问题。

**修复入口**：
- 建 `evaluation/fixtures/`，覆盖正常、失败、攻击和过期状态
- 使用 trace comparator 检查必备事件
- 对写动作检查 EffectRecord
- 对高风险动作检查 policy / approval / blocked
- 对失败检查 RecoveryAction
- 从真实失败提炼 regression fixture

**评审问题**：
```text
这个 eval 是否能在没有真实外部系统时运行？
它检查的是最终文本，还是完整 trace？
它能否捕捉工具成功但效果失败？
```

---

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
