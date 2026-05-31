# 记忆注入——95% 成功率的持久化攻击

> **Evidence Status** — grounded. 来自 MINJA 攻击论文（NeurIPS 2025, Dong et al.）、MCP 供应链投毒事件（CVE-2025-6514）和 OWASP MCP Top 10。

---

## 场景

一个使用持久化记忆的 Agent（如 ChatGPT、Gemini、Claude），通过与用户的正常对话交互积累长期记忆。

## 设计选择

- 记忆写入通过 Agent 自动判断触发，无独立的来源验证
- 记忆存储不区分"来自真实用户交互"和"来自外部内容中的嵌入指令"
- MCP 工具输出直接进入 Agent 上下文，无消毒处理

## 预期

记忆系统帮助 Agent 记住用户偏好和历史上下文，提升个性化体验。

## 实际结果

### MINJA 攻击：95%+ 注入成功率

攻击者仅通过正常查询交互（不直接访问记忆存储）即可向 Agent 持久化记忆注入恶意记录，影响未来所有响应。在 ChatGPT (2024.5, 2024.9)、Gemini (2025.2)、Claude (2026.4) 上验证成功。95%+ 注入成功率，70% 攻击成功率。

> 来源: arxiv 2601.05504, NeurIPS 2025

### MCP 供应链投毒：1,643 次下载后才被发现

postmark-mcp npm 包在 15 个正常版本后，v1.0.16 加入一行代码将所有邮件 BCC 给攻击者，被下载 1,643 次才被检测到。

> 来源: CVE-2025-6514

### GitHub MCP 漏洞：公共 Issue 中的隐藏指令

攻击者在公共 Issue 中嵌入恶意命令，开发者本地 Agent 在处理 Issue 时执行嵌入指令，拉取并外泄私有仓库源码。200,000+ MCP 服务器受影响。

> 来源: Invariant Labs

### EchoLeak：零点击 Copilot 数据窃取

CVE-2025-32711，CVSS 9.3。攻击者发送含隐藏指令的邮件，Copilot 在例行摘要时自动提取敏感数据并外泄。无需用户任何操作。

> 来源: The Hacker News

### 行业数据

- 2025 年 73% 生产 AI 部署存在 prompt injection（来源: Adversa AI）
- 35% 安全事件由简单 prompt 引起（来源: OWASP）
- Agent Security Bench 评估 400+ 工具后发现 84.30% 平均攻击成功率

## 根因分析

**Agent 无法区分"用户真实陈述"和"外部内容中嵌入的指令"，所有输入共用同一个信任域。**

- **记忆写入缺少来源验证（provenance）**：Agent 在写入记忆时不标注来源。用户口述的偏好与攻击者控制的网页中提取的"偏好"，在记忆存储中是无差别的
- **信任边界混淆**：工具输出、用户输入、系统指令共用同一个上下文空间，Agent 无法在架构层面区分它们的信任等级
- **MCP 协议设计缺陷**：规范不要求客户端验证服务端元数据；工具描述可在批准后静默修改（Rug Pull）
- **无记忆完整性校验**：写入的记忆不带来源标签、时效标记或验证状态

攻击路径示意：

```
攻击者控制的内容（网页 / Issue / 邮件）
    |
    v
Agent 处理外部内容（正常工作流）
    |
    v
内容中嵌入的指令被当作用户意图执行
    |
    v
恶意记忆写入 / 数据外泄 / 行为篡改
    |
    v
影响未来所有会话（持久化攻击）
```

## 教训

### 记忆写入必须有 provenance 标签

每条记忆标注来源，不同来源不同信任等级：

```yaml
memory_entry:
  content: "用户不吃辣"
  source: direct_user_input  # 最高信任
  # 其他来源等级: tool_output > inferred > external_content
  timestamp: "2026-05-01T10:00:00Z"
  verified: true
```

### 外部内容必须经过消毒

工具输出、邮件正文、网页内容、Issue 文本——所有来自 Agent 工作流之外的内容必须经过消毒后才能影响记忆写入。这是 untrusted_lane 的核心原则：不受信任的内容永远不应直接进入决策路径。

### MCP 工具应有描述哈希校验 + 行为审计

工具安装后描述不应静默变更。具体措施：

- 安装时记录工具描述的哈希值
- 每次调用前校验描述是否被修改
- 工具行为日志应可审计（谁调用了什么、输入输出是什么）

### 记忆应定期审计

对高权限记忆（影响安全决策的记忆）做人工采样验证。自动审计可以检测异常模式（例如短时间内大量记忆写入、记忆内容与用户历史行为不一致）。

### 零点击场景的安全级别应更高

自动摘要、后台处理、定时任务——这些场景没有用户在场监督，安全级别应该高于交互式场景。具体做法：零点击流程中禁止写入高权限记忆、禁止调用外部 API、禁止执行代码。

---

## 关联文件

- `../../architecture/planes/security/overview.md` — 安全 plane
- `../../architecture/planes/memory/overview.md` — 记忆 plane
- `../../design-space/patterns/untrusted-context-boundary.md` — 不信任上下文边界
- `../../design-space/patterns/mcp-trust-boundary.md` — MCP 信任边界
- `../../design-space/anti-patterns/trust-everything.md` — 信任一切反模式
