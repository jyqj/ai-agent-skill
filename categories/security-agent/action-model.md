# Security Agent Action Model

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

| 动作 | 风险 | Verification |
|---|---|---|
| 查询日志/流量 | safe | 结果相关 |
| 威胁情报查询 | safe | IOC 匹配 |
| 隔离主机/用户 | approval | 隔离生效 |
| 阻断 IP/域名 | approval | 规则生效+不误伤 |
| 修复漏洞 | approval | 不再检出+无回归 |

安全约束：最小权限、操作审计、隔离需双重确认、输入净化。
