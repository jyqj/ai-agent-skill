# Task Prioritization

> **Evidence Status** — synthesized. Gulli (2025) *Agentic Design Patterns* Ch20 + 多项目观察归纳。

## 问题

Agent 在多任务、多目标竞争下缺乏排序机制，导致低优先级任务占用资源、高优先级任务延迟、整体效率低下。

## 解法

建立显式的优先级评估-排序-调度机制，使 Agent 在资源约束下始终处理最高价值任务。

## 优先级评估标准

| 标准 | 权重因素 | 说明 |
|---|---|---|
| **Urgency** | 时间敏感性、截止日期 | 越紧迫权重越高 |
| **Importance** | 对主目标的影响程度 | 核心路径 vs 边缘任务 |
| **Dependencies** | 是否是其他任务的前置条件 | 阻塞链上游任务优先 |
| **Resource Cost** | 完成所需计算/时间/预算 | 低成本高收益优先 |
| **User Preference** | 用户明确指定的偏好 | 覆盖其他启发式 |
| **Risk** | 延迟的潜在负面后果 | 高风险延迟 → 升级优先 |

## 优先级分层

```text
Strategic Level    → 选择整体目标（"完成 PR review" vs "修复 CI"）
Tactical Level     → 子任务排序（"先读代码" → "再改代码" → "最后跑测试"）
Action Level       → 即时动作选择（"读哪个文件" → "用哪个工具"）
```

每一层的排序独立但受上层约束：战略目标确定后，战术排序在该目标内进行。

## 动态重排序

触发条件：
- 新的 critical event 到达（用户中断、CI 失败通知）
- 接近 deadline
- 资源预算变化（剩余 token 不足）
- 子任务完成后暴露新信息

重排序协议：
1. 暂停当前执行（在 checkpoint 处）
2. 重新评估所有待处理任务的优先级
3. 如果最高优先级任务变化，切换执行
4. 记录切换原因到 trace

## 与知识库其他模块的关系

| Plane | 交互方式 |
|---|---|
| Orchestration | 优先级排序是编排决策的输入信号 |
| Cost | 预算约束作为优先级的硬性过滤器 |
| Execution | 执行深度受优先级影响（高优先 → 更深验证） |
| State | 任务队列和优先级状态需要持久化 |
| Recovery | 恢复后需要重新评估优先级（可能已过期） |
| Interaction | 用户可显式调整优先级（覆盖启发式） |

## 实现模式

### P-Level 分级
```text
P0 — 阻塞性：必须立即处理（生产事故、安全告警）
P1 — 重要：当前迭代必须完成（主要功能、关键 bug）
P2 — 常规：计划内的标准工作
P3 — 低优先：有空再做（优化、文档补全）
```

### 评估函数

```text
priority_score = w_urgency * urgency
              + w_importance * importance
              + w_dependency * dependency_weight
              - w_cost * normalized_cost
              + w_user * user_override
```

权重可通过学习循环持续校准（→ Learning Plane）。

## 反模式

- **FIFO Blindness**：先到先服务，忽略任务价值差异
- **Starvation**：低优先级任务永远得不到执行 → 需要 aging 机制
- **Thrashing**：频繁重排序导致没有任务能完成 → 需要最小执行窗口
- **Priority Inversion**：高优先级任务被低优先级任务的依赖阻塞 → 需要优先级继承

## 参考

- Gulli, A. (2025). *Agentic Design Patterns*, Ch20: Prioritization.
- Claude Code: 隐式优先级——用户最新指令覆盖之前的任务
- Codex: Guardian 审批缓存 → 审批任务优先于执行任务
