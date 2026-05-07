# Stagehand 架构分析

> **Evidence Status**: grounded
> **来源**: [Stagehand GitHub (Vercel)](https://github.com/browserbase/stagehand) | [Stagehand vs Browser Use vs Playwright](https://www.nxcode.io/resources/news/stagehand-vs-browser-use-vs-playwright-ai-browser-automation-2026) | [Agentic Browser Landscape 2026](https://nohacks.co/blog/agentic-browser-landscape-2026)

## 项目概述

Stagehand 由 Vercel 旗下 Browserbase 团队开发，是一个 TypeScript-first 的 AI 浏览器自动化框架。核心设计哲学是"AI 原语叠加在 Playwright 之上"——不替代 Playwright，而是在其基础上提供三个 AI 增强原语，让开发者在确定性脚本和 AI 灵活性之间自由切换。

这一设计使 Stagehand 成为 2026 年多数生产团队趋近的模板：混合确定性/AI 架构的代表。

## 核心架构

```text
开发者代码
  → Stagehand SDK（TypeScript）
      ├─ act(instruction)     → 自然语言动作执行
      ├─ extract(schema)      → Zod schema 结构化数据提取
      └─ observe()            → 页面元素发现与描述
  → DOM-First 感知管线
      ├─ DOM Chunking（将页面 DOM 分块）
      ├─ Chunk Ranking（LLM 评估每块相关性）
      └─ 元素定位（精确到目标元素）
  → Playwright 执行层（底层浏览器控制）
  → 结果返回 → 开发者决定下一步
```

### 三原语设计

| 原语 | 签名 | 输入 | 输出 | 用途 |
|------|------|------|------|------|
| `act()` | `act(instruction: string)` | 自然语言动作描述 | 动作执行结果 | 点击按钮、填写表单、导航 |
| `extract()` | `extract(schema: ZodSchema)` | Zod schema 定义 | 类型安全的结构化数据 | 页面信息提取、数据采集 |
| `observe()` | `observe()` | 无 | 可交互元素列表 + 描述 | 页面元素发现、状态感知 |

三原语的设计核心是**让 AI 处理动态部分，让开发者保持控制权**。开发者编写确定性的控制流，仅在需要 AI 判断的节点调用原语。

### DOM-First 策略

与 Browser Use 的双通道架构不同，Stagehand 采用 **DOM-first** 策略：

1. **DOM Chunking**：将页面 DOM 树按语义结构分割为可管理的块
2. **Chunk Ranking**：LLM 评估每个块与当前任务的相关性，排序选择
3. **元素定位**：在排名最高的块中精确定位目标元素
4. **降级 Vision**：仅在 DOM 策略失败时（如 Canvas、复杂 SVG）才启用截图

这种策略的优势：token 消耗更低、定位更精确、确定性更强。

## 关键设计决策

| 决策 | 选择 | 理由 | 权衡 |
|------|------|------|------|
| 语言生态 | TypeScript-first | 对齐 Web 开发者工作流 | Python 生态用户需要额外适配 |
| 架构关系 | 叠加在 Playwright 之上 | 复用成熟基础设施，不重复造轮 | 依赖 Playwright 版本兼容性 |
| 感知策略 | DOM-first + Vision 降级 | 低 token、高精度优先 | Canvas / 视觉依赖场景需降级 |
| API 设计 | 三原语（act/extract/observe） | 最小 API 面积，降低学习成本 | 复杂多步工作流需要开发者自行编排 |
| 数据提取 | Zod schema 驱动 | 类型安全、可验证、IDE 友好 | schema 定义成本高于自由文本提取 |
| 控制模型 | 开发者控制循环 | 确定性 + 可调试 | 不适合完全自主的 Agent 场景 |

## 与知识库的映射

| Stagehand 概念 | 知识库 Plane / Pattern |
|----------------|----------------------|
| DOM Chunking + Ranking | Representation Plane — `representation-contract.md`（表示压缩策略） |
| 三原语（act/extract/observe） | Tools Plane — `tool-use.md`（最小工具 API 设计） |
| Playwright 底层执行 | Execution Plane — `execution-env.md` |
| Zod schema 结构化提取 | Representation Plane — `observation-semantics.md`（结构化输出约束） |
| DOM-first → Vision 降级 | Cost Plane — `cost-quality.md`（成本-质量权衡） |
| 开发者控制循环 | Control Plane — 人类保持循环控制权 |
| 叠加在 Playwright 之上 | Interface Plane — `platform-adapter.md`（平台适配层） |
| 混合确定性/AI 架构 | Design Space — Hybrid/Layered 架构模式 |

## 值得学习的模式

### 1. 最小 AI 原语设计

三个原语覆盖了浏览器自动化的核心需求（执行动作、提取数据、感知状态），没有多余的 API。这符合 Anthropic context engineering 中"工具设计应自包含、功能不重叠"的原则。

### 2. 叠加而非替代

不试图从零构建浏览器自动化栈，而是叠加在 Playwright 之上。这种设计让 Stagehand 能复用 Playwright 的跨浏览器支持、network interception、auth 状态管理等成熟能力，同时专注于 AI 增强。

### 3. Schema-Driven Extraction

`extract()` 使用 Zod schema 定义期望输出结构，LLM 的输出被强制拟合到 schema 中。这比自由文本提取更可靠，且支持 TypeScript 类型检查——开发者在编译时就能发现结构不匹配。

### 4. 维护成本优势

30 天选择器维护数据显示：传统 Playwright 选择器需要 15-25% 修复率，而 AI Agent 提示调整 <5%。Stagehand 的混合模式在稳定路径上使用 Playwright（零维护），在动态路径上使用 AI 原语（低维护），综合成本最低。

## 生产实践数据

| 指标 | 数据 | 来源 |
|------|------|------|
| 30 天选择器修复率（Playwright） | 15-25% | 行业基准 |
| 30 天提示调整率（AI Agent） | <5% | 行业基准 |
| Stagehand 混合模式综合维护成本 | 最低（稳定路径零维护 + 动态路径 <5%） | 推算 |

### 与同类项目的定位对比

| 维度 | Stagehand | Browser Use | Playwright（纯） |
|------|-----------|------------|-----------------|
| 控制权 | 开发者 | AI Agent | 开发者 |
| AI 介入方式 | 按需调用三原语 | 完全自主循环 | 无 AI |
| 适用团队 | Web 开发者 | AI/ML 工程师 | QA / 测试工程师 |
| 维护模型 | 选择器（稳定路径） + 提示（动态路径） | 提示工程 | 纯选择器 |
| 错误可追溯性 | 高（确定性控制流） | 中（AI 决策难审计） | 最高 |

## 局限与注意事项

| 维度 | 局限 | 影响 |
|------|------|------|
| **自主性** | 开发者必须编排控制流，不支持完全自主的 Agent 循环 | 不适合"给一个目标让 Agent 自由完成"的场景 |
| **语言限制** | TypeScript-first，Python 支持非原生 | Python 为主的 AI 团队需要适配成本 |
| **视觉能力** | DOM-first 设计在 Canvas、游戏、复杂视觉界面上需降级 | 纯视觉任务不是其强项 |
| **多步推理** | 三原语是单步操作，长链推理需要开发者自行实现 | 复杂多步任务的开发成本仍在开发者侧 |
| **Prompt Injection** | 与所有浏览器 Agent 共享此固有风险 | 不可信页面内容可能影响 AI 决策 |

**架构定位**：Stagehand 不是 Browser Use 的竞品——它们面向不同使用场景。Browser Use 面向完全自主的浏览器 Agent，Stagehand 面向需要精细控制的开发者工作流。两者代表了浏览器 AI 自动化频谱的两端：自主 vs 可控。

**架构收敛趋势**：2026 年的赢家架构是混合模式——对稳定、高频工作流使用确定性 Playwright 脚本，对动态、陌生界面使用 AI Browser Agent。Stagehand 的"AI 原语叠加在 Playwright 之上"正是多数生产团队趋近的模板。
