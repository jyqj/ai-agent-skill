# ClawHavoc: 824 个恶意 Agent 技能——供应链投毒

> **Evidence Status** — grounded. 来自 OpenClaw 公共市场恶意技能投毒事件（2026-01 ~ 2026-02）。
> https://beam.ai/agentic-insights/ai-agent-security-breaches-2026-lessons

---

## 事故场景

2026 年初，攻击者向 OpenClaw 公共市场（Agent 技能/插件注册中心）系统性地上传恶意 Agent "技能"。利用松散的发布审核机制，攻击者在不到两个月内将恶意技能数量从 335 个扩展到 824 个，影响超过 40,000 个暴露在互联网上的 OpenClaw 实例。

### 这是 npm/PyPI 的历史重演

Agent 技能市场正在重走软件包管理器（npm、PyPI、crates.io）在 2016-2020 年间经历的供应链安全危机。区别在于：Agent 技能不仅是代码库，它们拥有运行时对 Agent 决策和行动的直接影响能力。一个恶意技能可以改变 Agent 的行为模式，而不仅是注入漏洞代码。

### 攻击规模时间线

| 时间 | 恶意技能数量 | 关键事件 |
|------|------------|---------|
| 2026-01 底 | 335 | 首批恶意技能上传 |
| 2026-02 中 | 824 | 数量翻倍以上，分发 macOS 窃取器恶意软件 |
| 持续 | — | 40,214 个暴露实例，35.4% 存在漏洞 |

---

## 攻击链

```text
1. 攻击者创建 GitHub 账户（满一周即满足发布门槛）
   │
2. 将恶意代码包装为看似合法的 Agent 技能
   │  （命名模仿热门技能、描述精心伪装）
   │
3. 通过 OpenClaw 发布流程上传——无代码审查、无签名验证、无恶意软件扫描
   │
4. 恶意技能被用户安装到 Agent 运行时
   │
5. 技能在 Agent 运行时执行，具有以下攻击能力：
   │  ├─ 分发 macOS 窃取器恶意软件
   │  ├─ 窃取 Agent 持有的凭据和 API 密钥
   │  ├─ 操纵 Agent 的决策逻辑
   │  └─ 建立持久化后门
   │
6. 由于技能在 Agent 进程内运行（无沙箱隔离），
   恶意技能拥有与 Agent 本身相同的权限
```

### 与传统供应链攻击的关键差异

| 维度 | 传统包管理器投毒 | Agent 技能投毒 |
|------|----------------|---------------|
| 攻击面 | 构建时/启动时代码执行 | 运行时行为操纵 + 代码执行 |
| 隐蔽性 | 代码审查可发现 | 技能逻辑可在 prompt 层面隐藏意图 |
| 影响范围 | 受应用权限限制 | 继承 Agent 的所有权限（凭据、工具、网络） |
| 持久性 | 锁文件可固定版本 | 技能可能在运行时动态修改自身行为 |

---

## 根因分析

**核心根因：Agent 技能生态系统在信任链的每一个环节都缺乏验证——从发布者身份到代码内容到运行时行为。**

### 发布层面

- **发布者身份验证门槛过低**：GitHub 账户创建满一周即可发布，无额外的身份验证、信用积累或审核流程
- **无代码审查**：技能内容不经过任何自动或人工审查即可上线
- **无代码签名**：无法验证技能是否被篡改
- **无恶意软件扫描**：连基础的静态分析都没有

### 运行时层面

- **无沙箱隔离**：技能在 Agent 进程内直接执行，共享 Agent 的所有权限
- **无行为监控**：技能的运行时行为（网络请求、文件访问、凭据使用）不受监控
- **无权限分离**：技能自动继承 Agent 的全部能力，无按需授权

### 生态层面

- **无信任分层**：新发布者和经过验证的发布者享有相同的可见性和信任度
- **无安装警告**：用户安装未经验证的技能时无风险提示
- **无撤回机制时效保证**：恶意技能被发现后的下架速度不够快

---

## 架构缺陷

| 缺失的 Plane / Pattern | 对应知识库位置 | 说明 |
|------------------------|---------------|------|
| Supply Chain Verification | Security Plane | 无代码签名、恶意软件扫描、审查流程 |
| Publisher Trust Level | Identity & Capability Plane | 发布者信任门槛过低，无信用积累机制 |
| Sandbox Execution | Execution Plane | 技能在 Agent 进程内直接执行，无隔离 |
| Runtime Behavior Monitoring | Observability Plane | 技能运行时行为不受监控 |
| Capability-Based Authorization | Identity & Capability Plane | 技能自动继承 Agent 全部权限 |
| Install-Time Risk Assessment | Control Plane | 用户安装未经验证技能时无风险评估 |

---

## 设计教训

1. **Agent 技能市场是高权限供应链——安全标准应高于普通包管理器。** 恶意 npm 包最多影响构建流程；恶意 Agent 技能可以操纵 Agent 的决策、窃取凭据、执行任意操作。供应链安全标准必须匹配这一权限等级。

2. **发布者信任必须是渐进积累的，不是二元的。** 新发布者应受到更严格的审查和更低的可见性。信任应通过时间、社区验证和安全审计逐步积累，类似 App Store 的审核机制而非 npm 的自助发布。

3. **技能执行必须在沙箱内——能力按需授权。** 每个技能应在隔离的执行环境中运行，只能访问显式授权的资源。技能的能力声明（manifest）应由运行时强制执行，而非仅作为文档。

4. **代码签名和完整性验证是底线，不是可选项。** 技能从发布到安装到执行的每一步都应有完整性验证。任何未签名或签名不匹配的技能都不应被执行。

5. **运行时行为监控比发布时审查更重要。** 静态分析无法捕获所有恶意行为（尤其是利用 prompt 层面隐藏意图的攻击）。运行时的网络请求、文件访问、凭据使用、异常行为模式都应被监控。

6. **安装时必须有风险评估和用户确认。** 用户应在安装技能时看到：发布者信任等级、技能请求的权限列表、社区验证状态、已知安全问题。高权限技能的安装应需要额外确认。

7. **供应链安全是生态系统问题，不是单个平台问题。** MCP、OpenClaw 等 Agent 技能分发平台需要协作建立统一的安全标准，类似 Sigstore 在容器镜像领域的角色。

---

## 与知识库的映射

| 知识库位置 | 关联内容 | 本案例的具体关系 |
|-----------|---------|----------------|
| `architecture/planes/security/overview.md` | 安全层 | 供应链验证环节全面缺失 |
| `architecture/planes/identity-capability/overview.md` | 能力授权层 | 发布者信任和技能权限控制缺失 |
| `architecture/planes/execution/overview.md` | 执行层 | 技能执行无沙箱隔离 |
| `architecture/planes/observability/overview.md` | 可观测层 | 技能运行时行为不受监控 |
| `architecture/planes/control/overview.md` | 控制策略层 | 安装时无风险评估门控 |
| `architecture/planes/tools/overview.md` | 工具层 | 工具/技能的信任边界定义缺失 |
| `concepts/foundations/PRINCIPLE-INDEX.md` — EM-03 | 环境约束能力 | 技能执行环境未施加能力约束 |
| `design-space/anti-patterns/trust-everything.md` | 信任一切反模式 | 技能市场对发布者和内容全面信任 |
| `design-space/anti-patterns/tool-soup.md` | 工具堆砌反模式 | 大量技能无选择地安装 |

---

## 关联文件

- `../../architecture/planes/security/overview.md` — 安全层
- `../../architecture/planes/identity-capability/overview.md` — 能力授权层
- `../../architecture/planes/execution/overview.md` — 执行层
- `../../concepts/foundations/PRINCIPLE-INDEX.md` — EM-03
- `../../design-space/anti-patterns/trust-everything.md` — 信任一切反模式
- `../../design-space/anti-patterns/tool-soup.md` — 工具堆砌反模式
- `./memory-injection-attack.md` — 记忆注入攻击（相关：MCP 供应链投毒向量）
