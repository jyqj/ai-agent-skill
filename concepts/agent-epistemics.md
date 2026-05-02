# Agent Epistemics

> **Evidence Status** — synthesized. 从 Representation、World State、Verification、Security 等模块中归纳的共性需求。Agent 认识论是一个相对理论化的方向，但直接影响输出质量和安全性。

## 1. 核心问题

Agent 的错误常常不是不知道，而是不知道自己不知道。生产系统需要把“未知”变成可表示、可传递、可验证、可交互的对象。

```text
Unknown is not a mood. Unknown is a state in the runtime.
```

## 2. 未知类型

| 类型 | 说明 | 处理方式 |
|---|---|---|
| Unobserved | 系统从未观察过 | 获取数据或说明缺口 |
| Low-confidence | 观察存在但置信度低 | 标注置信度，避免升级为事实 |
| Stale | 曾经观察过但可能过期 | refresh before act |
| Conflicted | 多个来源冲突 | 保留冲突，不静默合并 |
| Lossy | 转换链有损 | 回查 raw ref |
| Unverifiable | 没有验证通道 | 降低结论强度或请求人工 |
| Out-of-scope | 工具/权限/接口不可达 | 明确边界，不伪装完成 |
| Adversarial | 输入可能有攻击意图 | 放入 untrusted lane |

## 3. 认识论对象

| 对象 | 作用 |
|---|---|
| EvidenceRef | claim 的来源 |
| Confidence | 表示或推断的可靠度 |
| Freshness | 状态是否仍然可用 |
| TrustLane | 信息是否可作为指令或只能作为数据 |
| ConflictRecord | 明确记录冲突 |
| UnknownRecord | 显式记录不可知缺口 |
| VerificationResult | 说明是否被验证 |

## 4. 输出原则

| 情况 | 输出方式 |
|---|---|
| 证据充分 | 直接结论 + 必要证据 |
| 证据不足 | 结论降级 + 缺口说明 |
| 来源冲突 | 并列冲突 + 不强行合并 |
| 状态过期 | 先刷新；不能刷新则声明过期 |
| 无验证通道 | 说“已执行”之前必须改成“已请求执行/未能验证” |
| 用户要求过度确定 | 拒绝虚假确定性，提供可验证路径 |

## 5. 设计检查

```text
最终回答的每个关键 claim 是否有 evidence_ref？
每个低置信度字段是否被标注，而不是静默使用？
每个世界状态是否有 observed_at 和 ttl？
每个外部效果是否有 verification_status？
Agent 是否知道哪些对象不可观察、不可验证或不可行动？
```
