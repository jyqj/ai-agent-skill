# Security Agent Closed Loop

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

```text
1. Detect: 告警接收 → 去重 → 优先级
2. Enrich: 关联 TI + 资产 + 历史
3. Investigate: 攻击链 → 影响 → 证据
4. Respond: 策略 → [确认] → 执行
5. Verify: 威胁已遏制 → 无残留
6. Report: incident 报告 + 更新规则
```

Stop Gate: 威胁遏制 + 影响确定 + 证据保存 + 无残留 + 规则更新
