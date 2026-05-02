# Control Layer 架构分析


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> 来源：Claude Code 源码逆向分析
> 路径：`src/services/compact/`, `src/hooks/useCanUseTool.tsx`, `src/utils/hooks/`

## 1. 上下文压缩系统

### 触发条件与阈值

**阈值设定逻辑**（`autoCompact.ts`）：
- **有效上下文窗口** = 模型上下文窗口 - 20,000 (输出预留)
- **自动压缩阈值** = 有效窗口 - 13,000 (缓冲令牌)
- **警告阈值** = 阈值 - 20,000 令牌
- **错误阈值** = 阈值 - 20,000 令牌
- **堵塞限制** = 有效窗口 - 3,000 令牌（手动压缩）

**触发条件评估**（`shouldAutoCompact`）：
```
递归保护：
  - session_memory / compact 查询源禁用（避免死锁）
  - marble_origami (上下文代理) 禁用

特性门禁:
  - REACTIVE_COMPACT: 抑制主动压缩
  - CONTEXT_COLLAPSE: 禁用自动压缩

多源判决:
  - 全局配置: userConfig.autoCompactEnabled
  - 环境变量: DISABLE_COMPACT / DISABLE_AUTO_COMPACT
  - 模型特定: CLAUDE_CODE_AUTO_COMPACT_WINDOW
```

### 压缩算法分层

**阶段 1：会话记忆压缩**（实验性）
- 配置：minTokens: 10K, minTextBlockMessages: 5, maxTokens: 40K
- 计算保留索引：从 `lastSummarizedMessageId` 开始扩展
- **关键不变量保护**：`adjustIndexToPreserveAPIInvariants()`
  - 收集保留范围内的所有 tool_result IDs
  - 向后查找缺失的 tool_use IDs
  - 防止孤立 tool_use/tool_result 对

**阶段 2：时间基础微压缩**（`microCompact.ts`）
- 触发条件：自上次助手消息以来的差距 >= 配置阈值
- 行为：内容清除（非缓存编辑），保留最近 N 个可压缩工具结果
- 消息变异：工具结果内容 → `[Old tool result content cleared]`

**阶段 3：缓存微压缩**（Ant 仅）
- 机制：`cache_edits` API 层级操作（不修改本地消息）
- 工具追踪：`CachedMCState` 按用户消息分组注册工具结果

**阶段 4：传统完整压缩**（`compactConversation`）
- 触发：自动或手动 `/compact` 命令
- 限制：调用无工具代理，生成完整摘要

### 熔断机制

**电路断路器模式**：
```typescript
if (tracking?.consecutiveFailures >= MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES) {
  return { wasCompacted: false }  // 跳过所有未来尝试
}
// MAX = 3，基于 BigQuery 数据：1,279 会话有 50+ 连续失败
```

---

## 2. 权限控制系统

### 权限模式枚举

**内部模式** (`PermissionMode`)：
```typescript
'default'            // 用户确认每个工具调用
'plan'              // 计划模式（被动）
'acceptEdits'       // 自动接受编辑工具
'bypassPermissions' // 无限自动批准
'dontAsk'           // 特定会话规则强制通过
'auto'              // Ant 仅：自动分类器
'bubble'            // 内部：提升到协调器
```

### 权限上下文结构

```typescript
ToolPermissionContext {
  mode: PermissionMode
  additionalWorkingDirectories: Map<string, AdditionalWorkingDirectory>
  alwaysAllowRules: ToolPermissionRulesBySource
  alwaysDenyRules: ToolPermissionRulesBySource
  alwaysAskRules: ToolPermissionRulesBySource
}
```

**规则来源**（优先级）：
- `policy`（最高）→ `user` → `project` → `local` → `session`（最低）

### 规则匹配与决策流

1. Policy 规则检查（最高优先级）
2. 精确匹配优于正则表达式
3. 阻止规则优先于允许规则（安全优先）
4. 匹配结果缓存在 `classifierApprovals` 中

### 拒绝追踪与恢复

**自动模式拒绝**：
- 记录每个拒绝：工具名称、输入、拒绝原因
- Hook 输出解析：`{ hookSpecificOutput: { retry: boolean }}`
- 模型可重试或更改策略

---

## 3. Hook 机制

### Hook 系统架构

**25 个事件类型**：

**工具相关**：
- `PreToolUse`: 工具执行前，exit 2 阻塞
- `PostToolUse`: 工具执行后
- `PostToolUseFailure`: 超时/错误
- `PermissionDenied`: 自动模式拒绝

**会话管理**：
- `SessionStart`: 恢复/清除/压缩
- `SessionEnd`: 原因 = clear/logout/prompt_input_exit/other
- `UserPromptSubmit`: exit 2 阻塞 + 擦除
- `Stop`: 响应之前，exit 2 继续对话

**编码**：
- `PreCompact`: exit 2 阻塞压缩，exit 0 追加自定义指令
- `PostCompact`: 输出 → 用户可见

**权限**：
- `PermissionRequest`: Hook 输出 = allow/deny 决策
- `PermissionDenied`: 自动模式拒绝通知

### Hook 执行模式

**1. 命令 Hook**（同步/异步）
```typescript
// Exit codes:
// 0: success, use output
// 2: blocking, show stderr to model/user
// other: non-blocking, show stderr to user only
```

**2. Agent Hook**（`execAgentHook`）：
- 创建子 Agent（`query()` 循环）
- StructuredOutput 工具强制返回结果
- Max 50 turns，15s 默认超时
- 权限：`dontAsk` 模式强制

### Stop Hook 自验证循环

**约束**：Agent 必须满足条件才能停止。

**执行流程**：
1. Hook 定义 `prompt`: 验证条件描述
2. 系统创建验证 Agent
3. Agent 检查成绩单和代码库
4. 调用 StructuredOutput：
   ```json
   { "ok": true }  // 条件满足，停止
   { "ok": false, "reason": "..." }  // 条件未满足，继续
   ```

---

## 4. Harness 设计洞见

### 自验证循环

**多层验证**：

1. **令牌预算验证**（`calculateTokenWarningState`）
   - warning (93%), error (93%), autocompact (86%), blocking (99.7%)

2. **API 不变量验证**（`adjustIndexToPreserveAPIInvariants`）
   - tool_use/tool_result 对必须相邻
   - thinking 块必须与其关联的 tool_use 在同一消息 ID

3. **压缩输出验证**
   - 会话记忆非空且非模板？
   - postCompactTokenCount >= autoCompactThreshold？

4. **权限验证**（`useCanUseTool`）
   - 预检查 → 交互 → 后验证

### 约束强制执行

**编译时**：
- 不可变类型（`DeepImmutable<ToolPermissionContext>`）
- Schema 验证（`z.enum(PERMISSION_MODES)`）
- Feature gate（`feature('CONTEXT_COLLAPSE')`）

**运行时**：
- 断路器：连续失败 ≥ 3 → 停止重试
- 令牌卫士：isAtBlockingLimit → 阻塞查询
- Hook 阻塞：exit 2 → 中止操作

### 关键设计模式

**1. 分层堕化**
- 会话记忆 (最便宜) → 时间基础 MC → 缓存 MC → 完整压缩 (最贵)

**2. 查询源隔离**
- `querySource` 参数区分主线程 vs 子代理 vs 特殊模式

**3. Hook 链条执行**
- PreToolUse → Tool execution → PostToolUse/PostToolUseFailure
- Stop 之前 (验证) → Synthetic output enforcement

**4. 令牌度量与保留**
- 精确计数：`tokenCountFromLastAPIResponse()`
- 估计：`estimateMessageTokens()` (4/3 倍填充以保守)
- 预留：20K 输出 + 13K 缓冲 + 3K 手动紧急空间

---

## 5. 核心设计原则

### 可观察性
- 每个压缩、权限决策、Hook 执行都记录到 BigQuery
- `logForDebugging()` (环境变量 CLAUDE_DEBUG)

### 安全第一
- 阻塞优先：不确定时，要求用户确认
- 策略覆盖：管理员规则 > 所有用户/项目规则
- 进程隔离：子代理强制 `dontAsk` 模式

### 效率
- 分类器批准缓存
- 微压缩状态缓存
- Hook 投机性结果

### 可恢复性
- 无损重压缩：边界消息 + preserved-segment 链
- 配置热加载：GrowthBook 特性门支持即时 A/B 测试

---

## 总结

Claude Code 的 Control Layer 展现了**分层防护、可验证约束和渐进降低**的架构：

1. **上下文压缩** = 多阶段削减 + 熔断保护
2. **权限控制** = 规则匹配 + 分类器 + Hook 干预 + 用户确认
3. **Hook 系统** = 25 事件类型 + 同步/异步/Agent 执行
4. **自验证** = API 不变量检查 + 令牌预算验证 + Stop Hook 循环
5. **约束执行** = 编译时 (types, gates) + 运行时 (breakers, guards)

设计优先级：**正确性 > 效率 > 灵活性**
