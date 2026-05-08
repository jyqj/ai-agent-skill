# Credential Pool Failover

> **Evidence Status** — production-validated. 来自 Hermes 的 `credential_pool.py`（1585 行），生产环境支撑多 LLM provider 的凭证管理与故障转移。

## 问题

依赖单一 API 凭证的 agent 系统面临多个脆弱性：单凭证的速率限制直接变成系统瓶颈、凭证过期或被吊销导致整个系统停摆、不同 provider 的配额重置周期不同无法统一管理。

当系统扩展到多凭证、多 provider 时，问题变得更复杂：如何在凭证间分配负载、如何在一个凭证耗尽时无缝切换、如何跨进程共享 OAuth token 状态、如何避免所有凭证同时耗尽。

## 核心机制

**多凭证故障转移引擎——统一管理凭证池的选择、租约、同步与恢复。**

### 架构总览

```
credential_pool
  ├── seed sources
  │     ├── env vars          ← 环境变量中的 API key
  │     ├── auth store        ← 持久化的 OAuth token
  │     └── custom providers  ← 自定义凭证提供者（如 vault）
  ├── selection strategy
  │     ├── fill_first        ← 优先填满单凭证配额
  │     ├── round_robin       ← 轮询分配
  │     ├── random            ← 随机选择
  │     └── least_used        ← 选择使用次数最少的
  ├── lease manager
  │     └── max_concurrent_per_credential
  └── recovery
        ├── exhaustion cooldown
        └── provider-supplied reset_at
```

### 四种选择策略

- **fill_first**: 优先使用同一凭证直到其配额接近耗尽，再切换到下一个。适用于按凭证计费的场景（最大化单凭证利用率）。
- **round_robin**: 按顺序轮询所有可用凭证。适用于需要均匀分散速率限制压力的场景。
- **random**: 随机选择可用凭证。适用于凭证数量大且无明显偏好的场景，提供统计意义上的均匀分布。
- **least_used**: 选择当前使用次数最少的凭证。适用于需要精确负载均衡的场景。

### 跨进程 OAuth Token 同步

对于需要 OAuth 刷新的凭证，采用磁盘 + 内存双层同步：

```
进程 A: token 过期 → 刷新 → 写入磁盘 + 更新内存
进程 B: 使用 token → 发现 401 → 检查磁盘
  ├── 磁盘 token 更新 ──→ 加载到内存，继续使用
  └── 磁盘 token 也过期 ──→ 自行刷新 → 写入磁盘
```

磁盘写入使用原子操作（写临时文件 + rename）避免并发读写竞态。内存层提供快速访问，磁盘层保证跨进程一致性。

### Exhaustion Cooldown 与 Reset

当凭证因配额耗尽被标记为不可用时：

- **provider-supplied reset_at**: 如果 API 响应头包含 `X-RateLimit-Reset` 或类似字段，使用 provider 提供的精确重置时间。
- **exhaustion cooldown**: 如果 provider 未提供重置时间，使用指数退避冷却期（如 30s → 60s → 120s）。
- 冷却期结束后凭证自动恢复为可用状态，重新进入选择池。

### Lease 机制

通过 `max_concurrent_per_credential` 控制单凭证的并发使用数：

```
credential.acquire_lease()   ← 并发计数 +1，达到上限时返回 unavailable
  → 执行 API 调用
credential.release_lease()   ← 并发计数 -1
```

这防止多个并行 agent 同时使用同一凭证导致速率限制集中爆发。

### 三源 Seed

凭证从三个来源加载并合并：

1. **环境变量**: 如 `OPENAI_API_KEY`、`ANTHROPIC_API_KEY`，支持逗号分隔多 key
2. **Auth Store**: 持久化存储的 OAuth token（如 Google、Azure AD），含刷新 token
3. **Custom Providers**: 插件化的凭证提供者，如 HashiCorp Vault、AWS Secrets Manager

三源加载后统一注册到凭证池，后续选择策略对来源透明。

## 项目对照

| 项目 | 实现方式 |
|---|---|
| Hermes | `credential_pool.py`（1585 行）：完整实现四种策略 + OAuth 双层同步 + cooldown + lease + 三源 seed |
| Claude Code | 内部凭证管理相对简单，主要依赖单 provider 单 key |
| LiteLLM | Router 层实现多 key 轮询和故障转移，但无 lease 机制和 OAuth 同步 |

## 与其他 plane/pattern 的关系

| 相关模式 | 关系 |
|---|---|
| `structured-error-classification.md` | 错误分类结果中的 `should_rotate_credential` 标志触发本模式的凭证切换 |
| `dynamic-model-routing.md` | model routing 决定使用哪个 provider，本模式决定使用该 provider 的哪个凭证 |
| `depth-budgeting.md` | 凭证池耗尽是 depth budget 的一种终止条件 |
| `streaming-tool-execution.md` | 流式执行中凭证过期需要中断当前流并用新凭证重连 |

## 适用条件

**适用：**
- 多 LLM provider agent 系统
- 高并发场景（多 agent 实例共享凭证池）
- 需要 7x24 无人值守运行的系统
- 凭证成本敏感（需要精确控制每个 key 的用量）

**不适用：**
- 单凭证、单 provider 的简单 agent——过度工程
- 凭证无速率限制或配额极充裕——无需故障转移
- 纯本地模型（如 ollama）——无凭证概念

## 反模式

| 反模式 | 表现 | 修复 |
|---|---|---|
| 全凭证同时耗尽 | 所有凭证在同一时间窗口被打满 | fill_first 策略 + 错开使用，或 round_robin 分散压力 |
| 无 cooldown 轮询 | 凭证耗尽后立即重试，浪费请求次数 | 使用 provider reset_at 或指数退避 cooldown |
| OAuth 刷新风暴 | 多进程同时发现 token 过期，全部发起刷新 | 磁盘锁 + 刷新结果共享 |
| 泄漏 lease | 异常路径未释放 lease，凭证被永久标记为满载 | lease 超时自动释放 + context manager 模式 |

## 参考实现

- Hermes: `credential_pool.py` — 多凭证故障转移引擎（1585 行）
- Hermes: `CredentialSelector` — 四种选择策略实现
- Hermes: `OAuthTokenSync` — 跨进程 OAuth token 双层同步
