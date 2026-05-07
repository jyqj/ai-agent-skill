# Control x Identity x Security 边界设计

> Evidence Status: synthesized
> 知识库映射: Governance (Control) x Trust&Identity (Identity-Capability, Security)

## 为什么需要这篇文档

Control、Identity-Capability 和 Security 三个 Plane 都在回答"谁能做什么"，但从不同角度：

- **Identity-Capability**：WHO + WHAT — 谁在操作、凭什么授权、能力范围多大
- **Control**：WHETHER + WHEN — 这个动作在当前上下文中是否放行、需不需要审批
- **Security**：AGAINST WHAT — 攻击面在哪里、注入防护、sandbox 隔离

三者独立维护，但每个高风险动作都需要经过全部三层。本文档明确它们的介入时序、数据依赖和常见混淆。

---

## 职责边界

| 问题 | Identity-Capability | Control | Security |
|---|---|---|---|
| 发起者是谁？ | **定义**（subject, delegation_chain） | 读取 | 读取 |
| 有没有权限做这件事？ | **定义**（CapabilityGrant.scope） | **判定**（allow/deny/approval） | 读取 |
| 这个动作的风险多高？ | 记录（resource sensitivity） | **应用**（risk gate） | **评估**（攻击面、泄漏风险） |
| 工具输出是否可信？ | 标记（tool identity, trust_level） | 不参与 | **检查**（注入检测、输出消毒） |
| 审计归因谁？ | **记录**（audit_context） | **记录**（verdict、approval_ref） | **记录**（security_event） |
| 第三方声明的能力？ | **限制**（只约束该 server 自身） | 不自动扩展为本地权限 | **检查**（Confused Deputy 防护） |

## 介入时序

一个工具调用从 Decide 到执行的完整检查链：

```text
1. Decide 产生 ToolCall 意图
     ↓
2. Identity 解析 subject → 查 CapabilityGrant → 输出 AllowedCapabilitySet
     ↓
3. Control 检查 ToolCall ∈ AllowedCapabilitySet？
     ├─ 不在 → deny + 解释
     ├─ 在，低风险 → allow
     └─ 在，高风险 → approval_required → 等待 InteractionEvent
     ↓
4. Security 检查
     ├─ 工具输入参数是否含注入 payload
     ├─ 目标资源是否在 sandbox 内
     └─ 执行环境是否满足隔离要求
     ↓
5. 全部通过 → 执行 → 工具返回
     ↓
6. Security 对工具输出做消毒（untrusted data lane 标记）
     ↓
7. Control 对效果做验证（postcondition check）
     ↓
8. Identity 记录 audit_context
```

## 常见混淆

| 混淆 | 表现 | 修正 |
|---|---|---|
| 把权限检查散在工具代码里 | 工具 A 检查权限用一套逻辑，工具 B 用另一套 | 权限统一在 Control 层，工具只声明 risk_level |
| Identity 和 Control 合为一体 | "有权限"和"被放行"不区分 | 有权限（Identity）+ 当前上下文允许（Control）是两个判断 |
| Security 只管攻击不管输出 | 工具输出直接进入 trusted 上下文 | 工具输出默认 untrusted data lane，Security 做消毒 |
| 审批等同于授权 | 用户审批了一个动作 = 用户授予了该类所有动作的权限 | 审批是单次，授权（CapabilityGrant）有范围和期限 |
| 第三方能力声明被信任 | MCP server 声称能做 X → Agent 认为自己也能做 X | 第三方声明只约束该 server，本地能力来自用户/系统授权 |

## 何时可以简化

不是每个 Agent 都需要三层完整展开：

| 场景 | 可简化为 | 条件 |
|---|---|---|
| 单用户 + 只读 + 无外部工具 | Control 做基本 risk gate 即可 | 没有身份复杂度，没有攻击面 |
| 单用户 + 可逆写 + 可信工具 | Control + 最小 Identity（单一 subject） | 不需要委托链或多租户 |
| 多用户 / 多租户 / 第三方工具 | 三层完整 | 身份、权限、攻击面都需要独立处理 |

## 延伸阅读

- `../planes/control/overview.md` — Control 的完整设计
- `../planes/identity-capability/overview.md` — Identity & Capability 的完整设计
- `../planes/security/overview.md` — Security 的完整设计
- `./protocol-x-security.md` — 协议层的信任边界（Confused Deputy 的协议级表现）
- `./multi-model-trust-boundary.md` — 多模型间的信任边界
