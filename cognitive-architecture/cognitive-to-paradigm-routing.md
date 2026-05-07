# 认知需求驱动的范式路由

> **Evidence Status** — synthesized. Wray et al. (2025) "Applying Cognitive Design Patterns to LLM Agents" 提供了 Soar/ACT-R 到 Agent 范式的映射框架；FoT (arXiv 2602.16512) 提出流式思维对 ReAct 循环的改进；SOFAI (Nature 2025) 描述了双过程元认知调度架构；Zylos Session-Governor-Executor 三层治理提供了生产参考。本文为交叉综合推导，尚未经系统性实证验证。

## 1. 为什么需要这篇

`paradigms/paradigm-routing.md` 回答的是"运行时何时切换范式"——触发信号来自执行状态（连续失败、上下文压力、任务阶段变化）。但这些信号是**症状**，不是**原因**。

范式选择应首先由认知需求驱动：

```text
当前问题：
  paradigm-routing.md          本文
  "什么信号触发切换"           "为什么需要这个范式"
  执行状态驱动                 认知需求驱动
  reactive routing             proactive routing
```

举例：一个 Debug 任务需要溯因推理 + 假设排除 + 工作记忆中并行追踪多个候选。这些认知需求决定了 ReAct 单步循环不够——需要 Plan-Execute 或 Reflection 范式来支撑假设管理。如果只看"连续 3 次工具调用未收敛"才切换，已经浪费了 3 次迭代。

## 2. 认知设计模式到 Agent 范式的映射

以下 7 个认知设计模式来自 Soar 和 ACT-R 的经典架构，每个都有对应的 Agent 范式映射和已知局限。

| # | 认知设计模式 | 来源 | Agent 范式映射 | 已知局限 |
|---|---|---|---|---|
| 1 | Observe-Decide-Act (ODA) | Soar decision cycle | ReAct | **缺少显式 commitment 步骤**——Soar 的 decision cycle 包含 preference 评估和 commitment，ReAct 直接从 thought 跳到 action |
| 2 | 层级任务分解 | ACT-R goal stack / Soar subgoaling | Plan-Execute | Plan 粒度与 goal stack 深度需要匹配 |
| 3 | 知识编译 | ACT-R production compilation | Skill 固化 | LLM Agent 的"编译"是 prompt 模板化，不是真正的程序化加速 |
| 4 | 冲突解决 | Soar preference evaluation | 多方案比较 / Tree Search | LLM 的偏好评估缺乏 Soar 的形式化保证 |
| 5 | Impasse 检测与恢复 | Soar impasse mechanism | Reflection + Escalation | Soar 自动检测 impasse；LLM Agent 需要显式触发条件 |
| 6 | 传播激活 | ACT-R spreading activation | Retrieval-Augmented Generation | RAG 的相似度检索是 spreading activation 的简化版本 |
| 7 | 元认知监控 | Soar meta-level reasoning | Metacognitive Control Loop | 见 `metacognitive-control.md` |

### 2.1 ReAct 的 commitment 缺口

Soar 的 ODA 循环实际包含四步：Observe → Propose → Evaluate → Act。Evaluate 阶段通过偏好规则（acceptable / best / worst / indifferent）对候选行动进行排序，**显式 commit** 到一个行动后才执行。

ReAct 模式将 Thought → Action 直接相连，缺少偏好评估和显式 commitment：

```text
Soar:   Observe → Propose candidates → Evaluate preferences → Commit → Act
ReAct:  Observe → Thought(单一候选) ──────────────────────→ Act
                   ↑ 缺少多候选评估和显式承诺
```

**设计建议**：在高风险决策点引入显式 commitment 步骤——列出候选行动、评估各自预期结果、选定后记录 commitment 理由。这对应 `paradigms/decision-trees.md` 中"风险高或写动作不可逆 → Plan + Approval + Verification Gate"的分支。

## 3. 双过程理论与范式选择

Kahneman 的 System 1 / System 2 区分在 Agent 架构中有直接映射：

| 维度 | System 1（快速/自动） | System 2（慢速/审慎） |
|---|---|---|
| 认知特征 | 模式匹配、习惯化响应、低认知负载 | 逻辑推理、假设验证、高认知负载 |
| Agent 范式 | FSM / 规则引擎 / Direct Answer | ReAct / Plan-Execute / Reflection |
| 触发条件 | 任务已见过、风险低、模式匹配成功 | 任务新颖、风险高、模式匹配失败 |
| 运行时成本 | token 少、延迟低 | token 多、延迟高 |
| 错误倾向 | 偏见、过度泛化、忽略异常 | 过度分析、延迟行动、资源消耗 |

### 3.1 SOFAI 架构：元认知调度器

SOFAI (Sloman's Orthogonal Framework for AI, Nature 2025) 提出一个显式的**元认知模块**负责在快/慢求解器之间调度：

```text
                  ┌─────────────────┐
                  │  Metacognitive   │
                  │   Dispatcher     │
                  └──┬──────────┬───┘
                     │          │
            ┌────────▼──┐  ┌───▼────────┐
            │  System 1  │  │  System 2   │
            │  Fast      │  │  Slow       │
            │  Solver    │  │  Solver     │
            └────────────┘  └─────────────┘

调度信号：
  - novelty score（任务与已知模式的距离）
  - risk level（操作的不可逆程度）
  - confidence gap（System 1 输出的置信度是否低于阈值）
  - time pressure（响应延迟预算）
```

**映射到 Agent 运行时**：

| 调度信号 | 低值 → System 1 | 高值 → System 2 |
|---|---|---|
| novelty | 模式匹配命中 → Direct/FSM | 未见过的任务类型 → ReAct/Plan |
| risk | 只读操作 → 直接执行 | 不可逆写入 → Plan + Approval |
| confidence gap | 高置信输出 → 直接返回 | 低置信 → Reflection + 多方案比较 |
| time pressure | 高时间压力 → 牺牲深度换速度 | 低时间压力 → 允许深度推理 |

## 4. 认知负载信号作为范式切换触发器

超越 `paradigm-routing.md` 中基于执行失败的被动切换，认知负载提供**主动**切换信号：

| 认知负载信号 | 测量方式 | 阈值 | 范式响应 |
|---|---|---|---|
| 工作记忆利用率 60-70% | context_tokens / max_tokens | 0.6-0.7 | 触发 compaction；切换到更简洁的范式（Plan-Execute → Direct + checkpoint） |
| 工作记忆利用率 > 80% | context_tokens / max_tokens | 0.8 | 强制 compaction + 子任务拆分 + 外化到 scratchpad |
| 推理链深度 > 阈值 | 连续 thought-action 步数 | 品类相关（Coding: 15, Browser: 8） | 暂停推理 → 生成中间摘要 → 重新评估方向 |
| 重复行动检测 | action 序列的重复模式 | 连续 2 次相同 action | impasse 检测 → 切换到 Reflection 或升级策略 |
| 假设栈溢出 | 并行追踪的候选假设数 | > 4（Cowan 容量限制） | 强制排序 → 修剪低优先级假设 → 聚焦 top 2 |
| 目标漂移检测 | 当前行动与原始目标的相关性评分 | 相关性 < 0.5 | 暂停 → 重新锚定目标 → 可能回退到 Plan 层 |

## 5. 认知特征 x 任务风险 x 模型能力 → 推荐范式

以下决策表综合三个维度：

| 认知特征 | 任务风险 | 模型能力 | 推荐范式组合 | 备注 |
|---|---|---|---|---|
| 高演绎 + 高工作记忆 | 高 | 强 | Plan-Execute + Verification Gate + Reflection | Coding Agent 典型 |
| 高演绎 + 高工作记忆 | 高 | 弱 | Plan-Execute + Human Approval + 保守执行 | 弱模型需更多护栏 |
| 高溯因 + 高注意力 | 高 | 强 | ReAct + 多假设追踪 + Reflection | Security/SRE 典型 |
| 高溯因 + 高注意力 | 高 | 弱 | 结构化假设模板 + 人工确认关键假设 | 降低对模型推理能力的依赖 |
| 高类比 + 高创意 | 低 | 强 | ReAct + 宽松 stop gate + 多样性采样 | Creative Agent 典型 |
| 高心智理论 + 高情绪 | 低 | 强 | Direct + 用户状态追踪 + 情感响应模板 | Companion 典型 |
| 中推理 + 高视觉注意力 | 中 | 强 | ReAct + GUI 验证循环 + 操作确认 | Browser Agent 典型 |
| 低推理 + 高目标层级 | 中 | 弱 | FSM / Workflow Engine + 规则驱动 | Enterprise Workflow 典型 |

## 6. 从 Flow of Thought 看范式改进

FoT (arXiv 2602.16512) 提出将 ReAct 的离散 Thought-Action-Observation 步骤改为流式思维：

```text
标准 ReAct:    Thought₁ → Action₁ → Obs₁ → Thought₂ → Action₂ → ...
FoT:           Thought stream ──────→ Action triggered by confidence threshold
                    ↑ 持续更新信念，action 是信念达到阈值时的涌现
```

这与 SOFAI 的元认知调度互补：FoT 改进了 System 2 内部的推理流，SOFAI 决定何时启用 System 2。

## 7. 研究缺口

| 缺口 | 现状 | 影响 |
|---|---|---|
| commitment 机制缺失 | ReAct 无显式 commitment；FoT 用置信阈值部分弥补 | 高风险场景下的决策可追溯性不足 |
| 认知负载测量 | 仅有 token 利用率等粗粒度指标 | 无法精确判断何时该简化范式 |
| System 1/2 自动调度 | 依赖手动规则或启发式 | SOFAI 提出了框架但缺乏 LLM Agent 上的实证 |
| 知识编译的效果评估 | skill 固化后是否真正降低了 token 成本和延迟？ | 需要 A/B 测试数据 |
| 跨品类范式迁移 | 某品类学到的范式组合能否迁移到相近品类？ | 缺乏系统性比较 |

## 8. 延伸阅读

- `paradigms/paradigm-routing.md` — 运行时范式切换的触发条件和状态迁移协议
- `paradigms/reasoning-paradigms.md` — 推理范式（ReAct / Plan-Execute / Reflection 等）详解
- `paradigms/decision-trees.md` — 范式选择的静态决策树
- `reasoning-modes.md` — 六种推理模式及其 prompt 策略
- `metacognitive-control.md` — 元认知监控与 impasse 检测
- `working-memory-dynamics.md` — 工作记忆容量与认知负载
- `category-cognitive-profiles.md` — 品类认知需求热力图
- `../architecture/planes/control/overview.md` — Control Plane 运行时实现
- Wray, R. et al. (2025). "Applying Cognitive Design Patterns to LLM Agents"
- Sun, Y. et al. (2025). "Flow of Thought" arXiv 2602.16512
- Sloman, A. et al. (2025). "SOFAI: A Meta-cognitive Architecture" Nature
- Zylos Architecture — Session-Governor-Executor 三层治理
