# Testability Design

> **Evidence Status** — synthesized. Eval Framework、fixtures、tool-use eval、effect eval、security eval 等既有评估文档；本知识库对可 mock、可重放、可回归 Agent 的工程化要求。

评估定义"测什么"，可测试性设计（Testability Design）定义"系统如何让自己可以被测"。不可 mock 的外部依赖、不可重放的 trace、不可固定的随机性都是可测试性的敌人。

## 1. Eval 与 Testability 的区别

Eval 说明“应该评什么”；Testability 说明“系统如何被评”。

一个可测试 Agent 需要：

```text
mock external world
trace replay
deterministic fixture
property-based invariant
shadow mode comparison
regression threshold
```

## 2. Mock 外部世界

| 外部对象 | Mock 方式 |
|---|---|
| API / CRM | tool stub + world state fixture |
| 文件系统 | temp workspace + diff assertion |
| 浏览器 | DOM fixture + screenshot fixture + action log |
| 邮件 | outbox simulator + delivery ack |
| 日志/告警 | event stream fixture |
| 机器人/设备 | sensor readback simulator |

## 3. Trace Replay

重放需要固定：

```text
input events
raw refs or deterministic fixtures
tool outputs
world state snapshots
config fingerprint
random seed / nondeterministic policy
```

## 4. Property-based Testing

不只测某个答案，还要测不变性：

| 不变性 | 示例 |
|---|---|
| No unsafe action | 不点击 place_order，不删除未授权对象 |
| Evidence required | 关键 claim 必须有 evidence_ref |
| Effect verified | 写动作后必须 readback |
| Trust lane integrity | untrusted_data 不得升级为 instruction |
| Budget respected | 超预算触发 budget_choice |
| Cancellation respected | 用户取消后不得继续写外部系统 |

## 5. Shadow Mode

```text
old runtime handles real task
new runtime receives same observation and state copy
new runtime dry-run only
compare decision / tool_call / cost / risk / final answer
block rollout if divergence exceeds threshold
```
