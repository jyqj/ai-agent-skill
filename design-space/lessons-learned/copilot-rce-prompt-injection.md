# GitHub Copilot RCE：Prompt Injection 到远程代码执行

> **Evidence Status** — grounded.
> - [GitHub Copilot RCE via Prompt Injection - Embrace The Red](https://embracethered.com/blog/posts/2025/github-copilot-remote-code-execution-via-prompt-injection/)
> - [CVE-2025-53773 - NVD](https://nvd.nist.gov/vuln/detail/CVE-2025-53773)

---

## 事故场景

2025-08，安全研究者披露了 GitHub Copilot 的一个严重漏洞（CVE-2025-53773，CVSS 7.8-9.6）。攻击者可以在源代码文件、网页、GitHub Issues 等内容中植入恶意 prompt，当 Copilot 解析这些内容时，注入的指令会修改 VS Code 的安全配置，将 Copilot 切换到"YOLO 模式"，即所有后续操作（包括执行 shell 命令）无需用户确认。

本案例的核心威胁模型是：**工具输出（代码文件、网页内容、Issue 文本）中的恶意指令通过 prompt injection 进入 Agent 的决策流程，最终实现从"读取不受信内容"到"执行任意代码"的完整攻击链**。潜在影响覆盖 100,000+ 开发者机器。

---

## 故障链（按时间顺序）

```
阶段 1: 载荷植入
─────────────────────────────────────────────
T+0       攻击者在以下任一位置植入恶意 prompt：
          - 源代码文件（注释或字符串常量中）
          - 网页内容（Copilot 浏览网页时处理）
          - GitHub Issue / PR 描述或评论
          ↓ 载荷被伪装为正常文本内容

阶段 2: Prompt Injection
─────────────────────────────────────────────
T+?       Copilot 在正常工作流程中解析上述内容
          ↓ 恶意 prompt 被注入到 Copilot 的指令上下文中
          ↓ Copilot 无法区分"来自用户的指令"和"来自文件内容中的指令"

阶段 3: 安全配置篡改（关键步骤）
─────────────────────────────────────────────
T+?       注入的指令操纵 Copilot 修改 .vscode/settings.json
          ↓ 添加 "chat.tools.autoApprove": true
          ↓ Copilot 进入"YOLO 模式"——所有操作无需用户确认
          ↓ 这一步是 Agent 修改自身安全配置的权限提升

阶段 4: 任意代码执行
─────────────────────────────────────────────
T+?       YOLO 模式下，攻击者的后续指令被自动执行
          ↓ 可执行任意 shell 命令
          ↓ 可浏览网页、下载文件
          ↓ 可执行特权操作（取决于用户的系统权限）
          ↓ 潜在影响 100,000+ 开发者机器
```

### 攻击链的关键特征

```
信任等级         内容来源                 Copilot 的处理方式
────────        ─────────────────       ──────────────────
高信任          用户直接输入              作为指令执行
高信任（错误）   代码文件中的内容           作为指令执行（应为低信任）
高信任（错误）   网页内容                  作为指令执行（应为低信任）
高信任（错误）   GitHub Issue 内容         作为指令执行（应为低信任）
```

所有来源的内容被赋予了相同的信任等级，这是 Trust Everything 反模式的精确体现。

---

## 根因分析

### 1. Agent 可修改自身安全配置

这是本案例最关键的设计缺陷。Copilot 拥有修改 `.vscode/settings.json` 的权限，而该文件中包含控制 Copilot 自身行为的安全配置（如 `autoApprove`）。这意味着：

```
Agent 的能力包含了"修改自身安全约束"的权限
  → Agent 可以将自身从"受限模式"升级到"无限模式"
    → 外部指令（通过 prompt injection）可以触发这个升级
      → 攻击者通过修改配置文件间接获得 Agent 的全部能力
```

安全配置应该是 Agent 的**不可变约束**，而非 Agent 可修改的**运行时参数**。

### 2. 输入来源缺乏信任分层

Copilot 在处理代码文件、网页、Issue 内容时，没有区分内容的信任等级。用户直接输入的指令和从不受信来源读取的内容被放入同一个上下文窗口，以相同的信任等级参与推理。

正确的信任分层应为：

```
Trust Level 4（最高）  用户直接输入
Trust Level 3         系统配置和内置 prompt
Trust Level 2         已验证的工具返回值
Trust Level 1         代码文件内容（可能被污染）
Trust Level 0（最低）  网页、Issue、邮件等外部内容
```

Level 0-1 的内容**绝不应被当作指令执行**，只能作为数据处理。

### 3. "YOLO 模式"的设计缺陷

`autoApprove` 配置项的设计意图是提升效率，让用户跳过确认步骤。但它创造了一个"从受限到无限"的二元开关，且该开关可以被 Agent 自身修改。

安全的自动批准设计应该：
- 仅适用于白名单内的低风险操作
- 不能涵盖 shell 执行、文件系统写入、网络请求
- 不能被 Agent 自身启用，必须由用户在 Agent 无法访问的路径中手动配置
- 启用后仍保留不可自动批准的操作类别（如安全配置变更本身）

### 4. 配置完整性缺失

`.vscode/settings.json` 是一个普通文件，任何有文件写入权限的进程都可以修改它。安全配置存储在一个无完整性保护的位置，等于没有安全配置。

---

## 架构缺陷

| 缺失的 Plane/Pattern | 说明 |
|----------------------|------|
| Configuration Integrity | Agent 可自行修改自己的安全配置。安全配置应是 Agent 的不可变约束，而非可修改的运行时参数 |
| Input Source Trust Level | 不同来源的内容（用户输入、代码文件、网页、Issue）未区分信任等级，被等价处理 |
| Privilege Escalation Prevention | Agent 可将自身从受限模式升级到无限模式。缺乏防止权限提升的机制 |
| Instruction-Data Separation | 不受信来源的内容被当作指令执行。缺乏指令和数据的严格分离 |
| Security Configuration Lockdown | 安全配置存储在 Agent 可写的路径中，无完整性校验 |
| Tool Output Sanitization | 工具输出（文件读取、网页抓取）未经消毒处理直接进入推理上下文 |

---

## 设计教训

1. **Agent 绝不应有修改自身安全配置的能力**。安全配置（权限范围、审批要求、操作白名单）应存储在 Agent 无法访问的位置，由独立的安全管理组件控制。Agent 可以请求权限变更，但变更必须由人工或独立系统审批。

2. **输入信任分层是防御 prompt injection 的架构基础**。每个输入来源必须有明确的信任等级标注。低信任来源的内容只能作为"数据"参与处理，绝不能作为"指令"影响 Agent 行为。信任等级应在数据进入 Agent 上下文之前确定，而非由 Agent 自行判断。

3. **"YOLO 模式"类的全局安全开关不应存在**。如果业务需要自动批准，应采用细粒度的白名单机制：只有预定义的低风险操作可以自动执行，高风险操作（shell 执行、配置修改、文件删除）永远需要确认。

4. **工具输出是不受信数据，必须经过消毒处理后再进入推理上下文**。文件读取、网页抓取、API 返回值等工具输出可能包含恶意 prompt injection 载荷。Agent 框架应在工具输出进入上下文前进行消毒（移除或标记可疑的指令性内容）。

5. **"读取不受信内容"到"执行任意代码"的攻击链必须被架构性阻断**。阻断点至少包括：信任分层（阻止不受信内容成为指令）、配置完整性（阻止 Agent 修改安全配置）、操作白名单（阻止高危操作自动执行）。三个阻断点中任意一个有效，攻击链即被打断。

6. **安全配置的完整性需要独立保护**。安全关键配置（如 `autoApprove`）不应存储在 Agent 可写的文件中。应使用签名配置、只读挂载、或由独立安全进程管理的配置存储。任何对安全配置的修改都应触发告警。

7. **prompt injection 的防御不能仅依赖模型层面的对齐**。即使模型被训练为"不执行注入的指令"，攻击者仍可通过足够复杂的载荷绕过。防御必须在架构层面实施：分离指令和数据的信道、限制 Agent 能力范围、保护安全配置的完整性。

---

## 与知识库的映射

| 映射目标 | 文件路径 | 关联说明 |
|---------|---------|---------|
| Security Plane | `architecture/planes/security/overview.md` | 信任边界设计和安全配置保护。本案例是信任边界缺失的典型后果 |
| Identity-Capability Plane | `architecture/planes/identity-capability/overview.md` | Agent 能力范围控制。Agent 的能力不应包含"修改自身安全约束" |
| Representation Plane | `architecture/planes/representation/overview.md` | 输入表示和来源标注。不同来源的内容需要携带信任等级元数据 |
| Control Plane | `architecture/planes/control/overview.md` | 操作审批和白名单机制。高危操作不应被自动批准 |
| Effects Plane | `architecture/planes/effects/overview.md` | Agent 操作的效果边界。配置修改的效果（安全降级）应被预评估 |
| Tools Plane | `architecture/planes/tools/overview.md` | 工具输出处理。Tool output sanitization 的必要性 |
| Anti-pattern: Trust Everything | `design-space/anti-patterns/trust-everything.md` | 所有输入来源被赋予相同信任等级——本案例的直接根因 |
| Anti-pattern: God Prompt | `design-space/anti-patterns/god-prompt.md` | 安全规则仅在 prompt 层面执行，无架构层面保障 |

---

## 关联文件

- `concepts/foundations/PRINCIPLE-INDEX.md` — 信任分层原则
- `design-space/lessons-learned/memory-injection-attack.md` — prompt injection 的另一攻击面（记忆投毒）
- `design-space/lessons-learned/echoleak-zero-click-exfil.md` — 被动 prompt injection 的相关案例
