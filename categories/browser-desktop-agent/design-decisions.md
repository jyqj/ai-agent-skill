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

## 混合模式架构（2026 更新）

> 来源：agent-category-corpus-2025-2026.md §1.1 架构收敛趋势、§1.4 独特设计模式

### 确定性 Playwright + AI Agent 混合架构

2026 年的架构收敛方向：稳定路径用确定性 Playwright 脚本，动态路径用 AI Agent——两层降级策略。这种混合模式兼顾可靠性和灵活性。

### Stagehand 三原语

**Stagehand**（Vercel）在 Playwright 之上提供三个 AI 原语：

| 原语 | 功能 | 输入 |
|------|------|------|
| `act()` | 自然语言动作执行 | 自然语言指令 |
| `extract()` | 结构化数据提取 | Zod schema 定义 |
| `observe()` | 元素发现与页面理解 | 观察目标描述 |

这是多数生产团队趋近的模板：确定性自动化 + AI 原语叠加。

### 确定性脚本 vs AI Agent 决策矩阵

| 维度 | 确定性脚本（Playwright） | AI Agent |
|------|-------------------------|----------|
| 适用场景 | 稳定、高频、结构已知的工作流 | 动态、陌生、结构变化的界面 |
| 可靠性 | 高（但脆弱于 UI 变更） | 中（依赖 LLM 推理质量） |
| 维护成本 | 30 天 **15-25%** 选择器需修复 | 30 天 **<5%** 提示需调整 |
| Token 消耗 | 无 | 每步需 LLM 调用 |
| 开发速度 | 慢（需编写精确选择器） | 快（自然语言描述意图） |
| 推荐策略 | 核心业务流程、合规操作 | 探索性任务、跨站点泛化 |

### Microsoft Agent Workspace 沙箱隔离

OS 级 Agent（Simular、Microsoft Agent Workspace）扩展到桌面应用控制。Microsoft 引入 **Agent Workspace** 作为隔离的 Windows 沙箱环境，防止 Agent 越权访问系统资源。MCP 协议通过 API 暴露特定功能（文件管理器、设置），而非原始 GUI 控制，缩减攻击面。

### 选择器维护 vs AI 维护成本对比

| 指标 | Playwright 选择器 | AI Agent 提示 |
|------|-------------------|---------------|
| 30 天修复率 | 15-25% 需修复 | <5% 需调整 |
| 失败模式 | UI 改版导致选择器失效 | LLM 幻觉/误解页面状态 |
| 修复方式 | 手动更新选择器 | 调整提示/更换模型 |
| 长期趋势 | 维护成本线性增长 | 随模型进步自然改善 |
