# Warp Contribution Workflow: Oz-Driven Development Pipeline

> **Evidence Status** — grounded. `CONTRIBUTING.md`、`.agents/skills/` 全部 skill 文件、`specs/` 目录结构与示例 spec。

## 总览

Warp 的贡献流程是 **Oz agent 深度参与的自动化开发管线**。Oz 在 triage、spec review、code review、SME 路由等阶段都有自主决策。

## 全流程

```text
Issue 提交
    ↓
┌────────────────────────────────┐
│  Phase 1: Triage (Oz)          │
│  triage-issue-local skill      │
│  - 分类、打标签                  │
│  - 检查现有功能是否已满足         │
│  - 最多 2 个 follow-up 问题      │
│  - 区分 bug vs feature request  │
└──────────┬─────────────────────┘
           ↓
    Bug? ──→ ready-to-implement (隐含)
    Feature? ──→ ready-to-spec 标签
                    ↓
┌────────────────────────────────┐
│  Phase 2: Spec (Contributor)   │
│  write-product-spec skill      │
│  write-tech-spec skill         │
│  - PRODUCT.md: 用户行为不变量    │
│  - TECH.md: 实现计划 + 验证      │
│  - 提交 spec PR                 │
└──────────┬─────────────────────┘
           ↓
┌────────────────────────────────┐
│  Phase 3: Spec Review (Oz)     │
│  review-pr skill               │
│  - 结构化 review.json 输出      │
│  - 标签化评论                    │
│  - 验证 spec 完整性             │
└──────────┬─────────────────────┘
           ↓
    Spec approved → ready-to-implement
           ↓
┌────────────────────────────────┐
│  Phase 4: Implementation       │
│  implement-specs skill         │
│  - 从 spec 实现代码              │
│  - Spec 和代码同一 PR           │
│  - 随实现演进更新 spec            │
│  - rust-unit-tests 验证         │
│  - warp-integration-test 验证   │
└──────────┬─────────────────────┘
           ↓
┌────────────────────────────────┐
│  Phase 5: Code Review (Oz)     │
│  review-pr skill               │
│  - 自动指派 Oz 为 reviewer       │
│  - 结构化 review 输出            │
│  - /oz-review 可触发重审         │
│  - 最多 3 次 re-review          │
└──────────┬─────────────────────┘
           ↓
┌────────────────────────────────┐
│  Phase 6: SME Review           │
│  Oz 自动路由到合适的 SME          │
│  - 基于 STAKEHOLDERS 文件        │
│  - 基于 area 标签               │
│  - 无需手动指派 reviewer          │
└──────────┬─────────────────────┘
           ↓
    CI 通过 → Merge
```

## Spec 设计详解

### Product Spec (PRODUCT.md)

核心结构：

```text
Required:
  1. Summary         ← 1-3 句，特性与期望结果
  2. Behavior         ← 核心：编号的可测试不变量

Optional (仅在有价值时包含):
  - Problem           ← 动机不明显时
  - Goals / Non-goals ← 范围有争议时
  - Figma             ← 有设计稿时链接，无设计稿时显式声明 "none provided"
  - Open questions    ← 优先内联到 Behavior 旁
```

**不包含 Validation/Testing 段** — 验证计划在 TECH.md 中。

Behavior 段要求：
- 默认行为和 happy path
- 所有用户可见状态及转换
- 所有输入及响应
- 空/错误/加载/取消状态
- 边缘案例：权限拒绝、离线、超时、竞态、多实例、过期数据、焦点丢失
- 键盘、可访问性、焦点预期
- 必须持续成立的不变量

### Tech Spec (TECH.md)

核心结构：

```text
Required:
  1. Context           ← 当前系统状态 + 相关文件（含行号引用）
  2. Proposed changes   ← 实现计划：模块、类型、API、数据流、权衡
  3. Testing/validation ← 映射回 PRODUCT.md 的编号不变量

Optional:
  - End-to-end flow     ← 跨层追踪有额外价值时
  - Diagram            ← Mermaid 图（仅在比文字更清晰时）
  - Risks              ← 真实失败模式、回归、迁移
  - Parallelization    ← 可分给多个 agent 的拆分
  - Follow-ups         ← 延后清理或后续工作
```

**关键规则**：
- 先研究代码再写 spec — 不对当前架构瞎猜
- 引用 PRODUCT.md 的行为不变量，不重述
- 每个重要不变量映射到具体测试或验证步骤
- Context 段包含文件路径和行号引用

### Spec 文件组织

```text
specs/
├── APP-1234/            ← Linear ticket
│   ├── PRODUCT.md
│   └── TECH.md
├── gh-4567/             ← GitHub issue
│   ├── PRODUCT.md
│   └── TECH.md
├── GH408/               ← 历史格式
│   ├── product.md
│   └── tech.md
└── feature-name/        ← 短横线分隔的特性名
    ├── PRODUCT.md
    └── TECH.md
```

## Readiness Label 门控

```text
┌─────────────┐     ┌──────────────┐     ┌───────────────────┐
│ Issue 提交    │ ──→ │ Warp 团队审核  │ ──→ │ 标签分配           │
└─────────────┘     └──────────────┘     └─────┬─────┬───────┘
                                               │     │
                                               ↓     ↓
                                    ready-to-spec   ready-to-implement
                                    (需要先写 spec)  (可以直接实现)
                                               │     
                                               ↓     
                                        needs-mocks
                                        (等设计稿)
```

**关键规则**：
- Readiness label 不是 assignment — 任何人可以认领
- Bug 无需等标签 — triage 后隐含 `ready-to-implement`
- Feature 必须走 spec 流程
- `needs-mocks` 阻塞实现直到设计完成
- 可 mention `@oss-maintainers` 请求标签评估

## Oz Agent 行为分析

### Triage 行为

`triage-issue-local` 定义了 Oz 的 triage 规则：

1. **最多 2 个 follow-up 问题** — 每个必须高价值，能改变标签或路由
2. **先检查再问** — 看日志/截图/已有功能，不问已知信息
3. **区分用户观察和用户猜测** — Warp 行为 vs 用户推测的内部原因
4. **环境信息检查清单** — channel/version、OS、shell、visual evidence、logs
5. **计费/申诉不处理** — 直接导向 support channel
6. **特化继承** — 基于核心 triage skill 做 repo-specific 适配

### Review 行为

`review-pr` 定义了 Oz 的 review 规则：

1. **结构化输出** — review.json，不直接 post GitHub
2. **优先级排序** — correctness > security > error handling > performance > style
3. **V0 宽容** — 初始实现的健壮性建议标记为"可选后续"，不阻塞
4. **NIT 门槛** — 只有附带 suggestion block 的 NIT 才输出
5. **不触碰 GitHub** — 不运行 `gh pr review`、`gh pr comment`、`gh api`
6. **可重触发** — `/oz-review` 评论触发重审，最多 3 次

### Deduplication 行为

`dedupe-issue-local` 处理重复 issue 检测。

### CI 诊断行为

`diagnose-ci-failures` 分析 CI 失败原因并提供修复建议。

## 多 Agent 协作模型

Warp 的架构支持多个 agent 在同一仓库协作：

```text
┌──────────────────────────────────────────┐
│              Warp Terminal               │
│                                          │
│  ┌────────────┐  ┌────────────┐          │
│  │ Oz (内置)   │  │ Claude Code │          │
│  │ 自动 triage │  │ 手动实现    │          │
│  │ 自动 review │  │            │          │
│  └──────┬─────┘  └──────┬─────┘          │
│         │               │                │
│         ▼               ▼                │
│  ┌──────────────────────────────┐        │
│  │  共享上下文                    │        │
│  │  WARP.md │ specs/ │ .agents/ │        │
│  └──────────────────────────────┘        │
└──────────────────────────────────────────┘
```

**关键设计**：
- `WARP.md` 是所有 agent 共读的工程指南
- `.agents/skills/` 是 agent 可组合的能力库
- `specs/` 是 agent 实现的契约来源
- 任何 agent harness（支持 SKILL.md 格式）都可以使用这些 skills

## Warp 自动化工作流

`.warp/workflows/` 包含 YAML 定义的自动化流程：

| 工作流 | 功能 |
|---|---|
| `start_new_task.yaml` | 开始新任务 |
| `run_unit_test.yaml` | 运行单元测试 |
| `run_integration_test.yaml` | 运行集成测试 |
| `create_feature_release_pr.yaml` | 创建发布 PR |
| `cherrypick_into_release.yaml` | Cherry-pick 到发布分支 |
| `run_warp_with_shell.yaml` | 用指定 shell 运行 Warp |
| `run_warp_with_version_and_channel.yaml` | 用指定版本/channel 运行 |
| `build_image_and_start_container_for_ssh_testing.yaml` | SSH 测试容器构建 |

## 与知识库的关联

### 印证

- `architecture/planes/control/overview.md`：Readiness label = 准入控制 gate
- `architecture/planes/effects/overview.md`：spec → code → CI → review → merge = 完整效果链
- `architecture/planes/orchestration/overview.md`：Oz 的 multi-phase pipeline = 多阶段 agent 编排

### 补充

- **Agent-as-Contributor**：agent 是有 role/permission 的项目贡献者
- **Spec-as-Contract**：spec 的编号不变量同时服务人类 reviewer 和 AI agent
- **Review-Triggered Escalation**：Oz review → SME review 的自动升级链

### 独特贡献

1. **完整的 agent-driven 开发管线**：从 issue 到 merge 的全自动化
2. **Readiness label 门控**：不是所有任务都适合 agent，label 控制进入门槛
3. **Review 行为约束**：优先级排序、V0 宽容、NIT 门槛、重审次数限制
4. **Multi-agent 协作**：内置 Oz + 外部 agent 共享同一套上下文资产
5. **Spec 和代码同 PR**：减少 spec 与实现的漂移
