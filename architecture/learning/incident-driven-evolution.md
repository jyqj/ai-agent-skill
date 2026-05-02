# Incident-Driven Harness Evolution

> **Evidence Status** — synthesized. 生产环境中的事故是 Harness 演化的最强信号。Recovery Plane 记录的 FailureRecord、eval 回归失败、用户上报的 P0/P1 问题，共同构成了持续改进的输入源。

## 核心观点

每次生产失败应产出三样东西：根因分析、新增 eval fixture、Harness 配置或策略变更。缺少任何一项，这次失败就只是被"修了"而没有被"学到"。

## 失败到演化的流程

### 1. 记录

事故发生后，Recovery Plane 写入 FailureRecord：

```yaml
failure_record:
  incident_id: string
  severity: P0 | P1 | P2 | P3
  trace_snapshot: []        # 完整 tool calls + 中间状态
  context_snapshot: {}      # 当时的 memory 召回、prompt 版本、model profile
  user_report: string|null  # 用户描述（如有）
  timestamp: datetime
```

### 2. 根因分类

不是所有失败都指向同一层。分类决定修复路径：

| 根因类别 | 典型表现 | 修复层 |
|---|---|---|
| 模型能力不足 | 推理错误、指令遵从差、幻觉 | Model Capability Profile、routing 策略 |
| 工具故障 | API 超时、返回格式变更、权限不足 | 工具注册表、retry/fallback 规则 |
| Harness 策略缺陷 | prompt 引导偏差、缺少 guard rule、错误的 policy | policy、prompt、guard 规则 |
| 表示不准确 | memory 召回错误、上下文拼装遗漏、embedding 偏移 | representation pipeline、验证步骤 |

分类应基于 trace 证据，不是直觉。如果 trace 不足以定位根因，说明 observability 本身需要改进。

### 3. 按分类路由修复

- **模型能力** — 更新 Model Capability Profile 中的弱项标记，调整 routing 策略避开已知盲区，必要时切换到更适合的模型。
- **工具故障** — 在工具注册表中添加已知故障模式，配置 retry 策略或 fallback 路径，更新 tool contract 版本。
- **Harness 策略** — 修改 policy rule、调整 prompt 版本、增加或收紧 guard 条件。这是最常见的修复路径。
- **表示不准确** — 更新 representation pipeline 的预处理逻辑，添加输出验证步骤，调整 embedding 参数或召回阈值。

### 4. 生成 eval fixture

将失败场景转化为回归测试用例，自动加入评估套件：

```yaml
eval_fixture:
  fixture_id: string
  source_incident: incident_id
  failure_mode: string          # 简短描述失败模式
  input_scenario: {}            # 触发条件
  expected_behavior: string     # 修复后应有的行为
  created_at: datetime
  status: active | deprecated
```

### 5. 变更验证

用新 fixture + 全量回归确认：修复有效、无副作用、不与现有 policy 冲突。验证通过后，变更进入正式生效状态。

## Eval 集自动扩张

每个 P0/P1 事故应产出至少一个 fixture。Fixture 必须标注来源 incident ID、失败模式和预期行为，使后续审查者能追溯"为什么有这条测试"。

Fixture 集会随时间膨胀。定期审查是必要的：环境已变化的场景标记 `deprecated`，重复覆盖的场景合并，确保 eval 运行时间不会无限增长。审查频率建议与 Model Capability Profile 更新周期对齐。

## Anti-pattern

只修 prompt 不建 fixture。这种做法在当前模型版本下看起来有效，但下次换模型、升级 API 或调整 routing 时，同样的失败会重现。没有 fixture 就没有回归保护。

## 关联文档

- `overview.md` — 学习模块总览
- `feedback-loops.md` — 反馈回路分类
- `safety-guardrails.md` — 变更的安全约束
- `../../planes/recovery/` — Recovery Plane 与 FailureRecord
