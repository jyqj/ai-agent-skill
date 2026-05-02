# Paradigm Routing

> **Evidence Status** — grounded. 从 Claude Code（ReAct/direct 动态选择）、Codex（guardian 切换策略）、Hermes Agent（多执行后端路由）的运行时行为中归纳。动态路由的系统化设计尚未在多数框架中被显式实现。

## 1. 问题

静态范式选择假设任务在启动时就能确定最佳推理策略。但生产中 Agent 经常需要在运行时切换范式：

```text
Coding Agent 理解需求时 → Direct/ReAct
           规划修改时 → Plan-and-Execute
           修复测试失败时 → Reflection
           比较多个方案时 → Tree Search
```

当前 `reasoning-paradigms.md` 和 `decision-trees.md` 提供了静态选择矩阵，但缺少：
- 运行时切换的触发条件
- 切换时的状态迁移协议
- 混合范式的组合约束

## 2. 范式路由模型

```text
ParadigmRouter = f(TaskSignal, ExecutionState, FailureHistory) → ActiveParadigm

TaskSignal:
  task_type_change    — 任务阶段变化（分析→规划→实现→验证）
  depth_change        — 执行深度升降级
  scope_change        — 目标范围扩大或缩小

ExecutionState:
  progress            — 当前完成度
  context_pressure    — 上下文窗口使用率
  tool_availability   — 当前可用工具集

FailureHistory:
  consecutive_failures — 连续失败次数
  failure_pattern      — 失败类型分布
  recovery_exhaustion  — 恢复策略是否用尽
```

## 3. 切换触发条件

| 触发信号 | 当前范式 | 切换目标 | 触发阈值 |
|---|---|---|---|
| 连续 3 次工具调用未收敛 | ReAct | Plan-and-Execute | consecutive_failures ≥ 3 |
| 计划步骤全部完成但验证失败 | Plan-and-Execute | Reflection | plan_complete && !verified |
| Reflection 未产生新证据 | Reflection | Escalation / Human | reflection_rounds ≥ 2 && no_new_evidence |
| 任务从分析进入实现 | Direct | ReAct | task_phase == "implement" |
| 多个等价方案需要比较 | ReAct | Tree Search | candidate_count ≥ 2 |
| 上下文窗口压力 > 80% | Plan-and-Execute | Direct + Compaction | context_pressure > 0.8 |
| 单步任务，无需多轮 | ReAct | Tool-Augmented Direct | estimated_steps == 1 |
| 高风险不可逆操作 | 任意 | Plan + Approval | risk_level == "high" |

## 4. 状态迁移协议

切换范式时，不是"重新开始"，而是迁移关键状态：

### 4.1 保留的状态

| 状态 | 说明 |
|---|---|
| TaskEnvelope | 目标、成功标准不变 |
| EffectRecord[] | 已完成的效果记录保留 |
| WorldStateSnapshot[] | 最新快照保留（检查 TTL） |
| FailureRecord[] | 失败历史保留，供新范式参考 |
| MemoryRecord[] | 长期记忆不受范式切换影响 |

### 4.2 重置的状态

| 状态 | 说明 |
|---|---|
| 当前计划（Plan） | 切换到新范式时旧计划失效 |
| ReAct 循环计数器 | 重新计数 |
| Reflection 轮次 | 重新计数 |
| Branch 预算 | 按新范式重新分配 |

### 4.3 迁移伪代码

```text
function switch_paradigm(current, target, state):
    # 1. 快照当前进度
    checkpoint = create_checkpoint(state)

    # 2. 提取可迁移状态
    portable = {
        task:          state.task_envelope,
        effects:       state.effect_records,
        world:         state.world_snapshots.filter(fresh),
        failures:      state.failure_records,
        context_summary: compact(state.context),  # 压缩当前上下文
    }

    # 3. 初始化新范式
    new_state = target.init(portable)

    # 4. 记录切换事件
    trace.append(ParadigmSwitch(
        from=current.name,
        to=target.name,
        trigger=trigger_signal,
        carried_effects=len(portable.effects),
        discarded=["plan", "loop_counter"],
    ))

    return new_state
```

## 5. 混合范式组合约束

不是所有范式都能任意嵌套。以下是组合规则：

### 5.1 可嵌套组合

| 外层 | 内层 | 场景 |
|---|---|---|
| ORDA-VU | ReAct | Decide/Act 阶段使用 ReAct 做工具交互 |
| ORDA-VU | Reflection | Verify 阶段使用 Reflection 做失败诊断 |
| Plan-and-Execute | ReAct | 每个 step 用 ReAct 执行 |
| Plan-and-Execute | Direct | 简单 step 直接执行 |
| Tree Search | ReAct | 每个 branch 用 ReAct 评估 |

### 5.2 互斥组合

| 组合 | 问题 |
|---|---|
| ReAct 嵌套 Plan-and-Execute | 内层规划会和外层观察循环冲突 |
| Reflection 嵌套 Reflection | 无限自省，无法收敛 |
| Tree Search 嵌套 Tree Search | 指数爆炸 |

### 5.3 组合深度限制

```text
最大嵌套深度 = 2
外层：生命周期范式（ORDA-VU / Plan-and-Execute）
内层：执行策略（ReAct / Direct / Reflection / Tree Search）
```

超过两层嵌套通常意味着任务拆分不够，应改为多 Agent 协作。

## 6. 常见失败与修复

| 失败 | 表现 | 修复 |
|---|---|---|
| 切换震荡 | 在两个范式间反复切换 | 加 cooldown（切换后至少执行 N 步才能再切换） |
| 状态丢失 | 切换后丢失已完成的效果 | 迁移协议必须保留 EffectRecord |
| 过度切换 | 每一步都重新选择范式 | 设置切换阈值，避免微小信号触发切换 |
| 切换后重做 | 新范式从零开始，忽略已有进度 | 迁移时传递 context_summary |
| 不切换 | 明显失败但坚持原范式 | 设置强制切换条件（如连续失败阈值） |

## 7. 实施清单

```text
[ ] 在 AgentLoop 中增加 ParadigmRouter 组件
[ ] 为每个范式定义可迁移状态和初始化接口
[ ] 设置切换冷却期（建议 ≥ 3 步）
[ ] 记录 ParadigmSwitch TraceEvent
[ ] 设置最大嵌套深度 = 2
[ ] 在 Eval 中增加范式切换场景的 fixture
[ ] 连续失败 ≥ 3 次时强制触发切换评估
```

## 8. 与本框架其他层的关系

| 层 | 关系 |
|---|---|
| `reasoning-paradigms.md` | 提供可选范式池；本文档定义运行时如何在池中切换 |
| `decision-trees.md` | 提供启动时选择；本文档补充运行时动态调整 |
| `architecture/lifecycle.md` | 范式切换是生命周期中的运行时事件 |
| `architecture/planes/state/` | 切换时的 checkpoint 保存/恢复 |
| `architecture/planes/context/` | 切换时的上下文压缩 |
| `architecture/planes/observability/` | ParadigmSwitch 作为 TraceEvent 记录 |
| `evaluation/` | 需要专门的范式切换评估 fixture |

## Evidence Status

混合来源。切换触发条件基于 Claude Code 和 Codex 的观察行为；状态迁移协议和组合约束为理论框架，尚未有项目显式实现完整的范式路由器。
