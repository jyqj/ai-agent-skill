# Security Agent Architecture

> **Evidence Status** — grounded. 基于 Databricks Lakewatch、SentinelOne Purple AI、Microsoft Sentinel、OWASP LLM Top-10、MITRE ATT&CK、SOC 自动化实践归纳。

## Core Job

Security Agent 的工作不是"替代安全分析师"，而是在真实安全运营中完成告警分诊、威胁调查、证据整理和响应建议，同时**确保自身不成为攻击通道**：

```text
检测/接收威胁信号 → 聚合关联 → 构建证据链 → 风险评估 → 响应决策 → 执行/升级 → 验证缓解 → 审计留痕
```

核心挑战有两个：一是在海量噪音中识别真正的威胁（信噪比），二是 Security Agent 自身也是攻击面（self-security）。

## 用户模型

| 用户 | 心智模型 | 信任建立方式 | 默认交互 |
|---|---|---|---|
| SOC 分析师 | 调查加速器 / Tier-1 分诊员 | 证据准确、减少噪音、不漏关键告警 | 告警摘要 + 证据链 + 建议动作 |
| 安全工程师 | 扫描/修复辅助 | 漏洞准确、修复方案可行 | 漏洞报告 + 修复 patch + 验证方法 |
| CISO / 管理层 | 风险感知器 | 风险量化准确、合规状态清晰 | 风险仪表板 + 趋势 + 合规差距 |
| IR 团队 | 事件响应助手 | 时间线准确、证据链完整 | 事件时间线 + IoC 列表 + 影响范围 |

信任建立依赖**零误导**：安全领域的错误建议可能导致攻击面扩大。Agent 不确定时必须明确表达不确定性，而非给出看似自信的错误判断。

## SIEM 集成与告警消费

> **Evidence Status** — grounded. Databricks Lakewatch 的 agentic detection 架构显示，AI agent 直接消费 SIEM 告警流时，关键挑战是关联分析和降噪。

### 告警消费流程

```text
SIEM 告警流（Splunk/Sentinel/Elastic）
  → 告警归一化（统一 schema）
  → 去重与聚合（同一事件的多条告警合并）
  → 上下文富化（资产信息、用户画像、历史行为）
  → 优先级评估（资产价值 x 威胁严重度 x 置信度）
  → 分诊决策（自动关闭 / 调查 / 升级）
```

### 关联分析

| 关联维度 | 方法 | 示例 |
|---|---|---|
| 时间关联 | 同一时间窗口内的异常聚合 | 5 分钟内同一 IP 触发 3 条不同规则 |
| 实体关联 | 围绕同一实体（IP/用户/主机）聚合 | 同一用户账号在多个系统出现异常 |
| 攻击链关联 | 映射到 MITRE ATT&CK kill chain | 侦察 → 初始访问 → 横向移动的完整链条 |
| 跨源关联 | 不同数据源的信号交叉验证 | 防火墙日志 + EDR 告警 + 身份认证日志 |

### 降噪策略

- 基线学习（Baseline Learning）：建立正常行为基线，偏离基线才告警
- 告警聚合：同类告警按时间窗口和实体维度合并
- 已知误报（Known FP）数据库：已确认的误报模式自动抑制
- 分析师反馈循环：分析师关闭告警时标注原因，反馈回降噪模型

## 威胁情报消费

| 环节 | 实现 | 注意事项 |
|---|---|---|
| IoC Feed 集成 | 消费 STIX/TAXII 格式的 IoC（Indicator of Compromise） | 多源 feed 去重、冲突处理 |
| 上下文富化 | 为裸 IoC 补充 TTP、来源可信度、关联 campaign | 区分高可信商业 feed 和低可信开源 feed |
| Stale Intel 处理 | IoC 有时效性；过期指标产生误报 | 设置 TTL、定期清理、标记 confidence decay |
| 内部情报生成 | 从自身检测结果中提取可复用的 IoC 和模式 | 脱敏后才可共享 |

## 自动化响应决策树

不是所有响应都应该自动化。决策依据两个轴：**风险等级**和**置信度**。

```text
                    高置信度              低置信度
  低风险     自动响应 + 记录        自动响应 + 通知分析师
  中风险     自动响应 + 需确认      升级到分析师
  高风险     建议动作 + 等待审批    升级到分析师 + 高优先级
  关键       仅建议 + 强制人工审批  紧急升级 + 多人确认
```

> **Evidence Status** — grounded. SentinelOne Purple AI 的实践表明，自动化响应的边界应由组织的风险容忍度决定，而非技术能力。

自动化可执行的动作示例：
- 低风险：更新防火墙规则阻断已确认恶意 IP、隔离已确认恶意文件
- 中风险：临时禁用可疑用户账号（需确认）、隔离受感染主机（需确认）
- 高风险及以上：网络段隔离、全量密码重置——仅建议，人工执行

## Security Agent 自身安全

> **Evidence Status** — grounded. OWASP LLM Top-10 明确指出 prompt injection 和 data poisoning 是 LLM 应用的首要威胁。Security Agent 处理的输入本身就可能是攻击载荷。

| 攻击面 | 威胁 | 防护 |
|---|---|---|
| 告警文本注入 | 攻击者在日志/告警字段中嵌入 prompt injection | 输入净化；告警内容作为 data lane 而非 instruction lane |
| 记忆投毒（Memory Poisoning） | 通过持续注入虚假信号污染 Agent 的历史判断 | 记忆隔离；写入验证；异常记忆检测 |
| 工具滥用 | Agent 被诱导执行危险操作（如关闭防火墙） | 最小权限原则；高危操作强制人工审批 |
| 供应链攻击 | 恶意 IoC feed 或插件 | feed 来源验证；插件沙箱化 |
| 信息泄露 | Agent 在回应中泄露内部安全架构 | 输出过滤；敏感信息 redact |

核心原则：**Security Agent 消费的每一条输入都是 untrusted data**。告警文本、日志、IoC feed、用户查询——全部经过净化后才可处理。

## 合规维度

| 合规要求 | Agent 实现 |
|---|---|
| 审计日志 | 所有 Agent 决策和动作记录不可变审计日志（who/what/when/why） |
| 证据链完整性 | 每个 finding 可追溯到原始信号；中间推理步骤保留 |
| GDPR 相关 | 日志中的个人数据按保留策略处理；支持数据主体请求 |
| SOC 2 | Agent 操作纳入访问控制和变更管理流程 |
| 数据分类 | 扫描结果按敏感度分级；高敏感度结果限制访问范围 |
| 保留策略 | 安全事件数据按法规要求保留期限存储 |

## 误报管理

> **Evidence Status** — synthesized. SOC 自动化研究显示，分析师疲劳（Alert Fatigue）是安全运营的头号效能杀手，误报率超过 50% 时分析师开始忽略真实告警。

| 策略 | 实现 |
|---|---|
| FP 抑制 | 已确认误报的模式签名化，后续自动抑制 |
| 反馈循环 | 分析师每次分诊结果回流到模型，持续校准 |
| 置信度标注 | 每条告警附带 Agent 的置信度评分，分析师优先处理高置信告警 |
| 疲劳预防 | 控制单位时间内推送到分析师的告警数量上限 |
| 默认偏向 | FP > FN（宁可多报不漏报），但持续优化降低 FP 率 |
| 周期性审查 | 定期回顾被自动抑制的告警，防止规则过时导致漏报 |

## 闭环模型

```text
Observe：接收告警/日志/IoC/用户查询
  → Represent：告警归一化 + 实体图 + 攻击链映射 + 上下文富化
  → Decide：优先级评估 + 响应策略选择（自动/升级/建议）
  → Act：执行响应动作 / 生成调查报告 / 升级通知
  → Verify：确认缓解有效 + 无附带损害 + 证据链完整
  → Update：更新基线 + 反馈降噪模型 + 审计日志
```

Stop gate：

```text
[ ] 证据链完整，每个结论可追溯到原始信号
[ ] 响应动作未超出授权范围
[ ] 敏感信息已 redact
[ ] 审计日志已记录
[ ] 高风险操作已获人工确认
```

## 品类设计决策

| 决策 | 默认建议 |
|---|---|
| 自身安全 | 输入净化、记忆隔离、最小权限、操作审计；告警内容为 data lane |
| 误报策略 | FP > FN（宁可多报）；分析师反馈持续优化 |
| 隔离 | 多租户隔离；扫描结果不跨租户 |
| 机密 | secret 自动 redact；不存入记忆/日志 |
| 证据链 | 每个 finding 可追溯到原始信号 |
| 响应控制 | 低风险高置信自动化；高风险强制人工 |

## Semi-Autonomous SOC Cycle（2026 趋势）

> **Evidence Status** — grounded. Google Cloud AI Agent Trends 2026 Report；Torq Socrates AI SOC Analyst；Google Secure AI Framework 2.0。

2026 年安全运营从被动响应进化为**半自治循环**——多个专任 AI Agent 编排协作：

```text
Detection (AI) → Alert (Human managed) → Triage & Investigation (AI)
  → Threat Research (AI) → Malware Analysis (AI) → Detection Engineering (AI)
  → Response (AI) → Recommendation (AI) → Escalation (Human managed)
```

关键架构特征：
- 多 SOC Agent 共享安全遥测数据（通过 MCP 连接 SIEM/EDR/身份系统）
- 通过 A2A 协议实现 Agent 间结构化通信和任务传递
- 人类在 Alert 评估和 Escalation 两个节点介入决策
- Agent 持续从安全专家的实际洞察中学习和演化

分析师角色升级（从反应到战略）：
| 新角色 | 活动 |
|---|---|
| Threat Hunter | 用直觉和经验引导 Agent 进行主动搜索 |
| Agent Supervisor | 微调 Agent 的交战规则、性能评审 |
| Strategic Defender | 关注长期安全态势和防御架构 |

生产数据：Torq Socrates 实现 90% Tier-1 自动化、95% 手动任务减少、10x 响应加速。

详见 `../../design-space/frontier/agentic-commerce-and-protocols.md`。

## 混合纵深防御

Security Agent 自身安全应采用混合纵深防御策略：

```text
Layer 1: Policy Engine — 确定性规则（如高危命令禁止自动执行）
Layer 2: Guard Model — 独立小模型检测告警文本中的注入攻击
Layer 3: Model Hardening — 对抗训练提高 base model 对安全场景的鲁棒性
Layer 4: Assurance — 红队测试、变体分析、回归检查
```

详见 `../../design-space/patterns/guard-model.md`。

## 参考实现

| 参考 | 学习点 |
|---|---|
| Databricks Lakewatch | 开放 SIEM 架构、agentic 检测、告警消费模型 |
| SentinelOne Purple AI | AI 调查加速、威胁猎杀、自动化响应边界 |
| Microsoft Sentinel | 云原生 SIEM、实体行为分析（UEBA）、实体图 |
| OWASP LLM Top-10 | LLM 应用安全框架、prompt injection 防护 |
| MITRE ATT&CK | 攻击链映射、TTP 分类、检测覆盖度评估 |
| Torq Socrates | AI SOC Analyst：多 Agent 编排、90% Tier-1 自动化 |
| Specular | 攻击性安全平台：Gemini 2.5 Pro 驱动渗透测试自动化 |
| Google Secure AI Framework 2.0 | 自主 AI Agent 风险框架 |
| Google CodeMender | AI 驱动代码安全修复，发现零日漏洞 |

## 阅读路径

```text
README.md（本文）
  → ../../paradigms/reasoning-paradigms.md（证据推理相关）
  → ../../architecture/planes/control/overview.md（权限与审批控制）
  → ../../architecture/planes/observability/overview.md（审计与追踪）
  → ../../architecture/planes/tools/overview.md（工具安全与最小权限）
```

- 主观性任务的验证扩展：`../../concepts/beyond-verification.md`
