# Warp Agent Architecture

> **Evidence Status** — grounded. `.agents/skills/` 全部 SKILL.md 文件逆向分析、`update-skill/references/best-practices.md`、spec 流程文件。

## Skills 系统：Agent 能力的工程化管理

### Skills 是什么

Warp 的 `.agents/skills/` 目录包含 20+ 个独立 SKILL.md 文件，每个是一个**自包含的 agent 任务指令**。Skills 是结构化的工作流定义，包含前置条件、步骤、验证方式和关联 skill。

```text
.agents/skills/
├── write-product-spec/     ← 写产品 spec
├── write-tech-spec/        ← 写技术 spec
├── implement-specs/        ← 从 spec 实现代码
├── spec-driven-implementation/ ← 完整的 spec-first 工作流编排
├── review-pr/              ← PR 审查（输出 review.json）
├── review-pr-local/        ← 本地 PR 审查
├── create-pr/              ← 创建 PR
├── triage-issue-local/     ← Issue 分类（repo 特化层）
├── dedupe-issue-local/     ← Issue 去重
├── diagnose-ci-failures/   ← CI 失败诊断
├── fix-errors/             ← 错误修复
├── rust-unit-tests/        ← Rust 单元测试编写
├── warp-integration-test/  ← 集成测试编写
├── warp-ui-guidelines/     ← WarpUI 开发指南
├── add-feature-flag/       ← 添加 feature flag
├── remove-feature-flag/    ← 移除 feature flag
├── promote-feature/        ← feature 推广（dogfood → preview → release）
├── add-telemetry/          ← 遥测事件添加
├── resolve-merge-conflicts/ ← 合并冲突解决
├── update-skill/           ← skill 自身的创建/更新（元技能）
└── references/             ← 共享参考文档（best-practices.md）
```

### Skill 结构规范

每个 SKILL.md 必须包含：

```yaml
---
name: kebab-case-identifier
description: 具体描述做什么 + 什么时候用。以动词开头，第三人称。
---
```

Frontmatter 的 `description` 同时服务两个目的：
1. **发现**：agent 通过 description 决定是否加载该 skill
2. **过滤**：包含 trigger terms 帮助匹配用户意图

### 三层渐进加载

```text
Layer 1: Metadata (name + description)  → 启动时始终加载
Layer 2: SKILL.md body                  → skill 触发时加载
Layer 3: references/ 子目录             → 按需加载具体参考文件
```

**设计洞察**：这是 Progressive Disclosure 模式在 agent 知识管理中的实现。Skill 越复杂，越需要分层：

- 简单 skill（≤200 行）：全部在 SKILL.md
- 复杂 skill（>200 行）：核心工作流在 SKILL.md，详细参考在 `references/`
- 引用只做一层深度，不嵌套

### Skill 品类分析

按功能分组后，skills 覆盖了开发生命周期的全阶段：

| 阶段 | Skills | 核心能力 |
|---|---|---|
| 需求理解 | triage-issue-local, dedupe-issue-local | issue 分类、去重、信息收集 |
| 设计 | write-product-spec, write-tech-spec, spec-driven-implementation | 结构化 spec 生成和工作流编排 |
| 实现 | implement-specs, add-feature-flag, add-telemetry | 从 spec 到代码 |
| 测试 | rust-unit-tests, warp-integration-test | 单元测试和集成测试 |
| 质量 | review-pr, review-pr-local, fix-errors, diagnose-ci-failures | 代码审查、错误修复、CI 诊断 |
| 发布 | promote-feature, remove-feature-flag | feature flag 管理和渐进发布 |
| 维护 | resolve-merge-conflicts, create-pr | 冲突解决、PR 创建 |
| 元管理 | update-skill, warp-ui-guidelines | skill 自身的维护和 UI 规范 |

## Skill 设计模式提炼

### 模式 1：Spec-as-Contract

`write-product-spec` 的核心设计：

- Product spec 的 Behavior 段必须是**编号的、可测试的不变量列表**
- 不包含实现细节 — 那是 tech spec 的职责
- "用户" 不限于终端用户，可以是 API 调用方、数据模型消费方、CLI 用户
- 包含 Figma mock 检查 — 强制可视化确认
- Behavior 段覆盖：默认行为、状态转换、输入响应、空/错误/加载状态、取消、竞态、可访问性

**关键洞察**：spec 同时服务两个消费方 — 人类 reviewer 和 AI agent。编号不变量让 agent 能直接引用"不变量 7 的验证"。

### 模式 2：Review-as-Structured-Output

`review-pr` 不直接 post 到 GitHub，而是输出 `review.json`：

```json
{
  "summary": "## Overview\n...\n## Concerns\n...\n## Verdict\nFound: X critical, Y important, Z suggestions\n\n**Request changes**",
  "comments": [
    {
      "path": "path/to/file",
      "line": 42,
      "side": "RIGHT",
      "body": "⚠️ [IMPORTANT] explanation\n\n```suggestion\nreplacement\n```"
    }
  ]
}
```

评论必须以标签开头：`🚨 [CRITICAL]`、`⚠️ [IMPORTANT]`、`💡 [SUGGESTION]`、`🧹 [NIT]`。

**设计洞察**：将 review 行为和 review 发布解耦。Agent 只负责判断，不触碰 GitHub API — 发布由外层 workflow 控制。这是 Effect Ledger 模式的变体：agent 记录意图，环境执行效果。

### 模式 3：Skill Specialization（特化继承）

`triage-issue-local` 的 frontmatter 包含 `specializes: triage-issue`：

```yaml
---
name: triage-issue-local
specializes: triage-issue
description: Repo-specific triage guidance for warp-external.
---
```

特化层只覆盖父 skill 允许覆盖的字段（label taxonomy、follow-up 模式、owner hints），不重新定义 schema 或安全规则。

**设计洞察**：Skill 继承。核心 skill 定义通用逻辑，repo-specific skill 只做本地适配。这让同一个 agent 系统可以跨仓库复用。

### 模式 4：Skill 互相引用

Skills 形成有向引用图：

```text
spec-driven-implementation
├── → write-product-spec
├── → write-tech-spec
├── → implement-specs
│      ├── → rust-unit-tests
│      └── → spec-driven-implementation (circular ref for context)
└── → rust-unit-tests

implement-specs
├── → write-product-spec (前置检查)
├── → write-tech-spec (前置检查)
├── → rust-unit-tests (验证)
└── → spec-driven-implementation
```

**设计洞察**：Skills 是可组合的任务图。`spec-driven-implementation` 是编排 skill，自身不做实现，按阶段调用其他 skill。

### 模式 5：Agent 默认智能假设

`update-skill/references/best-practices.md` 明确要求：

> **Default Assumption: Agent is Already Smart.** 只添加 agent 不已经知道的上下文。挑战每段内容："agent 真的需要这个解释吗？""这段话值这些 token 吗？"

这导致 SKILL.md 极其精简 — 不解释 Git 是什么，不解释 PDF 是什么，直接给出操作步骤。

## 与知识库的关联

### 印证

- `paradigms/methodology/harness-engineering.md`：skills 是 harness 的指令层，指令是工程化的知识资产
- `architecture/planes/tools/overview.md`：skills 作为 agent 的高层工具，每个 skill 是一个"元工具"
- `design-space/patterns/progressive-disclosure.md`：三层加载是 progressive disclosure 在 agent 知识管理中的落地

### 补充

- **Skill Composition**：skills 之间的引用图是一种新的工具组合模式，不同于工具注册表
- **Skill Specialization**：`specializes` 字段实现了 skill 继承，类似 OOP 的模板方法模式
- **Review-as-Structured-Output**：agent 行为和效果发布的解耦，是 Effect Ledger 的变体
- **Spec-as-Contract**：编号不变量同时服务人类和 agent，是 representation 的双消费方设计

### 独特贡献

1. **Skill 是可审计的知识资产**：有版本、有模板、有最佳实践、有验证工具
2. **三层渐进加载**：控制 agent 上下文开销
3. **Skill 继承**：通过 `specializes` 实现跨仓库复用
4. **元 Skill**：`update-skill` 是管理 skill 的 skill，自举设计
5. **指令-效果分离**：review 输出 JSON，不直接操作 GitHub
