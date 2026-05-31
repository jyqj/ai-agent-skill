# Browser / Desktop Agent Representation Model

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

## 核心表示对象

| 表示对象 | 含义 | Freshness | Trust |
|---|---|---|---|
| DOM/AccessibilityTree | 页面结构化表示 | 每操作后刷新 | medium（可被 JS 操纵） |
| Screenshot | 页面视觉快照 | 每操作后刷新 | high（所见即所得） |
| PageState | URL+title+scroll+loading | 实时 | high |
| FormFieldState | 表单当前值和验证状态 | 提交前刷新 | medium |
| ActionHistory | 已执行操作序列 | append-only | high |

## 双通道验证

```text
L1: DOM 状态变化（元素出现/消失/文本变化）
L2: 截图视觉确认（按钮灰化、成功提示）
L3: 后端效果验证（确认邮件、记录回读）
```

## 感知策略

| 策略 | 优势 | 劣势 | 适用 |
|---|---|---|---|
| DOM/A11y 优先 | 快、精确、低成本 | 不感知视觉渲染 | 标准 HTML |
| 截图优先 | 所见即所得 | 慢、贵 | 复杂 SPA/canvas |
| 混合 | 互补验证 | 实现复杂 | 生产推荐 |

## 双通道感知管线收敛趋势（2026 更新）

> 来源：agent-category-corpus-2025-2026.md §1.1 感知管线

### DOM/Accessibility Tree vs Screenshot/Vision 对比

| 维度 | DOM/Accessibility Tree | Screenshot/Vision |
|------|----------------------|-------------------|
| 输入 | 结构化 HTML 节点、ARIA 属性 | 页面截图 |
| 优势 | 精确元素定位、低 token 消耗 | 捕获视觉布局、处理 Canvas/动态渲染 |
| 劣势 | 无法捕获视觉渲染状态 | 高 token 消耗、坐标精度受限 |
| 适用场景 | 标准 HTML、表单交互 | 复杂 SPA、Canvas、视觉验证 |

### agent-browser 紧凑快照

Vercel **agent-browser** 的紧凑快照方案返回带稳定引用的极简表示（如 `button "Sign In" [ref=e1]`），比 Playwright MCP 的完整无障碍树减少 **82.5%** 上下文消耗。`[ref=eN]` 引用替代 CSS 选择器/XPath，减少歧义和 token 开销。

### Stagehand DOM-first 策略

**Stagehand**（Vercel）采用 DOM-first 策略：对 DOM 进行 **chunking + ranking** 定位元素，比纯视觉方案更可靠。渐进式感知：先 DOM extraction（低成本），失败时升级到 vision（高成本）。

### Browser Use 双通道同时使用模式

**Browser Use**（81,200+ GitHub stars，2026.03）支持三种感知模式：

1. **Vision model**：截图输入
2. **DOM extraction**：结构化 DOM 提取
3. **双通道验证**：两者同时使用，互补校验

WebVoyager 基准达 **89.1%** 成功率。双通道同时使用是当前生产推荐模式。

### 收敛趋势小结

2026 年多数生产团队收敛到**混合模式**：对稳定、高频工作流使用确定性 Playwright 脚本，对动态、陌生界面使用 AI Browser Agent。Stagehand 的"AI 原语叠加在 Playwright 之上"是这一方向的代表模板。
