# AI 路由表

> **Evidence Status** — synthesized. 给使用本 skill 的 AI 一个低上下文成本的路由表；目标是先读最少文件、产出可用方案，再按风险展开深层文档。

## 总规则

```text
1. 先判断用户意图，不要先读完整知识库。
2. 每次最多读取 3-5 个核心文件。
3. 先给 MVA / depth / module set，再展开 25 plane。
4. 哲学层默认不读，除非用户问“为什么”或方案存在原则冲突。
5. 项目层默认只读 README，除非用户要求源码观察。
```

## 意图 → 最小读取集

| 用户意图 | 必读 | 可选 |
|---|---|---|
| “我要做一个 Agent” | `../START-HERE.md`, `../toolkit/choose-agent-type.md`, `../toolkit/mva-planner.md` | `../toolkit/module-picker.md` |
| “帮我设计某类 Agent” | `../toolkit/choose-agent-type.md`, 对应 `../categories/<type>/README.md`, `../toolkit/module-picker.md` | `../index/category-module-map.md` |
| “这个 Agent 不够好/有问题” | `../toolkit/failure-router.md`, `../index/design-checklist.md` | 命中的 plane overview |
| “工具调用成功但没完成” | `../synthesis/tool-effect-verification.md`, `../architecture/planes/effects/overview.md`, `../design-space/lessons-learned/tool-success-as-completion.md` | `../design-space/patterns/effect-ledger.md` |
| “记忆系统怎么设计” | `../synthesis/context-memory-state-boundaries.md`, `../architecture/planes/memory/overview.md`, `../projects/memory-systems/nocturne-memory/README.md` | `../projects/memory-systems/mempalace/README.md` |
| “我要 browser/desktop 自动化” | `../categories/browser-desktop-agent/README.md`, `../design-space/patterns/dual-channel-gui-verification.md`, `../architecture/planes/effects/gui-verification.md` | `../projects/browser-desktop-agents/anthropic-computer-use/README.md` |
| “我要 coding agent” | `../categories/coding-agent/README.md`, `../categories/coding-agent/implementation-map.md`, `../synthesis/tool-effect-verification.md` | `../projects/coding-agents/codex/README.md` |
| “我要研究/报告 Agent” | `../categories/research-agent/README.md`, `../design-space/patterns/citation-chain.md`, `../design-space/patterns/conflict-preserving-synthesis.md` | `../evaluation/research-agent-evals.md` |
| “如何评估” | `../toolkit/eval-planner.md`, `../evaluation/eval-framework.md`, `../evaluation/fixtures/README.md` | `../evaluation/eval-meta/README.md` |
| “如何降低复杂度” | `../toolkit/mva-planner.md`, `../toolkit/module-picker.md`, `../architecture/reference-topologies.md` | `../index/maturity-ladders.md` |
| “为什么必须这样设计” | `../ARCHITECTURE.md`, `../concepts/foundations/PRINCIPLE-INDEX.md` | 相关 foundation 文件 |
| “推理模型” / “reasoning model” | `../paradigms/reasoning-model-integration.md` | `../ARCHITECTURE.md` |
| “context engineering” / “上下文工程” | `../concepts/context-engineering.md` | `../synthesis/context-memory-state-boundaries.md` |
| “记忆安全” / “记忆投毒” | `../architecture/cross-cutting/memory-x-security.md` | `../architecture/planes/memory/overview.md` |
| “协议” / “A2A” / “MCP” / “AG-UI” | `../architecture/evolution/ecosystem-protocols.md` | `../ARCHITECTURE.md` |
| “治理” / “governance” | `../design-space/frontier/agent-governance-frameworks.md` | `../concepts/foundations/PRINCIPLE-INDEX.md` |
| “基准” / “benchmark” / “评估可信度” | `../evaluation/benchmark-trust-crisis.md` | `../evaluation/eval-framework.md` |
| “成本” / “ROI” | `../architecture/planes/cost/paradigm-cost-benchmarks.md` | `../index/maturity-ladders.md` |
| “交叉” / “cross-cutting” | `../architecture/cross-cutting/README.md` | `../architecture/plane-interaction-matrix.md` |

## 输出时优先用这个骨架

```yaml
agent_design:
  user_job: ""
  agent_type: ""
  mva_level: ""
  required_depth: ""
  required_modules: []
  deferred_modules: []
  key_patterns: []
  verification_plan: []
  open_risks: []
```

## 何时展开 25 plane

只在这些场景展开：

- 用户明确要架构审计；
- 已有系统出现边界混淆；
- 设计进入 MVA-4 及以上；
- 涉及高风险写动作、生产环境、安全、金钱、多租户；
- 需要做完整 review。

展开时先读 `../toolkit/module-picker.md`，再读 `../architecture/plane-interaction-matrix.md`。
