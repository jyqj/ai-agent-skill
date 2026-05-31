# Controllers (Deprecated)

> **本目录已降级。** Execution Depth Controller 已迁移至 [`../kernel/execution-depth-controller/`](../kernel/execution-depth-controller/overview.md)。其余 controller 概念（Recovery Controller、Cost Controller、Freshness Controller）保留为 frontier 方向，待未来有实质内容时再独立建模。

> **Evidence Status** — synthesized. 基于 coding-agent、research-agent、workflow-agent 参考项目中控制逻辑的共性抽取；结合本知识库的 D0-D6 深度框架。

## 定位

Controllers 是运行时的**控制器层**，负责回答：

> Agent 应该继续深入、验证、恢复、请求审批，还是停止？

Controllers 做的是**元决策**，即关于执行过程本身的决策，而非生成答案（那是 Kernel 的职责）。

Controllers 是**跨 Plane 的控制逻辑集合**，从 Control Plane 获取策略，从 State Engine 获取任务状态，输出 ControlDecision 影响主循环的走向。

## 与 Control Plane 的关系

| | Control Plane | Controllers |
|---|---|---|
| 性质 | 策略定义层 | 策略执行层 |
| 内容 | Policy、Permission、Budget、Risk Threshold | 运行时判断逻辑 |
| 时机 | 部署前 / 配置时 | 每个 step 实时 |
| 类比 | 宪法 | 法官 |

Control Plane 定义"什么情况下需要审批"、"最大重试次数是多少"、"哪些工具需要沙箱"。Controllers 在运行时根据这些策略，结合当前 TaskState，做出具体的 continue / verify / recover / escalate / stop 判断。

## 通用接口

所有 Controller 共享统一的输入输出契约：

```text
输入: TaskState + Policy
输出: ControlDecision
```

### ControlDecision 类型

| Decision | 含义 | 后续动作 |
|---|---|---|
| `continue` | 继续执行下一步 | 进入 Kernel.decide() |
| `verify` | 需要验证当前结果 | 进入 Verify 阶段 |
| `recover` | 检测到失败，启动恢复 | 选择恢复策略并重试 |
| `escalate` | 需要人工审批或介入 | 暂停循环，等待外部输入 |
| `stop` | 停止执行 | 带证据交付或报告阻塞 |

### 通用决策伪代码

```python
def controller_decide(task_state, policy) -> ControlDecision:
    if task_state.budget_exhausted():
        return ControlDecision("stop", reason="budget_exhausted")

    if task_state.has_unverified_effects():
        return ControlDecision("verify", target=task_state.pending_effects)

    if task_state.last_action_failed():
        if policy.allow_recovery and task_state.retries_remaining > 0:
            return ControlDecision("recover", strategy=select_recovery(task_state))
        return ControlDecision("stop", reason="unrecoverable_failure")

    if task_state.next_action_risky(policy.risk_threshold):
        return ControlDecision("escalate", action=task_state.next_action)

    return ControlDecision("continue")
```

## 当前控制器

### Execution Depth Controller

管理 D0-D6 的深度推进、预算分配、里程碑验证。

核心职责：
- **Representation Gate** — 判断输入表示质量是否足够进入计划/执行
- **Depth Selection** — 根据任务类型、风险、工具可用性选择 required_depth
- **Milestone Gating** — 每个里程碑完成后验证退出条件，决定是否推进到下一层
- **Budget Control** — 管理 step / tool / token / risk / retry / human / branch / freshness 预算
- **Recovery Routing** — 根据失败类型（工具失败、验证失败、状态过期、权限不足）选择恢复策略
- **Stop Decision** — 判断继续执行、升级给用户、还是停止交付

详见 [`execution-depth/overview.md`](execution-depth/overview.md)。

## 未来可扩展的控制器

| 控制器 | 职责 | 触发条件 |
|---|---|---|
| **Recovery Controller** | 专门管理失败恢复策略选择、回退路径、降级方案 | 当恢复逻辑复杂到超出 Execution Depth Controller 的内联处理能力 |
| **Cost Controller** | 管理 token 消耗、API 调用成本、模型选择的成本约束 | 多模型 Kernel 场景，不同模型成本差异显著 |
| **Freshness Controller** | 管理 world state 的刷新策略、过期检测、refresh 调度 | 长时运行任务（D6）中外部状态频繁变化 |

## 子文件

| 路径 | 内容 |
|---|---|
| ~~`execution-depth/overview.md`~~ | 已迁移至 [`../kernel/execution-depth-controller/overview.md`](../kernel/execution-depth-controller/overview.md) |
