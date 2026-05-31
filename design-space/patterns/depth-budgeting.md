# Depth Budgeting Pattern

> **Evidence Status** — synthesized. 从多个成熟 Agent 运行时中提炼的控制模式（step/tool/token/retry 等），具体默认值仍需按产品类型验证。

## 问题

Agent 做长任务时的两种典型失败模式看似相反，但根源相同：缺乏资源边界。一边是无限探索——反复调用工具、重复失败、成本失控；另一边是过早停止——任务还没完成就放弃了。没有预算约束的 Agent 不知道什么时候该停，也不知道什么时候不该停。

## 解法

为任务设置多维预算（Depth Budget），并在每个里程碑（Milestone）后重新分配剩余资源。

```text
Depth Budget = Step + Tool + Token + Risk + Time + Branch + Retry + User Attention
```

## 八种预算维度

**Step Budget** 控制执行步数。设得太低，Agent 在复杂任务上被迫提前终止；设得太高，容易陷入无限循环。这是最基础的安全阀。

**Tool Budget** 控制工具调用总量。过低导致证据不足、结论缺乏支撑；过高则成本失控，尤其是涉及付费 API 时。

**Token Budget** 控制上下文消耗。过低意味着信息不足以完成推理；过高则引入上下文污染（Context Pollution），噪声淹没关键信息。

**Risk Budget** 控制自动化操作的风险上限。过低使 Agent 执行太浅，什么都需要人工确认；过高则可能越权操作，例如删除数据、发送邮件、修改生产配置。

**Time Budget** 控制实际运行时间。长任务需要足够的时间窗口，但用户不应无限等待。

**Branch Budget** 控制并行探索的分支数量。只走一条路可能错过更优方案；分支太多则合并困难，资源分散。

**Retry Budget** 控制失败重试，但必须按失败类型（Failure Type）分别计数，而不是全局简单累加。同一类错误反复重试毫无意义，不同类型的错误则各自值得尝试。

**Attention Budget** 控制打扰用户的次数。过低时 Agent 卡在不确定处无法推进；过高则沦为"每一步都问一句"的交互模式，失去自主性。

## 运行逻辑

```pseudo
budget = {
  steps: 30,
  tools: 50,
  tokens: 100000,
  risk: "check",
  approvals: 5,
  branches: 2,
  retries_per_failure_type: 2
}

for milestone in task_graph:
  local_budget = allocate(budget, milestone)
  result = run_milestone(milestone, local_budget)
  budget = update_budget(budget, result)

  if result.failed:
    if budget.retry_available(result.failure_type):
      recover_and_retry(result.failure_type)
    else:
      stop_with_evidence_and_blocker()

  if budget.exhausted():
    summarize_and_escalate()
```

关键点在于 `allocate` 和 `update_budget`：每完成一个里程碑，剩余预算根据实际消耗和任务进展重新分配，而不是平均切分。

## 适用场景

任何超过"单轮问答"复杂度的 Agent 系统（Coding Agent、Research Agent、企业流程 Agent、长时运行 Agent）都需要某种形式的深度预算。
