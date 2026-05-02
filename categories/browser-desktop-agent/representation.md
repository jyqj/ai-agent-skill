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
