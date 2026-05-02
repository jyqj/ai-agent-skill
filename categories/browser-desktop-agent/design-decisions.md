# Browser / Desktop Agent Design Decisions

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

| 决策 | 默认建议 | 升级触发器 |
|---|---|---|
| 感知 | DOM+截图双通道；A11y 优先 | canvas/复杂 SPA → 截图优先 |
| 沙箱 | 隔离 profile；独立 cookie | 多用户 → 容器化 (Browserbase) |
| 安全 | allowlist、anti-phishing、injection 防护 | 敏感操作 → 人工确认 |
| 定位 | 多策略降级 | 动态页面 → 视觉定位 |
| 成本 | 截图降分辨率；DOM 裁剪 | 批量 → 模板化路径 |

## 安全考量

- **DOM Prompt Injection：** 恶意网页在 DOM 注入指令。Agent 不将 DOM 文本作为指令。
- **凭证泄露：** 截图可能含敏感信息。存储需加密。
- **跨域攻击：** 验证当前 URL 防重定向。
