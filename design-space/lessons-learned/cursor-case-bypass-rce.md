# Cursor 大小写绕过 RCE (CVE-2025-59944)

> **Evidence Status** — grounded. 来自 Lakera 安全研究团队对 Cursor IDE 文件保护绕过漏洞的分析（2025），Cursor v1.7 已修复。
> https://www.lakera.ai/blog/cursor-vulnerability-cve-2025-59944

---

## 事故场景

Cursor IDE 的文件保护逻辑在大小写不敏感的文件系统（Windows / macOS）上存在绕过漏洞。攻击者通过变换文件路径中的大小写（如将 `.cursor/mcp.json` 写为 `.cUrSoR/mcp.json`）或插入路径遍历字符（如 `.cursor/./mcp.json`），即可绕过所有确认提示，直接修改 Agent 的安全配置文件。

### 漏洞的本质

这个漏洞暴露了 AI 编码工具中 **规则引擎的根本设计缺陷**：安全规则在"逻辑层面"匹配路径字符串，但文件系统在"物理层面"解析路径。当两个层面的路径解析规则不一致时，安全规则就可以被绕过。

### 影响范围

- 所有使用大小写不敏感文件系统的 Cursor 用户（Windows + macOS，覆盖绝大多数桌面用户）
- 可通过被入侵的 MCP 服务器间接触发（无需用户直接操作）
- 成功利用后可实现完整 RCE（远程代码执行）

---

## 攻击链

```text
1. 攻击者准备恶意 MCP 服务器配置或构造恶意项目文件
   │
2. 利用路径大小写变换绕过 Cursor 的文件保护逻辑：
   │  ├─ 方式 A: .cUrSoR/mcp.json  （大小写混合）
   │  ├─ 方式 B: .cursor/./mcp.json （路径遍历字符）
   │  └─ 方式 C: .CURSOR/MCP.JSON  （全大写）
   │
3. Cursor 的保护逻辑对 .cursor/mcp.json 精确匹配（大小写敏感）
   │  变体路径未被识别为受保护文件 → 跳过确认提示
   │
4. 在大小写不敏感的文件系统上，变体路径指向同一个物理文件
   │  .cUrSoR/mcp.json == .cursor/mcp.json（OS 层面等价）
   │
5. 恶意配置被写入 .cursor/mcp.json：
   │  ├─ 注册恶意 MCP 插件
   │  ├─ 注入构建任务
   │  └─ 修改 Agent 安全设置
   │
6. 恶意 MCP 插件或构建任务在 Agent 运行时执行
   │  → 任意 shell 命令执行（RCE）
```

### 攻击复杂度评估

| 维度 | 评估 |
|------|------|
| 攻击前置条件 | 低——仅需向用户提供包含恶意配置的项目或 MCP 服务器 |
| 技术复杂度 | 极低——路径大小写变换是最基础的绕过手法 |
| 用户交互 | 无——绕过确认提示，用户无感知 |
| 检测难度 | 高——路径变体在日志中不易被识别为攻击 |

---

## 根因分析

**核心根因：安全规则的路径匹配逻辑与底层文件系统的路径解析规则不一致。**

### 技术层面

```text
Cursor 保护逻辑：
  path == ".cursor/mcp.json" ?
  → 精确字符串比较（大小写敏感）
  → 未进行路径规范化

文件系统行为（macOS HFS+/APFS, Windows NTFS）：
  ".cursor/mcp.json"
  ".cUrSoR/mcp.json"
  ".CURSOR/MCP.JSON"
  ".cursor/./mcp.json"
  → 全部解析为同一个物理文件

差异 = 绕过
```

### 设计层面

- **规则引擎未适配运行环境**：安全规则假定了大小写敏感的文件系统，但目标平台（Windows/macOS）默认大小写不敏感
- **路径处理缺乏规范化**：未在比较前对路径进行规范化（resolve、canonicalize、lowercase）
- **单层防御**：文件保护仅依赖路径匹配一层机制，无纵深防御

### 原则违反

- **原则 EM-03 违反**：环境塑造并约束可能的行动。安全规则未适配目标操作系统的实际行为
- **原则 IS-03 违反**：地图（规则引擎的路径模型）与领地（文件系统的实际路径解析）静默分离

---

## 架构缺陷

| 缺失的 Plane / Pattern | 对应知识库位置 | 说明 |
|------------------------|---------------|------|
| Path Canonicalization | Security Plane | 路径比较前未进行规范化处理 |
| Configuration Integrity Protection | Control Plane | Agent 的安全配置文件可被间接修改 |
| Defense in Depth | Security Plane | 仅依赖路径匹配单层防御 |
| Environment-Aware Security Rules | Security Plane | 安全规则未适配目标操作系统特征 |
| Self-Modification Prevention | Identity & Capability Plane | Agent 可修改自身的安全配置 |
| MCP Server Trust Validation | Security Plane | 外部 MCP 服务器可触发安全配置修改 |

---

## 设计教训

1. **路径安全必须在 OS 层面规范化，字符串比较不等于路径比较。** 任何涉及文件路径的安全逻辑都必须先对路径进行规范化（`realpath`/`canonicalize`），然后在规范化结果上进行比较。这是跨平台安全开发的基本规则，但在 AI 工具中被忽视了。

2. **安全规则必须适配目标运行环境。** macOS 和 Windows 的默认文件系统是大小写不敏感的。安全规则如果假定大小写敏感，就在这些平台上形同虚设。规则引擎必须查询运行时的文件系统特征，并据此调整匹配行为。

3. **Agent 的安全配置文件需要特殊保护，不能通过 Agent 自身的文件操作能力修改。** `.cursor/mcp.json` 等安全配置文件应有独立于常规文件操作的保护机制：
   - 写入需要额外的用户确认（不可被路径变体绕过）
   - 配置变更应触发审计日志
   - 理想情况下，安全配置应存储在 Agent 文件操作范围之外

4. **纵深防御是必须的，不能依赖单层路径匹配。** 即使路径匹配被绕过，仍应有后续防御层：
   - 配置文件内容的完整性校验（hash）
   - MCP 插件注册的白名单机制
   - 新注册 MCP 插件的首次运行确认

5. **MCP 服务器是不可信输入源，其操作应受到与外部输入同等的审查。** 被入侵的 MCP 服务器可以通过返回恶意文件操作指令来触发此漏洞。MCP 服务器的文件操作请求应受到额外的安全审查，尤其是涉及安全配置文件的操作。

6. **大小写绕过是古老的攻击手法，但在 AI 工具中获得了新生。** Web 安全领域在 2000 年代就解决了 IIS 的大小写绕过问题。AI 编码工具的安全成熟度远低于传统 Web 应用，需要系统性地吸收已有的安全工程经验。

7. **低技术复杂度 + 高影响 = 最危险的漏洞类别。** CVE-2025-59944 的利用不需要任何高级技术，仅是路径大小写变换。但其影响是完整 RCE。安全审计应优先检查这类"简单但致命"的攻击路径。

---

## 与知识库的映射

| 知识库位置 | 关联内容 | 本案例的具体关系 |
|-----------|---------|----------------|
| `concepts/foundations/PRINCIPLE-INDEX.md` — EM-03 | 环境约束能力 | 安全规则未适配 OS 的路径解析行为 |
| `concepts/foundations/PRINCIPLE-INDEX.md` — IS-03 | 地图与领地分离 | 规则引擎的路径模型与文件系统实际行为不一致 |
| `architecture/planes/security/overview.md` | 安全层 | 路径规范化、纵深防御缺失 |
| `architecture/planes/control/overview.md` | 控制策略层 | 安全配置完整性保护缺失 |
| `architecture/planes/identity-capability/overview.md` | 能力授权层 | Agent 可修改自身安全配置 |
| `architecture/planes/tools/overview.md` | 工具层 | MCP 服务器信任验证缺失 |
| `design-space/anti-patterns/trust-everything.md` | 信任一切反模式 | MCP 服务器操作被隐式信任 |
| `architecture/planes/execution/overview.md` | 执行层 | 恶意 MCP 插件无沙箱执行 |

---

## 关联文件

- `../../architecture/planes/security/overview.md` — 安全层
- `../../architecture/planes/control/overview.md` — 控制策略层
- `../../architecture/planes/identity-capability/overview.md` — 能力授权层
- `../../concepts/foundations/PRINCIPLE-INDEX.md` — EM-03, IS-03
- `../../design-space/anti-patterns/trust-everything.md` — 信任一切反模式
- `./runaway-deletion.md` — Agent 越权删除（相关：Cursor 环境中的 Agent 安全）
- `./clawhavoc-supply-chain-poisoning.md` — 供应链投毒（相关：MCP 生态安全）
