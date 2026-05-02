# Starter Kits

> **Evidence Status** — synthesized. 本页来自 starter-kit 的参考代码、可选 smoke test 和本 skill 的最小闭环设计要求。

> **定位**：这些代码骨架展示知识库的核心对象（TaskEnvelope、EffectRecord、ToolRegistry、WorldStateSnapshot 等）如何串联成闭环。它们是**概念映射**，不是生产框架、构建起点或 MVA 实现路线图。

> **想真正构建 Agent？** 请走 `guides/build-research-agent.md` 等端到端指南，它们会引导你用知识库的方法论从零设计。starter-kit 只负责"概念长什么样的代码"，不负责"怎么做一个 Agent"。


## 骨架列表

| 骨架 | 入口 | 展示什么概念 |
|---|---|---|
| Verified Tool Agent | `verified-tool-agent/README.md` | EffectRecord、ToolRegistry、Verification、FailureRecord、TraceEvent、Stop Gate |
| React LLM Agent | `react-llm-agent/README.md` | ReAct 循环、LLM 决策、intended_effect、独立验证（readback/test） |
| Stateful Agent | `stateful-agent/README.md` | Checkpoint 持久化、WorldStateSnapshot TTL、中断恢复、上下文压缩 |

## 使用方式

```text
先读相应 category 和 architecture/planes
  → 再看 starter kit 如何把这些对象映射成参考代码
  → 若要落地，走 guides/ 的端到端指南
  → 落地时必须重新设计权限、安全、测试和运维
```

## 与知识库其他部分的关系

- `guides/` — 从知识到实践的端到端指南（想构建 Agent 走这里）
- `projects/` — 真实项目的架构分析和 snippet（想看生产实现走这里）
- `evaluation/eval-runner/` — 可执行的评估框架（想做评估走这里）
- `architecture/runtime-data-model.md` — 这些骨架中数据对象的完整定义
