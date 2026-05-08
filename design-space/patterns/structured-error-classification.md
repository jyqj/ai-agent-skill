# Structured Error Classification

> **Evidence Status** — production-validated. 来自 Hermes 的 `error_classifier.py`（1037 行）及 Codex 的错误处理实现，生产环境支撑精确错误恢复决策。

## 问题

Agent 系统与外部 API 交互时，错误类型极其多样：HTTP 状态码、SDK 异常、网络超时、SSL 错误、provider 特有的错误格式。如果对所有错误统一处理（如一律重试或一律放弃），会导致两种浪费：

- **该重试的没重试**: 瞬态网络抖动导致的 503 本可重试恢复，却直接终止了任务
- **不该重试的反复重试**: 账单耗尽的 402 永远不会自愈，却浪费了重试预算

更麻烦的是，同一 HTTP 状态码在不同上下文中含义不同。402 可能是"真的钱花完了"（需要充值），也可能是"月度配额重置前的临时限制"（等一等就好）。400 错误在会话很大时可能意味着上下文溢出，而非真正的参数错误。

## 核心机制

**将错误分类为枚举类型，每个类型关联精确的恢复动作标志，消除 agent 循环中的错误处理歧义。**

### 分类模型

```
错误输入（HTTP status + response body + 上下文信息）
  │
  ├── ErrorClassifier.classify()
  │
  └── ClassifiedError
        ├── reason: FailoverReason    ← 17 种枚举之一
        └── flags
              ├── retryable: bool                    ← 是否可重试
              ├── should_compress: bool              ← 是否应压缩上下文后重试
              ├── should_rotate_credential: bool     ← 是否应切换凭证
              └── should_fallback: bool              ← 是否应降级到备选 provider
```

### 17 种 FailoverReason

| 类别 | Reason | 恢复标志 | 说明 |
|---|---|---|---|
| 速率限制 | `rate_limited` | retryable | 标准 429，等待后重试 |
| 速率限制 | `rate_limited_extended` | retryable + fallback | 429 且 Retry-After > 阈值，优先切换 provider |
| 配额 | `quota_exhausted_billing` | rotate_credential | 402 真账单耗尽，需换凭证或充值 |
| 配额 | `quota_exhausted_periodic` | retryable + rotate_credential | 402 周期性配额，可等重置或换凭证 |
| 上下文 | `context_overflow` | should_compress | 400 + 大会话，推断为上下文溢出 |
| 上下文 | `context_overflow_confirmed` | should_compress | provider 明确报告 token 超限 |
| 认证 | `auth_expired` | rotate_credential | 401 token 过期 |
| 认证 | `auth_invalid` | rotate_credential | 403 凭证无效 |
| 服务端 | `server_error` | retryable | 500/502/503 |
| 服务端 | `server_overloaded` | retryable + fallback | 503 + 明确过载信号 |
| 网络 | `network_timeout` | retryable | 请求超时 |
| 网络 | `ssl_transient` | retryable | SSL 握手瞬态失败 |
| 网络 | `connection_reset` | retryable | 服务器主动断连 |
| 模型 | `model_not_found` | fallback | 请求的模型不存在或已下线 |
| 模型 | `content_filtered` | — | 内容安全过滤，不可重试 |
| 流式 | `stream_interrupted` | retryable | 流式响应中途断开 |
| 未知 | `unknown` | — | 无法分类，默认不重试 |

### 关键分类逻辑

**402 歧义消解** — 区分"真账单耗尽"与"周期性配额"：

```
HTTP 402
  ├── 响应体包含 "billing"/"payment"/"upgrade" ──→ quota_exhausted_billing
  ├── 响应体包含 "limit"/"quota" + 无付费提示 ──→ quota_exhausted_periodic
  └── 无法判断 ──→ 默认 quota_exhausted_billing（保守策略）
```

**400 + 大会话 = 上下文溢出推断**：

```
HTTP 400
  ├── 当前会话 token 数 > 阈值（如 80% 模型上限）
  │     └── 响应体包含 "token"/"length"/"context" ──→ context_overflow
  └── 否则 ──→ 普通 bad_request，不可重试
```

**SSL 瞬态 vs 服务器断连区分**：

```
网络异常
  ├── SSL handshake 阶段失败 ──→ ssl_transient（通常可重试）
  └── 连接建立后被 reset ──→ connection_reset（可重试，但可能是服务端问题）
```

## 项目对照

| 项目 | 实现方式 |
|---|---|
| Hermes | `error_classifier.py`（1037 行）：完整 17 种枚举 + 四标志分类器，含 402 消歧和上下文溢出推断 |
| Codex | 错误分类后的恢复策略实现，包括自动 context compression 和 provider fallback |
| LiteLLM | `exception_mapping_utils` 做 HTTP 到异常类的映射，但不含恢复动作标志 |

## 与其他 plane/pattern 的关系

| 相关模式 | 关系 |
|---|---|
| `credential-pool-failover.md` | `should_rotate_credential` 标志直接驱动凭证池的切换逻辑 |
| `dynamic-model-routing.md` | `should_fallback` 标志触发 model router 切换到备选 provider |
| `compaction.md` | `should_compress` 标志触发上下文压缩流程 |
| `token-budget-controller.md` | 上下文溢出推断依赖 token budget 提供的当前 token 使用量数据 |
| `streaming-tool-execution.md` | `stream_interrupted` 类型需要流式执行器配合做断点续传或重试 |
| `behavior-correction-layer.md` | 错误分类是系统级错误处理，behavior correction 是模型行为级偏差处理，两层互补 |

## 适用条件

**适用：**
- 需要精确错误恢复的 agent 系统
- 多 provider 环境（不同 provider 的错误格式各异）
- 高可用要求的生产系统（需要区分瞬态错误和永久错误）
- 成本敏感场景（需要避免对不可恢复错误的无意义重试）

**不适用：**
- 单 provider、容错要求低的原型系统——简单 try/retry 即可
- 纯本地模型——无 HTTP 错误
- 错误率极低且业务可接受偶尔失败——分类器的复杂度不值得

## 反模式

| 反模式 | 表现 | 修复 |
|---|---|---|
| 一律重试 | 对 402（账单耗尽）也重试 3 次，浪费时间和请求 | 按分类结果决定是否重试 |
| 一律放弃 | 503 瞬态错误也直接报错终止 | retryable 标志为 true 时自动重试 |
| 忽略上下文信号 | 400 错误统一当参数错误处理，不检查是否为上下文溢出 | 结合会话 token 数推断 context_overflow |
| 无消歧 | 402 统一当"没钱了"处理，实际只是周期配额 | 分析响应体关键词做 402 消歧 |

## 参考实现

- Hermes: `error_classifier.py` — 错误分类引擎（1037 行）
- Hermes: `FailoverReason` — 17 种错误原因枚举
- Hermes: `ClassifiedError` — 分类结果 + 四标志数据结构
- Codex: 错误恢复策略（compress / fallback / rotate）执行逻辑
