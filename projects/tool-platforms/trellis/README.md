# Trellis

## 证据卡

**证明了什么**：Agent Harness 可以与 Agent 本身完全解耦。通过 breadcrumb 状态注入、registry-driven 多平台配置生成和人工 spec 策展，为 14 个 AI Coding IDE 提供统一的任务生命周期基础设施。

**核心运行时对象**：

| 对象 | 实现 | 对应 Plane |
|------|------|-----------|
| AI_TOOLS Registry | 14 平台 TemplateContext + PlatformFunctions，单一真值源 | tools |
| Breadcrumb Injector | workflow-state tag 每轮注入（no_task/planning/in_progress/completed） | state, context |
| Task Manager | task.py 16+ 子命令，task.json schema 驱动生命周期 | state, operations |
| Spec System | .trellis/spec/ 树状结构 + implement.jsonl/check.jsonl 人工策展 | context |
| Journal System | workspace/\<dev\>/journal-N.md，2000 行自动轮转 | memory |
| Migration Engine | manifests/*.json 声明式文件操作迁移 | operations |

**可复用规则**：
1. Breadcrumb per-turn 注入比一次性 session-start 更 resilient，agent 崩溃重连后仍能恢复状态
2. 人工策展 JSONL 比自动 glob 更精准（spec curation gate），减少无关文件噪声
3. 中立占位符避免多平台共享 skill 冲突（Template Placeholder Neutralization）
4. Pull-based context 让无 hook 平台也能获取上下文（Class-2 平台靠 agent definition 前缀自发现）
5. Manifest-driven migration 让版本升级声明式可追溯

**不该照搬的**：
- 14 平台适配的复杂度对单平台 agent 是过度设计
- Python + TS 双语言栈增加维护成本，单一语言栈更易维护

**关键数值**：14 平台, 3 Phase, 13 Steps, 6 workflow states, 5 shared skills, 4 sub-agent types, 16+ task.py 子命令, 2000 行 journal 轮转

---

> **Evidence Status** — grounded. 基于仓库源码分析（~12.7K TS LOC + 27 Python scripts）。

## 基本信息

- **类型**：tool-platform（Agent Harness + Multi-Platform Configurator）
- **项目定位**：为 14 个不同的 AI Coding IDE 提供统一的任务生命周期、上下文注入和工作流驱动基础设施（自身不运行 Agent）。
- **学习来源**：仓库分析与源码观察。
- **推荐入口**：README → AI_TOOLS registry → task.py → breadcrumb 注入链路。

## 模块覆盖

| 模块 | 覆盖程度 | 可复用模式 |
|------|---------|-----------|
| tools | 深 | registry-driven configurator（AI_TOOLS 单一真值源 → 14 平台配置自动生成） |
| state | 深 | breadcrumb state machine（per-turn workflow-state tag 注入） |
| context | 深 | spec injection（JSONL 人工策展 + 树状 spec 结构） |
| memory | 中 | journal rotation（2000 行自动轮转 + dev 隔离） |
| orchestration | 中 | sub-agent dispatch（hook-based vs pull-based，Codex inline vs sub-agent 可配置） |
| operations | 中 | manifest-driven migration（JSON manifest 声明式文件操作） |

## 独特贡献

Trellis 的核心创新在于将 Harness 层从 Agent 中彻底剥离。它不绑定任何单一 AI Coding Agent，而是作为**跨平台任务基础设施**存在：breadcrumb per-turn 状态注入确保 agent 始终感知当前工作流阶段；人工 spec 策展（implement.jsonl / check.jsonl）在自动化流程中插入人类判断门控；模板中立化让同一套 skill 在 14 个平台上复用而不冲突。这展示了一种 **"Harness 即产品"** 的架构范式。

## 关键发现

- **Breadcrumb 比 Session Init 更可靠**：每轮注入 workflow-state tag 意味着 agent 崩溃重连、上下文截断后仍能恢复正确状态，而一次性 session-start 注入在长会话中容易丢失。
- **Registry 即真值源**：AI_TOOLS 注册表同时定义平台能力（TemplateContext）和平台函数（PlatformFunctions），14 个 configurator 从此处自动生成，消除了配置在代码、文档、模板之间的漂移。
- **Spec Curation 是关键人类门控**：Phase 1.3 的人工策展步骤（从自动分析结果中筛选 implement/check 条目）在全自动流程中保留了人类判断，平衡了自动化效率与精准度。
- **Class-1 vs Class-2 平台分化**：有 hook 能力的平台（Class-1）通过 breadcrumb 直接注入；无 hook 的平台（Class-2）靠 agent definition 前缀实现 pull-based 自发现，架构兼容两种模式。
- **Journal 轮转解决长会话记忆膨胀**：2000 行阈值自动创建新 journal 文件，避免单文件过大导致的上下文窗口浪费和读取性能下降。
- **Manifest-Driven Migration 让升级可审计**：版本迁移用 JSON manifest 声明文件操作（创建/移动/删除），而非命令式脚本，升级路径透明可回溯。

## 架构概览

```
Trellis = Harness Infrastructure (不含 Agent 本身)

核心循环：3 Phase / 13 Step Workflow (Plan → Execute → Finish)
状态管理：Breadcrumb per-turn 注入 (no_task → planning → in_progress → completed)
工具系统：AI_TOOLS Registry → 14 平台 Configurator 自动生成
上下文：.trellis/spec/ 树状 + implement.jsonl / check.jsonl 人工策展
记忆：workspace/<dev>/journal-N.md, 2000 行轮转
子代理：Codex dispatch (sub-agent vs inline 可配置)
迁移：manifests/*.json 声明式文件操作
```

## 关键设计决策

| 决策 | 选择 | 原因 |
|------|------|------|
| 架构定位 | Harness 与 Agent 解耦 | 支持 14 个异构平台，不绑定单一 agent |
| 状态注入 | Breadcrumb per-turn | 崩溃恢复 resilient，优于一次性 session init |
| 配置生成 | Registry-driven | AI_TOOLS 单一真值源，消除多平台配置漂移 |
| Spec 策展 | 人工 JSONL 门控 | 平衡自动化效率与精准度 |
| 无 Hook 平台 | Pull-based context | Agent definition 前缀自发现，兼容 Class-2 平台 |
| 共享 Skill | 中立占位符 | 跨平台复用不冲突 |
| Journal | 2000 行轮转 | 避免长会话单文件膨胀 |
| 迁移 | JSON manifest 声明式 | 可审计、可回溯、可测试 |
| 子代理 | 可配置 dispatch | Sub-agent vs inline 按场景切换 |

## 可复用洞察

1. **Breadcrumb State Machine** — 每轮 hook 注入 workflow-state tag，比 session-level 状态更 resilient
2. **Registry-Driven Configurator** — 单一真值源生成多平台配置，消除漂移
3. **Template Placeholder Neutralization** — 中立占位符让 skill 跨平台复用
4. **Spec Curation Gate** — 自动化流程中的人工策展步骤，精准优于全自动
5. **Pull-Based Sub-Agent Context** — 无 hook 平台通过 agent definition 前缀自发现上下文
6. **Journal Rotation** — 固定行数阈值自动轮转，简单有效解决长会话记忆膨胀
7. **Manifest-Driven Migration** — 声明式文件操作让版本升级透明可追溯
8. **Harness 即产品范式** — 将 Harness 从 Agent 中剥离为独立基础设施层，支持多 Agent 接入
