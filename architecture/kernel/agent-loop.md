# Agent Loop

> **Evidence Status** — grounded. 基于 Claude Code、OpenCode、Codex 等系统对 query loop、compaction、权限控制、subtask、重试的实际实现归纳。

## 问题

如何让 LLM 持续把任务推进到**可验证完成**？

最小答案是循环；生产级答案是把循环嵌入现实闭环。

## 最小闭环

单看模型，最小循环可以写成 TAO：Thought → Action → Observation。

但生产系统里，TAO 还不够，因为它没有显式回答：
- 观察到的东西是什么表示？
- 这个表示是否可靠、新鲜、可回查？
- 动作想改变什么外部对象？
- 工具成功后，现实是否真的改变？

因此更完整的主循环应写成：

```text
Observe → Represent → Decide → Act → Sense / Verify → Update
```

## 六步解释

### 1. Observe
采集当前任务相关的原始世界切片：用户输入、文件、网页、日志、DOM、数据库记录、传感器事件、工具回读。

### 2. Represent
将原始输入转成可处理表示，并记录：
- raw ref
- parser / transform chain
- confidence
- freshness
- trust tier
- lossy / replayable

### 3. Decide
结合目标、状态、预算、约束、world state 和记忆，决定下一步。Decide 的输入包含 PromptContract 中指定的 `reasoning_mode`，输出是一个结构化 Decision：

```yaml
decision:
  type: tool_call | tool_call_batch | plan_step | reflection | delegation | ask_human | finalize | stop_with_evidence
  reasoning_mode: direct | react | plan_execute | reflection | critique
  payload: {}          # 按 type 不同携带不同内容
  confidence: float
  rationale: string
```

不同范式产生不同的 decision type 分布：

| 范式 | 主要 decision types | Kernel 行为差异 |
|---|---|---|
| Direct | tool_call, finalize | 单步决策，无中间状态 |
| ReAct | tool_call, tool_call（嵌套） | 每次 tool_call 结果重新进入 Decide |
| Plan-Execute | plan_step → tool_call（逐步） | 先输出 plan，再逐步执行 |
| Reflection | tool_call → reflection → tool_call | Verify 后回到 Decide 做自检修正 |
| Delegation | delegation | 创建子任务，等待子 Agent 返回 |

Kernel 本身不实现范式逻辑，只根据 decision.type 调度到对应的执行路径。范式选择由 Prompting Plane 的 `reasoning_mode` 驱动。

### 4. Act
通过 Tool Runtime 和 Execution Host 发起动作，并显式声明：
- intended_effect
- target world objects
- preconditions
- postconditions
- verification method

### 5. Sense / Verify
对动作结果做四层验证：
- structural verification
- execution verification
- effect verification
- claim verification

### 6. Update
更新：
- task state
- world state snapshots
- effect ledger
- decision log
- trace / eval events
- recovery route

### ORDA-VU 完整数据流

下图展示主循环的完整数据流，包含正常路径和失败恢复路径：

```mermaid
graph LR
    O[Observe<br/>采集原始信号] --> R[Represent<br/>编码+trust/freshness]
    R --> D[Decide<br/>目标+状态+预算]
    D --> A[Act<br/>工具执行]
    A --> V[Verify<br/>效果校验<br/>structural/execution/effect/claim]
    V -->|pass| U[Update<br/>state/world/effect/trace]
    V -->|fail| REC[Recovery<br/>重试/补偿/升级]
    REC --> D
    U -->|下一轮| O
    D -->|finalize + stop gate pass| DEL[Deliver<br/>交付结果]
    D -->|ask_human| HI[Human Interaction<br/>审批/纠错]
    HI --> D
```

## 伪代码

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class LoopState:
    task: dict
    context: dict
    task_state: dict
    world_state: dict
    pending_effects: list[dict]
    budgets: dict
    trace_id: str


def agent_loop(task_envelope: dict, runtime: Any, max_steps: int) -> dict:
    state = runtime.bootstrap(task_envelope)

    for step in range(max_steps):
        # ── Observe & Represent ──
        raw_inputs = runtime.observe(state)
        observations = runtime.representation.build(raw_inputs)

        # ── Governance Pre-check ──
        verdict = runtime.control.precheck(
            observations=observations,
            world_state=state.world_state,
            budgets=state.budgets,
        )
        if verdict == "refresh_required":
            state.world_state = runtime.world_state.refresh(state)
            continue
        if verdict == "blocked":
            return runtime.finish_blocked(state)

        # ── Build Context ──
        context_pack = runtime.context.build(
            task=state.task,
            observations=observations,
            task_state=state.task_state,
            world_state=state.world_state,
        )

        # ── Decide（范式无关：reasoning_mode 由 PromptContract 指定）──
        decision = runtime.kernel.decide(context_pack)

        # ── 按 decision.type 分发 ──
        if decision.type == "finalize":
            if runtime.control.stop_gate(state):
                return runtime.finish_success(state)
            # stop gate 不满足时，要求补充验证而非直接结束
            decision = runtime.kernel.plan_next_verification(context_pack)

        if decision.type in ("tool_call", "tool_call_batch"):
            calls = decision.tool_calls if decision.type == "tool_call_batch" else [decision.tool_call]
            for call in calls:
                tool_result = runtime.tools.execute(call)
                effect_record = runtime.effects.record(call, tool_result)
                runtime.observability.emit(tool_result, effect_record)
                verification = runtime.control.verify(
                    tool_result=tool_result,
                    effect_record=effect_record,
                    verification_method=call.get("verification_method"),
                )
                state = runtime.state.update(
                    state=state, observations=observations,
                    tool_result=tool_result, effect_record=effect_record,
                    verification=verification,
                )
                if verification.needs_recovery:
                    state = runtime.controllers.recover(state, verification)
                    break  # 恢复后重新进入主循环

        elif decision.type == "plan_step":
            # Plan-Execute 范式：将计划存入 task_state，下一轮执行第一步
            state.task_state["plan"] = decision.plan
            state.task_state["current_step"] = 0

        elif decision.type == "reflection":
            # Reflection 范式：自检后修正策略，不产生外部效果
            state.task_state["reflection_log"] = decision.reflection
            # 下一轮 Decide 会看到 reflection_log 并调整行为

        elif decision.type == "delegation":
            # 多 Agent：创建子任务并等待
            sub_result = runtime.orchestration.delegate(decision.sub_task, state)
            state = runtime.state.merge_sub_result(state, sub_result)

        elif decision.type == "ask_human":
            return runtime.finish_waiting_approval(state, decision)

        elif decision.type == "stop_with_evidence":
            return runtime.finish_partial(state)

    return runtime.finish_budget_exhausted(state)
```

## Stop Gate：什么时候能停

成熟 Agent 的结束判定需要多项条件同时满足，而非依赖模型自行宣布完成：

```text
required_depth reached
+ key deliverables present
+ critical representation issues resolved
+ critical world state fresh enough
+ required effects verified
+ remaining risks explained
```

## 生产级保护机制

### 1. 多层预算
- step budget
- tool budget
- token / context budget
- retry budget
- approval budget
- risk budget

### 2. 循环检测
- 相同工具连续重复
- 相同 world state 上反复动作
- 相同失败模式无新证据重试

#### Doom Loop 语义检测

简单的轮数上限无法区分"有效重试"和"退化循环"。OpenCode 的语义检测方案提供了更精确的拦截：

检测条件：最近 N 次工具调用（默认 N=3）同时满足：
1. 调用同一个工具
2. 传入完全相同的参数
3. 均已完成（非 pending）

触发动作：请求用户权限确认是否继续，而非强行中止。

这比轮数上限更精准，因为它允许不同操作的多次尝试，只拦截真正的退化行为。Codex 采用类似思路但阈值更低（连续 2 次相同调用即告警）。Hermes 通过错误分类树将不同失败类型映射到不同的重试策略，从源头减少无效重试。

### 3. 状态外置
- checkpoint
- decision log
- effect ledger
- world state snapshot

### 4. stale state 防护
- 写动作前 refresh 关键 world object
- 最终交付前重新读回关键状态
- eventual consistency 场景采用 poll / backoff

### 5. 不可信输入隔离
- tool output / web page / email / log 默认进入 untrusted lane
- 不能直接升级为可执行 instruction

## 循环恢复策略

Agent loop 在运行时会遇到多种可恢复错误。以下是从生产系统中提炼的恢复策略分类：

| 错误类型 | 触发条件 | 恢复方式 | circuit breaker |
|---------|---------|---------|----------------|
| output_tokens_escalate | 输出触及 8K 上限 | 提升上限到 64K，重试同一请求 | — |
| output_tokens_recovery | 多次触及上限 | 注入恢复消息 | 连续 3 次后放弃 |
| context_overflow | token 用量 >= 阈值 | 触发压缩管线 | 连续 3 次压缩失败后放弃 |
| model_fallback | 主模型不可用 | 切换备用模型，清空已队列工具结果 | — |
| reactive_compact | 被动压缩失败 | 重试一次 | 单次机会 |
| tool_execution_error | 工具调用返回异常 | 按错误分类树选择重试/跳过/降级 | 同一工具连续 3 次失败后跳过 |
| rate_limit | API 速率受限 | exponential backoff（1s/2s/4s） | 累计 5 次后切换 provider |

> 来源：Claude Code query.ts 的 State.transition 机制。每次恢复都记录路径，防止同一恢复策略无限重试。Hermes 的错误分类树和 Codex 的 CancellationToken 提供了互补的恢复视角。

### 恢复决策树

```mermaid
flowchart TD
    ERR[错误发生] --> CLS{错误分类}

    CLS -->|output_tokens| OT{触及次数}
    OT -->|首次| ESC[提升上限到 64K<br/>重试同一请求]
    OT -->|2-3 次| REC[注入恢复消息<br/>缩减输出范围]
    OT -->|>3 次| FAIL_OT[放弃当前请求<br/>记录失败路径]

    CLS -->|context_overflow| CTX{压缩尝试次数}
    CTX -->|<3 次| CMP[触发压缩管线<br/>裁剪历史/摘要化]
    CTX -->|>=3 次| FAIL_CTX[停止循环<br/>返回 budget_exhausted]

    CLS -->|model_unavailable| MF[切换备用模型<br/>清空已队列工具结果<br/>重试]

    CLS -->|tool_error| TE{错误可重试?}
    TE -->|是 & <3 次| RETRY[backoff 重试]
    TE -->|是 & >=3 次| SKIP[跳过该工具<br/>标记 degraded]
    TE -->|否| FAIL_TE[记录不可恢复错误<br/>ask_human 或 stop_with_evidence]

    CLS -->|rate_limit| RL{累计次数}
    RL -->|<5 次| BACK[exponential backoff]
    RL -->|>=5 次| SWITCH[切换 provider]

    ESC --> LOOP[恢复后重新进入主循环]
    REC --> LOOP
    CMP --> LOOP
    MF --> LOOP
    RETRY --> LOOP
    BACK --> LOOP
    SWITCH --> LOOP
```

每条恢复路径都记录到 `recovery_route`（Update 步骤），用于：
- 事后审计哪些恢复策略被频繁触发
- 运行时检测恢复策略是否陷入循环（同一路径连续触发 N 次 → circuit breaker）
- 为 doom loop 检测提供额外信号（恢复路径重复 = 退化证据）

## 与经典循环的关系

| 形态 | 适用 | 局限 |
|---|---|---|
| TAO / ReAct | 简单探索、demo、低风险任务 | 没有显式表示层、world state、effect verification |
| Plan-then-Execute | 结构清晰、可审查 | 遇到新观察时计划可能过时 |
| ORDA-VU（Observe → Represent → Decide → Act → Verify → Update） | 生产级任务闭环 | 复杂度更高，需要更多运行时模块 |

## 从参考项目学到的生产细节

### Claude Code
- generator 式 query loop 支持流式事件和提前终止
- 循环内做多层 compaction
- 把 trace、状态、权限检查织进主循环，而不是散在工具外

### OpenCode
- subtask / compaction / normal processing 有显式优先级
- doom loop 检测进入权限系统
- retry / backoff 与错误类型绑定

### Codex
- execution sandbox 和 guardian policy 是循环能否放开执行深度的前提，需在主循环内集成

## 常见反模式

| 反模式 | 表现 | 修复 |
|---|---|---|
| Chat Loop Disguised as Agent | 看似多轮，其实没有状态和效果验证 | 补 state / effects / stop gate |
| Action Without Representation | 没确认输入质量就开做 | representation gate |
| Tool Success = Task Success | 工具成功就宣布完成 | effect verification |
| Memory-as-Context Dump | 把记忆直接全塞上下文 | disclosure + trust lanes |
| Retry Until Budget Dies | 无新证据重复尝试 | failure-mode-aware recovery |

## 实现模式分类

不同 Agent 系统对主循环采用了不同的工程实现模式。以下四种在生产项目中被验证过：

| 模式 | 代表项目 | 核心机制 | 适用场景 |
|------|---------|---------|---------|
| Generator/流式生成器 | Claude Code, GenericAgent | async generator yield 每个 token/chunk | 需要实时 UI 反馈、可暂停恢复 |
| Event-driven/事件驱动 | Codex | Submission→Event 通道，多路分发 | 高并发、多 Agent 协调、分布式追踪 |
| Atomic Turn/原子轮次 | Hermes | 每轮完整请求-响应，轮间持久化 | 崩溃恢复优先、多维预算控制 |
| Effect/函数式 | OpenCode | Effect.js Layer + DI，不可变状态容器 | 类型安全、可测试性、声明式组合 |

### Generator 模式细节

核心机制是将主循环实现为异步生成器（async generator / yield），每个 token 或 chunk 到达时即刻 yield 给消费者。

关键特征：
- 消费者可随时暂停/恢复（背压控制）
- 内存高效：无需等待完整响应再处理
- 工具调用本身也可以是嵌套生成器（如 code_run 逐行 yield 执行输出）
- 天然支持中断：检查 abort signal 后 return 即可

Claude Code 实现：`QueryEngine.submitMessage()` 是 async generator，yield 流式 token 和工具进度。
GenericAgent 实现：`agent_runner_loop()` 是 Python generator，yield from 嵌套委托工具生成器。

权衡：
- 调试困难：生成器的调用栈不如同步代码直观
- 状态管理复杂：生成器恢复时需确保上下文一致
- 不适合需要原子性保证的场景（崩溃时 yield 的中间状态可能不一致）

```mermaid
graph TD
    Q{需要实时流式反馈?}
    Q -->|是| G[Generator 模式<br/>Claude Code / GenericAgent]
    Q -->|否| Q2{需要高并发多 Agent?}
    Q2 -->|是| E[Event-driven 模式<br/>Codex]
    Q2 -->|否| Q3{崩溃恢复是否关键?}
    Q3 -->|是| A[Atomic Turn 模式<br/>Hermes]
    Q3 -->|否| F[Effect 模式<br/>OpenCode]
```

### 循环实现模型运行时对比

上述四种模式在运行时行为上有关键差异，以下从上下文传递、取消机制、适用场景三个维度对比：

| 模型 | 代表项目 | 上下文传递 | 取消机制 | 适用场景 |
|------|---------|-----------|---------|---------|
| Generator/yield | Claude Code | 堆栈帧隐式保留，yield 点自动挂起恢复 | 协作式（检查 abort signal 后 return） | 单线程、流式输出、需要背压控制 |
| Event-driven + bounded channel | Codex | `Arc<TurnContext>` 显式传递，跨线程共享 | `CancellationToken` 抢占式，支持 timeout | 多任务并行、Rust 生态、分布式追踪 |
| 消息不累积（每轮只发最新） | GenericAgent | 摘要注入替代历史，每轮 context 独立构建 | 简单退出（无需复杂取消） | 极简 loop、token 成本敏感（<4K/轮） |
| Atomic Turn + 轮间持久化 | Hermes | SQLite 存储轮间状态，每轮从 DB 重建 | 进程级 graceful shutdown | 崩溃恢复优先、长运行任务、多维预算 |

选择依据：
- 如果需要流式输出且单线程足够 → Generator
- 如果需要多 agent 并行或跨进程协调 → Event-driven
- 如果 token 预算极紧（每轮 <4K tokens） → 消息不累积
- 如果任务可能跨小时/天运行且中途可能崩溃 → Atomic Turn

## 参考实现

- `projects/coding-agents/claude-code/query-loop.md` — 生产系统主循环观察
- `projects/coding-agents/opencode/orchestration.md` — Effect.js 循环 + Doom Loop 检测
- `projects/coding-agents/codex/orchestrator.md` — 编排与受控执行
