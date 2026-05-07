# Kernel 边界说明

> **Evidence Status** — synthesized. 基于 Agent Loop 伪代码和参考项目中 Kernel 与周边模块的实际交互关系归纳。

## 核心原则

Kernel 是**纯决策函数**：接收 ContextPack，输出 Decision。它不持有状态、不执行动作、不直接与外部世界交互。

所有副作用通过其他模块完成。Kernel 的边界清晰度直接决定系统的可测试性和可审计性。

## 边界矩阵

| 模块 | 方向 | 关系类型 | 说明 |
|---|---|---|---|
| **Prompting Plane** | Prompting → Kernel | 读 | Prompting 构造 system prompt、few-shot、格式指令，作为 ContextPack 的一部分送入 Kernel |
| **Context Engine** | Context → Kernel | 读 | Context Engine 将 task、observations、task_state、world_state 组装为 ContextPack，Kernel 消费但不修改 |
| **Tools Plane** | Kernel → Tools | 写 | Kernel 输出 `ToolCall` 意图（工具名、参数、intended_effect、verification_method），Tool Runtime 负责执行 |
| **Control Plane** | Control → Kernel | gate | Control 通过 precheck 和 verify 约束 Kernel 的行为。Kernel 的 Decision 必须通过 Control 的验证才能执行 |
| **Memory Plane** | Memory → Context → Kernel | 间接读 | Memory 提供检索结果给 Context Engine，Kernel 通过 ContextPack 间接获取历史信息，不直接调用 Memory 的读写接口 |
| **World State** | WorldState → Context → Kernel | 间接读 | World State 的快照通过 Context Engine 进入 ContextPack。Kernel 基于快照做决策，不直接查询或修改外部状态 |
| **Observability** | Kernel → Observability | 写 | Kernel 输出 DecisionEvent（决策类型、依据、耗时、置信度），供 trace、eval、审计使用 |
| **State Engine** | State → Context → Kernel | 间接读 | Task State、Decision Log、Effect Ledger 通过 Context Engine 进入 ContextPack。状态更新由主循环的 Update 步骤完成，不由 Kernel 触发 |

### 关系类型说明

- **读** — Kernel 从该模块获取信息，不改变该模块状态
- **写** — Kernel 向该模块输出数据（意图、事件），由该模块决定如何处理
- **gate** — 该模块对 Kernel 的输入或输出施加约束，可以阻止执行
- **间接读** — 信息经过中间模块（通常是 Context Engine）转换后到达 Kernel

## 数据流图

```text
Memory ──┐
          ├─→ Context Engine ──→ ContextPack ──→ Kernel ──→ Decision
World State ─┤                                      │           │
Task State ──┘                                      │           │
                                                    │           ├─→ Tools (ToolCall)
Prompting ──────────────────────────────────────────┘           ├─→ Observability (DecisionEvent)
                                                                └─→ Control (验证 gate)
```

## 禁止耦合

以下耦合模式在架构中被明确禁止：

### 1. Kernel 不直接执行系统命令

Kernel 输出 ToolCall 意图，由 Tool Runtime 在沙箱环境中执行。Kernel 不持有执行权限、不调用 subprocess、不访问文件系统。

**违反表现**: Kernel 内部直接调用 `os.system()`、`subprocess.run()` 或文件 I/O。

**修复**: 将所有执行逻辑封装为 Tool，通过 ToolCall 意图表达。

### 2. Kernel 不直接写入 Memory

记忆的写入由主循环的 Update 步骤根据 Decision 和执行结果决定。Kernel 可以在 Decision 中建议"这条信息值得记住"，但不直接调用 Memory 的写接口。

**违反表现**: Kernel 在决策过程中调用 `memory.store()` 或 `memory.update()`。

**修复**: 在 Decision 中附加 `memory_hints`，由 Update 步骤处理。

### 3. Kernel 不直接修改 World State

World State 的变更只能通过 Tool 执行产生。Kernel 不直接修改文件、数据库、API 状态或任何外部对象。

**违反表现**: Kernel 在决策过程中直接修改 `state.world_state` 的值。

**修复**: 所有状态变更通过 ToolCall → Tool Execution → Effect Record → State Update 链路完成。

### 4. Kernel 不绕过 Control 的策略检查

每个 Decision 在执行前必须通过 Control 的 precheck（预检）和 verify（后验）。Kernel 不能自行判断"这个动作安全所以不需要检查"。

**违反表现**: 在主循环中存在不经过 `runtime.control.precheck()` 或 `runtime.control.verify()` 的 ToolCall 执行路径。

**修复**: 确保主循环中所有 Decision → Execution 路径都经过 Control gate。

## 常见违反场景和修复

| 场景 | 违反 | 后果 | 修复 |
|---|---|---|---|
| "快速模式"跳过验证 | Kernel 的 Decision 直接送 Tool Runtime，不经 Control | 高风险动作无审批、无预算检查 | 即使快速模式也必须过 precheck，可以简化 verify |
| Kernel 内嵌 tool 执行 | 为了减少延迟，在 Kernel 内直接执行简单工具 | 绕过沙箱、权限控制、effect tracking | 所有工具执行走 Tool Runtime，无论复杂度 |
| 决策过程中刷新状态 | Kernel 发现信息不够，直接调 Memory/WorldState | 状态读取不受 freshness policy 控制 | Kernel 输出 `refresh_needed` Decision，由主循环处理 |
| 多模型 Kernel 内部通信 | Router 和专家模型直接共享内存 | 模型边界模糊，无法独立审计 | 模型间通信通过显式 message passing，每次传递可追踪 |
| Kernel 自行决定结束 | Kernel 输出 finalize 后直接返回 | 跳过 Stop Gate 的验证 | finalize 必须经过 `runtime.control.stop_gate()` 验证 |

## 边界检查清单

设计或审查 Kernel 实现时，逐条确认：

- [ ] Kernel 是否只接收 ContextPack、只输出 Decision？
- [ ] 是否所有 ToolCall 都通过 Tool Runtime 执行？
- [ ] 是否所有 Decision 都经过 Control 的 precheck/verify？
- [ ] Kernel 内部是否无直接的 Memory 读写？
- [ ] Kernel 内部是否无直接的 World State 修改？
- [ ] Kernel 是否输出了足够的 DecisionEvent 供审计？
- [ ] 多模型 Kernel 的模型间通信是否可追踪？
