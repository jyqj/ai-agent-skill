# Kernel

> **Evidence Status** — grounded. 基于 Claude Code、OpenCode、Codex 等系统的决策核心实现归纳。

## 定位

Kernel 是 Agent 运行时的**决策核心**：接收 `ContextPack`，输出 `Decision`。

Kernel 是 ORDA-VU 六步循环中 **Decide** 步骤的实现者（非独立 Plane）。它回答的核心问题是：

> 给定当前目标、状态、预算、约束、world state 和记忆，下一步该做什么？

Kernel 的输出是一个 `Decision`，类型包括：

- `tool_call` — 调用工具执行动作
- `finalize` — 请求结束（需通过 Stop Gate）
- `ask_human` — 升级给用户
- `stop_with_evidence` — 预算耗尽或无法继续，带证据停止

## 与其他模块的边界

| 边界 | 职责划分 |
|---|---|
| **Kernel vs Prompting Plane** | Prompting 构造输入（system prompt、few-shot、格式指令）送给 Kernel。Kernel 不负责 prompt 工程，只消费最终 prompt |
| **Kernel vs Control Plane** | Control 是 Kernel 的约束层。Kernel 的 Decision 必须通过 Control 的 precheck 和 verify。Control 定义策略，Kernel 服从策略 |
| **Kernel vs Memory Plane** | Memory 提供检索结果给 Context 构建过程。Kernel 通过 ContextPack 间接获取历史信息，不直接操作 Memory 的读写 |
| **Kernel vs Tools Plane** | Kernel 输出 `ToolCall` 意图（工具名、参数、预期效果、验证方法）。Tool Runtime 负责实际执行、沙箱隔离和结果回传 |

详细边界矩阵见 [`boundaries.md`](boundaries.md)。

## Kernel 的实现选择

从最简单到最复杂，Kernel 有四种典型实现形态：

### 1. 单次 LLM 调用

最简形态。ContextPack 直接拼成 prompt，一次调用返回 Decision。

- 适用：D0-D2 低深度任务、延迟敏感场景
- 局限：无自我纠正能力，输出质量完全依赖 prompt 质量

### 2. LLM + 后处理规则

LLM 输出结构化内容（JSON / tool_use），后处理层做 schema 验证、字段补全、安全检查。

- 适用：需要可靠结构化输出的生产系统
- 典型实现：Claude Code 的 tool_use 模式 + JSON schema 验证

### 3. 多步 LLM 推理

单次决策内进行 chain-of-thought、self-critique、reflection。Kernel 内部形成 mini-loop。

- 适用：高风险决策、复杂推理任务
- 局限：延迟和 token 成本显著增加

### 4. 多模型 Kernel

Router 模型判断任务类型，分发到专家模型。不同深度、不同领域使用不同模型。

- 适用：大规模 Agent 平台、成本优化场景
- 典型架构：轻量 router + 重量级 reasoning model + 快速 coding model
- 参考：`architecture/multi-model/` 目录

## 与 ORDA-VU 的关系

```text
Observe → Represent → [Decide] → Act → Verify → Update
                        ↑
                      Kernel
```

Kernel 只负责 Decide 这一步。它的输入来自 Observe + Represent 的结果（封装为 ContextPack），它的输出交给 Act 阶段的 Tool Runtime 执行。

Kernel 不执行动作、不验证结果、不更新状态。这些职责分别属于 Tools Plane、Control Plane 和 State Engine。

## 从参考项目学到的

### Claude Code

- generator 式 query loop：Kernel（LLM 调用）嵌入 generator，支持流式事件和提前终止
- 多层 compaction 在 Kernel 调用前完成，确保 ContextPack 不超限
- 权限检查织进主循环，作为循环内步骤而非外挂组件

### Codex

- guardian policy 前置于 Kernel 决策：先过策略检查，再调用 LLM
- execution sandbox 是 Kernel 能输出高深度 ToolCall 的前提条件

### OpenCode

- subtask / compaction / normal processing 有显式优先级，Kernel 根据 task state 选择处理路径
- doom loop 检测在 Kernel 层面触发，进入权限系统而非简单重试

## 子文件

| 文件 | 内容 |
|---|---|
| [`execution-depth-controller/overview.md`](execution-depth-controller/overview.md) | Execution Depth Controller：D0-D6 分级、深度推进、预算分配、里程碑验证、9 个瓶颈（从 controllers/ 迁入） |
| [`agent-loop.md`](agent-loop.md) | Agent 主循环伪代码、六步解释、Stop Gate、生产级保护机制、常见反模式 |
| [`boundaries.md`](boundaries.md) | Kernel 与周边模块的边界矩阵、禁止耦合规则、常见违反和修复 |
| [`permission-decision.md`](permission-decision.md) | 权限决策通用流程：三态输出、多源规则堆叠、参数键缓存、拒绝跟踪 |
| [`tool-lifecycle.md`](tool-lifecycle.md) | 工具调用完整生命周期：定义、发现、执行、并发分区、结果回收 |
| [`context-budget.md`](context-budget.md) | 上下文预算管理：退化模型、多触发条件、五级压缩管线、恢复预算 |
| [`effect-verification.md`](effect-verification.md) | 效果验证：Ghost Success、验证方法矩阵、EffectRecord、退化策略、补偿事务 |
