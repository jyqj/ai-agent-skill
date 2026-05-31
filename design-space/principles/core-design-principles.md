# 核心设计原则

> **Evidence Status** — grounded. 从 Claude Code、Codex、OpenCode、Augment、Hermes、MemPalace 等项目中反复观察到的共性原则。

以下 12 条原则来自多个项目反复印证的设计规律。每条都附有相关模式或文档的链接，方便深入了解。

### 1. Context is a Scarce Resource

上下文窗口是有限的。所有架构决策都应考虑上下文预算。不要一次性加载所有信息，按需加载、主动压缩、及时卸载。

- **正例**：milestone 级 context pack，最近观察按 trust tier 分层。
- **反例**：把整份日志、整篇网页、整个仓库都塞进模型。

相关模式：`../patterns/compaction.md`、`../patterns/progressive-disclosure.md`、`../patterns/tool-output-offloading.md`

### 2. Agent Operates on Representations, Not Reality

Agent 看到的是经过采样、解析、结构化、压缩后的表示，而不是现实本身。设计输入链路时，必须显式记录 raw refs、transform chain、freshness 和 confidence。

- **正例**：OCR 结果、数据库行、网页正文、语音转写都带 raw_ref、解析器修订、置信度和时效性。
- **反例**：把一段经过多次摘要的文本当成事实本身。

相关：`representation-first-design.md`、`../../architecture/planes/representation/overview.md`

### 3. Verify Before Claiming Done

Agent 完成任务前必须验证产出。"我修了 bug"不算完成，"测试通过并且相关状态回读一致"才算。执行深度的核心差异在于验证层。

相关模式：`../patterns/self-verification.md`、`../patterns/milestone-gated-execution.md`、`../patterns/effect-ledger.md`

### 4. Tool Success Is Not World Success

调用成功只是动作被执行，不代表外部世界已经达到目标状态。所有写动作都应考虑 postcondition、read-after-write、external ack 或 human confirm。

- **正例**：写操作之后强制 read-after-write 或外部确认。
- **反例**：发邮件接口 success 后就宣布"邮件已送达"。

相关：`../../architecture/planes/effects/overview.md`、`../../architecture/planes/world-state/overview.md`

### 5. Trust is Graduated, Not Binary

Agent 的权限不是全有或全无。根据操作风险、用户信任度、操作可逆性以及信息来源可信度，选择不同的介入程度。

相关：`../../architecture/planes/control/overview.md`、`../../architecture/planes/security/overview.md`

### 6. Keep Instruction Lanes Separate from Data Lanes

系统约束、用户意图、可信数据、不可信外部内容、记忆投影、模型推断必须分 lane。否则网页、日志、issue 或 MCP 返回值会间接接管 Agent 行为。

- **正例**：区分 developer policy、user intent、tool observation、retrieved content、memory、model inference。
- **反例**：把网页正文、issue 评论、README 里的提示语直接并入系统级指令区。

相关模式：`../patterns/untrusted-context-boundary.md`、`../patterns/tool-output-sanitization.md`

### 7. Fail Gracefully, Recover Explicitly

工具会失败，网络会超时，文件会不存在。Agent 必须有明确的恢复策略，而不是死循环重试或静默忽略。

- **正例**：每个 tool call 都有 failure_mode、recoverable、suggested_recovery、compensation。
- **反例**：只测试 happy path，失败时无限重试。

相关模式：`../patterns/checkpoint-hydration.md`、`../patterns/loop-detection.md`

### 8. State Must Survive Interruption

长任务会中断——用户关闭窗口、网络断开、token 用完。Agent 的状态必须能从中断点恢复，而不是从头来过。

- **正例**：Context Engine 有预算管理；State Engine 有 checkpoint；Operations 有配置追踪与回归。
- **反例**：一个 while 循环调 LLM，工具结果直接拼进 prompt。

相关模式：`../patterns/checkpoint-hydration.md`、`../patterns/scratchpad-progress-file.md`

### 9. Harness Defines the Ceiling, Model Defines the Floor

模型能力决定 Agent 能做的最少工作；Harness 工程决定 Agent 能做的最多工作。同一个模型，不同的 Harness 设计，产品能力差距巨大。

- **正例**：Coding Agent 从"用户需要可审查 diff + 测试通过"开始，再反推出需要 read/edit/test/git 和 D5。
- **反例**：先接入 20 个 MCP 工具，再思考用户能拿它做什么。

相关：`../../design-space/methodology/harness-engineering.md`

### 10. Fingerprint Everything That Changes Behavior

模型、prompt、tool schema、policy、memory policy、eval suite 只要变了，就可能改变行为。生产 Agent 必须让这些变化可追踪、可回放、可回归；不需要给无状态知识库制造发布标签。

- **正例**：发布前跑 eval runner，灰度后看 canary，异常可回滚。
- **反例**：直接线上替换 prompt 和 tool schema，然后靠用户报错。

相关：`../../architecture/planes/operations/overview.md`

### 11. Paradigms Are Choices, Not Defaults

不要把某一种 Agent 循环当作唯一正确答案。ReAct、Plan-and-Execute、Reflection、RAG、Disclosure、Worker Orchestration、Rule Policy、LLM Judge 都有适用边界。设计时先根据任务深度、风险、延迟、成本和验证能力选择范式，再装配模块。

相关：`../../paradigms/README.md`、`../../paradigms/reasoning-paradigms.md`

### 12. Start Minimal, Add Complexity from Evidence

轻量级 Agent 不需要第一天拥有完整生产架构。先构建最小闭环，用真实失败作为升级触发器，再逐步引入 memory、world state、effect ledger、observability、operations。

- **正例**：先有 Observe → Represent → Decide → Act → Verify，再加入 world state、effect ledger、canary。
- **反例**：第一版就实现全模块、多 Worker、分布式 checkpoint，却没有真实任务闭环。

相关：`../../design-space/methodology/minimum-viable-agent.md`、`../../architecture/reference-topologies.md`

---

### 补充原则（从概念索引版迁入）

以下原则在概念索引版中作为独立条目存在，与上述 12 条存在交叉但角度独特，作为补充保留。

#### A. 产品先于技术

先定义用户工作、交付物和验收标准，再决定 Runtime、表示层和工具。与原则 9（Harness Defines the Ceiling）互补：原则 9 强调 Harness 工程的杠杆作用，本条强调设计起点必须是用户价值。

#### B. 结构化边界优先于自然语言约定

工具、状态、观察、效果、评估都应该尽量结构化。

- **正例**：tool spec 有 input/output schema、failure_mode、postcondition、verification_method。
- **反例**：工具只返回"执行成功""执行失败"两个字符串。

#### C. 记忆保存的是可追溯主张，不是现实本身

长期记忆应该保存稳定主张、来源指针、技能和修订记录，而不是不带 provenance 的"印象"。

- **正例**：记忆条目包含来源、时间、敏感度、失效条件。
- **反例**：用户说"今天烦 Java"，就永久写成"用户讨厌 Java"。

#### D. 工具面决定行动边界，接口面决定现实边界

模型决定推理质量，工具决定行动能力，接口决定它能接触和改变哪一部分世界。

- **正例**：Browser Agent 同时建模 DOM、截图、点击、后端状态回读。
- **反例**：只有 `click_button`，没有任何页面状态验证。
