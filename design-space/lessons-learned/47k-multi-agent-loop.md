# $47,000 多 Agent 循环失控事件

> **Evidence Status** — grounded.
> - [The $47,000 Agent Loop - DEV Community](https://dev.to/waxell/the-47000-agent-loop-why-token-budget-alerts-arent-budget-enforcement-389i)
> - [AI Agents Horror Stories - Tech Startups](https://techstartups.com/2025/11/14/ai-agents-horror-stories-how-a-47000-failure-exposed-the-hype-and-hidden-risks-of-multi-agent-systems/)

---

## 事故场景

2025-11，一个市场研究团队部署了基于 LangChain 的 4-Agent 协作系统，通过 A2A（Agent-to-Agent）协议协调工作。Agent 分工如下：

- **Research Agent** — 收集市场数据
- **Analysis Agent (Analyzer)** — 分析数据、生成洞察
- **Verification Agent (Verifier)** — 验证分析结论
- **Summary Agent** — 汇总输出最终报告

系统在部署初期运行正常，日成本约 $18。但 Analyzer 和 Verifier 之间逐渐形成了一个自我强化的 ping-pong 循环，最终在 11 天内产生了 $47,000 的 API 费用。

---

## 故障链（按时间顺序）

```
T+0       系统正常运行。Analyzer 提交分析结果给 Verifier。
          ↓ Verifier 回复："结论需要进一步分析。"

T+几分钟  Analyzer 收到反馈，扩展分析后再次提交。
          ↓ Verifier 再次回复："仍需进一步分析。"
          ↓ 循环形成

T+1天     循环已运行数十轮。每轮的 context 因携带完整对话历史而不断膨胀。
          ↓ 单轮 token 消耗开始超线性增长

T+3天     日成本从 $18 跃升至约 $130
          ↓ 团队将成本上升归因于"用户增长"

T+7天     周成本累计 $891
          ↓ 成本监控告警触发，但被解释为"业务增长的正常现象"

T+11天    累计成本突破 $47,000
          ↓ 收到最终账单时才发现异常

T+264小时 循环持续 264 小时（11 天），无自动终止
```

### 成本增长曲线

| 时间节点 | 累计成本 | 日均成本 | 增长倍数 |
|---------|---------|---------|---------|
| 第 1 周 | $127 | ~$18/天 | 1x（基线） |
| 第 2 周 | $891 | ~$109/天 | 6x |
| 第 3 周 | $6,240 | ~$763/天 | 42x |
| 第 4 周 | $18,400 | ~$1,737/天 | 96x |
| 最终 | **$47,000** | — | — |

超线性增长的原因：每轮循环的 context 包含完整的对话历史，token 消耗随轮数二次增长。

---

## 根因分析

### 1. 无循环检测机制

系统中没有任何机制来检测跨 Agent 的通信循环。Analyzer 和 Verifier 之间的 ping-pong 模式——"需要更多分析" → "扩展分析" → "仍需更多分析"——在消息层面每轮都略有不同（因为 LLM 生成的文本不完全重复），但语义上是等价的。

缺失的检测手段：

```
应有的检测                      实际情况
─────────────────────          ─────────────────────
跨 Agent 消息的语义去重          无（每条消息被视为全新输入）
Agent 间通信轮次上限             无（无限轮次）
任务进度评估（是否有新信息产出）   无（无法区分"有效工作"和"空转"）
全局 orchestrator 监控           无（Agent 间直接通信，无中央可见性）
```

### 2. 无成本硬上限

系统设置了成本告警，但告警与执行之间存在关键差距：

- **Budget Alert（预算告警）**：通知"成本超标了"——需要人工响应
- **Budget Enforcement（预算执行）**：自动"停止运行"——机器自动响应

告警被团队忽略（归因为业务增长），因为告警不携带上下文信息（"哪个 Agent 在消耗"、"消耗是否合理"）。没有硬性预算上限意味着成本可以无限增长。

### 3. 无共享状态/记忆

4 个 Agent 各自维护独立的上下文，没有共享记忆。Analyzer 不知道自己已经提交了多少轮"扩展分析"，Verifier 不知道自己已经要求了多少轮"进一步分析"。如果存在共享状态，系统可以检测到"过去 50 轮的分析结论没有实质性变化"。

### 4. 认知偏误：将异常成本归因于业务增长

团队收到成本告警后，将成本上升解释为"用户增长带来的正常消耗"。这是一个典型的确认偏误——人类倾向于将异常信号解释为符合已有预期的正常信号。这表明成本监控不仅需要触发告警，还需要提供归因分析（"成本增长来自哪个 Agent"、"增长模式是否与用户行为相关"）。

---

## 架构缺陷

| 缺失的 Plane/Pattern | 说明 |
|----------------------|------|
| Cost Circuit Breaker | 无预算硬上限和自动熔断。Budget alert ≠ budget enforcement——告警需要人工响应，熔断自动执行 |
| Loop Detection | 跨 Agent 通信无循环检测。语义级去重缺失，Agent 间的 ping-pong 模式未被识别 |
| Progress Monitoring | 无任务进度评估机制。系统无法区分"正在产出新信息"和"在已有信息上空转" |
| Shared State / Memory | 4 个 Agent 无共享上下文。重复工作无法被检测，通信轮次无法被全局追踪 |
| Observability Plane | 无跨 Agent 行为仪表盘。Agent 间通信对运维团队不可见，异常模式无法被发现 |
| Step Count Limit | 无 per-task 步数上限。单个任务可以无限执行，无强制终止条件 |
| Cost Attribution | 成本告警不携带归因信息。"成本增加了"不如"Agent X 的成本在过去 24 小时增加了 6 倍"有用 |

---

## 设计教训

1. **预算告警不等于预算执行——必须有硬性熔断器**。Budget alert 通知人类"出问题了"，budget enforcement 自动执行"停止运行"。在 $47,000 案例中，告警被人类忽略了。正确的设计是：设置绝对上限（$X/天 或 $Y/任务），达到后自动停止 Agent 运行并通知运维。

2. **多 Agent 系统必须有全局循环检测**。检测手段至少包括：跨 Agent 消息的语义去重（embedding 相似度超过阈值 → 标记为疑似循环）；Agent 间通信轮次的硬性上限；全局 orchestrator 对所有 Agent 间消息的可见性。

3. **每个 Agent 和每个任务都需要步数/成本硬上限**。Per-agent token limit、per-task step limit、per-session cost limit。三者任一达到时强制终止并上报。上限值可以动态调整，但不能不存在。

4. **成本监控必须提供归因分析，而非仅提供总量告警**。有效的成本告警应回答："哪个 Agent 在消耗"、"消耗模式是否正常"、"与历史基线的偏差是多少"。无归因的成本数字容易被错误解释。

5. **多 Agent 系统需要共享状态来检测重复工作**。共享记忆/状态存储使系统可以回答"这个分析结论和 30 轮前的有什么不同？"。如果答案是"没有实质性不同"，系统应终止循环。

6. **"将成本上升归因于业务增长"是致命的认知偏误**。系统设计应假设人类会忽略或误读告警。关键安全机制（成本控制、循环检测）不应依赖人工判断——它们必须是自动的、硬性的、不可绕过的。

7. **context 膨胀是循环场景中的成本加速器**。每轮循环携带完整对话历史导致 token 消耗超线性增长。多 Agent 通信应采用摘要式传递（只传结论，不传完整历史）或滑动窗口，避免 context 无限膨胀。

---

## 与知识库的映射

| 映射目标 | 文件路径 | 关联说明 |
|---------|---------|---------|
| Cost Plane | `architecture/planes/cost/overview.md` | 成本熔断器设计。本案例是 budget alert vs budget enforcement 的典型对照 |
| Economics Plane | `architecture/planes/economics/overview.md` | Agent 运行时经济模型。per-agent/per-task 的成本约束 |
| Orchestration Plane | `architecture/planes/orchestration/overview.md` | 多 Agent 协调。全局 orchestrator 对循环检测和通信可见性的作用 |
| Observability Plane | `architecture/planes/observability/overview.md` | 跨 Agent 行为仪表盘。Agent 间通信的运维可见性 |
| Memory Plane | `architecture/planes/memory/overview.md` | 共享记忆/状态存储。多 Agent 重复工作检测 |
| State Plane | `architecture/planes/state/overview.md` | 任务进度状态追踪。区分"有效工作"和"空转" |
| Anti-pattern: Hidden Cost Explosion | `design-space/anti-patterns/hidden-cost-explosion.md` | 隐性成本爆炸反模式。多 worker 重复上下文的成本增长 |
| Anti-pattern: Infinite Retry | `design-space/anti-patterns/infinite-retry.md` | 无限重试反模式。Analyzer-Verifier 的 ping-pong 是一种跨 Agent 的无限重试 |
| Lessons: Agent Cost Explosion | `design-space/lessons-learned/agent-cost-explosion.md` | Agent 成本失控的通用教训。本文件提供多 Agent 循环这一特定场景的详细分析 |

---

## 关联文件

- `architecture/planes/execution/overview.md` — 执行步数限制和强制终止条件
- `architecture/planes/context/overview.md` — context 膨胀控制和摘要式传递
- `design-space/lessons-learned/multi-agent-deadlock.md` — 多 Agent 死锁，循环失控的另一种表现形式

---

## 附：循环检测的最小实现参考

有效的循环检测不需要复杂的基础设施，以下是最小必要组件：

```
组件                      作用                          复杂度
────────────────         ─────────────────────         ────────
per-task step counter    硬性步数上限                    低
per-agent token meter    per-agent 成本追踪              低
message hash ring        近似重复消息检测                 中
embedding similarity     语义级循环检测                   中
global cost gate         到达预算上限自动停止              低
```

最小可行方案：step counter + cost gate。仅这两个组件就能防止本案例中的 $47,000 损失。
