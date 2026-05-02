# World State Layer
>
> **所属域**：3. World Modeling — 外部对象的当前状态快照
>
> **Evidence Status** — synthesized. workflow、browser、ops、memory、coding 场景对外部对象状态回读与刷新的一般需求；this repository 对外部对象状态管理的统一抽象。

**Principle Refs**: IS-01, IS-03, BR-02 — Agent 操作模型而非现实，地图与领土可能静默偏离，状态随时间退化。

## 定义

World State Layer 维护 Agent 对外部对象当前状态的**可刷新的快照**。

Task State 关心“任务做到哪一步”；World State 关心“外部对象现在是什么样”。

例如：
- CRM ticket 当前状态是什么？
- Git 分支现在的 HEAD 是什么？
- 页面按钮当前是否可点击？
- 服务器告警现在是否仍在 firing？
- 机器人当前坐标在哪里？

## 模块接口

**输入**：tool readback、sensor reading、API read、DOM snapshot
**输出**：world state snapshot、freshness verdict、conflict signal
**配置**：TTL、refresh policy、consistency model、conflict policy

## Snapshot Schema

```yaml
snapshot_id: string
target: string
object_type: crm.ticket | git.repo | browser.page | server.alert | robot.pose
observed_at: datetime
observed_by: tool_id
state: object
freshness_ttl: duration
confidence: float | null
source: api | human | log | sensor | browser
consistency_model: strong | eventual | unknown
stale_policy: refresh_before_act | allow_if_recent | require_human
```

## 何时必须刷新

| 场景 | 默认策略 |
|---|---|
| 写动作前读取关键业务对象 | refresh_before_act |
| 最终交付前确认状态 | refresh_before_act |
| 最终一致系统（邮件、队列、缓存） | poll_until_timeout |
| 高风险生产变更 | require_human 或 double-check |
| 低风险只读分析 | allow_if_recent |

## 常见失败

| 失败 | 表现 | 修复 |
|---|---|---|
| Stale Snapshot | 基于旧状态继续操作 | ttl + refresh gate |
| State Conflict | 多 Actor 同时修改对象 | etag / optimistic lock |
| False Completion | 任务状态完成，但世界状态未达标 | stop gate 绑定 world state |
| Eventual Consistency Blindness | 刚写完就立刻读空 | poll / backoff / consistency policy |

## 关联文档

- `../state/overview.md`
- `../effects/overview.md`
- `../../../evaluation/effect-evals.md`
