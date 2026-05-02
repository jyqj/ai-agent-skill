# Reference to Module Map

> **Evidence Status** — synthesized. `projects/` 下各项目 README 与专题分析文件。


## 项目 → 模块（该项目在哪些模块有深度实现）

| 参考项目 | 模块深度覆盖 | 核心学习点 |
|---|---|---|
| Claude Code | Context ★★★, Tools ★★★, Execution ★★★, Control ★★★, Orchestration ★★, State ★★ | 4 阶段压缩、工具并发控制、Hook、子代理隔离 |
| Codex | Execution ★★★, Control ★★★, Orchestration ★★, Security ★★ | 沙箱隔离、Guardian Policy、多 agent 控制 |
| OpenCode | Context ★★★, Tools ★★★, Control ★★, Orchestration ★★, Operations ★ | Doom Loop、权限模型、函数式 runtime |
| Augment | Tools ★★★, Orchestration ★★★, State ★★★, Interface ★ | 分层工具主机、Worker 编排、Checkpoint |
| Nocturne | Memory ★★★, Context ★★, Representation ★★ | Disclosure、记忆审计、修订链 |
| MemPalace | Memory ★★★, Representation ★★, Tools ★★ | 原文存储、KG、MCP 工具、benchmark |
| Hermes | Interface ★★★, Tools ★★★, Execution ★★★, Memory ★★ | Multi-platform Gateway、学习循环 |
| Generic | Memory ★★, Tools ★★, Learning ★★★ | 最小 Agent Loop、自我进化 |
| NagaAgent | Memory ★★★, Context ★★, Interface ★★ | 分层 Prompt、GRAG、Voice / Avatar |
| VCPToolBox | Tools ★★★, Platform ★★★, Memory ★★ | 插件系统、分布式工具、TagMemo |
| Warp | Tools ★★★, Orchestration ★★★, Control ★★★, Operations ★★★, Interface ★★ | Skills 系统、Oz Pipeline、Spec-Driven、Readiness Label |

## 模块 → 项目（想学某个模块，看哪些项目）

| 模块 | 首选项目 | 次选项目 |
|---|---|---|
| Representation | Nocturne（disclosure） | MemPalace（原文 + 结构） |
| Context | Claude Code（4 阶段压缩） | OpenCode（压缩联动） |
| Memory | Nocturne（审计 + disclosure） | MemPalace（KG + benchmark） |
| Tools | Claude Code（60+ 工具） | Augment（分层 host） |
| Execution | Codex（完全沙箱） | Hermes（多 backend） |
| Control | Claude Code（Hook） | Codex（Guardian） |
| Orchestration | Augment（Worker） | Claude Code（子代理）/ Warp（Oz Pipeline） |
| State | Augment（Checkpoint） | Claude Code（git-based） |
| Interface | Hermes（multi-platform） | Naga（多模态）/ Warp（terminal-native） |
| Operations | Warp（Oz triage/review） | Hermes（multi-platform） |
| Learning | Generic（self-evolution） | VCPToolBox（TagMemo） |
