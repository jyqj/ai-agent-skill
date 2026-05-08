# Browser Use 架构分析

> **Evidence Status**: synthesized. 基于 Browser Use GitHub README、行业报告与深度指南的架构综合，非源码级分析。
> **来源**: [Browser Use GitHub](https://github.com/browser-use/browser-use) | [Agentic Browser Landscape 2026](https://nohacks.co/blog/agentic-browser-landscape-2026) | [Browser Agents Deep Guide 2026](https://o-mega.ai/articles/agentic-computer-use-the-ultimate-deep-guide-2026)

## 项目概述

Browser Use 是当前最流行的开源浏览器 Agent 框架（81,200+ GitHub stars，2026.03 数据），提供 Python-first 的 LLM 驱动浏览器自动化能力。核心定位是让 LLM 能够像人类一样操作浏览器完成复杂网页任务——从信息采集到表单填写、从多步导航到交互验证。

在 WebVoyager 基准（586 tasks）上达到 89.1% 成功率，显著超越 OpenAI Operator 在 WebArena 上的 ~32.6%。

## 核心架构

```text
用户任务描述
  → LLM 决策引擎（接收页面状态 + 任务上下文）
  → 动作决策（click / type / scroll / navigate / extract）
  → Playwright 执行层（原子操作）
  → 双通道感知管线
      ├─ DOM/Accessibility Tree 通道（结构化节点 + ARIA 属性）
      └─ Screenshot/Vision 通道（页面截图 → 视觉模型）
  → 验证 & 状态更新
  → 循环，直到任务完成或失败
```

### 双通道感知管线

| 通道 | 输入格式 | 优势 | 劣势 | token 消耗 |
|------|---------|------|------|-----------|
| **DOM/Accessibility Tree** | 结构化 HTML 节点、ARIA 属性 | 精确元素定位、低 token 消耗 | 无法捕获视觉渲染状态、Canvas 内容不可见 | 低 |
| **Screenshot/Vision** | 页面截图（PNG） | 捕获视觉布局、处理动态渲染 | 高 token 消耗、坐标精度受限 | 高（10-100x） |

Browser Use 的关键区分点：支持 DOM extraction、vision model、或**两者同时使用**的三种模式。双通道验证模式在一个通道失败时可降级到另一个。

### Observe-Act 自主循环

1. **感知**：获取当前页面状态（DOM 快照 + 可选截图）
2. **推理**：LLM 接收完整页面状态 → 决定下一步动作
3. **执行**：通过 Playwright 执行受限动作空间中的操作
4. **验证**：执行后重新获取 DOM / 截图，确认动作效果
5. **循环**：重复直到任务完成、失败或达到步数上限

这是一个完全自主的循环——不需要人工介入每一步决策，但在敏感操作（密码输入、支付确认）时可配置 Human-in-the-Loop 检查点。

## 关键设计决策

| 决策 | 选择 | 理由 | 权衡 |
|------|------|------|------|
| 执行引擎 | Playwright | 成熟、跨浏览器、原生 async | 依赖 Node.js 生态 |
| 感知策略 | 双通道可切换 | 覆盖 DOM 不可见场景（Canvas, SVG） | 双通道模式增加 latency 和 token 成本 |
| 动作空间 | 约束型（click/type/scroll/navigate） | 限制攻击面，减少幻觉动作 | 无法处理拖拽等复杂手势 |
| LLM 集成 | Provider-agnostic | 支持多种模型后端 | 不同模型的视觉能力差异大 |
| 循环控制 | 步数上限 + 任务完成检测 | 防止无限循环和成本失控 | 复杂任务可能被过早截断 |
| 错误恢复 | 重试 + 替代策略 | "遇到意外页面时尝试替代策略" | 无法处理 CAPTCHA 和 bot 检测 |

## 与知识库的映射

| Browser Use 概念 | 知识库 Plane / Pattern |
|------------------|----------------------|
| 双通道感知（DOM + Screenshot） | Representation Plane — `representation-contract.md`；`multimodal-grounding.md` |
| Observe-Act 循环 | ORDA-VU 闭环（Observe → Represent → Decide → Act → Verify → Update） |
| Playwright 执行层 | Execution Plane — `execution-env.md` |
| 动作空间约束 | Control Plane — 动作边界约束 |
| 步数上限 / token 预算 | Cost Plane — `token-budgeting.md` |
| 人工介入检查点 | Interaction Plane — `trust-escalation.md`、`interruption.md` |
| 截图验证 | Effects Plane — `gui-verification.md` |
| 错误恢复策略 | Recovery Plane — 降级策略 |
| 页面状态追踪 | World State Plane — 外部状态快照 |

## 值得学习的模式

### 1. 渐进式感知降级

先用 DOM extraction（低成本），失败时升级到 vision（高成本）。这种分层策略在成本和覆盖率之间取得了有效平衡，可泛化到其他需要多模态感知的 Agent 类型。

### 2. 动作空间约束

限制 Agent 可执行的动作类型（click、type、scroll、navigate），而非开放任意 API 调用。这种设计减少了幻觉动作的发生概率，也缩小了安全攻击面。

### 3. 每步验证循环

每次动作执行后都重新获取页面状态进行验证，而不是盲目执行多步。这对应 ORDA-VU 中 Verify 阶段的 Micro-loop 粒度实践。

### 4. 混合确定性/AI 架构方向

Browser Use 社区正在趋向"稳定路径用 Playwright 脚本、动态路径用 AI Agent"的混合模式。这种两层降级策略将确定性和灵活性结合，是浏览器自动化领域 2026 年的赢家架构。

## 性能基准

| 基准 | 任务规模 | Browser Use 成绩 | 对比 |
|------|---------|-----------------|------|
| WebVoyager | 586 tasks | **89.1%** | OpenAI Operator (WebArena): ~32.6% |
| 30 天选择器维护 | — | <5% 提示调整 | Playwright: 15-25% 选择器修复 |

### 与同类项目的架构对比

| 维度 | Browser Use | Stagehand | agent-browser |
|------|------------|-----------|--------------|
| 控制模型 | 完全自主循环 | 开发者控制循环 | 自验证循环 |
| 感知策略 | 双通道（DOM + Vision） | DOM-first + Vision 降级 | 紧凑快照 + 稳定引用 |
| 上下文消耗 | 中-高 | 低-中 | 极低（减少 82.5%） |
| 适用场景 | 端到端自主浏览器任务 | 开发者嵌入式自动化 | Vercel 部署验证闭环 |

## 局限与注意事项

| 风险类型 | 具体表现 | 当前状态 |
|----------|---------|---------|
| **Prompt Injection** | 不可信网页内容中嵌入对抗性输入 | 固有脆弱性，"可能永远无法完全解决" |
| **幻觉动作** | Agent 点击不存在的元素 | 需要动作后验证机制缓解 |
| **Bot 检测** | 网站反自动化机制 | 需要速率限制和会话状态管理 |
| **动态内容等待** | LLM 无法可靠预测页面加载时机 | 依赖显式 wait 策略和超时机制 |
| **维护成本** | AI Agent 提示调整 <5%（vs Playwright 选择器 15-25%） | 优势明显但仍有长尾问题 |
| **成本控制** | 双通道模式下 token 消耗显著增加 | 需要按任务类型选择感知模式 |

**WebMCP 方向**：Google 于 2026.02 在 Chrome Canary 引入 WebMCP 协议，将网站转化为 AI Agent 的结构化工具接口。这可能改变 Browser Agent 的感知策略——从"逆向解析页面"转向"消费网站主动暴露的结构化 API"。Browser Use 未来可能需要适配这一标准化方向。
