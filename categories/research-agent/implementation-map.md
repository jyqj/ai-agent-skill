# Research Agent Implementation Map

> **Evidence Status** — synthesized. `projects/research-agents/openai-deep-research/`、`projects/general-agents/hermes-agent/`、`projects/general-agents/generic-agent/` 以及 research 相关 patterns。

## 项目覆盖矩阵

| 设计问题 | OpenAI Deep Research | Hermes Agent | Generic Agent |
|---|---|---|---|
| Report Artifact | ★★★ `README.md` | ★ | ★ |
| Citation / Evidence Binding | ★★★ `citation-loop.md` | ★ | ★ |
| Raw Ref vs Summary | ★★ | ★★★ `README.md` | ★★ |
| Long-Horizon Loop | ★★★ `README.md` | ★★ | ★★ `agent-loop.snippet.md` |
| Memory / Skill Growth | ★ | ★★ | ★★★ `self-evolution.snippet.md` |
| Tool Orchestration | ★★ | ★★ | ★★★ `tool-system.snippet.md` |

## 品类模块 → 项目证据

| 品类模块 | 参考项目 | 观察 |
|---|---|---|
| Representation | OpenAI Deep Research / Hermes | 研究型交付需要把 source、summary、report 区分开 |
| Context | Hermes / Generic Agent | 冻结快照、按需载入、压缩历史能减少摘要塌缩 |
| Tools | OpenAI Deep Research / Generic Agent | search、read、artifact、tool routing 是研究闭环骨架 |
| State | OpenAI Deep Research / Generic Agent | 长时研究任务需要 section state 和 partial deliver |
| Learning | Generic Agent | 成功研究流程可以提炼为 reusable skill |
| Effects | Research 场景写 effect 少，但 delivery / publish 仍需 gate |

## 推荐阅读路径

### 学 citation-driven research

```text
../../projects/research-agents/openai-deep-research/README.md
../../projects/research-agents/openai-deep-research/citation-loop.md
../../design-space/patterns/citation-chain.md
```

### 学 raw ref / summary 分离

```text
../../projects/general-agents/hermes-agent/README.md
../../architecture/planes/representation/overview.md
../../categories/research-agent/representation.md
```

### 学长期演进与 tool scaffolding

```text
../../projects/general-agents/generic-agent/README.md
../../projects/general-agents/generic-agent/self-evolution.snippet.md
../../architecture/learning/overview.md
```

## 结论

| 结论 | 含义 |
|---|---|
| Research Agent 的核心不是“联网”，而是 citation integrity | search 只是开始，evidence binding 才决定可信度 |
| 报告是 first-class artifact | final deliverable 不该只是聊天回答 |
| 冲突需要成为对象而不是文风修饰 | preserve-first 比 smooth-first 更稳 |
| 长时研究更需要 checkpoint 和 partial deliver | 否则任务越长越容易漂移 |
