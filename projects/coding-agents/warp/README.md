# Warp

> **Evidence Status** — grounded. 本目录下的源码分析、`.agents/skills/` 逆向、spec 流程分析与架构拆解。

## 基本信息

- **类型**：coding-agent / agent-platform
- **项目定位**：Agentic Development Environment，既是 Rust 实现的跨平台终端模拟器，又是内置 AI coding agent 的开发平台。内置 Oz 自动化 agent 驱动 issue triage、spec 写作、代码实现和 PR review 全流程。
- **学习来源**：GitHub `warpdotdev/warp` 开源仓库，本地源码分析。
- **推荐入口**：README → agent-architecture.md → contribution-workflow.md → terminal-ai-integration.md。

## 模块覆盖

| 模块 | 覆盖程度 | 证据文件 | 可复用模式 |
|---|---|---|---|
| interface | 深 | terminal-ai-integration.md | terminal-native UI + cloud agent web viewer |
| representation | 中 | README.md | spec-as-representation: product.md + tech.md 作为需求的结构化表示 |
| context | 中 | agent-architecture.md | skill-driven context injection |
| tools | 深 | agent-architecture.md | 20+ agent skills 作为可组合工具 |
| execution | 深 | terminal-ai-integration.md | Rust 终端 + 跨平台沙箱 + Cargo workspace |
| control | 深 | contribution-workflow.md | readiness-label gating + Oz auto-review + SME escalation |
| orchestration | 深 | agent-architecture.md / contribution-workflow.md | Oz multi-phase agent pipeline (triage → spec → implement → review) |
| state | 中 | terminal-ai-integration.md | session/workspace state + SQLite persistence + Drive sync |
| world-state / effects | 深 | contribution-workflow.md | spec → code → CI → Oz review → SME review → merge 全闭环 |
| security | 中 | agent-architecture.md | feature flag gating + terminal model lock safety |
| operations | 深 | contribution-workflow.md | Oz 自动化 triage/review + changelog + presubmit |

## 核心模式

- **Spec-Driven Development**：所有 feature 必须先写 product spec + tech spec，作为代码实现的前置契约
- **Oz Agent Pipeline**：AI agent 驱动完整开发流水线：triage → label → spec review → code review → SME escalation
- **Skills as Composable Agent Instructions**：20+ 可组合 SKILL.md 文件，每个是 agent 可读取的自包含任务指令
- **Entity-Component-Handle UI**：自研 WarpUI 框架，全局 App 持有所有 view/model，通过 ViewHandle 引用
- **Feature Flag Lifecycle**：编译期 + 运行时 feature flag，从 dogfood → preview → release 渐进推出
- **Readiness-Label Gating**：通过 readiness label 控制 issue 进入 spec 和实现阶段的门槛

## 独特贡献

Warp 的独特价值不在于它是另一个 coding agent，而是它把 agent 作为**开发流程的一等参与者**，从 issue triage 到 PR merge 全链路嵌入。特别是：

1. **Agent-as-Contributor 模式**：Oz 是拥有 reviewer/implementer 角色的自动化贡献者
2. **Spec-as-Contract 模式**：product spec 的 testable behavior invariants 同时服务人类 reviewer 和 AI agent
3. **Skill System 设计**：将 agent 能力拆分为独立可组合的 skill 文件，每个 skill 有完整的指令、上下文需求和输出格式
4. **Terminal-native Agent Integration**：agent 直接运行在终端环境中，天然获得 shell 执行、文件系统和 git 能力
5. **Multi-Agent Coding Platform**：支持内置 agent 和外部 agent（Claude Code、Codex、Gemini CLI 等）在同一终端协作

## 关键发现

- Spec-driven 流程把"需求理解"从 agent 隐性推理变成显性文档，降低了实现偏差
- Skills 设计证明了"给 agent 写指令"本身需要工程化管理（版本、模板、最佳实践）
- Oz 的 multi-phase pipeline 展示了 agent 不需要一次性完成所有事，分阶段 + 门控是更可靠的选择
- Readiness label 实际上是 agent 的准入控制：不是所有任务都适合 agent 执行
- 集成测试不只是代码层面的，spec 本身就是一种"需求层面的测试用例"

## 与其他 Coding Agent 的关键差异

| 维度 | Claude Code / Codex / OpenCode | Warp |
|---|---|---|
| 定位 | CLI agent 产品 | 终端+agent 开发平台 |
| Agent 角色 | 用户的工具 | 项目的贡献者（Oz） |
| 任务入口 | 用户对话 | GitHub Issue → readiness label → spec |
| 质量保证 | 工具验证 + 人工 review | spec contract + Oz review + SME review 三重门控 |
| 技能管理 | 内置或简单 skill 文件 | 20+ 结构化 SKILL.md + 更新/审计流程 |
| 协作模型 | 单 agent + 子代理 | multi-agent platform（内置 + 外部 agent 共存） |

## 项目概述

Warp 是一个 Rust 构建的跨平台（macOS/Windows/Linux/WASM）终端模拟器，自 2021 年发展为 Agentic Development Environment。核心技术栈：

- **语言**：Rust（核心）+ TypeScript（前端集成）
- **UI 框架**：自研 WarpUI（Entity-Component-Handle，Flutter 启发的元素系统）
- **持久化**：Diesel ORM + SQLite
- **通信**：GraphQL（客户端-服务端）+ IPC
- **构建**：Cargo workspace（60+ member crates）

### 仓库结构

```text
app/                 ← 主应用（终端、AI、Drive、认证、设置、工作区）
  src/ai/            ← AI 集成（Agent Mode）
  src/terminal/      ← 终端模拟
  src/workspace/     ← 工作区管理
crates/              ← 核心库
  warpui/            ← UI 框架
  warpui_core/       ← UI 框架核心
  warp_core/         ← 核心工具与平台抽象
  editor/            ← 文本编辑
  ipc/               ← 进程间通信
  graphql/           ← GraphQL
  persistence/       ← 数据库迁移与 schema
  integration/       ← 集成测试框架
.agents/skills/      ← 20+ agent skills
specs/               ← Feature specs（product.md + tech.md）
.warp/workflows/     ← Warp 自动化工作流
```

## 架构层深度分析

| 文档 | 覆盖范围 | 核心洞察 |
|------|---------|---------|
| [agent-architecture.md](agent-architecture.md) | .agents/skills/, SKILL.md 设计, skill 更新流程 | 20+ skills 的分类体系、skill 即指令的设计模式、agent 可组合能力 |
| [contribution-workflow.md](contribution-workflow.md) | CONTRIBUTING.md, Oz pipeline, spec flow | issue → spec → implement → review 的 agent 驱动全流程 |
| [terminal-ai-integration.md](terminal-ai-integration.md) | app/, crates/, WarpUI | 终端 + AI + 自研 UI 框架的架构整合 |

## 关键代码片段

| 片段 | 源码路径 | 核心内容 |
|------|---------|---------|
| [feature-flags.snippet.md](feature-flags.snippet.md) | `crates/warp_features/src/lib.rs` (1188行) | 150+ Feature Flags、三层状态优先级、RAII 测试隔离、四阶段渐进发布 |
| [skill-system.snippet.md](skill-system.snippet.md) | `crates/ai/src/skills/` + `app/src/ai/skills/` | 10 种 Provider 兼容、ParsedSkill 解析、SkillManager 生命周期、条件激活 |
| [agent-controller.snippet.md](agent-controller.snippet.md) | `app/src/ai/blocklist/controller.rs` (2870行) + `permissions.rs` (1197行) | BlocklistAIController 编排、带原因的权限枚举、多模型路由、Orchestration 事件系统 |

## 与知识库的关联

### 印证的概念

- `paradigms/methodology/harness-engineering.md`：Warp 的 skill system 是 Harness 的指令层
- `architecture/planes/control/overview.md`：readiness-label 是 agent 准入控制的新范式
- `architecture/planes/orchestration/overview.md`：Oz 的 multi-phase pipeline 是 agent 编排的全流程实现
- `architecture/planes/effects/overview.md`：spec → code → CI → review → merge 是完整的效果验证链

### 补充的模式

- `design-space/patterns/`：Spec-Driven Development、Agent-as-Contributor、Skill Composition
- `categories/coding-agent/`：从"agent 做代码"到"agent 做全流程"的品类扩展
- `synthesis/`：coding agent 从工具走向平台的演化趋势

### 独特贡献

1. **Agent-as-Contributor**：agent 是项目的贡献者，有自己的角色和权限
2. **Spec-as-Contract**：需求文档同时服务人类和 agent，产品 spec 的 testable invariants 是 agent 的验收标准
3. **Skill Engineering**：skill 文件是有模板、审计、最佳实践的工程化产物
4. **Multi-Agent Platform**：终端作为 agent 运行平台，内置和外部 agent 共存协作
5. **Readiness-Label Gating**：不是所有任务都让 agent 做，通过 label 控制进入门槛
