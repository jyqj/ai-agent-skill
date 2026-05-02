# Frontier

> **Evidence Status** — speculative. 本页来自本 skill 的设计模式、反模式和评估准则综合整理，用于识别架构风险和修复路径。

> **定位**：尚未成熟、仍在演进的设计方向。这里的内容还没有足够多的项目验证，但已经值得关注。

与 `patterns/` 的区别：patterns 里的条目至少被 2 个以上项目印证，可以直接复用；frontier 里的条目更多是趋势观察和设计问题，可能在未来升级为 pattern，也可能被证伪。

当前关注的方向：

- `reasoning-tool-coupling.md` — 推理和工具调用的耦合方式正在变化
- `agentic-rag-and-citation-loops.md` — 检索增强从单次查询变成多轮闭环
- `long-horizon-runtime.md` — 长时任务的运行时需要哪些额外机制
- `multimodal-and-computer-use.md` — 多模态和 GUI 操作迫使多个架构层同时升级
- `agent-protocols-and-boundaries.md` — MCP、A2A、Repo Instructions 是不同的边界
- `observability-control-plane.md` — 可观测性正在从"事后看日志"变成"运行时控制面"
- `multi-agent-governance.md` — Agent 经济学、涌现治理、Agent 宪法、跨组织治理标准化

**使用方式**：先用 `categories/` 和 `architecture/` 形成当前设计，再读 frontier 判断未来扩展点。某个做法在多个案例中复现后，再提升到 `patterns/`。
