# State & UI Layer 架构分析


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> 来源：Claude Code 源码逆向分析
> 路径：`src/state/`, `src/ink/`, `src/components/`

## 1. 状态管理 (state/)

### AppState 结构

AppState 是一个 **700+ 行的巨大状态树**，使用 `DeepImmutable<T>` 类型包装保证不变性。

**核心状态分组**：
- **会话上下文**：`settings`, `verbose`, `mainLoopModel`, `agent`, `kairosEnabled`
- **UI 呈现状态**：`expandedView`, `isBriefOnly`, `statusLineText`, `footerSelection`
- **任务管理**：`tasks` (键值对存储), `foregroundedTaskId`, `viewingAgentTaskId`
- **远程/Bridge 状态**：`remoteSessionUrl`, `remoteConnectionStatus`, `replBridgeEnabled`
- **MCP 系统**：`mcp.clients`, `mcp.tools`, `mcp.commands`, `mcp.resources`
- **插件系统**：`plugins.enabled/disabled`, `plugins.errors`, `installationStatus`
- **特殊状态**：
  - `speculation`：推测执行的消息缓存（使用可变引用避免数组频繁重建）
  - `teamContext`/`standaloneAgentContext`：代理管理
  - `replContext`：REPL 虚拟机上下文持久化

### Store 实现

```typescript
type Store<T> = {
  getState: () => T
  setState: (updater: (prev: T) => T) => void
  subscribe: (listener: Listener) => () => void
}
```

**关键特性**：
- 发布-订阅模式
- 浅比较优化：`Object.is(next, prev)`
- 更新函数式：`setState` 接收 `(prev) => T`
- 可选 onChange 钩子

### onChangeAppState 变化观测器

```typescript
onChangeAppState({ newState, oldState }) {
  // 1. toolPermissionContext.mode → 同步到 CCR + SDK
  // 2. mainLoopModel → 写入 settings
  // 3. expandedView → 保存到 globalConfig
  // 4. settings 变化 → 清空认证缓存
}
```

**设计模式**：
- **Derived State**: 状态变化 → 持久化操作
- **Side Effect Isolation**: 所有外部通知集中处理
- **Diff-Based Routing**: 只在真实变化时触发

---

## 2. Ink 框架 (ink/)

### 核心架构：Fork-based DOM 模型

**DOM 树结构**（dom.ts）：
```typescript
DOMElement {
  nodeName: 'ink-root' | 'ink-box' | 'ink-text' | 'ink-virtual-text' | ...
  childNodes: DOMNode[]
  yogaNode?: LayoutNode
  dirty: boolean
  _eventHandlers: {}
  scrollTop, pendingScrollDelta
}
```

### 核心渲染管道

1. **React Reconciliation** (reconciler.ts)
   - 自定义 host config
   - 与 react-reconciler 的 Dispatcher 集成

2. **Layout Engine** (layout/yoga.ts)
   - 原生 Yoga 布局引擎（WASM）
   - 支持 Flexbox 属性
   - 文本测量函数

3. **Screen Rendering** (render-node-to-output.ts)
   - DOM 树遍历
   - Blitting 优化
   - 绝对定位、滚动支持

4. **Diff & Patch** (log-update.ts, optimizer.ts)
   - DECSTBM 优化：硬件滚动指令
   - 合并相邻风格指令

5. **Terminal Output** (terminal.ts, termio/)
   - ANSI 转义序列
   - Kitty Keyboard Protocol
   - Mouse Tracking、Alt Screen

### 关键性能优化

**1. Screen Buffer Pooling**
```typescript
CharPool {
  ascii: Int32Array      // ASCII 快速路径
  stringMap: Map<string, number>
}
StylePool {
  transitionCache: Map   // 预计算 ANSI 转义
}
```

**2. Dirty Bit & Blit**
- 节点标记 `dirty: true` 时触发重新计算
- 清洁的子树可直接从前一帧复制

**3. Yoga 性能计数器**
```typescript
{
  visited: 节点遍历数
  measured: 文本测量调用数
  cacheHits: 单槽缓存命中
  live: 当前活动 Yoga 节点数
}
```

**4. 懒渲染与虚拟滚动**
- `ink-virtual-text` 不占用布局空间
- ScrollBox 支持 viewport culling

### 事件系统

**两层次事件分发**：

1. **Terminal 事件源**
   - `keydown`/`keyup`
   - `click`/`mousemove`
   - `paste`、`resize`

2. **Dispatcher & Event Priority**
   ```typescript
   keydown, click, focus → DiscreteEventPriority
   resize, scroll, mousemove → ContinuousEventPriority
   ```
   - capture → at_target → bubble 阶段

**Focus 管理**：
```typescript
FocusManager {
  activeElement: DOMElement | null
  focusStack: DOMElement[]  // 最近 32 个焦点的历史
}
```

### Ink 组件库

**核心组件**：
- `<Box>` — Flexbox 容器
- `<Text>` — 文本节点
- `<ScrollBox>` — 可滚动区域
- `<AlternateScreen>` — Alt Screen 模式
- `<Button>` — 可聚焦按钮
- `<Link>` — OSC 8 超链接

**上下文提供者**：
- `<TerminalSizeContext>`
- `<TerminalFocusContext>`
- `<StdinContext>`
- `<ClockContext>`

---

## 3. 组件系统 (components/)

### 顶层 App 包装

```typescript
function App({ getFpsMetrics, stats, initialState, children }) {
  return (
    <FpsMetricsProvider>
      <StatsProvider>
        <AppStateProvider initialState={initialState} onChangeAppState={onChangeAppState}>
          {children}
        </AppStateProvider>
      </StatsProvider>
    </FpsMetricsProvider>
  )
}
```

### 消息渲染

处理 Claude 响应的多种内容类型：
- 文本块：流式接收，实时渲染
- 工具使用：ToolUseLoader 显示执行进度
- 思考：conditional rendering
- 错误：FallbackToolUseErrorMessage

### 交互组件

- **PromptInput** — 用户输入行
- **QuickOpenDialog** — 快速打开对话框
- **TagTabs** — 标签页导航
- **Settings** — 配置 UI
- **StatusLine** — 底部状态栏
- **FullscreenLayout** — 全屏模式容器

---

## 4. Harness 设计洞见

### 临时脚本沙箱
- 允许 bash 命令编写临时脚本到 `/tmp`
- 用于多步竞态条件测试

### Memdir 保证
- Harness 保证 memdir 目录存在
- 模型可以无条件写入

### 权限系统的 Harness 通知
- 内部 mode 不暴露给 harness
- `set_permission_mode` 是单向通道

### Claude Code Hints（side channel）
```
<!-- CLAUDE_CODE_HINT version=1 type=allow_read path=/etc/passwd -->
```
- Harness 扫描工具输出中的标签
- 在模型看到之前移除

---

## 5. 跨层设计模式

### 单向数据流

```
AppState (store.ts)
  ↓ setState 更新
  → onChangeAppState 观测
    → 同步到 globalConfig/settings
    → 通知 CCR/SDK
  ↓ context 订阅
    → React 重新渲染
    → Ink DOM 树更新
    → Yoga 布局计算
    → Screen 渲染
    → LogUpdate diff
    → Terminal 输出
```

### 状态隔离的分段

| 类型 | 位置 | 持久化 |
|------|------|--------|
| 持久化状态 | settings, globalConfig | onChangeAppState |
| 会话状态 | tasks, MCP connections | 内存 AppState |
| 临时 UI 状态 | expandedView | 仅 AppState |
| 异步状态 | speculation | 可变 ref |

### 渲染优化的分层

| 层级 | 优化 | 成本 |
|------|------|------|
| React | Compiler codegen | 编译时 |
| Ink DOM | dirty bit + blit | O(changed nodes) |
| Yoga | 缓存、measuredFunc 去重 | 文本测量缓存 |
| Screen | 风格 ID 池化 | 字符串驻留 |
| Terminal | DECSTBM 硬件滚动 | O(changed cells) |

### 错误边界

```typescript
static getDerivedStateFromError(error: Error) {
  return { error }
}
// 显示 ErrorOverview 组件
```

### 事件优先级

```
Discrete (高) → click、keydown、blur
Default (中) → 大多数状态更新
Continuous (低) → mousemove、scroll
```

---

## 总结

Claude Code 的 State & UI Layer 采用**最小化、分离的架构**：

- **状态管理**：纯 JavaScript Store（无 Redux/Zustand），配合 DeepImmutable 类型约束
- **Ink 框架**：自定义 React 渲染器，充分利用 Yoga 和终端特性
- **性能**：多层优化（dirty bits、blit、screen pooling、yoga 缓存）
- **可测试性**：明确的事件分发、焦点管理、SSOT 原则
- **可维护性**：分层 context、清晰责任划分、显式副作用管理

这种设计特别适合**终端 UI 的约束**（无 DOM、同步输出、有限重绘预算）。
