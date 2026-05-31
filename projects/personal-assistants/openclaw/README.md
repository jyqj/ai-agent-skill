# OpenClaw

## 证据卡

**证明了什么**：大规模个人助手需要 manifest-first plugin 生态、thin versioned gateway protocol、DM-first 安全模型和 session-scoped 全局隔离，才能在 125 个扩展、20+ 渠道、5 个原生平台之间维持一致性和安全性。

**核心运行时对象**：

| 对象 | 实现 | 对应 Plane |
|------|------|-----------|
| Gateway Protocol | 100+ RPC methods, AJV schema 校验, additive-only 版本演进 | sensing-representation |
| Plugin Registry | manifest-first, 125 extensions, capability provider 声明 | tools |
| Channel Dispatcher | 20+ channel adapters, DM-first, allowlist policy | sensing-representation |
| ACP | session-scoped approval, persistent bindings, policy enforcement | security |
| Context Engine | token budget per turn, smart trimming, streaming-aware | context |
| Session Store | flat file YAML/JSONL, session-scoped overrides | state |
| Auth Profiles | OAuth + API-key, round-robin fallback, refresh cooldown | identity-capability |

**可复用规则**：
1. Manifest-first plugin discovery 避免 import-time side effects，启动时即可校验全量 capability
2. Thin gateway protocol + additive-only evolution 保证向后兼容，新旧客户端共存
3. DM-first security 保护个人 assistant 免受未授权访问，公开渠道默认拒绝
4. Prepared runtime facts 在启动时预计算，避免 hot path 重复发现 plugin 元数据
5. Memory plugin slot（单一激活）允许运行时切换记忆后端而不影响其他 plugin
6. Plugin SDK boundaries（api.ts facade + narrow subpaths）防止 extension 访问 core internals

**不该照搬的**：
- 1.78M LOC + 125 extensions 的复杂度对小型 agent 是过度设计
- 20+ 渠道适配的维护成本极高，多数场景只需 2-3 个渠道
- Gateway 作为控制平面增加了部署和调试复杂度，单机场景可直接嵌入

**关键数值**：1.78M LOC, 125 extensions, 55 skills, 20+ channels, 5 native platforms, 100+ RPC methods, 40+ model providers

---

> **Evidence Status** — grounded. 基于源码结构与运行时行为分析。

## 基本信息

- **类型**：personal-assistant + gateway-control-plane
- **项目定位**：统一个人助手，通过 Gateway 适配多个渠道和工具，manifest-first plugin 生态驱动扩展。
- **规模**：~1.78M LOC TypeScript, 125 extensions, 55 skills
- **学习来源**：仓库分析与源码观察。
- **推荐入口**：README → 架构概述 → plugin 系统 → channel 适配。

## 架构概述

```
Agent = Gateway Protocol + Plugin Registry + Channel Dispatcher + ACP

核心循环：Gateway 接收请求 → Channel Dispatcher 路由 → Plugin Registry 发现能力 → ACP 鉴权 → 执行 → 响应
Plugin 系统：manifest-first 声明（openclaw.plugin.json）+ capability provider + SDK facade
渠道层：20+ channel adapters + DM-first security + allowlist policy
执行环境：Docker/SSH/OpenShell/Local 四种沙箱后端
技能系统：bundled(55)/managed/workspace 三层 ClawHub Skill Registry
多平台：macOS(SwiftUI)/iOS(Swift)/Android(Kotlin)/WebChat/Canvas A2UI
记忆系统：单一激活 memory plugin (lancedb), per-agent configurable
认证系统：OAuth + API-key, round-robin fallback, session-scoped override
上下文管理：token budget per turn, smart trimming, streaming-aware
```

## 核心架构模式

| 模式 | 实现 | 设计意图 |
|-----|------|---------|
| Manifest-First Plugin | openclaw.plugin.json 声明 capability | 消除 import-time side effects，启动时全量校验 |
| Thin Gateway Protocol | 100+ RPC, data-first/acyclic, additive-only | 保证向后兼容，新旧客户端共存 |
| Channel Adapter + DM-First | 20+ 渠道统一抽象, DM pairing security | 公开渠道默认拒绝，保护个人数据 |
| ACP (Agent Control Plane) | session-scoped approval, persistent bindings | 本地执行权限精细控制 |
| Plugin SDK Boundaries | api.ts/runtime-api.ts facade, narrow subpaths | 防止 extension 访问 core internals |
| Prepared Runtime Facts | 启动时预计算 plugin 元数据 | 避免 hot path 重复发现 |
| Memory Plugin Slot | 单一激活 memory plugin (lancedb) | 运行时可切换记忆后端 |
| Session-Scoped Auth | per-session provider/model, OAuth refresh + cooldown | 会话级别认证隔离 |
| ClawHub Skill Registry | bundled(55)/managed/workspace 三层 | 技能分级管理与分发 |
| Multi-Platform | 5 原生平台 + Canvas A2UI | 统一体验跨设备 |
| Sandbox Backends | Docker/SSH/OpenShell/Local | 按需选择隔离级别 |
| Context Engine | token budget per turn, smart trimming | streaming-aware 上下文管理 |
| Hook Plugin Registration | agent turn/message inbound/reply dispatch/tool execution/session/heartbeat | 生命周期事件驱动扩展 |

## 关键设计决策

| 决策 | 选择 | 原因 |
|-----|------|------|
| Plugin 发现 | manifest-first | 避免 import-time 副作用，支持静态分析 |
| 协议演进 | additive-only | 不破坏现有客户端，渐进式增强 |
| 安全默认 | DM-first | 个人助手场景下公开渠道风险高 |
| 记忆后端 | 单一 slot + lancedb | 简化竞争条件，允许运行时切换 |
| 认证 | session-scoped override | 不同会话可用不同 provider/model |
| 沙箱 | 四种后端 | 本地开发用 Local，生产用 Docker/SSH |
| 技能分层 | bundled/managed/workspace | 平衡开箱即用与用户自定义 |

## 模块覆盖

| 模块 | 覆盖程度 | 可复用模式 |
|------|---------|-----------|
| tools | 深 | manifest-first plugin + capability provider + factory |
| sensing-representation | 深 | channel adapter + gateway protocol + DM-first |
| security | 深 | ACP + DM pairing + sandbox backends |
| context | 中 | context engine + prepared runtime facts |
| memory | 中 | memory plugin slot + lancedb |
| identity-capability | 中 | auth profiles + session-scoped override + round-robin |
| orchestration | 中 | multi-agent routing + session isolation |
| state | 中 | session store + transcript events |

## 独特贡献

OpenClaw 是统一个人助手，通过 Gateway 适配多个渠道和工具。核心创新的四项设计详见上方证据卡"可复用规则"一节（manifest-first plugin、thin gateway protocol、DM-first security、session-scoped everything）。这套组合使得一个 1.78M LOC 的系统能在 5 个原生平台、20+ 渠道上保持一致的行为和安全边界。

## 可复用洞察

1. **Prepared Runtime Facts** - 启动时预计算 plugin 元数据，避免 hot path 反复发现
2. **Memory Plugin Slot** - 单一激活约束简化竞争条件，运行时可切换后端（lancedb）
3. **Plugin SDK Facade** - api.ts/runtime-api.ts 双层 facade + narrow subpaths，防止 extension 越权
4. **Hook Plugin Lifecycle** - agent turn/message inbound/reply dispatch/tool execution/session/heartbeat 六种钩子，事件驱动扩展
5. **ClawHub 三层技能** - bundled(55)/managed/workspace 分级管理与分发
6. **Multi-Platform Consistency** - 5 原生平台 + Canvas A2UI，统一体验跨设备
