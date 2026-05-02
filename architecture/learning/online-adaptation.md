# Online Adaptation 与权重不变假设

> **Evidence Status** — synthesized. 当前知识库的架构以"模型权重不变，Harness 演化"为基础假设。生产中的 prompt A/B 测试、tool routing 动态调权、memory 策略调参等实践，验证了这一假设在大多数场景下成立。但模型微调、版本升级、RL from feedback 等场景需要显式处理。

## 核心观点

在线适应发生在 Harness 层，不触碰模型权重。这个边界清晰、可审计、可回滚。当适应需要越过这个边界时，应作为显式的版本变更事件处理，而非隐式漂移。

## Harness 层在线适应

以下机制不需要改模型权重，属于 Harness 层的正常演化范围：

**Prompt 版本热切换**：对同一任务维护多个 prompt 版本，通过 A/B 测试或 multi-armed bandit 策略，根据 eval 指标自动收敛到更优版本。切换记录写入 decision log，确保可追溯。

**Tool routing 动态调整**：根据工具的实时成功率、延迟、错误率调整 routing 权重。连续失败的工具自动降权或触发 fallback，恢复后逐步提权。这比静态配置更健壮，但需要设置调整幅度上限，防止单次异常导致过度反应。

**Memory 策略自适应**：根据召回命中率和下游任务成功率，调整 embedding model 选择、检索参数（top-k、相似度阈值）、reranking 策略。调整粒度应足够细，使每次变更的影响可度量。

**Guard rule 动态更新**：从 red-team 测试结果、安全事件中自动生成新的拦截规则。新规则先进入 shadow mode（只记录不拦截），确认误杀率可接受后再激活。

## 模型权重变化的场景

以下场景突破了"权重不变"假设，需要额外的流程保障：

**Fine-tuning on task data**：在特定任务数据上微调会改变模型行为分布。微调后必须跑全量 eval 回归，更新 Model Capability Profile，重新验证所有依赖该模型的 routing 策略。微调前后的模型应视为不同版本。

**Model version upgrade**：供应商发布新版本时，即使 API 兼容，模型行为也可能变化。Profile 需要重新评估，prompt 可能需要适配。建议在 staging 环境完成全量回归后再切换生产流量。

**RL from feedback**：如果使用用户反馈做在线学习（RLHF / RLAIF），模型行为会持续漂移。Harness 需要额外的 safety guardrail：设置行为漂移的监控指标，超过阈值时冻结学习并触发人工审查。

## 设计原则

在线适应的粒度应该是可审计的配置变更，而非不可追溯的隐式漂移。每次自动调整都应记录在 decision log 中：

```yaml
adaptation_event:
  event_id: string
  timestamp: datetime
  adaptation_type: prompt_switch | routing_update | memory_param | guard_rule
  previous_value: {}
  new_value: {}
  trigger: string         # 触发适应的原因
  evidence_refs: []       # 支撑决策的数据
  rollback_path: string   # 如何撤回
```

如果一次自动适应无法用上述结构描述，说明它的粒度太粗或边界不清晰，需要拆分。

## 关联文档

- `overview.md` — 学习模块总览
- `feedback-loops.md` — 反馈回路与适应的关系
- `incident-driven-evolution.md` — 失败驱动的 Harness 演化
- `safety-guardrails.md` — 适应过程中的安全约束
