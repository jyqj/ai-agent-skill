# 成本爆炸——$47,000 的乒乓循环和 $18,000 的一夜账单

> **Evidence Status** — grounded. LangChain 研究管线事故公开复盘（DEV Community）、Google Cloud API key 泄露事件（Tom's Hardware）、行业成本数据（Waxell, Datadog）。

---

## 场景

**案例 A**：一个 LangChain 研究管线，包含 Analyzer 和 Verifier 两个 Agent，设计为互相验证对方的输出。

**案例 B**：AI 顾问在项目中遗留了公开的 Google Cloud API key。

## 设计选择

**案例 A**：

- 无 per-session 成本上限
- 无进度检测（no-progress rule）
- 无循环检测机制
- 团队以为系统在正常工作

**案例 B**：

- API key 硬编码在代码中
- Google Cloud budget alert 设为告警而非阻断
- $1,400 支出上限设为软限制

## 预期

- A：两个 Agent 互相提升输出质量
- B：预算不超过 $7

## 实际结果

### 案例 A：$47,000 乒乓循环

Analyzer 和 Verifier 进入乒乓循环，持续 11 天，生成 $47,000 账单。团队以为系统在正常工作，没有人检查实际输出。另一个类似案例中，数据增强 Agent 在一个周末内发出 230 万次 API 调用。

> 来源: DEV Community, Waxell

### 案例 B：$18,391.78 一夜账单

攻击者一夜间发起 60,000+ 请求，账单从 $7 飙升到 $18,391.78，穿透了 $1,400 支出上限（2500 倍超支）。Budget alert 只发了通知邮件，没有阻断请求。

> 来源: Tom's Hardware

### 行业规模数据

- Fortune 500 公司集体 AI 云支出泄漏 $4 亿（来源: Waxell）
- 未优化 Agent 每会话成本 $10-$100+
- 多 Agent 系统 Token 消耗是单 Agent 的 4-15 倍（来源: Datadog）

## 根因分析

**成本上限应该是熔断器，不是告警器。**

- **原则 BR-01 违反**：资源预算是硬约束。当消耗超过阈值时应硬停止，而非发通知然后继续消耗
- **缺少 Circuit Breaker**：没有任何机制在消耗异常时自动切断调用链
- **缺少 Progress Detection**：连续 N 轮无实质进展应触发停止，但系统没有"实质进展"的定义
- **缺少 Loop Detection**：Analyzer 和 Verifier 的输出高度相似但系统无法识别循环
- **密钥管理失败**：API key 暴露 + 无硬阻断 = 攻击者可以无限消耗

乒乓循环的机制：

```
Analyzer 输出 V1 -> Verifier: "V1 有问题 X"
Analyzer 输出 V2 -> Verifier: "V2 修了 X 但引入了 Y"
Analyzer 输出 V3 -> Verifier: "V3 修了 Y 但 X 又出现了"
... 无限循环，11 天，$47,000
```

## 教训

### 成本上限必须是硬阻断

Budget alert 是告警机制，不是阻断机制。生产系统需要的是 circuit breaker——超过阈值时硬停止所有调用，而不是发一封邮件等人来处理。

### 多 Agent 系统必须有 token budget

每个 session 和每天都应有 token 消耗上限，超过即停：

```yaml
budget:
  per_session_max: 50000 tokens
  per_day_max: 500000 tokens
  action: hard_stop  # 不是 alert，是 stop
```

### 需要 no-progress-rule

如果连续 N 轮（建议 3-5 轮）任务状态没有实质变化，强制停止并上报。"实质变化"需要有明确的定义——例如输出的 embedding 相似度低于阈值才算"有变化"。

### 多 Agent 通信需要循环检测

相同消息模式出现 3 次即触发告警。检测方法可以是输出哈希比对、embedding 相似度或结构化状态比对。

### API key 永远不应硬编码

使用短生命周期凭证 + 硬支出上限。密钥轮换周期应短于潜在攻击窗口。

### 行业参考数据（2026）

成本优化的已知杠杆：

| 策略 | 节省幅度 | 来源 |
|---|---|---|
| 模型路由（RouteLLM） | 30-85%（仅 26% 请求发到 GPT-4 即达 95% 性能） | RouteLLM |
| Prompt 缓存 | 最高 90%（Anthropic 缓存命中价为标准价 10%） | Anthropic |
| 优化后 SWE 任务 | 从 $5-$8/次 降至 $0.02/会话 | 行业数据 |

---

## 关联文件

- `../../architecture/planes/cost/overview.md` — 成本 plane
- `../../design-space/methodology/agent-economics.md` — Agent 经济学
- `../../design-space/anti-patterns/hidden-cost-explosion.md` — 隐性成本爆炸反模式
- `../../design-space/patterns/loop-detection.md` — 循环检测模式
