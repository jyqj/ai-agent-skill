# Incident Response

> **Evidence Status** — synthesized. 生产 Agent 系统对 trace、配置指纹、effect record、回滚和后续评估的需求。

## 事故排查顺序

1. 确认 config fingerprint。
2. 查看 representation event：输入是否错误、过期、丢字段。
3. 查看 prompt / context event：是否遗漏关键约束。
4. 查看 control / security / cost event：是否误放权、误拦截或预算降级。
5. 查看 interaction event：用户审批、纠错、取消是否被正确处理。
6. 查看 tool / execution event：是否执行失败或重试失控。
7. 查看 world state / effect event：是否误判完成。
8. 查看 external dependency：第三方系统、网络、权限、最终一致性。

## 最小事故包

```yaml
incident_bundle:
  trace_id: string
  config_fingerprint: {}
  representative_task: {}
  failure_stage: representation | prompt | planning | interaction | tool | effect | policy | external_system
  impact: string
  rollback_plan: string
  followup_evals: []
```
