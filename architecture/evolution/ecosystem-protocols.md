# 多 Agent 生态中的协议演化

> **Evidence Status** — theoretical
> 来源：MCP (Model Context Protocol) 规范演化历史、A2A (Agent-to-Agent) 协议设计讨论、AGENTS.md 约定的社区采纳实践、微服务 API 版本管理经验的迁移应用。

## 1. 问题

当多个 Agent 通过协议协作时，协议本身也在演化。

```text
Agent-A (MCP v1.0) ←→ Agent-B (MCP v1.0)  ← 正常工作
Agent-A (MCP v1.1) ←→ Agent-B (MCP v1.0)  ← 兼容吗？
Agent-A (MCP v2.0) ←→ Agent-B (MCP v1.0)  ← 很可能不兼容
```

与单体系统不同，多 Agent 生态中的协议升级不能"停机统一升级"。不同 Agent 由不同团队/组织维护，升级节奏不同。

## 2. 协议版本管理

### 2.1 语义化版本 (Semantic Versioning)

```text
MAJOR.MINOR.PATCH
  2.1.3

MAJOR: 不兼容的 API 变更
MINOR: 向后兼容的功能新增
PATCH: 向后兼容的问题修正
```

### 2.2 向前兼容策略

新版本的 Agent 应能处理旧版本的消息：

```yaml
compatibility_rules:
  - rule: "忽略未知字段"
    description: "收到不认识的字段时跳过，不报错"
  - rule: "缺失字段用默认值"
    description: "旧版本消息缺少新字段时，用合理默认值"
  - rule: "新增字段为可选"
    description: "新版本新增的字段在初期不设为必填"
```

### 2.3 优雅降级

当对端使用旧版本协议时，Agent 应降级到双方都支持的版本：

```text
Agent-A (支持 v1.0, v1.1, v2.0)
Agent-B (支持 v1.0, v1.1)

握手:
  A → B: "我支持 v2.0, v1.1, v1.0"
  B → A: "我支持 v1.1, v1.0"
  协商结果: v1.1

A 在与 B 通信时降级到 v1.1 的能力子集
```

### 2.4 能力协商 (Capability Negotiation)

不只协商版本，还协商具体能力：

```yaml
capability_advertisement:
  agent_id: "agent-a"
  protocol_version: "2.0"
  capabilities:
    - tool_discovery: true
    - streaming: true
    - batch_requests: true
    - auth_methods: ["api_key", "oauth2"]
    - max_context_size: 128000
    - supported_modalities: ["text", "image"]
```

对端根据对方的能力清单调整交互方式。

## 3. 信任网络的演化

### 3.1 新 Agent 加入生态

```text
信任建立流程:
  1. 身份验证: 新 Agent 提供身份凭证
  2. 能力声明: 新 Agent 声明能力和权限需求
  3. 沙箱期: 新 Agent 在受限环境中运行
  4. 渐进授权: 根据表现逐步提升权限
  5. 正式加入: 达到信任阈值后获得完整权限
```

```yaml
trust_lifecycle:
  stages:
    - name: unknown
      permissions: none
      duration: "until identity verified"
    - name: probationary
      permissions: read_only
      duration: "7 days or 100 interactions"
      monitoring: enhanced
    - name: trusted
      permissions: read_write
      duration: "ongoing"
      monitoring: standard
    - name: privileged
      permissions: admin_subset
      duration: "ongoing"
      monitoring: standard
      requires: human_approval
```

### 3.2 旧 Agent 退出生态

Agent 退出时需要清理依赖关系：

```text
退出流程:
  1. 通知: 向依赖方发送 deprecation 通知
  2. 迁移期: 提供替代方案或迁移路径
  3. 降级: 逐步减少能力，只保留基本响应
  4. 关闭: 停止服务，返回标准错误消息
  5. 清理: 从服务发现中移除，撤销凭证
```

### 3.3 信任衰减

长期不互动的 Agent 之间的信任应逐渐衰减：

```yaml
trust_decay:
  rule: "每 30 天无交互，信任等级降一级"
  minimum: probationary  # 不降到 unknown，保留身份
  reactivation: "一次成功交互即可恢复到衰减前等级"
```

## 4. 协议演化的治理

### 4.1 变更提案流程

```text
协议变更流程:
  1. 提案: 描述变更内容、动机、影响范围
  2. 兼容性分析: 评估对现有 Agent 的影响
  3. 参考实现: 提供新旧版本共存的示例
  4. 迁移指南: 为每种 Agent 类型提供升级路径
  5. 过渡期: 定义旧版本的支持截止日期
  6. 废弃: 旧版本正式标记为 deprecated
```

### 4.2 协议分叉风险

```text
当生态中出现协议分叉:
  - 子集 A 用 Protocol-X v2.0
  - 子集 B 用 Protocol-X v2.0-fork

处理方式:
  - 维护转换网关 (gateway)
  - 推动合并或明确分离
  - 避免隐式的不兼容
```

## 5. 与 Orchestration Plane 的关系

Orchestration Plane 定义了多 Agent 间的编排模式（topology, communication）。协议演化影响编排的可行性：

```text
Orchestration Plane
├── 拓扑: 谁和谁通信
├── 通信模式: 同步/异步/pub-sub
└── 协议版本: 通信用什么版本的协议
    └── 协议演化: 协议版本不一致时如何处理
```

编排层需要感知协议版本差异，在路由消息时做版本适配。

## 6. 与 Identity & Capability Plane 的关系

Identity & Capability Plane 管理 Agent 的身份和能力声明。协议演化时：

- 新版本可能引入新的能力类型 → 需要更新 Capability Schema
- 旧版本的能力声明可能不再被理解 → 需要能力翻译层
- 身份验证方式可能变化 → 需要支持多种认证机制共存

```yaml
capability_evolution:
  v1_capabilities: ["search", "summarize"]
  v2_capabilities: ["search", "summarize", "stream", "batch"]
  mapping:
    v1_search: v2_search  # 直接映射
    v2_stream: null        # v1 没有对应能力
    v2_batch: null          # v1 没有对应能力
```

## 7. 实际协议案例

| 协议 | 版本管理方式 | 兼容性策略 |
|---|---|---|
| MCP | 语义化版本 + 能力协商 | 向前兼容，忽略未知字段 |
| A2A | 能力声明 + AgentCard | 能力协商，优雅降级 |
| AGENTS.md | 约定式，无版本号 | 最小公共子集 |
| OpenAPI | 语义化版本 | 端点级版本化 |
| gRPC | proto 文件版本 | 向前兼容，保留字段号 |

## 8. 反模式

| 反模式 | 风险 |
|---|---|
| 无版本管理 | 任何变更都可能破坏现有集成 |
| 强制同步升级 | 在去中心化生态中不可行 |
| 忽略向后兼容 | 旧 Agent 突然无法通信 |
| 信任不衰减 | 长期不活跃的 Agent 保留高权限 |
| 协议变更不通知 | 依赖方在运行时才发现不兼容 |

## 协议栈分层模型（2026 更新）

六层模型覆盖从工具接入到支付的完整 Agent 协作栈。各层正交互补，生产级系统通常需要组合使用。

| 层级 | 职责 | 主力协议 | 备选 | 状态 |
|------|------|---------|------|------|
| **L0 工具/上下文接入** | Agent 访问外部工具、数据源 | **MCP** (Anthropic) | — | 生产稳定；9700 万月 SDK 下载；10,000+ 活跃服务器 |
| **L1 Agent 间消息** | 轻量异步多模态消息传递 | **ACP** (IBM BeeAI) | — | Linux Foundation 孵化；适合快速原型和遗留集成 |
| **L2 Agent 间协调** | 发现、委托、任务管理 | **A2A** (Google) | ACP | v1.2 稳定；150+ 组织；AAIF 治理 |
| **L3 开放网络协作** | 跨组织/跨平台去中心化发现 | **ANP** (W3C 社区) | A2A | W3C 社区组推进；预计 2026-2027 形成正式标准 |
| **L4 Agent-用户交互** | 前端状态同步、人机协作 | **AG-UI** (CopilotKit) | Google A2UI | 9,000+ GitHub Stars；$27M Series A (2026.05) |
| **L5 Agent 支付/商务** | 自主交易授权与验证 | **AP2** (Google) | — | v0.2；已捐献 FIDO Alliance；60+ 合作组织 |

**互补关系**：MCP (工具) + A2A (协调) + AG-UI (用户交互) 构成"协议三角"，AP2 叠加支付层，ANP 扩展开放网络层，ACP 提供轻量消息备选。

## 治理统一体 — AAIF、W3C、FIDO

| 治理组织 | 范围 | 成员规模 | 托管协议 |
|---------|------|---------|---------|
| **Linux Foundation AAIF** | Agent 基础设施标准 | 150+ 组织 (2026.04)；OpenAI, Anthropic, Google, Microsoft, AWS, Block 六方发起 | MCP, A2A, AGENTS.md, Goose |
| **W3C AI Agent Protocol CG** | 开放网络 Agent 标准 | 社区组推进 | ANP；预计 2026-2027 正式 Web 标准 |
| **FIDO Alliance** | Agent 支付与可验证意图 | 全球身份认证联盟 | AP2, Verifiable Intent (与 Mastercard 联合开发) |

**趋势**：协议治理正从单一公司主导走向行业基金会共治。MCP 和 A2A 捐献 AAIF 标志着 Agent 标准从实验走向工业级。

## A2A v1.2 核心设计 — Agent Card、Task 状态机、三种传输绑定

### Agent Card

JSON 元数据文档，发布于 `/.well-known/agent.json` (RFC 8615)：

| 字段 | 内容 |
|------|------|
| 身份元数据 | Provider name, description, version |
| 安全方案 | API keys, OAuth2, mTLS, OpenID Connect |
| 能力标志 | 流式支持、推送通知、扩展卡可用性 |
| 技能声明 | 输入/输出规格 |
| 扩展 | 核心规范外的附加功能 |
| 签名 | 密码学验证卡片真实性 |

### Task 状态机

Task 是有状态工作单元，服务端生成唯一 ID，单任务上下文支持多轮消息。

```text
            ┌─────────────────────────────┐
            │         working             │
            └──────┬───┬───┬──┬──┬───┬────┘
                   │   │   │  │  │   │
     completed ◄───┘   │   │  │  │   └──► auth-required
     failed    ◄───────┘   │  │  └──────► input-required
     canceled  ◄───────────┘  │
     rejected  ◄──────────────┘
```

终态触发清理策略；中断状态 (`input-required`, `auth-required`) 支持人机协作。

### 三种传输绑定（语义等价）

| 绑定 | 机制 | 流式 | 适用场景 |
|------|------|------|---------|
| **JSON-RPC 2.0** | HTTP/WebSocket 上的方法调用 | SSE | 通用 Web 集成 |
| **gRPC** | Protocol Buffers, 二进制帧 | 原生双向流 | 高吞吐低延迟的内部服务 |
| **HTTP+REST** | RESTful 端点, JSON 载荷 | SSE | 遗留系统集成、简单客户端 |

### 信任模型

- **不透明执行原则**：Agent 基于声明能力协作，无需共享内部思考或工具实现
- **无共享状态**：信息仅通过显式消息/产物交换流动
- **声明式安全**：Agent 指定所需认证方案，客户端必须遵从
- **版本协商**：`A2A-Version` 头协商；不匹配返回 `VersionNotSupportedError`

## ACP 轻量消息协议 — IBM BeeAI、RESTful 异步

**定位**：L1 层轻量 Agent 消息传递，无 SDK 依赖，标准 HTTP 动词即可集成。

| 维度 | 设计 |
|------|------|
| 架构 | Brokered Client-Server；ACP Server 作为协议代理管理发现和任务路由 |
| 传输 | 标准 HTTP (GET, POST, PUT, DELETE) |
| 消息格式 | 结构化多部分消息，MIME 类型部分，有序内容交付 |
| 多模态 | 文本、图像、音频、视频、二进制 |
| 异步 | 为长时运行任务设计，异步优先 |
| 发现 | 基于注册表的 Agent Detail 模式 |
| 安全 | 能力范围限定 + 短期令牌 + 双向 TLS + 身份撤销 |

**优势**：快速原型、无框架锁定、遗留系统集成友好。

**局限**：需要注册表基础设施；假设强服务端控制；流中断风险。

**与 A2A 的关系**：ACP 聚焦轻量消息传递（L1），A2A 聚焦发现和任务协调（L2）。简单场景 ACP 足够；复杂多 Agent 编排需要 A2A 的 Agent Card 发现和 Task 状态机。

## ANP 去中心化协议 — W3C DID + JSON-LD

**定位**：L3 层开放网络协作，目标是成为"Agent 时代的 HTTP"。

| 维度 | 设计 |
|------|------|
| 身份 | W3C 去中心化标识符 (DID)，HTTPS 托管 DID 文档 |
| 消息格式 | JSON-LD + Schema.org 词汇表 |
| 发现 | 搜索引擎发现 + Agent Description Protocol 文档 |
| 安全 | 端到端加密 + 密码学凭证验证 |

**局限**：高协商开销、生态采纳仍在早期、元数据过时挑战、DID 解析延迟。

**与 A2A 的关系**：A2A 适合组织内和可信伙伴间的协调；ANP 解决跨组织、跨平台的开放网络发现问题。二者分别覆盖 L2 和 L3 层。

## AG-UI Agent-用户交互协议 — CopilotKit、事件驱动双向同步

**定位**：L4 层 Agent-用户-应用间的双向同步，填补 Agent 与前端之间的协议空白。

### 核心能力

| 能力 | 说明 |
|------|------|
| 共享状态 | Agent 与应用间双向状态同步 |
| 基于工具的 GenUI | 工具规范驱动的生成式 UI |
| 子图 | 嵌套 Agent 工作流支持 |
| Human-in-the-Loop | 用户干预机制 |
| Agent GenUI | AI 生成的界面组件 |
| 预测性更新 | 预期性状态变更 |

### 生态集成

- **一方客户端**：React, Angular
- **社区实现**：Golang, Rust, Java
- **框架集成**：Google ADK, Microsoft Agent Framework, AWS Strands, LangGraph, Mastra, PydanticAI, Agno
- **企业采纳**：Google, Microsoft, Amazon, Oracle

### 与 A2UI 的关系

Google 发布了 A2UI (Agent-to-User Interface) 规范，AG-UI 与其兼容并互补。CopilotKit 提供了 A2UI + AG-UI 的集成方案。

**关键数据**：9,000+ GitHub Stars；120,000 周安装量；200 万+ 周 Agent-User 交互；$27M Series A (2026.05, Glilot Capital 领投)。

## AP2 Agent 支付协议 — Verifiable Credentials、三层 Mandate

**定位**：L5 层 Agent 自主支付，解决传统支付系统假设"人类点击购买按钮"的根本矛盾。

### 三大核心问题

1. **授权**：证明用户授予 Agent 特定购买权限
2. **真实性**：确保 Agent 请求准确反映用户真实意图
3. **问责**：确定欺诈/错误交易的责任归属

### Mandate 三层体系

基于 Verifiable Credentials (VCs) 的防篡改、密码学签名数字合约：

| Mandate 类型 | 场景 | 流程 |
|-------------|------|------|
| **Intent Mandate** | 委托式未来交易 | 用户预签详细指令（价格上限、时间、条件）→ Agent 条件满足时自动生成 Cart Mandate |
| **Cart Mandate** | 即时购买 | 用户批准商户签名购物车 → 不可变密码学签名记录（精确物品、价格、配送信息） |
| **Payment Mandate** | 金融网络信号 | 向金融网络标识 AI 参与，支持风险管理可见性 |

### 授权链

```text
商户密码学签名 → 用户设备签名 → 双重签名 (Cart + Payment Mandate) → 执行
```

创建不可否认的密码学审计追踪。

### Human-Not-Present 支付

v0.2 引入：Agent 基于预授权用户指令 (Intent Mandate) 自主执行支付，无需即时用户交互。条件匹配时自动触发。

**关键数据**：v0.2 版本；60+ 合作组织 (Coinbase, Mastercard, PayPal, Adyen)；已捐献 FIDO Alliance。Verifiable Intent 标准与 Mastercard 联合开发。

## MCP 2026 路线图 — 无状态操作、session 迁移

### 当前状态

- 10,000+ 活跃 MCP 服务器；9700 万月 SDK 下载
- 已集成到 OpenAI、Google DeepMind、Microsoft、AWS 的主流工具链
- 核心原语：Resources, Tools, Prompts, Sampling
- 消息格式：JSON-RPC 2.0；连接模型：双向客户端-服务端

### 安全模型演进

| 机制 | 说明 |
|------|------|
| 签名清单 | signed manifests 验证服务器完整性 |
| OAuth 2.1 | 标准化令牌管理 |
| Syscall 过滤 | 沙箱保护 |
| 能力型令牌 | capability-based tokens 附带特定权限 |

### 路线图重点

| 方向 | 说明 | 解决的问题 |
|------|------|-----------|
| **无状态操作** | MCP Server 支持无状态请求模式，降低服务端内存占用 | 水平扩展和 serverless 部署 |
| **Session 迁移** | 会话状态可在 MCP Server 实例间迁移 | 高可用和滚动升级 |
| **Streamable HTTP** | 替代旧 SSE 传输，统一流式和非流式场景 | 简化传输层实现 |
| **协议桥** | MCP ↔ A2A 互操作桥 | Agent 通过 MCP 工具触发 A2A 任务 |

### 已知局限

- 集中式服务器假设（去中心化场景需 ANP 补充）
- 易受提示注入攻击
- 对复杂多 Agent 协调支持有限（需 A2A 补充）

## 协议选择决策树

```text
你的 Agent 需要做什么？
│
├─ 访问外部工具/数据源
│  └─► MCP（L0）— 标准化工具接入，消除 N×M 集成
│
├─ 与其他 Agent 协作
│  ├─ 组织内 / 可信伙伴
│  │  ├─ 需要发现 + 任务管理？ → A2A（L2）
│  │  └─ 只需轻量消息传递？ → ACP（L1）
│  └─ 跨组织 / 开放网络
│     └─► ANP（L3）— W3C DID + 去中心化发现
│
├─ 与用户/前端交互
│  └─► AG-UI（L4）— 双向状态同步 + GenUI
│
├─ 需要自主支付
│  └─► AP2（L5）— Verifiable Credentials + Mandate
│
└─ 生产级完整栈
   └─► MCP + A2A + AG-UI（协议三角）+ 按需叠加 AP2/ANP/ACP
```

**选型原则**：
1. **从 MCP 开始**：几乎所有 Agent 都需要工具接入
2. **按需叠加**：单 Agent 只需 MCP；多 Agent 协调加 A2A；面向用户加 AG-UI
3. **不要过度设计**：简单场景不需要完整六层栈
4. **治理先行**：选定协议后，在 AAIF/W3C/FIDO 框架下评估安全和合规要求

## 延伸阅读

- `co-evolution.md` -- 单 Agent 内的版本协同
- `retirement.md` -- Agent 退出生态的完整流程
- `../planes/orchestration/overview.md` -- 多 Agent 编排
- `../planes/orchestration/communication.md` -- 通信模式
- `../planes/identity-capability/overview.md` -- 身份与能力管理
