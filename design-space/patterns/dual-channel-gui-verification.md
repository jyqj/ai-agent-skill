# Dual-Channel GUI Verification

> **Evidence Status** — synthesized. 从 browser-use、desktop-use、computer-use 等多个 GUI 自动化项目中提炼的共性需求，在截图+DOM 双通道验证这一点上有较强共识。

GUI 自动化中最常见的错觉是：点击发生了，不等于任务完成了。

单看 DOM 容易被隐藏状态、虚拟节点或延迟渲染误导；单看截图又会丢失结构信息和可编辑字段的真实状态。只依赖一个通道，就容易出现以下问题：

- DOM 中元素存在，但在用户视口中不可见；
- 截图看起来正确，但实际表单未提交；
- OCR 识别错误，坐标点击偏移；
- 页面局部刷新后，旧截图仍被当成最新观察。

## 做法

对关键动作默认使用双通道验证（Dual-Channel Verification）：

- **结构通道**：DOM / 无障碍树（Accessibility Tree）/ 网络状态
- **视觉通道**：截图 / OCR / 像素差分（Pixel Diff）/ 视口状态

只有两个通道都确认、或其中一个被证明足够强时，才把操作效果升级为"已验证"。

## 常见动作的验证策略

| 动作 | 结构通道 | 视觉通道 | 完成条件 |
|---|---|---|---|
| 输入表单 | field value / DOM state | 新截图显示目标值 | 两者一致 |
| 点击提交 | DOM state + network / URL | 成功页或 toast 可见 | 至少一强一弱组合 |
| 页面导航 | URL / title / DOM landmark | 目标页面截图 | 刷新后回读 |
| 高风险按钮 | target element identity | viewport highlight | 两通道确认目标一致 |

## 配套规则

- 每次关键动作前刷新当前 view token。
- 坐标点击前，先确认元素身份（Element Identity）和视口对齐（Viewport Alignment）。
- DOM 与截图冲突时，不自动选择"看起来更像对的那个"；应重新观察或降级交付。

## 关联文档

- `../../architecture/planes/representation/multimodal-grounding.md`
- `../../architecture/planes/effects/gui-verification.md`
- `../../evaluation/fixtures/browser_gui_grounding_001.yaml`
