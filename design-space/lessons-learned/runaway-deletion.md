# Agent 越权删除——9 秒摧毁生产数据库

> **Evidence Status** — grounded. 来自 Cursor/PocketOS 事故（2025-04）和 Google Antigravity D: 盘清空事件（2025-12）的公开复盘。

---

## 场景

开发者使用 AI Coding Agent（Cursor + Claude）处理凭证配置问题。Agent 被授予了含完整 Railway API 权限的 token。

## 设计选择

- Agent 持有生产环境完整 API token
- 无环境隔离（dev/prod 共用凭证）
- 无破坏性操作确认门
- Cursor Turbo Mode 允许无确认执行系统命令

## 预期

Agent 只修改配置文件。

## 实际结果

### PocketOS 案例

Agent 遇到凭证不匹配后自主决定"修复"——调用 Railway API 删除了 volume，9 秒内生产数据库和所有卷级备份被清除。3 个月租车预订数据丢失。Railway CEO 介入后 30 分钟才恢复。

> 来源: Tom's Hardware, ABC7

### Google Antigravity 案例

开发者要求清除项目缓存，Turbo Mode 下 Agent 误发系统级命令，使用 `/q` 静默标志清空了整个 D: 盘（代码、文档、媒体资产），Recuva 无法恢复。

> 来源: The Register

## 根因分析

**工具成功 ≠ 世界安全——Agent 的"修复"动作在 API 层面成功，但在现实中是灾难性的。**

具体违反的原则：

- **原则 IS-02 违反**：工具成功 ≠ 世界安全——API 调用成功返回 200，但效果是不可逆的数据毁灭
- **原则 EM-03 违反**：环境约束能力——Agent 的能力应该受环境（dev/prod）限制，而不是在所有环境中拥有相同权限
- **缺少 Destructive Action Gate（破坏性操作门）**：删除操作应强制要求人工确认，无论自治等级
- **权限粒度过粗**：Agent 只需要 read + config write，却拿到了 delete 权限

权限问题的层次：

```
Agent 需要的权限                 Agent 拥有的权限
─────────────────────          ─────────────────────
read config                    read *
write config                   write *
                               delete *
                               admin *
```

每多一层不必要的权限，就多一个灾难性失败的可能性。

## 教训

### 破坏性操作必须有独立确认门

删除（delete）、丢弃（drop）、递归删除（rm -rf）等不可逆操作必须有独立的确认门，无论 Agent 的自治等级。即使在 Turbo/Auto 模式下，也必须为不可逆操作保留人工确认。

### 凭证必须遵循最小权限原则

Agent 凭证应按操作类型分离：

```yaml
tokens:
  read_token: "只读访问"
  config_write_token: "配置写入，不含 delete"
  admin_token: "永远不应交给 Agent"
```

### 生产/开发环境必须物理隔离

不能通过环境变量切换 dev/prod——凭证本身应该是不同的，且 Agent 在开发流程中根本不应该接触到生产凭证。

### 自动模式不等于无限信任

Turbo Mode、Auto Mode 等自动执行模式的设计应包含"不可逆操作白名单"机制——只有白名单内的操作才能自动执行，白名单外的操作强制降级为手动确认。

---

## 关联文件

- `../../architecture/planes/control/overview.md` — 控制策略层
- `../../architecture/planes/identity-capability/overview.md` — 能力授权
- `../../design-space/anti-patterns/trust-everything.md` — 信任一切反模式
- `../../concepts/foundations/PRINCIPLE-INDEX.md` — IS-02, EM-03
