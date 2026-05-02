# Evaluation

> **Evidence Status** — synthesized. coding、workflow、memory、research、browser 场景中对任务完成、验证、恢复、证据与回归的共同需求；this repository 对 Agent 评估维度和运行方式的统一抽象。

评估（Evaluation）是 Agent 系统质量的度量基础——没有可回归的评估，任何改进都只是猜测。

Agent 评估不只是看回答质量，而是看：

- 任务是否真实完成；
- 表示是否可靠；
- 外部效果是否被验证；
- 过程是否可控；
- 失败是否可恢复；
- 上线升级是否会回归；
- 成本与质量是否可量化对比；

| 文件 | 作用 |
|---|---|
| `eval-framework.md` | 通用评估框架、Eval Case 格式、Scorecard |
| `eval-runner-spec.md` | 评测运行器、fixture、failure injection、回归门禁 |
| `fixtures/README.md` | fixture 目录约定与样例说明 |
| `failure-taxonomy.md` | 失败模式分类（含表示、效果、安全、运维） |
| `representation-evals.md` | 表示层专项评估 |
| `effect-evals.md` | 外部效果与回读验证专项评估 |
| `security-evals.md` | prompt injection、tool output injection、memory poisoning 等安全评估 |
| `human-in-the-loop-evals.md` | 审批疲劳、升级、人工兜底评估 |
| `execution-depth-evals.md` | 执行深度专项评估 |
| `coding-agent-evals.md` | Coding Agent 评估场景 |
| `research-agent-evals.md` | Research Agent 的 citation / conflict / freshness 评估 |
| `cost-evals.md` | 成本与质量曲线评估 |
| `memory-evals.md` | Memory Agent 评估场景 |
| `tool-use-evals.md` | Tool Use 评估场景 |

| `trajectory-evaluation.md` | 轨迹评估：六维指标、多 Agent 轨迹、参考轨迹构造 |

推荐配合 `../meta/templates/eval-case-template.yaml` 一起使用。

## 可执行评估入口

- `eval-runner/README.md`：最小可执行 eval runner。
- `eval-runner/tests/`：对 runner 的基础回归测试。
- `testability-design.md`：mock world、trace replay、property-based testing、shadow mode。
- `.github/workflows/skill-checks.yml`：示例 CI 入口。
