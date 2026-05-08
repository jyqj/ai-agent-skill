# Failure Router

> **Evidence Status** — synthesized. 从 `../index/design-checklist.md`、`../design-space/anti-patterns/` 和 25 plane 边界压缩而来，用于从症状快速定位该读什么。

## 30 秒判断

| 症状 | 最可能边界 | 先读 |
|---|---|---|
| 输入一变就误解 | Representation / Context | `../architecture/planes/representation/overview.md` |
| 工具 success 但任务没完成 | Execution / Effects | `../synthesis/tool-effect-verification.md` |
| 长任务中断后接不上 | State / World State / Recovery | `../synthesis/runtime-vs-world-state.md` |
| 记忆越来越不准 | Memory / Representation / Time | `../synthesis/context-memory-state-boundaries.md` |
| 外部网页或工具输出带偏 Agent | Security / Context | `../design-space/patterns/untrusted-context-boundary.md` |
| 多 Agent 输出无法合并 | Orchestration / Dataflow | `../architecture/planes/orchestration/overview.md` |
| 成本失控 | Cost / Operations | `../architecture/planes/cost/overview.md` |
| 用户觉得不可控 | Interaction / Control / Explainability | `../architecture/planes/interaction/overview.md` |
| 反复重试同一步 | Recovery / Concurrency | `../architecture/planes/recovery/overview.md` |
| 上线后行为漂移 | Operations / Observability / Eval | `../architecture/planes/operations/overview.md` |
| Agent 自主删除生产数据 | Control / Identity-Capability | `../design-space/lessons-learned/pocketos-9-second-deletion.md`, `../design-space/lessons-learned/replit-deletion-and-coverup.md`, `../architecture/planes/control/overview.md` |
| Agent 生成虚假输出掩盖错误 | Effects / Verification | `../design-space/lessons-learned/replit-deletion-and-coverup.md`, `../synthesis/tool-effect-verification.md` |
| 多 Agent 循环烧钱 | Cost / Orchestration | `../design-space/lessons-learned/47k-multi-agent-loop.md`, `../architecture/planes/cost/overview.md`, `../architecture/planes/orchestration/overview.md` |
| Agent 越权执行金融交易 | Identity-Capability / Control | `../design-space/lessons-learned/step-finance-40m-loss.md`, `../architecture/planes/identity-capability/overview.md` |
| Prompt Injection 导致代码执行 | Security / Trust-Boundary | `../design-space/lessons-learned/copilot-rce-prompt-injection.md`, `../architecture/planes/security/overview.md` |
| 记忆被外部内容篡改后持续误导 | Memory / Security | `../design-space/lessons-learned/memory-poisoning-84pct-success.md`, `../architecture/cross-cutting/memory-x-security.md` |
| 评估分数高但生产表现差 | Evaluation / Observability | `../design-space/lessons-learned/benchmark-reward-hacking.md`, `../evaluation/eval-framework.md` |
| Agent 技能/工具被供应链投毒 | Security / Tool Registry | `../design-space/lessons-learned/clawhavoc-supply-chain-poisoning.md`, `../architecture/planes/security/overview.md` |

## 输出格式

```yaml
symptom: "tool returned success but CRM field unchanged"
likely_boundary:
  - execution_vs_effects
root_question: "was the external world independently read back?"
read_next:
  - ../synthesis/tool-effect-verification.md
  - ../architecture/planes/effects/overview.md
  - ../design-space/lessons-learned/tool-success-as-completion.md
repair_pattern:
  - effect-ledger
  - self-verification
```

## 下一步

1. `../index/category-pattern-matrix.md`
2. `eval-planner.md`
3. `../design-space/anti-patterns/README.md`
