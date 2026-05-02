# Security Agent Implementation Map

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

## 参考

| 参考 | 学习点 |
|---|---|
| Databricks Lakewatch | 开放 SIEM |
| SentinelOne | AI 调查 |
| OWASP LLM Top-10 | 安全框架 |

## 架构

```text
Orchestrator
  ├── Triage Agent (SIEM)
  ├── TI Agent (威胁情报)
  ├── Investigation Agent (日志/流量)
  └── Remediation Agent (修复/隔离)
```

## MVA: 0(摘要) → 2(分诊+富化) → 3(攻击链+证据) → 4(半自动响应) → 5(检测规则生成+猎杀)
