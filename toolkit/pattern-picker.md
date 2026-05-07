# Pattern Picker

> **Evidence Status** — synthesized. 面向开发者的 pattern 选择器；避免直接进入完整模式库造成路径爆炸。

## 30 秒判断

| 设计问题 | 首选 pattern | 不要误用 |
|---|---|---|
| 任务规格不清 | `../design-space/patterns/contract-agent.md` | 不要用长 prompt 替代验收标准 |
| 阶段太长易跑偏 | `../design-space/patterns/milestone-gated-execution.md` | 不要只有自然语言计划 |
| 工具结果很大 | `../design-space/patterns/tool-output-offloading.md` | 不要把全文塞上下文 |
| 外部输入不可信 | `../design-space/patterns/untrusted-context-boundary.md` | 不要让网页/日志变成指令 |
| 写动作要验证 | `../design-space/patterns/effect-ledger.md` | 不要把 tool success 当 done |
| 需要长期经验复用 | `../design-space/patterns/skill-crystallization.md` | 不要未经验证直接激活 skill |
| 多 Worker 并行 | `../design-space/patterns/worker-orchestration.md` | 不要共享裸上下文 |
| 需要回归测试 | `../design-space/patterns/shadow-mode-regression.md` | 不要只看单次 demo |

## 模式选择规则

```text
先选当前最高风险对应的 1-2 个 pattern。
如果一个 pattern 没有触发风险，不要提前引入。
```

## 最小产出

```yaml
selected_patterns:
  - effect-ledger
  - untrusted-context-boundary
why:
  - "agent writes external CRM"
  - "tool output contains third-party text"
not_selected:
  worker-orchestration: "single-agent MVA-3 for now"
```

## 下一步

1. `eval-planner.md`
2. `../design-space/patterns/README.md`
3. `../index/category-pattern-matrix.md`
