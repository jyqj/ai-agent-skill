# Security Agent Representation Model

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

| 对象 | 含义 | Freshness | Trust |
|---|---|---|---|
| SecurityAlert | 来源/类型/MITRE 映射 | 实时 | medium |
| ThreatIntelligence | IOC/TTP/攻击者 | 小时/天 | 来源分级 |
| VulnerabilityRecord | CVE/CVSS/影响范围 | 天级 | high |
| AssetInventory | 主机/服务/暴露面 | 天/周 | medium |
| ScanResult | SAST/DAST/SCA | 扫描时 | high |
| FindingEvidence | 原始信号 | 发现时 | high |

原则：证据链不可断；secret 自动 redact；IOC 有时效；MITRE ATT&CK 映射。
