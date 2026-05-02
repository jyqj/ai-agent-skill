# Browser / Desktop Agent Implementation Map

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

## 参考实现

| 参考 | 学习点 |
|---|---|
| Claude Computer Use | screenshot-action loop、Zoom Action、安全沙箱 |
| Claude in Chrome | 浏览器扩展、tab 管理 |
| OpenAI Operator/CUA | 任务规划、安全约束 |
| Browser Use (81K★) | DOM+视觉混合、89% WebVoyager |
| Browserbase/Steel | 云浏览器基础设施 |
| WebMCP | 网站工具协议 |

## MVA 阶梯

| 级别 | 能力 |
|---|---|
| MVA-0 | 截图 → LLM 理解 → 建议 |
| MVA-2 | 单页面 DOM 操作 |
| MVA-3 | 多步 + 截图验证 + 错误恢复 |
| MVA-4 | 跨页面 + 会话管理 + 效果验证 |
| MVA-5 | 批量 + 云浏览器 + 完整审计 |
