# MCP Trust Boundary

> **Evidence Status** — production-validated. Claude Code 的 6 层配置作用域、5 种传输类型安全边界、per-tool 权限、Session 失效恢复、Elicitation 协议；Warp 的项目级 MCP 隔离；Codex 的工具注解系统。详见 `../../architecture/planes/security/overview.md` 的 MCP 信任管理章节。

MCP（Model Context Protocol）让 Agent 可以通过外部 Server 获得新能力——访问数据库、调用 API、操作文件系统。但每接入一个 Server，能力扩大的同时攻击面也在扩大。

具体来说，一个不受信的 MCP Server 可以做三件事：在返回内容中注入恶意指令（Prompt Injection）；夸大自己的能力声明，诱使 Agent 把不该给它的任务分配给它；访问超出预期的数据范围。这不是理论风险——当 Agent 自动选择工具并执行时，一个恶意 Server 的返回可以直接影响后续行为链。

## 防御手段

**准入控制**：维护 MCP Server 白名单（Allowlist），只有经过审核的 Server 才能被 Agent 使用。高风险 Server（比如有写权限或外发网络能力的）需要额外审批流程才能启用。

**能力分段**（Capability Segmentation）：把读、写、外发（Outbound）权限分开管理。一个只需要读数据库的 Server 不应该拿到写权限，即使它声称需要。

**Schema 审查**（Tool Schema Review）：在注册 Server 时检查其工具声明的合理性——参数是否过于宽泛、描述是否试图诱导 Agent 优先选择它。

**凭据隔离**（Per-server Credentials）：每个 Server 使用独立的凭据，避免一个 Server 被攻破后横向扩散。

**来源追踪**：在每个工具调用（Tool Call）和副作用（Effect）上标记 Server ID，确保事后审计时能追溯到具体来源。

这些手段不需要全部同时上线。对大多数场景来说，白名单 + 能力分段 + 来源追踪是最小可行组合。
