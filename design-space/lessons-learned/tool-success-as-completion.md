# 把工具成功当任务完成

> **Evidence Status** — synthesized. 企业 Workflow Agent 的生产事故复盘；API 异步处理导致的数据一致性问题；Effect Verification 缺失的系统性失败。

---

## 场景

一个企业级 Workflow Agent，负责自动处理客户请求：读取工单、更新 CRM 记录、发送通知邮件。日均处理量约 500 个工单。

核心流程：用户在 Slack 中说"把客户 A 的续约状态改成已确认"，Agent 调用 CRM API 更新状态，然后向用户报告完成。

## 设计选择

团队采用了最直接的实现方式：

1. 解析用户指令
2. 调用 CRM API 的 `update` 端点
3. 检查 HTTP 响应码
4. 如果返回 200，向用户报告"已完成"

不做 read-after-write。理由：
- API 返回 200 就是成功，为什么要多此一举再读一次？
- 额外的 read 调用增加延迟，用户体验变差
- CRM 系统是公司核心系统，"应该是可靠的"

## 预期

- API 返回 200 意味着数据已写入
- CRM 系统的可靠性有保证
- Agent 报告"已完成"时，任务确实完成了

## 实际结果

上线第一周就出现了三类问题：

### 异步处理的幻觉

CRM 系统内部使用消息队列处理写入请求。API 返回 200 的含义是"请求已入队"，不是"数据已写入"。在高峰期，队列延迟可达 30 秒。Agent 报告"已完成"时，数据可能还在队列中。

更糟糕的是：队列偶尔会丢消息。大约 0.3% 的写入请求最终没有执行，但 API 已经返回了 200。

### 竞态覆盖

Agent 写入成功后，另一个自动化流程（定时同步脚本）把状态覆盖回了旧值。Agent 的写入在时间窗口上"存活"了约 5 分钟，然后被覆盖。用户看到的最终状态和 Agent 报告的不一致。

### 静默格式错误

某些工单的客户名称包含特殊字符，API 接受了请求（返回 200），但内部的字段校验把名称截断了。数据确实写入了，但写入的值和预期不一致。Agent 报告"已更新客户名称为 XXX"，实际写入的是截断后的版本。

## 根因分析

核心问题：**工具返回的是"请求已接受"（ExecutionResult），不是"效果已达成"（EffectRecord）**。

这是整个知识库的核心命题之一。HTTP 200 的语义是"服务器已接收并处理了你的请求"，但"处理"可能是"放入队列"、"部分执行"、"接受但忽略了某些字段"。

信任链断裂的三个层次：

```
Agent 的假设                    现实
─────────────────────          ─────────────────────
API 返回 200 = 写入成功         API 返回 200 = 请求已接受
写入成功 = 数据持久化            写入成功 = 数据暂时存在
数据持久化 = 任务完成            数据持久化 = 数据未被覆盖
```

每一层都有可能断裂。不做 read-after-write，就是在三个假设上同时赌博。

## 教训

### 写动作必须有 postcondition + verification method

每个写动作在设计时就应该定义：

```yaml
action: update_crm_status
postcondition: "customer.status == 'confirmed'"
verification_method: "crm_read(customer_id).status"
verification_delay: 5s    # 等待异步处理完成
max_retries: 3
```

### 不能信任 ExecutionResult 替代 EffectRecord

- **ExecutionResult**：工具说它做了什么（"API 返回 200"）
- **EffectRecord**：世界实际发生了什么变化（"读回来确认 status == confirmed"）

这两者之间存在语义鸿沟。高风险动作必须用 EffectRecord 验证，不能止步于 ExecutionResult。

### 验证成本远低于错误成本

多一次 read 调用的成本：约 100ms 延迟 + 微量 API 配额。

不做验证的潜在成本：客户续约状态错误导致合同纠纷、客户流失、合规风险。

### 异步系统需要延迟验证

如果目标系统是异步的，verification 需要等待一个合理的延迟后再执行。这个延迟应该是可配置的，并且在 SLA 超时后上报而不是静默放弃。

---

## 关联文件

- `concepts/representation-and-effects.md` — 表示、接口与效果的三道边界
- `architecture/planes/effects/overview.md` — Effect Plane 的架构设计
- `evaluation/effect-evals.md` — 效果验证的评估方法
- `design-space/anti-patterns/depth-without-verification.md` — 深度执行但不验证的反模式
