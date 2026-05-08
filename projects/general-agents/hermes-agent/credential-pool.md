# 多凭证故障转移引擎

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> 来源：`hermes_cli/auth/credential_pool.py`, `hermes_cli/auth/provider_config.py`

## 架构概览

CredentialPool 管理同一 Provider 的多个 API Key / OAuth token，在限流、余额耗尽、临时故障时自动切换。

```python
class CredentialPool:
    def __init__(self, provider: str, credentials: List[Credential]):
        self._credentials = credentials
        self._strategy: SelectionStrategy = RoundRobinStrategy()
        self._cooldowns: Dict[str, float] = {}     # key_id → cooldown_until
        self._leases: Dict[str, str] = {}           # key_id → holder_id
        self._lock = threading.Lock()

    def acquire(self, holder_id: str) -> Credential:
        with self._lock:
            cred = self._strategy.select(self._available())
            self._leases[cred.key_id] = holder_id
            return cred

    def release(self, key_id: str, failure: Optional[FailoverReason] = None):
        with self._lock:
            del self._leases[key_id]
            if failure:
                self._cooldowns[key_id] = time.monotonic() + self._cooldown_for(failure)
```

---

## 四种选择策略

| 策略 | 触发条件 | 行为 |
|------|---------|------|
| **RoundRobin** | 默认 | 循环分配，均匀消耗配额 |
| **LeastUsed** | 配额感知模式 | 选择剩余配额最多的凭证 |
| **PriorityFallback** | 主备模式 | 主凭证优先，故障时降级到备用 |
| **Random** | 高并发场景 | 随机选择，避免锁竞争热点 |

```python
class SelectionStrategy(ABC):
    @abstractmethod
    def select(self, available: List[Credential]) -> Credential: ...

class PriorityFallbackStrategy(SelectionStrategy):
    def select(self, available):
        # 按 priority 排序，优先返回最高优先级且未冷却的凭证
        return sorted(available, key=lambda c: c.priority)[0]
```

---

## 跨进程 OAuth 同步

OAuth token 刷新需要跨进程互斥（多个 agent 实例共享同一 token）：

```python
class OAuthTokenSync:
    def __init__(self, token_path: Path):
        self._lock_path = token_path.with_suffix('.lock')

    def refresh_if_needed(self, credential: OAuthCredential) -> str:
        with FileLock(self._lock_path, timeout=10):
            # 再次检查（另一进程可能已刷新）
            fresh = self._read_token(credential.token_path)
            if fresh and not fresh.is_expired:
                return fresh.access_token
            # 执行刷新
            new_token = credential.refresh()
            self._write_token(credential.token_path, new_token)
            return new_token.access_token
```

**洞察**：文件锁 + double-check 模式，防止多进程同时刷新导致旧 token 被多次使用。

---

## Exhaustion Cooldown

所有凭证耗尽时进入全局冷却，而非无限重试：

```python
def _available(self) -> List[Credential]:
    now = time.monotonic()
    available = [c for c in self._credentials
                 if c.key_id not in self._leases
                 and self._cooldowns.get(c.key_id, 0) < now]
    if not available:
        # 所有凭证不可用 → 计算最短冷却剩余时间
        min_wait = min(self._cooldowns.values()) - now
        raise CredentialExhaustedError(
            f"所有 {len(self._credentials)} 个凭证不可用，最短等待 {min_wait:.0f}s",
            retry_after=min_wait
        )
    return available
```

---

## Lease 机制

Lease 防止同一凭证被并发请求同时使用（尤其是有 RPM 限制的 API）：

- `acquire()` 获取 lease，绑定 holder_id（通常是 session_key）
- `release()` 归还凭证，可选附带 failure reason 触发冷却
- 超时未释放的 lease 被自动回收（默认 300s），防止 agent 崩溃后凭证永久锁定

**设计意图**：将凭证从"全局共享资源"转变为"受控租借资源"，使故障转移和配额管理成为可能。
