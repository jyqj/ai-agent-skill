# Collaboration Paradigms

> **Evidence Status** — grounded. `architecture/planes/orchestration/`、Claude Code 子代理、Codex orchestrator、Augment worker 编排、OpenCode agent registry 的项目观察。


## 协作范式

| 范式 | 核心机制 | 适合 | 风险 |
|---|---|---|---|
| Single Agent + Tools | 一个主循环直接调用工具 | 绝大多数低到中复杂度任务 | 上下文过载、任务串行 |
| Subagent / Isolated Context | 主 Agent 派生隔离上下文处理子任务 | 需要不同角色或独立证据收集 | 结果合并失真 |
| Coordinator-Worker | 协调者拆分任务，worker 并行执行 | 可并行、输出可合并的任务 | shared state 冲突、协调成本 |
| Peer Collaboration | 多 Agent 对等协商或互审 | 需要多视角、辩论、审查 | 协议复杂、责任不清 |
| Blackboard / Shared World Model | 多 Agent 读写共享对象和冲突记录 | 长流程、跨角色、需要一致状态 | 写冲突、stale state |
| Event-driven Agents | 事件触发、异步处理、租约和 heartbeat | 持续任务、监控、企业流程 | 取消传播、重复处理 |
| Human-in-the-loop | 人类作为审批者、教师、仲裁者、监督者 | 高风险、模糊、用户信任未建立 | 交互过载、审批疲劳 |

## 选择矩阵

| 场景特征 | 推荐协作范式 | 必备机制 |
|---|---|---|
| 单人短任务 | Single Agent + Tools | 明确 stop gate |
| 需要隔离上下文做研究或审查 | Subagent | OutputContract、source refs |
| 多个独立文件/模块可并行分析 | Coordinator-Worker | branch budget、merge strategy |
| 需要 reviewer 独立挑错 | Peer / Critic Agent | conflict policy、rubric |
| 跨系统长流程 | Blackboard / Shared World Model | object refs、state refresh、arbitration |
| 监控或持续运营 | Event-driven | lease、heartbeat、idempotency、incident response |
| 高风险写动作 | Human-in-the-loop | approval gate、explainable diff、rollback plan |

## 协作的最小协议

```yaml
agent_message:
  message_id: string
  from: agent_id
  to: agent_id | group
  task_ref: string
  intent: request | result | evidence | conflict | cancel | heartbeat
  payload: object
  evidence_refs: []
  world_state_refs: []
  deadline_or_lease: string | null
  merge_hint: append | override | conflict_review
```

Worker 输出必须结构化：

```yaml
worker_output:
  worker_id: string
  status: complete | partial | failed
  summary: string
  artifacts: []
  evidence_refs: []
  decisions_made: []
  open_questions: []
  conflicts: []
```

## 合并策略

| 策略 | 使用条件 | 风险 |
|---|---|---|
| Append | 输出独立，如多来源摘要 | 重复、冗余 |
| Priority | 有明确权威来源或角色优先级 | 低优先级证据被忽略 |
| Synthesis | 多个输出需要综合 | 模型可能抹平冲突 |
| Conflict Review | 输出互相矛盾 | 成本上升 |
| Human Arbitration | 影响高或冲突无法自动解决 | 人类成为瓶颈 |

## 设计原则

```text
并行只适合“可分解 + 可合并”的任务。
隔离上下文适合“需要不同证据视角”的任务。
多 Agent 不等于更智能；没有协议、状态和合并策略，只会制造更多不一致。
```

实施检查：

```text
[ ] 子任务是否真的独立？
[ ] 每个 worker 是否有明确 OutputContract？
[ ] 共享 world state 的刷新和锁定策略是什么？
[ ] 冲突如何记录、仲裁、回滚？
[ ] 取消、超时、失败是否会传播？
[ ] 人类在哪些节点介入，介入时看到什么证据？
```

## 扩展协作模式（Multi-Agent Design Patterns）

来自汽车 AI、企业工作流和科研系统的实践补充：

| 模式 | 核心 | 适用 |
|---|---|---|
| Diamond | 主 Agent→专家 Agents→统一后处理（Rephraser/Mixer） | 需要一致输出风格或安全过滤 |
| Response Mixer | 多专家生成→mixer 选取最优部分合并 | 复杂问题需要多视角最佳组合 |
| Adaptive Loop | 迭代搜索/生成→评估→改进查询 | 初始结果不满足时渐进式优化 |
| Contract-based (Contractor) | Agent 接收结构化契约，可协商、可拆分子契约 | 高 stakes 复杂任务、需要明确验收标准 |
| Digital Assembly Line | 人类监督→协调 Agent→多专家 Agent (A2A) | 端到端企业流程自动化 |

详见：
- `../design-space/patterns/contract-agent.md`
- `../design-space/frontier/agentic-commerce-and-protocols.md`

## 跨组织协作协议

当多 Agent 跨越组织边界时，需要标准化协议：

| 协议 | 层级 | 解决什么 |
|---|---|---|
| MCP | Agent-to-Tool | 工具能力声明、参数、调用 |
| A2A | Agent-to-Agent | 任务委派、结果流式、取消/中断 |
| AP2 | Agent-to-Commerce | 购买授权、金额限制、欺诈防护 |

相关文件：`../architecture/planes/orchestration/overview.md`、`../architecture/planes/orchestration/communication.md`、`../architecture/planes/orchestration/shared-world-model.md`、`../design-space/patterns/worker-orchestration.md`、`../design-space/patterns/subagent.md`。


## 决策树速用

```text
单 Agent 可完成 → Single Agent + Tools
需要隔离证据或角色 → Subagent
任务可并行且可合并 → Coordinator-Worker
需要独立审查/辩论 → Peer / Critic Agent
共享外部对象 → Shared World Model + arbitration
持续运行 → Event-driven + heartbeat + idempotency
高风险或歧义 → Human-in-the-loop
去中心化 + 能力重叠 → Market-Based Coordination
需要对抗性推理验证 → Debate-Based Convergence
Agent 数量大 + 低耦合 → Stigmergic Communication
高可靠性 + 成本可接受 → Ensemble / Voting
```

完整跨范式决策树见 `decision-trees.md`。


---

## 去中心化协作形态

前面的范式共享一个隐含假设：存在某个角色知道全局任务结构。Coordinator 知道怎么拆分，Worker 知道自己是 Worker，Peer 至少知道对方存在。下面四种形态放弃这个假设的不同部分，换来不同的可扩展性和鲁棒性。

它们与 `agent-typology.md` 中的"涌现协作型"对应，是该形态在协作协议层面的具体展开。

### Market-Based Coordination

想象一个没有项目经理的工程团队：任务被贴到公告板上，每个人根据自己的能力和当前负载决定是否接单，接单前先报价。

核心对象：

- **TaskAuction**：一次任务拍卖。包含任务描述、质量要求、截止时间、预算上限。
- **Bid**：Agent 的出价，包含预估成本（token / 时间 / 工具调用次数）、预估完成时间、Agent 自评的能力匹配度。
- **Settlement**：拍卖结果。记录中标者、实际成本、质量评分，作为后续拍卖的历史参考。

竞标价格不是凭空喊的——它需要基于 Cost Plane 的真实预算约束。一个 Agent 报价 10k token 完成代码审查，这个报价的可信度取决于它历史上类似任务的实际消耗。Settlement 记录反哺 Cost Plane，形成价格信号的正反馈循环。

适用场景比较明确：任务可以独立完成、输出质量可以事后评估、多个 Agent 具备重叠能力。典型例子是多模型 API 网关的路由——每个模型就是一个 Agent，路由器就是拍卖师，价格信号就是延迟 × 成本 × 质量的综合评分。

风险在冷启动和博弈。没有历史报价时，第一轮拍卖本质上是盲拍。如果 Agent 能观察到彼此的报价，可能出现价格操纵——总是报比对手低一点的价格，而不是基于真实成本报价。应对方式是密封拍卖（sealed-bid）加上事后质量审计：报价低但交付差的 Agent，在后续拍卖中竞争力下降。


### Debate-Based Convergence

单个模型做复杂推理时，错误往往"看起来很对"——因为没有人质疑。Debate-Based Convergence 的核心思路是让质疑制度化。

流程不是线性的"生成→检查"，而是对抗性的：

1. **独立推理**：多个 Agent 各自分析同一问题，互不可见。
2. **陈述**：每个 Agent 提出 Claim（主张），附带 Argument（论证），论证必须包含可检验的 Evidence（证据引用）。
3. **交叉质询**：Agent A 读到 Agent B 的 Claim 后，可以提出 Rebuttal（反驳），反驳同样必须附带证据。被反驳方可以修正、坚持（附加更强证据）或撤回。
4. **裁决**：由独立的 Judge Agent 或预定义规则产出 Verdict。裁决依据是证据强度和论证一致性，而不是"谁说得更自信"。

这里的关键设计决策是**裁决者是谁**。三种选择各有取舍：规则裁决（如证据数量、来源权威性打分）最透明但最死板；第三方 Agent 裁决灵活但引入了裁决者偏见；人类裁决最可靠但不可扩展。实践中常用规则初筛 + Agent 复裁 + 高冲突时升级到人类的分层策略。

优势不只是"减少幻觉"——辩论过程本身就是推理质量的可观测信号。如果三个 Agent 独立推理后结论一致且论证路径不同，这个结论的置信度远高于单个 Agent 的输出。反之，如果辩论三轮仍无法收敛，这本身就说明问题存在真正的歧义，不应该强行给出唯一答案。

风险是收敛效率。辩论可能陷入循环——A 反驳 B，B 反驳 A 的反驳，无限递归。需要硬性的轮次上限和"无法收敛"的显式输出路径。Constitutional AI 中的 critique-revision 可以视为退化版本：只有一个 Agent 自我辩论，没有真正的对抗性。


### Stigmergic Communication

直接通信的代价是 O(n²)——10 个 Agent 互相通信需要 90 条消息通道。Stigmergy 把通信成本降到 O(n)：每个 Agent 只与共享环境交互，不需要知道其他 Agent 的存在。

核心机制借鉴蚁群：蚂蚁不会开会讨论觅食路线，它们在路上留下信息素，后来的蚂蚁根据信息素浓度选择路径。浓度高的路径被更多蚂蚁选择，留下更多信息素，形成正反馈。信息素会自然衰减（Decay），防止过时信号误导后来者。

映射到 Agent 系统：

- **SharedEnvironment**：所有 Agent 可读写的共享状态空间。可以是数据库、文件系统、共享内存。
- **Signal**：Agent 在环境中留下的标记。比如"这个文件我已经审查过，发现 3 个问题"——不是发消息告诉其他 Agent，而是在文件旁边打一个标记。
- **Decay**：信号的时效性。24 小时前的审查标记，在代码已经变更后应该自动失效。

软件工程中最成功的 Stigmergy 实例是 Git：开发者不需要实时通信，他们通过 commit 修改共享仓库，其他人 pull 时感知变化。CI 状态徽章是信号，分支命名约定是弱协议，merge conflict 是信号冲突的显式化。

优势是天然可扩展——加入第 101 个 Agent 不需要修改前 100 个 Agent 的任何配置。劣势是收敛性极难保证，调试几乎不可能（你无法 replay 100 个 Agent 与环境的交互序列来复现一个 bug），信号冲突（两个 Agent 同时修改同一个环境对象）需要额外机制处理。

适用场景：Agent 数量多且动态变化、任务之间耦合度低、通信基础设施不可靠或成本高。不适合需要严格一致性的场景。


### Ensemble / Voting

最简单的多 Agent 协作：让 N 个 Agent 各自独立做同一件事，然后投票。

核心对象只有三个：

- **Candidate**：每个 Agent 的独立输出。
- **VotingRule**：聚合规则。多数投票（majority）、加权投票（按历史准确率加权）、排名选择（Borda count）。
- **Aggregator**：执行投票并输出最终结果。

优势是实现简单、完全可并行、在理论上能提高可靠性。N 个独立判断者多数正确的概率高于单个判断者——这是 Condorcet 陪审团定理的直接应用。

但"独立"这个前提在 LLM 场景下几乎不成立。同族模型（比如三个 GPT-4o 实例）的错误高度相关——它们在同一个问题上犯错的概率远高于随机独立。提高 ensemble 有效性的方式：使用不同模型族（GPT + Claude + Gemini）、使用不同 prompt 策略（CoT vs direct vs few-shot）、或在输入侧引入随机扰动。

成本是线性增长的：N 个 Agent 意味着 N 倍的 token 消耗。所以 Ensemble 通常只用于高可靠性要求且单次成本可接受的场景——比如安全分类、关键事实判断——而不是日常对话。

与 Debate-Based 的区别：Ensemble 中 Agent 互不可见，各自输出后由外部聚合；Debate 中 Agent 看到彼此的输出并交互式改进。Ensemble 更快但更浅，Debate 更慢但更深。


### 去中心化形态的选择指引

```text
任务可独立完成 + 多 Agent 能力重叠 → Market-Based
需要多角度深度分析 + 结论可辩护 → Debate-Based
Agent 数量大 + 动态变化 + 低耦合 → Stigmergy
高可靠性 + 单次成本可接受 → Ensemble / Voting
```

这四种形态不互斥。一个系统可以用 Market-Based 分配任务，每个任务内部用 Ensemble 提高可靠性，跨任务的事实核查用 Debate 收敛。关键是每一层协作的通信成本和收敛保证是否匹配场景需求。
