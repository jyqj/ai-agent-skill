# Execution Layer 架构分析


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> 来源：Claude Code 源码逆向分析
> 路径：`src/tools/`, `src/services/mcp/`, `src/Tool.ts`, `src/tools.ts`

## 1. 工具系统架构

### Tool 接口核心设计

**核心方法签名**：
- `call(args, context, canUseTool, parentMessage, onProgress)`: 异步执行
- `description(input, options)`: 动态描述，支持上下文感知
- `checkPermissions(input, context)`: 权限决策（"allow"/"deny"/"ask"）
- `validateInput(input, context)`: 输入验证（业务逻辑约束）

**关键特性**：
- **隔离的权限模型**：`checkPermissions` 和 `validateInput` 分离
- **进度报告**：`ToolCallProgress<P>` 支持流式进度推送
- **结果大小管理**：`maxResultSizeChars` 限制，超限持久化到磁盘
- **并发安全申明**：`isConcurrencySafe()` 驱动调度决策

### 工具注册与发现

**分层加载策略**：
```
1. getAllBaseTools() → 60+ 内置工具 (feature-gated)
   - 条件导入：Ant-only (ConfigTool, REPLTool)
   - 环境检测：hasEmbeddedSearchTools()

2. getTools(permissionContext) → 权限过滤后的工具列表
   - 拒规则过滤：filterToolsByDenyRules()
   - 模式过滤：REPL 启用时隐藏原始 Bash/Read/Edit

3. assembleToolPool(permissionContext, mcpTools) → 合并内置 + MCP
   - 去重策略：uniqBy(name) 保持插入序
```

### buildTool 工厂默认值

```typescript
const TOOL_DEFAULTS = {
  isEnabled: () => true,
  isConcurrencySafe: () => false,          // 保守
  isReadOnly: () => false,                 // 保守
  checkPermissions: async () => ({ behavior: 'allow', updatedInput: input }),
  toAutoClassifierInput: () => '',         // 安全工具必须覆盖
}
```

---

## 2. 核心工具实现分析

### BashTool

**沙箱与超时**：
- `shouldUseSandbox()` 动态决定
- 超时：20s 默认，600s 最大
- 排除列表：user 配置的 `sandbox.excludedCommands`

**权限与验证**：
```typescript
validateInput():
  1. 检查 sleep N 反模式
  2. 检查 sed 编辑合法性
  3. 检查只读模式冲突

checkPermissions():
  1. parseForSecurity() AST 分析
  2. bashToolHasPermission() → 检查命令前缀规则
```

**安全边界**：
- 隐式管道语义：`cat file | bq` 被视为读操作
- 递归保护：`&&` / `||` 中的 BASH_SILENT_COMMANDS
- 输出截断：预设大小或磁盘持久化

### FileEditTool

**原子性与冲突检测**：
```typescript
// 读-修改-写：最小化窗口期
1. beforeFileEdited() hooks
2. mkdir() 确保父目录存在
3. fileHistoryTrackEdit() 备份

// 关键区间（无 await）:
4. readFileSyncWithMetadata()
5. 时间戳检查 → Stale write 防护
6. findActualString() → 引号归一化
7. getPatchForEdit() → 生成补丁
8. writeTextContent() → 原子写入
```

**权限决策**：
- `checkTeamMemSecrets()`：防止密钥注入
- UNC 路径跳过：防止 SMB 凭证泄露
- MAX_EDIT_FILE_SIZE = 1 GiB

### GrepTool

**Ripgrep 集成**：
- 隐藏文件：`--hidden`
- VCS 排除：.git, .svn 等（自动）
- 列长度限：`--max-columns 500`

**输出模式**：
- `files_with_matches` (-l)：仅文件名
- `content`：行内容 + 行号
- `count` (-c)：匹配计数

**结果处理**：
- 默认 limit=250（防止结果集膨胀）
- 路径相对化：节省 token
- 并发安全：`isConcurrencySafe() = true`

---

## 3. MCP 客户端架构

### 连接管理与传输

**传输层支持**：
- `stdio`: Child process
- `sse`: Server-Sent Events
- `http`: StreamableHTTPClientTransport
- `ws`: WebSocket
- `ws-ide` / `sse-ide`: IDE 内置
- `sdk`: SDK Control (in-process)

**连接池与缓存**：
- `ensureConnectedClient()` 使用 memoizeWithLRU
- MCP_AUTH_CACHE_TTL_MS = 15min

### 身份认证

**多种机制**：
1. **OAuth**：Authorization Code + 刷新令牌
2. **XAA**：企业 IdP 配置
3. **会话认证**：后端签发的 JWT
4. **自定义头部**：Node.js 脚本动态生成

### 工具代理与执行

**工具规范化**：
```typescript
buildMcpToolName(serverName, tool.name)
// → "mcp__serverName__toolName"
```

**执行流**：
```typescript
MCPTool.call(args, context):
  1. 查询 tools 列表
  2. schema 验证
  3. callTool() (MCP JSON-RPC)
  4. truncateMcpContentIfNeeded() → 20KB 限制
  5. persistBinaryContent() → 大输出
```

---

## 4. 权限模型设计

### 权限决策流

**决策模式（按优先级）**：
1. `validateInput()`：业务规则
2. `checkPermissions()`：权限规则
3. **自动分类器**（可选）

**权限行为**：
```typescript
type PermissionBehavior = 'allow' | 'deny' | 'ask'
```

### 工具特定权限检查

**FileEditTool**：
```typescript
checkWritePermissionForTool(tool, input, permissionContext):
  1. expandPath() → 规范化
  2. matchingRuleForInput(path, context, 'edit', 'deny')
```

**BashTool**：
```typescript
bashToolHasPermission(permission, command, context):
  1. parseForSecurity(command) → AST
  2. permissionRuleExtractPrefix(rule)
  3. matchWildcardPattern(rule, cmd)
```

---

## 5. 工具编排原则

### 流式执行与进度

**StreamingToolExecutor 特性**：
- 并发安全分类：`isConcurrencySafe() = true` → 可并行
- 进度流式推送：BashTool 2s 后显示进度
- 中断行为：`interruptBehavior() = 'cancel'` 或 `'block'`

### 权限与验证流水线

```
[1] validateInput() → 业务规则
         ↓
[2] checkPermissions() → Tool 的权限逻辑
         ↓
[3] PermissionContext 规则检查
         ↓
[4] 自动分类器（可选）
         ↓
[5] 权限对话（如果需要）
         ↓
[6] canUseTool() 最终决定
         ↓
[7] runTools() 执行
```

### 安全边界与隔离

**系统隔离（核心原则）**：
1. 输入验证 → 权限检查 → 执行（纵深防御）
2. 工具自主权：各自实现 validateInput、checkPermissions
3. 特殊路径处理：UNC、~、symlink

**资源限制**：
- FileEditTool: MAX_EDIT_FILE_SIZE = 1 GiB
- Bash: 超时 + SandboxManager
- GrepTool: DEFAULT_HEAD_LIMIT = 250

---

## 6. Harness 安全核心

### 权限决策可视化

```
用户输入（模型建议工具）
         ↓
[1] validateInput() → fail → 错误给模型
         ↓
[2] checkPermissions() → allow/deny/ask/passthrough
         ↓
[3] PermissionContext 规则 → deny/allow/ask
         ↓
[4] 自动分类器 → 安全/不安全
         ↓
[5] 权限对话 → 用户选择
         ↓
[6] 执行或拒绝
```

### 输入规范化与安全

**路径规范化**：
```typescript
expandPath(path: string):
  ~/foo → /Users/jin/foo
  ./foo → /current/working/dir/foo
```

**特殊处理**：
- UNC 路径：跳过 fs 操作
- symlink：工具链决定
- 引号归一化：智能引号匹配

---

## 总结

Claude Code 的 Execution Layer 以三个轴线组织：

1. **工具供应链**（Tool → Tools → assembleToolPool）
   - 特征门控条件加载
   - 权限过滤在模型获得工具前完成

2. **权限决策树**（validateInput → checkPermissions → rules → classifier → dialog）
   - 分层防御，每层独立可验证
   - 工具声明式接口 + 系统集中规则

3. **执行隔离**（StreamingToolExecutor → 进度 + 结果大小 + 持久化）
   - 并发安全分类
   - 流式进度和完全结果的统一处理

**安全核心承诺**：
- 任何工具执行前必须通过完整流程
- 权限规则全局生效，模型无法绕过
- 工具默认行为保守
- 边界情况有明确处理
