# Reference to Module Map

> **Evidence Status** — synthesized. `projects/` 下各项目 README 与专题分析文件。


## 项目 → 模块（该项目在哪些模块有深度实现）

| 参考项目 | 模块深度覆盖 | 核心学习点 |
|---|---|---|
| Claude Code | Context ★★★, Tools ★★★, Execution ★★★, Control ★★★, Orchestration ★★, State ★★, Recovery ★★ | 4 阶段压缩、工具并发控制、Hook（25 事件类型）、Fork 缓存共享、子代理隔离、413 三阶段恢复 + 熔断器 |
| Codex | Execution ★★★, Control ★★★, Orchestration ★★, Security ★★, Memory ★★ | 沙箱隔离、Guardian LLM 审批、多 agent 控制、Rollout 两阶段记忆管道 |
| OpenCode | Context ★★★, Tools ★★★, Control ★★, Orchestration ★★, Operations ★, Recovery ★★ | Doom Loop 检测、deny>ask>allow 权限、Zod schema、函数式 DI runtime、分级重试 |
| Augment | Tools ★★★, Orchestration ★★★, State ★★★, Interface ★ | 分层工具主机、Worker 编排、Checkpoint |
| Nocturne | Memory ★★★, Context ★★, Representation ★★ | Disclosure、记忆审计、修订链 |
| MemPalace | Memory ★★★, Representation ★★, Tools ★★ | 原文存储、KG、MCP 工具、benchmark |
| Hermes | Interface ★★★, Tools ★★★, Execution ★★★, Memory ★★, Recovery ★★, Orchestration ★★ | Multi-platform Gateway、学习循环、IterationBudget consume/refund、Kanban Worker 分派、双引擎浏览器 |
| Generic | Memory ★★, Tools ★★, Learning ★★★, Interface ★★★ | 最小 Agent Loop、自我进化、13 渠道前端适配、Agent BBS 分布式协作 |
| NagaAgent | Memory ★★★, Context ★★, Interface ★★ | 分层 Prompt、GRAG、Voice / Avatar |
| VCPToolBox | Tools ★★★, Platform ★★★, Memory ★★ | 插件系统、分布式工具、TagMemo |
| Warp | Tools ★★★, Orchestration ★★★, Control ★★★, Operations ★★★, Interface ★★, Learning ★★ | Skills 系统（10 Provider 兼容 + Skill 继承）、Oz Pipeline、Spec-Driven、Readiness Label、AgentDriver 多 Harness 托管 |
| Browser Use | Tools ★★★, Execution ★★★, Interface ★★, Control ★★ | 81K stars 开源 Browser Agent、DOM 操作、多步浏览器任务 |
| Stagehand | Tools ★★★, Interface ★★★, Execution ★★ | Vercel DOM-first Browser Agent、结构化 DOM 抽取 |
| Perplexity | Orchestration ★★★, Context ★★★, Representation ★★ | 19 模型编排、搜索 + 生成流水线、引用链 |
| OpenAI Agents SDK | Orchestration ★★★, Tools ★★★, Control ★★, Execution ★★ | OpenAI 官方 Agent 框架、Handoff、Guardrails |
| Google ADK | Orchestration ★★★, Tools ★★★, Memory ★★, Execution ★★ | Google Agent Development Kit、多 Agent 编排、工具生态 |
| LangGraph | Orchestration ★★★, State ★★★, Concurrency ★★★, Tools ★★ | 有向图状态机、Superstep 并行、持久化 Checkpointer、中间件模式 |
| CrewAI | Orchestration ★★★, Interaction ★★★, Memory ★★, Tools ★★ | 角色驱动多 Agent、Flows 事件管道、四层记忆、团队隐喻 |
| Letta | Memory ★★★, Context ★★★, State ★★ | OS 风格记忆层级、自编辑记忆工具、V1 原生推理转型 |
| Mem0 | Memory ★★★, Economics ★★★, Security ★★ | 三层存储(Vector+Graph+KV)、选择性记忆、actor-aware、90%+ 成本降低 |

## 模块 → 项目（想学某个模块，看哪些项目）

| 模块 | 首选项目 | 次选项目 |
|---|---|---|
| Representation | Nocturne（disclosure） | MemPalace（原文 + 结构）/ Perplexity（引用链） |
| Context | Claude Code（4 阶段压缩） | OpenCode（压缩联动）/ Perplexity（搜索上下文）/ Letta（自管理分页） |
| Memory | Nocturne（审计 + disclosure） | MemPalace（KG + benchmark）/ Google ADK（Agent 记忆）/ Letta（OS 式记忆层级）/ Mem0（选择性记忆平台） |
| Tools | Claude Code（60+ 工具） | Augment（分层 host）/ Browser Use（浏览器工具）/ Stagehand（DOM 工具）/ OpenAI Agents SDK / Google ADK |
| Execution | Codex（完全沙箱） | Hermes（多 backend）/ Browser Use（浏览器执行）/ OpenAI Agents SDK / Google ADK |
| Control | Claude Code（Hook） | Codex（Guardian）/ Browser Use（浏览器控制）/ OpenAI Agents SDK（Guardrails） |
| Orchestration | Augment（Worker） | Claude Code（子代理）/ Warp（Oz Pipeline）/ Perplexity（19 模型编排）/ OpenAI Agents SDK（Handoff）/ Google ADK（多 Agent）/ LangGraph（图状态机）/ CrewAI（Flows 事件管道） |
| State | Augment（Checkpoint） | Claude Code（git-based）/ LangGraph（持久化 Checkpointer） |
| Interface | Hermes（multi-platform） | Naga（多模态）/ Warp（terminal-native）/ Browser Use（浏览器 UI）/ Stagehand（DOM-first） |
| Operations | Warp（Oz triage/review） | Hermes（multi-platform） |
| Learning | Generic（self-evolution） | VCPToolBox（TagMemo）/ Warp（Skill 继承 + 10 Provider 发现）/ Hermes（学习循环 + Skill Curator） |
| Recovery | Claude Code（413 三阶段 + 熔断器） | Hermes（IterationBudget + 压力注入）/ OpenCode（Doom Loop + 分级重试）/ Generic（轮次梯级降级） |
