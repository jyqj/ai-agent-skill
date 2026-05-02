# Failure Taxonomy

> **Evidence Status** — synthesized. 从多个 Agent 项目的生产失效中归纳，覆盖表示、执行、验证、控制、记忆、安全和运维层面。

Agent 的失败不是随机的——它们有模式。识别模式才能系统修复。

## 1. 任务理解失败

| 失败 | 表现 | 场景 | 修复方向 |
|---|---|---|---|
| Intent Mismatch | 做了错误任务 | 用户说“帮我看看”，Agent 直接执行写动作 | intent router + risk gate |
| Scope Creep | 超出任务范围 | 修一个 bug 变成重构整个模块 | success_criteria 绑定 + milestone gate |
| Premature Completion | 过早宣布完成 | 工具 success 就停止 | effect verification + stop gate |

## 2. 表示失败

| 失败 | 表现 | 场景 | 修复方向 |
|---|---|---|---|
| Raw Input Loss | 丢失原始材料 | 只保留 OCR 文本，没有原图 | raw_ref retention |
| Summary Collapse | 摘要替代原文 | 限制条件在 compaction 中丢失 | transform chain + replayable refs |
| Freshness Blindness | 过期状态继续使用 | 昨天的 dashboard 当今天状态 | ttl + refresh policy |
| Trust Confusion | 外部文本被当指令 | issue 评论操控 agent | trust tier separation |

## 3. 上下文失败

| 失败 | 表现 | 场景 | 修复方向 |
|---|---|---|---|
| Missing Context | 没读关键信息 | 不读 README 就开始修改代码 | convention discovery |
| Context Rot | 长上下文后质量下降 | 第 30 步开始忘记第 3 步约束 | compaction + decision log |
| Information Overload | 塞了太多无关信息 | 把 10 个文件全文放上下文 | offloading + context pack |

## 4. 工具失败

| 失败 | 表现 | 场景 | 修复方向 |
|---|---|---|---|
| Wrong Tool | 选错工具 | 用 grep 查函数定义，应使用 AST | 工具描述优化 + router eval |
| Bad Arguments | 参数错误 | 路径拼写错误、JSON 格式错误 | schema 验证 + 示例 |
| Tool Failure Loop | 工具失败后重复同一调用 | 文件不存在，反复 read 同一路径 | failure_mode 分类 + retry budget |
| Output Misinterpretation | 错误理解工具结果 | warning 被当 failure | standard observation |

## 5. 世界状态 / 效果失败

| 失败 | 表现 | 场景 | 修复方向 |
|---|---|---|---|
| Stale World State | 基于旧状态行动 | ticket 状态已被他人改动 | read-before-write |
| Ghost Success | tool success 但现实没变 | API 200 但字段未更新 | postcondition + readback |
| Duplicate Side Effect | 重试导致重复外发 / 重复扣费 | 超时后盲重试 | idempotency key |
| Partial Effect | 多步流程只成功一半 | step2 失败，step1 已执行 | compensation transaction |

## 6. 执行深度失败

| 失败 | 表现 | 场景 | 修复方向 |
|---|---|---|---|
| Too Shallow | 只给方案不执行 | 用户要修 bug，Agent 只解释原因 | required_depth + stop gate |
| No Verification | 执行后不检查 | 改了代码但不跑测试 / 不回读 | D5 verification gate |
| Goal Drift | 执行中偏离目标 | 越做越偏 | step 绑定 goal_id + milestone |
| Budget Exhaustion Panic | 预算耗尽时硬停 | 没交代做了什么、还差什么 | stop_with_evidence |

## 7. 控制 / 安全失败

| 失败 | 表现 | 场景 | 修复方向 |
|---|---|---|---|
| Permission Bypass | 越权动作 | 未经授权执行 shell / send | policy before tool execution |
| Approval Miss | 高风险未审批 | 直接 git push / 发邮件 | risk classification |
| Tool Output Injection | 外部内容影响高风险行为 | 网页正文指挥 agent | untrusted context boundary |
| Secret Exfiltration | 读取并外发敏感信息 | 外部内容诱导发送 token | redaction + network policy |

## 8. 记忆失败

| 失败 | 表现 | 场景 | 修复方向 |
|---|---|---|---|
| False Memory | 记错事实 | 引用用户从未说过的偏好 | provenance 标记 + 审计 |
| Stale Memory | 旧信息未更新 | 用户已换工作仍用旧信息 | invalidation + 时间衰减 |
| Emotion Fixation | 把一次性情绪固化 | “今天烦 Java” → 永久偏好 | 情绪层短生命周期 |
| Delete Leak | 删除后仍使用 | 用户删了记忆但 Agent 仍基于它推理 | 物理删除 + 召回验证 |

## 9. 编排失败

| 失败 | 表现 | 场景 | 修复方向 |
|---|---|---|---|
| Merge Conflict | 多 Worker 输出冲突 | 两个 Worker 修改了同一文件 | output contract + merge strategy |
| Context Leak | 子代理看到不该看的内容 | 高权限主上下文泄露给 worker | isolated context |
| Orphan Worker | Worker 完成但结果没收集 | 超时后结果丢失 | lifecycle 管理 |

## 10. 运维失败

| 失败 | 表现 | 场景 | 修复方向 |
|---|---|---|---|
| Silent Regression | 升级后效果变差没人知道 | prompt / model / tool schema 改了 | eval regression |
| Untraceable Failure | 出事后定位不了 | trace 不含配置指纹或 effect 事件 | config fingerprint + observability |
| Config Drift | 环境不同步 | staging / prod 行为不一致 | config fingerprint + rollout discipline |
