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

## 延伸阅读

- `co-evolution.md` -- 单 Agent 内的版本协同
- `retirement.md` -- Agent 退出生态的完整流程
- `../planes/orchestration/overview.md` -- 多 Agent 编排
- `../planes/orchestration/communication.md` -- 通信模式
- `../planes/identity-capability/overview.md` -- 身份与能力管理
