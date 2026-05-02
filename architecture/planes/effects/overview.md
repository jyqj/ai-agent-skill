# Effects & External Action Verification
>
> **所属域**：4. Action & Effect — 外部效果与验证闭环
>
> **Evidence Status** — synthesized. coding、workflow、browser、ops 场景对写动作、回读验证、补偿事务的共同需求；this repository 对外部效果闭环的统一抽象。

**Principle Refs**: IS-02, BDI-02 — 效果验证本质是信念修正；工具执行成功不等于外部效果已达成

## 定义

Effects 层管理：
- Agent 想改变什么；
- 实际调用了什么动作；
- 外部世界是否真的改变；
- 如果没有，如何补偿、回滚或解释。

这层存在的原因是：**工具执行成功 ≠ 外部效果成功。**

## 最小 Effect 闭环

```text
Intended Effect
  ↓
Tool Call
  ↓
Execution Result
  ↓
Readback / External Ack / Human Confirm
  ↓
Effect Status
```

## Effect Record

```yaml
effect_id: string
tool_call_id: string
world_object_refs: []
intended_effect: string
preconditions_checked: []
postconditions_expected: []
verification_method: read_back | test | external_ack | human_confirm | none
verification_status: unverified | verified | failed | partially_verified
verification_evidence: []
rollback_or_compensation: string | null
notes: string | null
```

## 验证方法

| 方法 | 适用场景 |
|---|---|
| read_back | CRM、数据库、Git、文件系统、DOM |
| test | 代码修改、配置变更 |
| external_ack | 邮件、消息、队列、第三方 API |
| human_confirm | 不可感知的业务变化、线下动作 |
| sensor_confirm | 机器人、IoT、物理环境 |

## 不同动作的默认策略

| 动作类型 | 默认策略 |
|---|---|
| read | 无 effect ledger，记录 observation 即可 |
| write | 记录 intended effect + read-after-write |
| send / notify | 需要 outbox / ack / bounce 信息 |
| delete | 必须声明 reversibility 和确认策略 |
| deploy | 需要 rollout signal + health check + rollback |
| purchase / transfer | 强制人工确认 + 双重验证 |

## 常见失败

| 失败 | 表现 | 修复 |
|---|---|---|
| Ghost Success | 接口成功但状态没变 | postcondition + readback |
| Duplicate Side Effect | 重试导致重复发送 / 重复扣费 | idempotency key |
| Partial Effect | 多步流程只成功一半 | compensation transaction |
| Irreversible Misfire | 删除 / 外发动作无法挽回 | staged approval + dry-run |

## 关联模式

- `../../../design-space/patterns/effect-ledger.md`
- `../../../design-space/patterns/self-verification.md`
- `../../../design-space/patterns/dual-channel-gui-verification.md`
- `gui-verification.md`
- `../../../evaluation/effect-evals.md`
