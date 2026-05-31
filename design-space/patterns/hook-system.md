# Hook 生命周期系统 (Hook System)

> **Evidence Status** — grounded. Augment 实现了 SessionStart/PreToolUse/PostToolUse/Stop 四阶段 Hook + 缓存机制；Claude Code 在 settings 中支持 pre-tool-use/post-tool-use hooks。两者设计高度趋同。

Agent 执行过程中，外部系统（Harness）经常需要在关键节点介入：记录审计日志、检查安全策略、向用户展示信息、拦截危险操作。如果每个介入点都硬编码，系统很快就会变成一团条件分支。Hook 系统的价值在于把"在哪介入"和"介入时做什么"解耦。

## 生命周期事件

标准的 Hook 事件通常覆盖四个节点：

- **SessionStart**：会话开始时触发，用于加载用户偏好、展示欢迎信息、初始化审计上下文
- **PreToolUse**：工具调用前触发，这是最关键的拦截点——权限检查、危险操作阻断、输入审计都在这里发生
- **PostToolUse**：工具调用后触发，用于记录结果、自动格式化、发送通知
- **Stop**：会话结束时触发，用于清理资源、保存状态、生成总结

## 核心接口

```typescript
interface HookContext {
  conversationId: string;
  requestId: string;
  toolName?: string;
  toolInput?: object;
  toolOutput?: object;
  changedFiles?: string[];
}

interface HookOutput {
  displayMessages?: string[];  // 展示给用户
  blockTool?: boolean;         // 拦截工具调用
  stopAgent?: boolean;         // 停止 Agent
  modifiedInput?: object;      // 修改工具输入
}
```

Hook 处理器按注册顺序执行。如果任何一个处理器返回 `blockTool: true` 或 `stopAgent: true`，后续处理器不再执行——这是一个短路（Short-circuit）语义，设计时需要注意注册顺序。

## PreToolUse 缓存

PreToolUse 是调用频率最高的 Hook 事件，而且在某些实现中会被执行两次（先 dryRun 预检、再正式执行）。为避免重复计算，可以对相同的 toolName + toolInput 组合做缓存：

```typescript
function createPreToolUseCache() {
  const cache = new Map<string, HookOutput>();
  return {
    getOrExecute: async (toolName, toolInput, executor) => {
      const key = hash(toolName, toolInput);
      if (cache.has(key)) return cache.get(key)!;
      const result = await executor();
      cache.set(key, result);
      return result;
    },
    invalidate: () => cache.clear()
  };
}
```

## 权衡

Hook 系统最大的优势是可扩展性和关注点分离：新增一个安全检查只需要注册一个 PreToolUse Handler，不用改动 Agent 主循环。但这也带来了调试困难。当多个 Hook 同时注册在同一事件上时，执行顺序、短路行为和输出合并逻辑可能产生难以预料的交互效果。实际项目中建议对 Hook 执行链做日志记录，并为每个 Hook 标注优先级。

性能方面，Hook 链的开销通常可以忽略（相比 LLM 调用），但如果某个 Hook 需要做网络请求或复杂计算，应当考虑异步化或使用上述缓存机制。

## 实践参考

- **Augment**：SessionStart/PreToolUse/PostToolUse/Stop + 缓存
- **Claude Code**：pre-tool-use/post-tool-use hooks in settings

## Breadcrumb Per-Turn Injection (Trellis)

> **Evidence**: Trellis — 14-platform Agent Harness

传统 Hook 系统在 SessionStart 一次性注入上下文。Trellis 的 breadcrumb 模式超越了这个限制：

**机制**：每轮 AI 交互，Hook 读取 `task.json` 的 `status` 字段，从 `workflow.md` 中提取对应的 `[workflow-state:STATUS]` tag 块内容，注入到 user prompt。

**状态**：`no_task` → `planning` → `in_progress` → `completed`（+ `planning-inline` / `in_progress-inline` 变体）

**注入路径**：
- SessionStart hook（Claude Code / Cursor）
- UserPromptSubmit hook（Codex / Gemini / Copilot）—— 每轮触发
- Plugin entry（OpenCode）—— JS 插件调用 Python helper

**优势**：
- 无状态、可重复 —— resilient to hook 失败
- 声明式 —— 修改 workflow.md 直接影响 AI 行为
- Per-turn 颗粒度 —— 比一次性 session-start 更精准

**与传统 Hook 的对比**：
| 维度 | SessionStart Hook | Breadcrumb Per-Turn |
|------|------------------|-------------------|
| 触发频率 | 一次/会话 | 每轮 |
| 状态感知 | 初始状态 | 实时状态 |
| 恢复能力 | 需重启会话 | 自动修正 |
| 复杂度 | 低 | 中 |

## Plugin Hook Registration (OpenClaw)

> **Evidence**: OpenClaw — 125 extensions, 50+ hook directories

OpenClaw 将 Hook 从固定生命周期点扩展为 plugin 可注册的全面事件系统：

**Hook 类型**：
- **Plugin lifecycle** — setup / teardown
- **Agent turn** — before/after execution（修改 agent context）
- **Message inbound** — raw filter / processing
- **Reply dispatch** — customize outbound delivery
- **Tool execution** — pre/post tool call
- **Session events** — create / close / persist
- **Heartbeat** — 周期性后台工作（proactive agent behavior）

**注册模式**：
```
plugin.hooks.registerAgentTurnPrepare((event) => {
  return { ...event, customField: value };
});
plugin.hooks.registerHeartbeatPromptContribution((event) => {
  return { prompts: [...] };
});
```

**与传统 Hook 的关键差异**：
- 传统：固定 4 点（SessionStart/PreToolUse/PostToolUse/Stop）
- OpenClaw：7+ 类型，每个类型支持多 plugin 注册
- 冲突解决：plugin 优先级 + 注册顺序
- Heartbeat hook 实现了 proactive agent（无用户输入时也能工作）
