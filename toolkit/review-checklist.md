# Review Checklist

> **Evidence Status** — synthesized. 从完整 `../index/design-checklist.md` 压缩出的轻量评审入口；用于开发中快速查漏。

## 10 分钟 review

```text
[ ] 用户 job 和交付物是否明确？
[ ] 当前是哪个 MVA 级别？有没有过度设计？
[ ] 是否选择了正确品类，而不是泛泛“通用 Agent”？
[ ] 是否区分 Context / Memory / Task State / World State？
[ ] 写动作是否有 postcondition 和 read-after-write / test / ack？
[ ] 外部文本、工具输出、网页内容是否默认 data lane？
[ ] 高风险动作是否有 approval / capability / audit？
[ ] 失败是否有 FailureRecord、retry budget、recovery action？
[ ] 是否有最小 eval 或 fixture？
[ ] 未验证、部分验证、不可验证是否会明确交付？
```

## 30 分钟 review

加查：

```text
[ ] 模型 / prompt / tool schema / policy 是否有配置指纹？
[ ] 是否有 loop detection 和 context compaction 策略？
[ ] 多 Worker 是否有 output contract 和 merge strategy？
[ ] 成本接近阈值时是否 partial deliver 或 ask user？
[ ] 学习/skill 固化是否需要 replay/eval 后再激活？
```

## 输出格式

```yaml
review_result:
  status: pass_with_gaps
  must_fix:
    - "effect verification missing for write action"
  should_fix:
    - "no config fingerprint yet"
  intentionally_deferred:
    learning-adaptation: "not needed before MVA-5"
```

## 深入入口

1. `../index/design-checklist.md`
2. `../concepts/foundations/principle-obligation-eval-map.md`
3. `../architecture/plane-interaction-matrix.md`
