# Paradigm Map

> **Evidence Status** — synthesized. 快速把设计问题映射到合适的范式文档。

| 设计问题 | 优先读 | 辅助读 |
|---|---|---|
| 为什么选 ReAct 而不是 Plan-and-Execute？ | `../paradigms/reasoning-paradigms.md` | `../architecture/kernel/agent-loop.md` |
| ORDA-VU 和 ReAct 是什么关系？ | `../paradigms/reasoning-paradigms.md` | `../architecture/lifecycle.md` |
| RAG、Disclosure、Layered Memory 如何取舍？ | `../paradigms/memory-paradigms.md` | `../architecture/planes/memory/overview.md` |
| 静态工具、动态发现、MCP 怎么选？ | `../paradigms/tool-paradigms.md` | `../architecture/planes/tools/overview.md` |
| 原子工具和 Rich Tool 什么时候用？ | `../paradigms/tool-paradigms.md` | `../design-space/patterns/tool-registry.md` |
| 单 Agent、Subagent、Worker 怎么选？ | `../paradigms/collaboration-paradigms.md` | `../architecture/planes/orchestration/overview.md` |
| rule、LLM judge、hook、sandbox 如何组合？ | `../paradigms/control-paradigms.md` | `../architecture/planes/control/overview.md` |
| 轻量级 Agent 要不要全量 plane？ | `../paradigms/methodology/minimum-viable-agent.md` | `../architecture/reference-topologies.md` |
| 自治等级和执行深度怎么定？ | `../paradigms/methodology/autonomy-and-depth.md` | `../architecture/controllers/execution-depth/overview.md` |
| 如何把产品需求变成 Agent 架构？ | `../paradigms/methodology/agent-product-model.md` | `../index/design-checklist.md` |
| 性能优化和成本控制怎么选技术？ | `../paradigms/methodology/performance-optimization.md` | `../architecture/planes/cost/model-routing.md` |
| 高 stakes 任务如何标准化契约？ | `../design-space/patterns/contract-agent.md` | `../paradigms/collaboration-paradigms.md` |
| 安全该用规则还是 AI 检测？ | `../design-space/patterns/guard-model.md` | `../paradigms/control-paradigms.md` |
| 记忆该用什么形态承载？ | `../design-space/frontier/memory-forms-and-dynamics.md` | `../paradigms/memory-paradigms.md` |
