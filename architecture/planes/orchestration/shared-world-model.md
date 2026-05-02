# Shared World Model

> **Evidence Status** — synthesized. World State 与 Orchestration 的交叉需求。

## 1. 定义

Shared World Model 是多 Agent 对同一外部对象状态的共同引用机制，通过共享 `WorldStateSnapshot` 和冲突记录实现。

## 2. 一致性规则

| 场景 | 规则 |
|---|---|
| 只读研究 | eventual consistency 可接受 |
| 写外部对象 | 写前 refresh，写后 readback |
| 多 Agent 写同一对象 | 需要 lock / lease / authority_scope |
| 状态冲突 | 生成 ConflictRecord，不静默覆盖 |
| stale snapshot | 根据 stale_policy 刷新或阻断 |

## 3. ConflictRecord

```yaml
conflict_record:
  conflict_id: conflict_...
  target_object: string
  snapshots: []
  claims: []
  detected_by: agent_id
  impact: low | medium | high | critical
  resolution: pending | refreshed | arbitrated | escalated
```
