# Agent Platform Closed Loop

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

## 执行闭环
```text
Receive → Validate(鉴权+配额) → Route(环境+模型) → Execute(checkpoint) → Monitor → Deliver+Trace
```

## 部署闭环
```text
Build → Eval(离线) → Deploy(canary) → Monitor(baseline 对比) → Promote/Rollback
```
