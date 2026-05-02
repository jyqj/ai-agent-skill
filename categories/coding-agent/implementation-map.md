# Coding Agent Implementation Map

> **Evidence Status** — synthesized. `projects/coding-agents/` 下参考项目 README、分析文档和 snippet。

## 项目覆盖矩阵

| 设计问题 | Claude Code | Codex | OpenCode | Augment | Warp |
|---|---|---|---|---|---|
| Context/Compaction | ★★★ `context-layer.md` | ★ | ★★★ `context-engineering.snippet.md` | ★★ | ★★ `agent-architecture.md` |
| Tool System | ★★★ `execution-layer.md` | ★★ | ★★★ `tool-system.snippet.md` | ★★★ `README.md` | ★★★ `agent-architecture.md` |
| Execution/Sandbox | ★★ | ★★★ `guardian-policy.snippet` | ★★ | ★★ | ★★ `terminal-ai-integration.md` |
| Control/Permission | ★★★ `control-layer.md` | ★★★ | ★★ `control-memory.snippet.md` | ★★ | ★★★ `contribution-workflow.md` |
| Orchestration | ★★ `orchestration-layer.md` | ★★ `orchestrator.snippet` | ★★ `orchestration.snippet.md` | ★★★ `patterns.md` | ★★★ `contribution-workflow.md` |
| State/Checkpoint | ★★ `state-ui-layer.md` | ★ | ★★ | ★★★ `patterns.md` | ★★ |
| Memory/Learning | ★ | ★★ `memory-pipeline.snippet` | ★★ | ★ | ★ |
| UI/Interaction | ★★★ `state-ui-layer.md` | ★ | ★ | ★ | ★★★ `terminal-ai-integration.md` |
| Operations/Workflow | ★ | ★ | ★ | ★ | ★★★ `contribution-workflow.md` |

## 品类模块 → 项目证据

| 品类模块 | 参考项目 | 观察 |
|---|---|---|
| Representation | Claude Code / OpenCode / Warp | 通过上下文层、文件读取、工具输出规范化构造代码库表示；Warp 用 spec 作为需求的结构化表示 |
| Context | Claude Code / OpenCode / Warp | 压缩、offloading、阶段性上下文管理是 coding agent 核心能力；Warp 的 skill 三层渐进加载是另一种上下文管理 |
| Tools | Claude Code / Augment / OpenCode / Warp | 从丰富工具集到分层 host，不同系统在工具粒度上取舍不同；Warp 把 skill 作为元工具 |
| Execution | Codex / Claude Code / Warp | 沙箱、命令策略、环境隔离决定能否安全执行测试和 shell；Warp 的终端即执行环境 |
| Control | Claude Code / Codex / OpenCode / Warp | hook、guardian、deny>ask>allow、readiness-label 都是控制范式落地 |
| State | Augment / Claude Code | checkpoint 和 UI/progress 让长任务可恢复、可观察 |
| Orchestration | Augment / Claude Code / Codex / Warp | worker、subagent、orchestrator、Oz pipeline 用于上下文隔离和多阶段编排 |
| Effects | All | diff、test、CI/readback 是 coding agent 完成判断的关键证据；Warp 的 spec→code→CI→review→merge 是最完整的效果链 |
| Operations | Warp | Oz 自动化 triage/review/routing 让 agent-driven ops 成为可能 |

## 参考阅读路径

### 学 Context / Compaction

```text
../../projects/coding-agents/claude-code/context-layer.md
../../projects/coding-agents/claude-code/compaction.snippet
../../projects/coding-agents/opencode/context-engineering.snippet.md
../../design-space/patterns/compaction.md
```

### 学 Tool / Execution

```text
../../projects/coding-agents/claude-code/execution-layer.md
../../projects/coding-agents/claude-code/tool-orchestration.snippet
../../projects/coding-agents/opencode/tool-system.snippet.md
../../projects/coding-agents/augment/README.md
../../architecture/planes/tools/overview.md
```

### 学 Control / Safety

```text
../../projects/coding-agents/claude-code/control-layer.md
../../projects/coding-agents/codex/guardian-policy.snippet
../../projects/coding-agents/opencode/control-memory.snippet.md
../../architecture/planes/control/overview.md
../../architecture/planes/security/overview.md
```

### 学 Orchestration / State

```text
../../projects/coding-agents/claude-code/orchestration-layer.md
../../projects/coding-agents/claude-code/state-ui-layer.md
../../projects/coding-agents/codex/orchestrator.snippet
../../projects/coding-agents/augment/patterns.md
../../architecture/planes/orchestration/overview.md
```

### 学 Agent-Driven Workflow / Operations

```text
../../projects/coding-agents/warp/contribution-workflow.md
../../projects/coding-agents/warp/agent-architecture.md
../../architecture/planes/operations/overview.md
```

## 实现对比结论

| 结论 | 含义 |
|---|---|
| 工具越丰富，控制层越重要 | 60+ 工具没有 permission / hook 会变成 Tool Soup |
| 沙箱只能限制破坏，不能证明完成 | 仍需 test/diff/readback 的 effect verification |
| 上下文工程是 coding agent 的核心竞争力 | 大仓库任务中，能否找到和保持正确上下文决定质量 |
| 子代理解决上下文隔离，不自动解决合并 | OutputContract 和 merge strategy 仍必需 |
| 生产 coding agent 必须能承认 partial verification | 无法运行测试时，诚实报告比虚假完成更重要 |
| Spec-driven 流程把隐性推理变显性契约 | Warp 的 spec 不变量让 agent 和人共享期望 |
| Agent-as-Contributor 需要准入控制 | Readiness label 证明不是所有任务都适合 agent 执行 |
| Skills 需要工程化管理 | 模板、审计、最佳实践、渐进加载让 skill 成为可维护资产 |

## 待补证据

- 不同项目对“写操作串行 / 只读并行”的具体策略对比。
- 大型 repo 中 symbol graph 与 semantic search 的精度/成本权衡。
- 从 bug fix 成功轨迹提炼 skill 的长期可靠性。
- coding agent 在真实团队工作流中的 incident / rollback 机制。
