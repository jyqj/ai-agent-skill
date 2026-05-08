# 结构化错误分类管道

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> 来源：`hermes_cli/providers/error_classifier.py`, `hermes_cli/providers/failover.py`

## FailoverReason 枚举

17 种结构化错误类型，每种携带 4 个恢复标志：

```python
@dataclass
class FailoverReason:
    code: str                    # 如 "rate_limited", "context_overflow"
    retryable: bool              # 是否可直接重试
    credential_rotate: bool      # 是否应切换凭证
    model_fallback: bool         # 是否应降级模型
    context_reduce: bool         # 是否应压缩上下文
```

| 分类 | 典型 code | retry | cred_rotate | model_fb | ctx_reduce |
|------|----------|-------|-------------|----------|------------|
| 限流 | `rate_limited` | Y | Y | N | N |
| 余额 | `insufficient_funds` | N | Y | N | N |
| 上下文溢出 | `context_overflow` | N | N | Y | Y |
| 内容过滤 | `content_filtered` | N | N | Y | N |
| 服务不可用 | `service_unavailable` | Y | N | N | N |
| 认证失败 | `auth_error` | N | Y | N | N |
| 超时 | `timeout` | Y | N | N | N |
| 格式错误 | `invalid_response` | Y | N | N | N |

（完整 17 种包括 `model_not_found`, `region_unavailable`, `billing_hard_limit`, `streaming_error`,
`connection_reset`, `dns_resolution`, `ssl_error`, `proxy_error`, `server_error` 等。）

---

## 402 歧义消解

HTTP 402 (Payment Required) 在不同 Provider 含义不同，需要二次判断：

```python
def classify_402(response, provider: str) -> FailoverReason:
    body = response.json() if response.content else {}
    error_msg = body.get("error", {}).get("message", "").lower()

    # OpenAI: 402 通常是真正的余额不足
    if provider == "openai":
        return FailoverReason("insufficient_funds", retryable=False, credential_rotate=True, ...)

    # Anthropic: 有时用 402 表示临时限流
    if provider == "anthropic" and "rate" in error_msg:
        return FailoverReason("rate_limited", retryable=True, credential_rotate=True, ...)

    # 第三方代理: 402 可能是代理商余额而非上游余额
    if "proxy" in provider or "relay" in provider:
        return FailoverReason("proxy_billing", retryable=False, credential_rotate=True, ...)

    # 兜底：保守处理为不可重试
    return FailoverReason("payment_required_unknown", retryable=False, credential_rotate=True, ...)
```

**洞察**：同一 HTTP 状态码在不同生态中语义不同。分类器必须结合 provider 上下文和 body 内容联合判断。

---

## 上下文溢出推断

部分 Provider 不返回明确的 context_length_exceeded 错误码，需要启发式推断：

```python
def _infer_context_overflow(error: Exception, request_tokens: int, model_limit: int) -> bool:
    msg = str(error).lower()
    # 1. 显式错误信息
    if any(kw in msg for kw in ["context length", "max tokens", "too many tokens"]):
        return True
    # 2. 请求 token 数接近或超过模型限制
    if request_tokens and model_limit and request_tokens > model_limit * 0.95:
        return True
    # 3. 特定 Provider 的非标准错误码
    if hasattr(error, 'status_code') and error.status_code == 400:
        if "length" in msg or "too long" in msg:
            return True
    return False
```

推断为上下文溢出后，恢复管道触发：截断历史 → 压缩工具结果 → 降级到更大上下文窗口的模型。

---

## 恢复管道编排

```python
def recover(reason: FailoverReason, pool: CredentialPool, context: AgentContext):
    if reason.credential_rotate:
        pool.release(context.current_key, failure=reason)
        context.current_key = pool.acquire(context.session_key)

    if reason.context_reduce:
        context.messages = trim_messages_for_recovery(context.messages)

    if reason.model_fallback:
        context.model = get_fallback_model(context.model)

    if reason.retryable:
        return RetryDecision(delay=reason.suggested_delay)

    return EscalateDecision(reason=reason)
```

恢复标志可叠加：如 `context_overflow` 同时触发 `context_reduce + model_fallback`。
