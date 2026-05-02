# Time Plane
>
> **所属域**：3. World Modeling — 时序约束与有效期管理
>
> **Evidence Status** — synthesized. World State TTL/freshness、Memory expiry/review_policy、Plan 过期、Approval valid_until、Capability expires_at 等时间属性散布于多个 plane；本文件将时间约束、过期和因果关系统一为横切 plane。

**Principle Refs**: BR-02, IS-03 — 时间推移导致上下文结构性腐化；时间维度上的地图-领土偏差（过期信息被当作当前事实）

Time Plane 统一管理 Agent 系统中所有时间相关的约束、过期和因果关系。

## 1. 核心对象

| 对象 | 职责 | 典型来源 |
|---|---|---|
| `TemporalAnchor` | 任何带时间戳的观察、决策或效果的时间锚点，记录"这个信息是什么时候获取的" | Observation.observed_at、EffectRecord.timestamp、Checkpoint.created_at |
| `ValidityWindow` | 有效期窗口，定义一个对象从创建到过期的生命区间 | World State TTL、Approval valid_until、Memory expiry、Cost budget_period |
| `CausalChain` | 因果链，记录"A 发生在 B 之前，B 依赖 A 的结果"的时序约束 | Effect 序列、Plan 步骤依赖、多步 tool call 的先后关系 |
| `StalenessPolicy` | 过期策略，定义对象超过有效期后的处理方式 | World State stale_policy、Memory review_policy、Cache eviction |

## 2. 对象 Schema

```yaml
temporal_anchor:
  anchor_id: string
  source_object: string          # 关联的 Observation / Effect / Checkpoint ID
  timestamp: datetime
  clock_source: system | harness | external | model_injected
  precision: millisecond | second | minute | approximate

validity_window:
  window_id: string
  target_object: string
  created_at: datetime
  expires_at: datetime | null    # null = 不过期
  ttl: duration | null
  status: active | stale | expired | refreshed

causal_chain:
  chain_id: string
  links:
    - step_id: string
      anchor: temporal_anchor_id
      depends_on: [step_id] | null
      effect_ref: string | null
  ordering_guarantee: strict | best_effort

staleness_policy:
  policy_id: string
  target_type: world_state | memory | approval | capability | cache | plan
  max_age: duration
  on_stale: refresh | degrade | block | notify
  on_expired: refresh | block | drop | escalate
  refresh_strategy: poll | event_driven | on_access
```

## 3. 跨 Plane 映射

| 其他 Plane | 原有属性 | Time Plane 对象 |
|---|---|---|
| World State | freshness, TTL, stale_policy | ValidityWindow + StalenessPolicy |
| Memory | review_policy, expiry | ValidityWindow + StalenessPolicy |
| Effects | timestamp, sequence | TemporalAnchor + CausalChain |
| Recovery | checkpoint_at | TemporalAnchor |
| Approval | valid_until | ValidityWindow |
| Cost | budget_period | ValidityWindow |
| State | step 顺序、plan 过期 | CausalChain + ValidityWindow |
| Identity & Capability | expires_at | ValidityWindow |

映射方向：各 Plane 仍然持有自己的时间字段，Time Plane 提供统一的查询、校验和过期处理接口。各 Plane 不需要自己实现过期扫描和因果校验逻辑。

## 4. Agent 时间感

LLM 没有内置时钟。模型无法感知两次调用之间过了多久，也无法判断一条 Observation 是 5 秒前还是 5 小时前获取的。Harness 必须主动在上下文中注入时间信息：当前时间、观察年龄（距 observed_at 的时间差）、任务已用时间和剩余预算时间。

长任务中这一点更加关键。一个运行 30 分钟的 Agent，前期获取的 World State 可能已经过期，早期的审批窗口可能已经关闭，预算时间可能所剩无几。Time Plane 的职责是在这些时间约束被违反前发出信号——而不是等到写动作失败后才发现快照已过期。

## 5. 时间相关的失败模式

| 失败 | 表现 | 根因 | 修复 |
|---|---|---|---|
| Stale Act | 基于过期快照执行写动作 | ValidityWindow 过期但未检查 | 写动作前强制 freshness gate |
| Expired Approval | 审批已过期但 Agent 仍继续执行 | Approval 的 ValidityWindow 未被 gate 检查 | 在 Action 前校验 approval 时效 |
| Causal Inversion | 步骤 B 先于步骤 A 执行，但 B 依赖 A 的结果 | CausalChain 约束缺失或未执行 | 强制 CausalChain ordering |
| Clock Drift | Harness 注入的时间与外部系统时间不一致 | 多 clock source 未对齐 | 统一使用 Harness 时钟，记录 clock_source |
| Phantom Freshness | 刷新了对象但只更新了时间戳，没有真正重新获取 | refresh 操作只改 metadata | refresh 必须产生新 Observation |

## 6. 权衡

**集中管理 vs 各 Plane 自管理。** 集中管理的好处是过期策略一致、时间查询有统一接口、跨 Plane 的时效校验不需要各自实现。代价是引入了一个横切依赖——所有需要时间约束的 Plane 都要与 Time Plane 交互。对于简单 Agent（C0-C2），各 Plane 自管理 TTL 就够了；C3 以上，当多个 Plane 的过期策略需要协调时，集中管理的收益才显现。

**时间精度 vs 实现复杂度。** 大多数 Agent 场景不需要毫秒级精度——分钟级甚至"最近 5 分钟内"就足够做过期判断。追求高精度意味着需要处理时钟同步、网络延迟和跨系统时间偏移，这些复杂度在大多数场景中不值得。schema 中保留 precision 字段，让实现者按需选择。

## 7. 关联文档

- `../world-state/overview.md`
- `../effects/overview.md`
- `../recovery/overview.md`
- `../cost/overview.md`
- `../../lifecycle.md`
