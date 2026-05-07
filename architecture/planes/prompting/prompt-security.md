# Prompt Security — Prompt 层安全

>
> **所属域**：2. Cognition & Continuity — 指令结构与推理模式（与 5. Trust & Identity 交叉）
>
> **Evidence Status** — grounded. OWASP Agentic Security Initiative Top 10 (2026) 对 Agent 安全风险的系统分类；Rule of Two (Meta AI) 对 Agent 权限的不可能三角证明；PCFI 中间件 (arXiv 2603.18433) 的分层检测方案；TokenMix 2026 排名对防御技术的定量评估；500 人红队赛对 12 种公开防御的攻破数据。

**Principle Refs**: IS-02, IS-03, EM-03 — 工具输出不是指令；信任假设需持续校验；环境约束决定信任边界。

Prompt 安全不是"加一句'不要被注入'"就能解决的问题。这是一个攻防不对称的领域：防御者必须堵住所有路径，攻击者只需找到一条。

## 1. 攻防不对称："Attacker Moves Second"

2025-2026 年间多次红蓝对抗赛的核心结论：

| 事件 | 结果 | 关键数据 |
|---|---|---|
| HackAPrompt 2025 | 500+ 红队人员攻破所有 12 种公开防御 | 100% 攻破率 |
| OpenAI IH-Challenge | 指令层级在对抗场景下被系统性绕过 | 多层嵌套加剧脆弱性 |
| TokenMix 2026 Ranking | 最强防御也有已知绕过方式 | 没有银弹 |

### 关键推论

```text
1. 不存在单一技术能完全防御 prompt injection。
2. 防御必须是分层的，每层降低攻击成功率，叠加后达到可接受风险。
3. 安全策略的目标不是 0% 攻破率，而是：
   - 高风险操作有额外保护
   - 攻击被检测并记录
   - 攻击成功后的影响被限制（blast radius minimization）
```

## 2. Rule of Two

Meta AI 提出的 Agent 安全不可能三角：

```text
一个 Agent 最多同时满足以下三条中的两条：

  ① 处理不可信输入（untrusted input）
  ② 拥有敏感访问权限（sensitive access）
  ③ 执行状态变更（state mutation）

三条同时满足 = 必然存在可被利用的攻击面。
```

### 设计约束

| 组合 | 风险 | 设计策略 |
|---|---|---|
| ① + ② | 可读不可信内容 + 有敏感权限 | 不允许基于不可信内容触发敏感操作 |
| ① + ③ | 可读不可信内容 + 可写状态 | 写操作必须基于可信指令，而非不可信数据 |
| ② + ③ | 有敏感权限 + 可写状态 | 可以执行，但输入必须来自可信来源 |
| ① + ② + ③ | 全部满足 | **违反 Rule of Two — 必须拆分** |

### 拆分策略

```text
违规场景：Agent 读取用户上传文件（不可信），有数据库写权限（敏感），执行 SQL 更新（状态变更）

拆分方案：
  Agent A：读取文件 + 提取意图 → 结构化请求（① only）
  Agent B：验证请求 + 执行写操作（② + ③，但输入已可信化）
  隔离层：Agent A 的输出经 Policy Engine 审核后才传给 Agent B
```

## 3. 防御技术排名

基于 TokenMix 2026 排名和多项评估的综合数据：

| 排名 | 技术 | 攻击降低率 | 延迟增加 | 误拒率 | 适用层 |
|---|---|---|---|---|---|
| 1 | PromptArmor（专用检测模型） | >99% | 200-600ms | 2-4% | 高风险层 |
| 2 | Instruction Hierarchy Hardening | 92-96% | 50-100ms | 1-3% | 基础层 |
| 3 | Sandwich Defense（重复系统指令） | 85-90% | <10ms | <1% | 基础层 |
| 4 | XML/Delimiter Tagging | 80-88% | <5ms | <1% | 基础层 |
| 5 | Input/Output Filtering | 75-85% | 30-80ms | 3-8% | 工具使用层 |
| 6 | Paraphrasing（输入改写） | 70-80% | 100-200ms | 5-10% | 工具使用层 |
| 7 | Perplexity Detection | 65-75% | 50-150ms | 8-15% | 工具使用层 |
| 8 | Naive Instruction（"忽略注入"） | 30-50% | 0ms | 0% | 无实际保护 |

### 核心发现

- 排名第 1 的 PromptArmor 攻击降低率最高，但 200-600ms 延迟在实时场景中可能不可接受。
- 排名第 8 的 Naive Instruction 几乎无效，但在生产中仍被广泛使用。
- **单一技术不够**：即使 >99% 降低率，在百万级调用下仍有数千次可能被攻破。

## 4. 分层防御栈

生产系统应按风险等级部署不同强度的防御：

### 4.1 三层架构

```text
┌─────────────────────────────────────────────┐
│  高风险层 — 涉及敏感访问 + 状态变更          │
│  PromptArmor + Rule of Two 拆分 + 人工审批   │
├─────────────────────────────────────────────┤
│  工具使用层 — 涉及工具调用但风险可控          │
│  Input Filtering + Hierarchy Hardening       │
│  + Tool Output Sanitization                  │
├─────────────────────────────────────────────┤
│  基础层 — 所有请求都经过                      │
│  XML Tagging + Sandwich Defense              │
│  + Trust Lane 标注                           │
└─────────────────────────────────────────────┘
```

### 4.2 各层详细策略

| 层 | 技术组合 | 延迟预算 | 目标 |
|---|---|---|---|
| 基础层 | XML Tagging + Sandwich + Trust Lane | <15ms | 阻止低成本注入 |
| 工具使用层 | Input Filter + Hierarchy Hardening + Output Sanitization | <150ms | 阻止工具输出注入 |
| 高风险层 | PromptArmor + Rule of Two + Human Approval | <1000ms | 阻止高价值攻击 |

## 5. PCFI 中间件

PCFI (arXiv 2603.18433) 提出了一种轻量级分层检测中间件：

```text
请求流入 → 词法启发式 → 角色切换检测 → 层级策略检查 → 放行/拦截

Stage 1: 词法启发式（确定性，<5ms）
  - 检测已知注入模式：ignore previous, forget instructions, you are now, etc.
  - 检测编码绕过：base64、unicode、homoglyph
  - 正则匹配 + 黑名单

Stage 2: 角色切换检测（轻量模型，<50ms）
  - 检测文本中是否试图切换说话者身份
  - 检测伪造 system/developer/user 标签
  - 语义分类器：inject_attempt | role_switch | benign

Stage 3: 层级策略检查（规则引擎，<10ms）
  - 验证请求是否符合 Trust Lane 约束
  - 检查是否有越权操作
  - 执行 Rule of Two 检查
```

### PCFI 与纯模型防御对比

| 维度 | 纯模型防御 | PCFI 中间件 |
|---|---|---|
| 检测速度 | 200-600ms | 15-65ms |
| 已知模式覆盖 | 高 | 高（Stage 1+2） |
| 新型攻击适应 | 中（需重训） | Stage 1 低 / Stage 2 中 |
| 可审计性 | 低 | 高（每 stage 有日志） |
| 误拒率 | 2-4% | 1-3% |
| 部署成本 | 需要 GPU | Stage 1+3 仅 CPU |

## 6. OWASP Agentic Top 10 关联

本文件重点关联以下两项：

### ASI01 — Goal Hijack（目标劫持）

```text
攻击方式：通过注入内容改变 Agent 的任务目标
攻击面：用户输入、工具返回值、RAG 检索内容、记忆条目

防御映射：
  - Trust Lane 隔离 → 不可信内容无法覆盖任务目标
  - PCFI Stage 2 → 检测目标切换意图
  - Rule of Two → 限制不可信输入的影响范围
```

### ASI06 — Memory & Context Poisoning（记忆与上下文投毒）

```text
攻击方式：向 Agent 的长期记忆或上下文注入恶意内容
攻击面：可写记忆接口、RAG 索引、对话历史

防御映射：
  - 记忆写入审批 → 不允许外部内容直接写入记忆
  - Provenance 标注 → 每条记忆标记来源和信任等级
  - 过期与隔离 → 可疑内容进入隔离区，不参与推理
```

## 7. Prompt 安全策略模板

```yaml
prompt_security_policy:
  # 基础层 — 所有请求
  base_layer:
    trust_lane_marking: required
    delimiter_tagging: xml  # <system>, <user>, <tool_output>, <retrieved>
    sandwich_defense: enabled
    instruction_repetition: end_of_prompt

  # 工具使用层 — 涉及工具调用
  tool_layer:
    tool_output_sanitization: enabled
    instruction_hierarchy_hardening: enabled
    input_filtering:
      encoding_detection: [base64, unicode_escape, homoglyph]
      known_pattern_blocklist: updated_weekly

  # 高风险层 — 敏感操作
  high_risk_layer:
    dedicated_detector: promptarmor | guard_model
    rule_of_two_enforcement: enabled
    human_approval: required_for_irreversible
    blast_radius_limit:
      max_affected_resources: 10
      rollback_plan: required

  # 监控与响应
  monitoring:
    detection_logging: all_stages
    alert_threshold: 3_attempts_per_session
    incident_response: quarantine_and_notify
```

## 8. 反模式

| 反模式 | 问题 | 修复 |
|---|---|---|
| Naive Defense | 只在 prompt 里写"不要被注入" | 部署分层防御栈 |
| Single-Layer Trust | 所有内容同一信任等级 | 实施 Trust Lane 标注 |
| Detect-Only | 检测到攻击但不阻止 | 检测 + 拦截 + 告警 |
| Over-Trust Tool Output | 工具返回值直接作为指令 | Tool Output 默认进 data lane |
| Security Theater | 部署了防御但不做红队测试 | 定期红蓝对抗 + 回归 |
| All-or-Nothing | 要么不防御，要么所有请求过最严检查 | 按风险分层，平衡安全与延迟 |

## 9. 关联模块

- `instruction-layering.md` — 指令层级是 prompt 安全的前提
- `overview.md` — PromptContract 中的 trust lane 定义
- `../security/overview.md` — 全局安全策略和混合纵深防御
- `../security/red-team-cases.md` — 红队案例库
- `../../../design-space/patterns/untrusted-context-boundary.md` — 不可信上下文边界模式
- `../../../design-space/patterns/guard-model.md` — Guard Model 模式
- `../../../design-space/patterns/tool-output-sanitization.md` — 工具输出净化模式
- `../../../design-space/lessons-learned/memory-poisoning-84pct-success.md` — 记忆注入 84% 成功率实例
- `../../../design-space/lessons-learned/copilot-rce-prompt-injection.md` — Copilot RCE 注入实例
- `../../../design-space/lessons-learned/echoleak-zero-click-exfil.md` — EchoLeak 零点击窃取实例
- `../../../evaluation/security-evals.md` — 安全评估集

## 10. 检查清单

- [ ] 是否部署了分层防御栈，而非依赖单一技术？
- [ ] 涉及敏感操作的路径是否遵守 Rule of Two？
- [ ] Tool output 和 retrieved content 是否默认进入 data lane？
- [ ] 是否有定期红队测试和防御回归？
- [ ] 检测到注入尝试时，是否有拦截、告警和日志记录？
- [ ] 高风险操作的 blast radius 是否受限？
- [ ] 记忆写入是否有审批和 provenance 标注？
