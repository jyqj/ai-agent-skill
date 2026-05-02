# Execution Depth Across Agent Types

> **Evidence Status** — synthesized. 从 coding、research、workflow、browser、ops、memory 等多个品类的项目中归纳的执行深度差异。

## 核心观察

不同品类的 Agent 需要"做到多深"差别巨大。Research Agent 可能只需要整理证据和组织报告，而 Browser Agent 必须点击、填写、提交并验证页面确实发生了变化。执行深度（Execution Depth）是选择架构复杂度的关键维度。

## 品类默认深度

| 品类 | 默认深度 | 为什么 |
|---|---|---|
| Personal Memory Agent | D2-D4 | 检索端较浅，但记忆写入和审计需要更深的验证 |
| Research Agent | D3-D4 | 核心在证据整理和断言验证，通常不直接改变外部世界 |
| Coding Agent | D4-D5 | 需要真实修改代码、运行测试、确认通过并恢复失败 |
| Enterprise Workflow | D4-D5 | 需要写入业务系统状态，配合审计和回读确认 |
| Browser/Desktop Agent | D5 | 点击成功不等于任务成功，必须验证页面和后端状态 |
| Ops/SRE Agent | D5-D6 | 长时监控、分阶段回滚、需要阶段汇报和人工升级 |

## 规律

执行深度越高，系统对以下能力的依赖越强：

- **状态连续性（State Continuity）**：中断后从断点恢复，而不是丢弃已完成的步骤重新执行整个计划
- **世界状态新鲜度（World State Freshness）**：在发起写动作前主动回读，确认前提条件（如分支状态、ticket 状态）未被外部改变
- **效果验证（Effect Verification）**：不信任工具返回值，通过独立回读（测试、截图、health check）确认外部世界的实际变化
- **恢复路由（Recovery Routing）**：区分瞬时故障、前提失效、语义错误等不同失败类型，分别采用重试、重新规划或人工升级

浅层 Agent 可以只靠模型能力和上下文管理；深层 Agent 必须有完整的 Harness 工程支撑。
