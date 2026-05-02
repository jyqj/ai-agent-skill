# Ops / SRE Agent Closed Loop

> **Evidence Status** — synthesized. 基于品类架构模板和 Ops/SRE 场景的通用设计。

## 核心循环

```text
1. Detect: 告警接收+去重+优先级
2. Triage: 聚合关联（metrics+logs+traces+deploys）
3. Diagnose: 根因假设+证据排序+置信度
4. Mitigate: 选择策略 → [确认] → 执行
5. Verify: 监控 SLI 恢复 → 确认有效 → 或回滚
6. Learn: incident timeline + 复盘 + 更新 runbook
```

## Stop Gate

```text
[ ] SLI 已恢复正常
[ ] 根因已识别或已排除高优假设
[ ] 缓解动作已记录
[ ] 未引入新问题
[ ] incident 记录完整
```
