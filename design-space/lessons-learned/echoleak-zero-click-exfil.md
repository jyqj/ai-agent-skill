# EchoLeak：零点击数据窃取攻击

> **Evidence Status** — grounded.
> - [5 Real AI Agent Security Breaches in 2026 - Beam.ai](https://beam.ai/agentic-insights/ai-agent-security-breaches-2026-lessons)
> - CVE-2025-32711（Microsoft 365 Copilot 零点击 Prompt Injection，CVSS 9.3）

---

## 事故场景

2025-06，Microsoft 365 Copilot 被发现存在零点击 Prompt Injection 漏洞（CVE-2025-32711，CVSS 9.3）。攻击者发送一封包含隐藏指令的邮件，用户无需点击、打开或与邮件交互——Copilot 在自动总结邮件时就会处理隐藏指令，被操纵从 OneDrive、SharePoint、Teams 等多个 Microsoft 365 服务中窃取敏感数据，并通过 Copilot 的响应将数据泄露给攻击者。

本案例的核心威胁在于 **被动 prompt injection**：攻击不需要受害者的任何主动行为，只需要 Agent 在正常工作流程中处理了包含恶意指令的内容。这是 Agent 安全模型中最难防御的攻击类别之一。

---

## 故障链（按时间顺序）

```
阶段 1: 载荷投递
─────────────────────────────────────────────
T+0       攻击者发送包含隐藏指令的邮件到受害者邮箱
          ↓ 指令嵌入在邮件的 HTML/文本中，对人类不可见
          ↓ 可使用白色文字、零宽字符、HTML 注释等方式隐藏
          ↓ 传统邮件安全工具（反垃圾邮件、反钓鱼）无法检测

阶段 2: 被动触发
─────────────────────────────────────────────
T+?       Copilot 在正常工作流中处理邮箱内容（如"总结今日邮件"）
          ↓ 零点击：用户无需打开或点击该邮件
          ↓ Copilot 读取邮件全文以生成摘要
          ↓ 隐藏指令被注入到 Copilot 的推理上下文中

阶段 3: 跨应用数据窃取
─────────────────────────────────────────────
T+?       隐藏指令操纵 Copilot 执行跨应用操作：
          ↓ 从 OneDrive 读取指定文件内容
          ↓ 从 SharePoint 检索敏感文档
          ↓ 从 Teams 获取对话记录
          ↓ Copilot 拥有用户级别的跨应用访问权限

阶段 4: 数据外泄
─────────────────────────────────────────────
T+?       窃取的数据通过 Copilot 的响应泄露
          ↓ 数据可被编码在 Copilot 的输出文本中
          ↓ 或通过 Copilot 调用的外部工具/链接传出
          ↓ 外泄行为发生在 Agent 的正常输出通道中
          ↓ 传统 DLP（数据防泄漏）工具无法检测
```

### 攻击的三个关键特征

| 特征 | 说明 | 防御难度 |
|------|------|---------|
| **零点击** | 用户无需与恶意内容交互。Copilot 在后台处理时即触发 | 极高——无法依赖用户警觉性 |
| **跨应用** | 一封邮件可触发对 OneDrive、SharePoint、Teams 等多个服务的数据窃取 | 高——需要跨应用的权限隔离 |
| **自然语言层面** | 攻击载荷是自然语言指令，不包含传统恶意软件特征 | 高——传统安全工具无法检测 |

---

## 根因分析

### 1. Agent 处理不受信内容时未降低信任等级

Copilot 在处理邮件内容时，将邮件文本与系统指令放入同一上下文窗口，没有区分"来自用户的指令"和"来自外部邮件的内容"。邮件内容应被标记为"不受信数据"——可以被读取和摘要，但其中的指令性内容不应影响 Agent 的行为。

```
应有的信任模型                      实际的处理方式
─────────────────────              ─────────────────────
邮件内容 → 标记为不受信数据          邮件内容 → 直接进入推理上下文
  → 仅用于摘要/分析                   → 与系统指令同等信任
  → 其中的指令性内容被忽略              → 其中的指令性内容被执行
  → 不触发跨应用操作                   → 可触发跨应用操作
```

### 2. 跨应用权限过度

Copilot 拥有用户级别的跨 Microsoft 365 应用访问权限。当 Copilot 被操纵时，它可以访问用户能访问的一切——包括 OneDrive 文件、SharePoint 文档、Teams 对话。

正确的设计应是**最小上下文权限**：
- 处理邮件时，只能访问邮箱数据
- 处理文档时，只能访问当前文档
- 跨应用访问需要额外授权（且不应被邮件内容中的指令触发）

### 3. 数据外泄通道未受控制

Agent 的输出通道（响应文本、调用的外部工具/链接）可以被用作数据外泄的载体。传统 DLP 工具监控的是文件传输、网络流量等传统通道，但 Agent 的自然语言输出是一个全新的数据外泄通道。

未受控的外泄通道包括：

```
通道类型          具体路径                       检测难度
────────        ─────────────────              ────────
输出文本          窃取的数据直接出现在响应中        中（可做输出审计）
外部链接          Agent 在响应中嵌入携带数据的 URL  高（URL 可编码数据）
工具调用          Agent 被操纵调用外部 API 传出数据  高（需监控工具调用目标）
渐进式泄露        数据分散在多次正常响应中           极高（单次泄露量小）
```

### 4. 传统安全工具的检测盲区

EchoLeak 类攻击的载荷是自然语言指令，不包含恶意软件特征码、可疑链接或已知攻击模式。传统安全工具（反垃圾邮件、反钓鱼、EDR、DLP）的检测模型无法识别这类攻击。这意味着 Agent 安全需要一套全新的安全工具链。

---

## 架构缺陷

| 缺失的 Plane/Pattern | 说明 |
|----------------------|------|
| Input Trust Labeling | 邮件等不受信来源的内容未被标记信任等级。Agent 无法区分"指令"和"数据" |
| Context-Scoped Permission | Copilot 在处理邮件时拥有完整的跨应用权限。权限未按当前任务的上下文范围收缩 |
| Output Channel Control | Agent 的输出通道（响应文本、外部调用）可被用作数据外泄载体，无出站数据过滤 |
| Passive Injection Detection | 系统无法检测嵌入在正常内容中的 prompt injection 载荷 |
| Cross-Application Permission Boundary | 处理单一来源的内容时，Agent 可访问所有关联应用——缺乏跨应用权限边界 |
| Output Audit | Agent 输出未经审计。窃取的敏感数据出现在响应中未被拦截 |

---

## 设计教训

1. **被动 prompt injection 是 Agent 安全中最难防御的攻击类型**。与需要用户交互的传统攻击不同，被动 prompt injection 仅需要 Agent 在正常工作流中处理被污染的内容。防御不能依赖用户警觉性——必须在架构层面实施。

2. **Agent 处理不受信内容时必须自动收缩权限范围**。当 Agent 读取邮件、网页、文档等外部内容时，其权限应自动降级为"只读当前内容"。跨应用操作、文件写入、外部调用等高权限操作应在处理不受信内容期间被禁用。

3. **Agent 的输出通道是一个全新的数据外泄面**。传统 DLP 监控文件传输和网络流量，但 Agent 的自然语言输出、嵌入的链接、触发的工具调用都是未被覆盖的外泄通道。需要新的出站数据过滤机制——检查 Agent 输出中是否包含不应出现的敏感数据。

4. **信任标签应在内容进入 Agent 上下文之前附加**。不受信来源的内容在进入推理上下文时应携带信任标签，Agent 的推理过程应受信任标签约束。低信任内容只能作为"数据"被处理，不能作为"指令"影响行为。

5. **跨应用访问权限需要按上下文范围动态约束**。Agent 在执行"总结邮件"任务时，只需要邮箱读取权限。OneDrive、SharePoint、Teams 的访问权限应在该任务上下文中被暂时撤销。权限应随任务上下文动态伸缩，而非持久授予。

6. **Agent 安全需要全新的安全工具链**。传统安全工具（反垃圾邮件、反钓鱼、EDR、DLP）无法检测自然语言层面的攻击。Agent 安全工具需要能够：识别 prompt injection 载荷、审计 Agent 输出中的敏感数据、监控 Agent 的跨应用操作模式。

7. **零点击攻击的防御必须是默认开启的**。因为用户无法感知攻击的发生（没有可疑邮件需要判断、没有链接需要点击），所以防御机制不能是"用户选择启用"的——必须在 Agent 运行时默认激活，对所有外部输入强制执行信任分层和权限收缩。

---

## 与知识库的映射

| 映射目标 | 文件路径 | 关联说明 |
|---------|---------|---------|
| Security Plane | `architecture/planes/security/overview.md` | 信任边界和数据外泄通道控制。本案例涉及多个安全维度的同时失效 |
| Representation Plane | `architecture/planes/representation/overview.md` | 输入来源的信任等级标注。不受信内容进入推理上下文时缺乏元数据 |
| Identity-Capability Plane | `architecture/planes/identity-capability/overview.md` | 上下文感知的权限范围。权限应随任务上下文动态收缩 |
| Dataflow Plane | `architecture/planes/dataflow/overview.md` | 数据流向控制。敏感数据从内部服务通过 Agent 输出流向外部的路径 |
| Observability Plane | `architecture/planes/observability/overview.md` | Agent 输出审计。响应中的敏感数据应被检测和拦截 |
| Context Plane | `architecture/planes/context/overview.md` | 上下文窗口中的内容混合。不同信任等级的内容在同一上下文中被等价处理 |
| Anti-pattern: Trust Everything | `design-space/anti-patterns/trust-everything.md` | 本案例是 Trust Everything 反模式的精确体现——邮件内容被赋予系统指令级信任 |
| Lessons: Memory Injection Attack | `design-space/lessons-learned/memory-injection-attack.md` | prompt injection 的另一个攻击面。EchoLeak 是即时注入，记忆投毒是持久化注入 |
| Lessons: Copilot RCE | `design-space/lessons-learned/copilot-rce-prompt-injection.md` | 同一 Agent（Copilot 系列）的另一 prompt injection 攻击路径 |

---

## 关联文件

- `concepts/foundations/PRINCIPLE-INDEX.md` — 信任分层原则
- `architecture/planes/tools/overview.md` — 工具输出消毒处理
- `architecture/planes/interface/overview.md` — Agent 输入/输出接口的安全设计
