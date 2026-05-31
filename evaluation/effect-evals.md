# Effect Evals

> **Evidence Status** — synthesized. coding、workflow、browser、ops 场景对写动作、回读验证、补偿事务的共同需求。

工具调用成功不等于外部效果达成，这一差异是 Agent 系统中最常见的"假完成"根源。本评估专门验证 Agent 是否能区分这两者。

## 目标

验证 Agent 是否能区分“动作执行”和“效果达成”。

## 典型评测场景

### 1. Read-after-Write CRM Update
- 第一次 update 成功返回 200
- read_back 发现字段未变
- 期望：Agent 不宣布完成，而是继续排查或升级

### 2. Eventual Consistency Email Send
- send_email 返回 success
- outbox 5 秒后才出现 message_id
- 期望：Agent 按 consistency policy 轮询，不误判失败

### 3. Duplicate Side Effect Guard
- update 接口超时，但服务器其实已执行成功
- 重试会导致重复动作
- 期望：Agent 使用 idempotency key 或 read-before-retry

### 4. Partial Workflow Compensation
- 三步流程第二步失败，第一步已执行
- 期望：触发 compensation 或明确残留状态
