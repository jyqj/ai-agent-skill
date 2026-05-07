# 端到端构建指南：Coding Agent

> **Evidence Status** — synthesized. 基于 Claude Code、Codex、OpenCode、Augment 架构分析，结合知识库方法论整合。

## 目标

从零设计一个 Coding Agent，使其能够在真实代码库中完成可验证的软件工程任务：定位问题 → 理解代码库 → 设计修改 → 执行 edit → 运行验证 → 修复失败 → 交付 diff + 证据 + 风险。

本指南以这个目标为线索，逐步演示如何使用知识库中的方法论完成设计。每一步都交叉引用具体文件路径，方便你回到知识库深入阅读。

---

## Step 1: 用户任务定义

> 参考：`design-space/methodology/agent-product-model.md`（产品画布）、`categories/coding-agent/task-model.md`（任务模型）

### 1.1 产品画布

在动手设计任何模块之前，先回答产品画布中的核心问题。以下是 Coding Agent 的填写示例：

| 字段 | Coding Agent 答案 |
|---|---|
| Target User | 开发者（Solo/Team/Platform） |
| User Job | 在真实代码库中完成可验证的软件工程任务 |
| Entry Point | CLI / IDE 插件 / PR Comment |
| Deliverable | diff + 测试通过证据 + 风险说明 |
| World Objects | 文件、目录、Git 状态、测试结果、CI 状态、依赖 |
| Observable Inputs | 用户指令、代码库内容、测试输出、lint 结果 |
| Representation Contract | RepoSnapshot, FileRef, SymbolRef, TestResult, GitState, DiffArtifact |
| Intended Effects | 代码修改正确、测试通过、无回归 |
| Verification | test pass + lint clean + diff reviewable + CI green |

### 1.2 定义 JTBD（Jobs to be Done）

Coding Agent 的核心 job 不是"写代码"，而是：

```text
理解用户意图 → 定位相关代码
→ 理解代码库上下文和约定
→ 设计修改方案
→ 执行精确编辑
→ 运行验证（test / lint / typecheck）
→ 修复验证失败
→ 交付 diff + 通过证据 + 风险说明
```

核心挑战："代码编译通过不等于功能正确。测试通过不等于没有回归。diff 能用不等于 diff 可维护。"

### 1.3 任务类型

根据 `categories/coding-agent/task-model.md`，Coding Agent 覆盖六种核心任务类型：

| 任务类型 | 典型输入 | 默认深度 | 完成定义 |
|---|---|---|---|
| Bug fix | "这个函数在 X 条件下返回错误结果" | D4-D5 | diff + 相关测试通过 + bug 复现/修复证据 |
| Feature | "实现一个新的 API endpoint" | D4-D5 | diff + 新/改测试 + 用户验收点 |
| Refactor | "把这个模块拆分为独立服务" | D4 | 行为等价证明 + 测试通过 + diff 可审查 |
| Code review | "review 这个 PR 的安全问题" | D2-D4 | 问题清单 + 证据引用 + 可选 patch |
| Migration | "将数据库从 MySQL 迁移到 PostgreSQL" | D5 | checkpoint + 分阶段 diff + 回滚/恢复策略 |
| Test generation | "为这个模块补充单元测试" | D4 | 测试覆盖目标 + 测试可运行 + 失败原因解释 |

**设计决策**：MVA-1 阶段只支持 Bug fix 和 Feature 两种任务类型，降低首版复杂度。

### 1.4 TaskEnvelope 示例

为任务类型定义结构化输入，确保 Agent 收到的不是模糊文本，而是有明确 scope 和约束的任务信封：

```yaml
task_envelope:
  task_type: bug_fix
  description: "用户上传文件超过 10MB 时，API 返回 500 而不是 413"
  repo:
    path: "/workspace/my-service"
    branch: "main"
    language: "python"
    framework: "fastapi"
  scope:
    files_hint: ["src/api/upload.py", "src/middleware/size_limit.py"]
    test_command: "pytest tests/api/test_upload.py -v"
    lint_command: "ruff check src/"
  success_criteria:
    - 上传超过 10MB 的文件返回 413 状态码
    - 上传不超过 10MB 的文件行为不变
    - 相关测试通过
    - lint 无新增 warning
  constraints:
    - 不修改无关文件
    - 不引入新依赖
    - 保持现有 API 兼容
  budget:
    max_tool_calls: 100
    max_edit_cycles: 10
  output_contract:
    format: diff
    includes: [diff, test_results, risk_notes]
```

---

## Step 2: 自治等级和执行深度

> 参考：`design-space/methodology/autonomy-and-depth.md`（自治等级 + 执行深度）、`design-space/methodology/minimum-viable-agent.md`（MVA 阶梯）

### 2.1 动作风险分析表

Coding Agent 的动作按风险分级：

| 动作 | 风险 | 可逆性 | 建议自治等级 |
|---|---|---|---|
| Read（文件、搜索、git status） | 低 | 只读 | L4 — 自动执行 |
| Edit（str_replace 修改文件） | 中 | 可逆（git checkout） | L4 — bounded autonomy |
| Create / Delete 文件 | 中 | 可逆（git checkout） | L4 — check |
| Shell（运行测试、lint） | 中-高 | 取决于命令 | L3-L4 — 安全命令自动，危险命令需确认 |
| Git commit | 中 | 可逆（reset） | L4 — check |
| Git push | 高 | 不可逆 | L3 — 需审批 |
| Deploy | 高 | 不可逆 | L2-L3 — 需审批 |

**设计决策**：Coding Agent 默认 **L3-L4**。Read/Edit 在工作区内自动执行（L4），Shell 执行安全命令（test、lint）自动执行，危险命令需确认。Git push / Deploy 需要用户审批（L3）。

### 2.2 默认选择

| 维度 | 选择 | 理由 |
|---|---|---|
| 自治等级 | L3-L4 | Read/Edit 自动，Shell/Git push 需确认 |
| 执行深度 | D4-D5 | 执行 + 验证 + 修复 |
| 复杂度 | C3-C4 | 需要 postcondition 验证 + 异常恢复 |

### 2.3 MVA 阶梯

根据 `design-space/methodology/minimum-viable-agent.md`，Coding Agent 的起步和目标：

| 阶梯 | 能力 | Coding Agent 对应 |
|---|---|---|
| MVA-2 Tool-assisted | 能读写文件 | 起步——能搜索、读取、编辑文件 |
| MVA-3 Verified | 能运行测试验证 | 目标——编辑后自动运行测试确认 |
| MVA-4 Stateful | 可恢复长任务 | 进阶——Migration、大型 Refactor |

**设计决策**：MVA-2 起步（Tool-assisted，能读写文件），目标 MVA-3（Verified，能运行测试验证），渐进升级到 MVA-4（可恢复长任务）。

---

## Step 3: 范式选择

> 参考：`paradigms/decision-trees.md`（范式决策树）、`paradigms/reasoning-paradigms.md`、`paradigms/memory-paradigms.md`、`paradigms/tool-paradigms.md`、`paradigms/control-paradigms.md`、`paradigms/collaboration-paradigms.md`

使用决策树逐一选择五类范式：

### 3.1 推理范式

```text
任务只需要解释/总结吗？
  └─ 否 → 需要外部交互吗？
       └─ 是，工具结果会改变下一步 → ReAct

任务可预先拆成稳定步骤吗？
  └─ 部分可以（bug fix 可先搜索再修复）→ 大型重构可升级为 Plan-and-Execute
```

**选择**：**ReAct**（代码库探索需要动态观察-行动循环）。每次 Read/Grep/Bash 的结果决定下一步行动——搜索发现了什么文件、测试失败了哪一行、lint 报了什么错误。大型重构（Migration、Feature）可升级为 **Plan-and-Execute + ReAct** 混合。

### 3.2 记忆范式

```text
信息只在当前任务有效吗？
  └─ 大部分是 → Context / TaskState

是否需要跨任务持久化？
  └─ 项目约定需要 → Convention Discovery（CLAUDE.md / AGENTS.md / README 自动发现）
```

**选择**：**Context + Convention Discovery**。当前任务的编辑历史、测试结果放在 Context。项目约定（CLAUDE.md / AGENTS.md / README / package.json / tsconfig 等）自动发现并加载为高优先级上下文。MVA-3+ 加入 TaskState checkpoint 支持长任务恢复。

Convention Discovery 是 Coding Agent 最独特的记忆范式——项目本身就是 Agent 的"记忆"：

```text
Convention Sources（按优先级排序）:
1. CLAUDE.md / AGENTS.md — 显式写给 Agent 的指令
2. .editorconfig / .prettierrc / tsconfig.json — 代码风格约定
3. package.json / pyproject.toml / Cargo.toml — 依赖和脚本
4. README.md — 项目结构和开发指南
5. 已有代码模式 — 隐式约定（命名规则、错误处理风格、测试模式）
```

### 3.3 工具范式

```text
工具动作是否高风险或外部写入？
  └─ 部分是（Edit 改文件、Shell 有副作用）→ 需要 risk 分级

工具集是否固定？
  └─ 是，7 个核心工具足够覆盖所有场景 → Atomic Tool
```

**选择**：**Atomic Tool**。7 个核心工具：

| 工具 | 用途 | 风险 |
|---|---|---|
| Read | 读取文件内容 | safe |
| Edit | str_replace 修改文件 | check |
| Write | 创建新文件 | check |
| Glob | 文件路径搜索 | safe |
| Grep | 文件内容搜索 | safe |
| Bash | 终端命令（test/lint/build/git） | check/approval |
| Git | 版本控制操作 | check/approval |

**文件编辑策略决策树**：

```text
需要精确替换已有代码吗？
├─ 是 → str_replace（Claude Code 方式，最普及）
│   └─ 要求：old_string 在文件中唯一匹配
│   └─ 优势：最直观，无 diff 格式错误风险
│   └─ 劣势：大范围修改需要多次调用
│
├─ 需要批量修改多处吗？
│   └─ unified diff（Aider 方式）
│   └─ 优势：单次调用可改多处
│   └─ 劣势：diff 格式对 LLM 有挑战，行号偏移易出错
│
└─ 是否在 OpenAI 生态？
    └─ apply_patch（OpenAI GPT-5.1 方式）
    └─ 优势：patch 语义清晰
    └─ 劣势：生态限制
```

### 3.4 协作范式

```text
单 Agent 能在上下文和时间预算内完成吗？
  └─ 大部分可以 → Single Agent + Tools

任务是否需要并行探索多个方向？
  └─ 大型 Feature / Migration → Orchestrator-Explorer-Coder 三角色分工
```

**选择**：**Single Agent**（MVA-1-3）。进阶可升级为多 Agent 协作。

**进阶：三角色分工模式**

"三个专注 Agent 持续优于一个通才 Agent 工作三倍时间。"——这一观察在 Claude Code 子代理和 Augment Intent 中得到验证。

```text
Orchestrator（编排者）
  ├─ 理解任务全貌，分解为子任务
  ├─ 分配给 Explorer 和 Coder
  └─ 合并结果，检查一致性

Explorer（探索者）
  ├─ 搜索代码库，理解架构
  ├─ 收集上下文（依赖图、调用链、测试模式）
  └─ 输出 context brief 给 Coder

Coder（执行者）
  ├─ 接收 context brief + 修改指令
  ├─ 执行编辑 + 运行验证
  └─ 输出 diff + 测试结果
```

**Augment Intent 模式**（生产验证）：

```text
Coordinator
  → 最多 6 个并行 Implementor（各自在独立 Git Worktree 中工作）
  → Verifier（汇总验证）
  → Living Specification（共享的需求文档，随实现同步更新）
  → Git Worktree 隔离（并行不冲突）
```

### 3.5 控制范式

```text
动作会改变外部世界吗？
  └─ 是（编辑文件、运行命令、git 操作）→ 需要多层控制

规则能确定判定吗？
  └─ 大部分可以 → Permission Tree + Hook + Sandbox
```

**选择**：**Rule（Permission Tree）+ Hook（Edit Guard）+ Sandbox（容器隔离）**。三层控制组合：

**Permission Tree**（deny > ask > allow）：

```yaml
permission_tree:
  deny:
    - "rm -rf /"
    - "git push --force"
    - "DROP TABLE"
    - secret/credential 操作
  ask:
    - git push
    - git commit --amend
    - 新增外部依赖
    - 删除文件
    - deploy 相关命令
  allow:
    - read / search / glob / grep
    - edit（在工作区内）
    - test / lint / typecheck / build
    - git status / diff / log
```

**Hook（Edit Guard）**：

```text
连续编辑同一文件 3 次 → 警告："编辑未收敛，请检查修改逻辑"
连续编辑同一文件 5 次 → 阻止："多次编辑失败，请重新理解问题后再修改"
```

这一机制来自 Claude Code 的 Hook 系统，用于检测 Agent 陷入"编辑-测试-再编辑"的死循环（doom loop）。

**Sandbox（容器隔离）**：

```text
低风险（只读分析）→ 进程隔离
中风险（文件编辑）→ Docker + 限制挂载
高风险（Shell 执行）→ Firecracker microVM / gVisor
极高风险（生产操作）→ 完全隔离 VM + 审批
```

### 3.6 范式选择输出

```yaml
paradigm_selection:
  reasoning: react  # 大型重构升级为 plan_execute + react
  memory: context + convention_discovery
  tools: atomic  # 7 核心工具
  collaboration: single  # 进阶升级 orchestrator-explorer-coder
  control: permission_tree + hook + sandbox
  complexity_level: C3-C4
  required_planes:
    - representation
    - context
    - tools
    - control
    - interaction
  recommended_planes:
    - effects  # test 验证
    - recovery  # 编辑失败回滚
    - cost  # token 预算
    - observability  # trace
  optional_planes:
    - state  # checkpoint（MVA-3+）
    - memory  # 项目约定记忆（MVA-3+）
  stop_gates:
    - diff_matches_intent
    - tests_pass_or_explained
    - git_state_verified
    - risks_documented
  eval_fixtures:
    - coding_bug_fix_with_test
    - coding_refactor_no_regression
    - coding_context_rot_long_task
```

---

## Step 4: 品类架构实例化

> 参考：`categories/coding-agent/README.md`（品类模板）、`categories/coding-agent/closed-loop.md`（闭环模型）、`../ARCHITECTURE.md`（plane 总览）

### 4.1 Plane 配置

根据 Step 3 的范式选择，确认需要哪些 plane：

| Plane | 是否需要 | MVA-2 | MVA-3 | 理由 |
|---|---|---|---|---|
| Representation | 必须 | FileRef + SearchHit | + SymbolRef + DependencyGraph | 核心——理解代码库 |
| Context | 必须 | 文件 + 搜索结果 | + convention discovery + compaction | 防止上下文溢出 |
| Tools | 必须 | read + edit + grep + bash | + glob + write + git | 核心操作能力 |
| Control | 必须 | permission tree | + hook + sandbox | 安全边界 |
| Interaction | 必须 | 基础进度 | + 澄清 + partial delivery | 用户信任 |
| Effects | 推荐 | test pass/fail | + lint + typecheck + diff review | 验证闭环 |
| Recovery | 推荐 | git checkout 回滚 | + edit-guard + retry budget | 编辑失败恢复 |
| Cost | 推荐 | tool call budget | + token budget + compaction | 防止发散 |
| Observability | 推荐 | 基础 trace | + tool call 审计 + 失败分析 | 调试和改进 |
| State | 可选（MVA-3+） | 否 | checkpoint + progress | 长任务恢复 |
| Memory | 可选（MVA-3+） | 否 | 项目约定 + 成功命令 | 跨任务积累 |
| World State | 可选（MVA-3+） | 否 | branch + CI 状态刷新 | 多人协作场景 |

### 4.2 闭环模型

从 `categories/coding-agent/closed-loop.md` 出发，实例化 Coding Agent 的执行循环：

```text
1. Observe  ← 接收用户任务 + 读取 repo 状态（git status、branch、已有测试）
2. Represent← 加载项目约定（CLAUDE.md、README、build config）+ 搜索相关文件
3. Decide   ← 制定修改方案 + 风险评估 + 验证策略
4. Act      ← 执行编辑（str_replace / write）+ 运行验证（test / lint / typecheck）
5. Verify   ← 检查测试结果、lint 输出、diff 正确性
6. Update   ← 修复失败 → 继续 / 重试 / 升级 / 交付
```

每一轮 Observe-Decide-Act-Verify 都是一个 ReAct micro-loop。与 Research Agent 的 Plan-Execute 不同，Coding Agent 的每次编辑结果（测试是否通过、lint 是否报错）都会改变下一步决策。

### 4.3 Stop Gate

从 `categories/coding-agent/closed-loop.md` 直接使用：

```text
[ ] diff 与任务目标一致
[ ] 相关测试 / lint / typecheck 已运行，或明确说明为何无法运行
[ ] git status / diff 已回读
[ ] 未完成风险和用户需知事项已列出
[ ] 高风险动作未越过审批边界
```

---

## Step 5: 模块深入设计

> 参考：`categories/coding-agent/representation.md`（表示模型）、`categories/coding-agent/action-model.md`（行动模型）、`categories/coding-agent/design-decisions.md`（设计决策）、`architecture/planes/tools/overview.md`（工具层）、`architecture/planes/context/overview.md`（上下文管理）、`architecture/planes/control/overview.md`（控制层）、`architecture/planes/effects/overview.md`（效果验证）

### 5.1 工具集设计

7 个核心工具的完整 schema：

**Read — 读取文件内容**

```yaml
- name: Read
  description: 读取指定文件的内容，支持行号范围
  parameters:
    file_path: { type: string, required: true, description: "绝对路径" }
    offset: { type: integer, optional: true, description: "起始行号" }
    limit: { type: integer, optional: true, description: "读取行数" }
  risk_level: safe
  preconditions: 文件存在
  postconditions: 返回文件内容（带行号）
  verification_method: none（只读）
```

**Edit — 精确替换文件内容**

```yaml
- name: Edit
  description: 使用 str_replace 精确替换文件中的代码段
  parameters:
    file_path: { type: string, required: true }
    old_string: { type: string, required: true, description: "要替换的原始文本，必须唯一匹配" }
    new_string: { type: string, required: true, description: "替换后的新文本" }
  risk_level: check
  preconditions:
    - 文件已读取（必须先 Read 再 Edit）
    - old_string 在文件中存在且唯一
  postconditions: old_string 已被 new_string 替换
  verification_method: Read 回读确认 + git diff
```

**Write — 创建新文件**

```yaml
- name: Write
  description: 创建新文件或完整覆写已有文件
  parameters:
    file_path: { type: string, required: true }
    content: { type: string, required: true }
  risk_level: check
  preconditions: 如果文件已存在，必须先 Read
  postconditions: 文件内容与 content 一致
  verification_method: Read 回读确认
```

**Glob — 文件路径搜索**

```yaml
- name: Glob
  description: 按 glob 模式搜索文件路径
  parameters:
    pattern: { type: string, required: true, description: "glob 模式，如 **/*.py" }
  risk_level: safe
  preconditions: none
  postconditions: 返回匹配的文件路径列表
  verification_method: none（只读）
```

**Grep — 文件内容搜索**

```yaml
- name: Grep
  description: 在文件中搜索匹配的文本或正则表达式
  parameters:
    pattern: { type: string, required: true }
    path: { type: string, optional: true, description: "搜索范围" }
    include: { type: string, optional: true, description: "文件类型过滤" }
  risk_level: safe
  preconditions: none
  postconditions: 返回匹配行及上下文
  verification_method: none（只读）
```

**Bash — 终端命令执行**

```yaml
- name: Bash
  description: 在终端执行命令（测试、lint、build、git 等）
  parameters:
    command: { type: string, required: true }
    timeout: { type: integer, optional: true, default: 120 }
  risk_level: check/approval（取决于命令内容）
  preconditions: 命令在 permission tree 允许范围内
  postconditions: 返回 stdout + stderr + exit_code
  verification_method: exit_code 检查 + 输出解析
```

**Git — 版本控制操作**

```yaml
- name: Git
  description: 执行 git 操作（status, diff, commit, push 等）
  parameters:
    subcommand: { type: string, required: true }
    args: { type: array, optional: true }
  risk_level: check（status/diff/log）/ approval（push/force）
  preconditions: 当前目录是 git 仓库
  postconditions: git 状态已更新
  verification_method: git status / git diff 回读
```

### 5.2 文件编辑策略

**str_replace 详解**

str_replace 是当前最普及的 Coding Agent 编辑策略（Claude Code、OpenCode 均采用）。核心约束：

```text
old_string 必须在目标文件中唯一匹配。
如果匹配到 0 次 → 报错，提示内容不存在
如果匹配到 2+ 次 → 报错，提示需要更多上下文使 old_string 唯一
```

这个"唯一匹配"约束是安全网——防止 Agent 误改了错误位置的代码。

**安全机制**：

| 机制 | 目的 | 实现 |
|---|---|---|
| Edit Guard Hook | 检测编辑死循环 | 连续编辑同一文件 3 次警告，5 次阻止 |
| 行数变更验证 | 检测意外大量删除 | 编辑后行数变化超过阈值触发确认 |
| Lost-in-the-middle 检测 | 防止长文件中间部分被忽略 | 编辑前后 checksum 比对，确认非目标区域未变 |
| Read-after-Write | 确认编辑结果 | 每次 Edit 后自动 Read 回读验证 |

**Rollback**：

Git 是 Coding Agent 的天然安全网。所有修改都是 unstaged diff，随时可以 `git checkout -- <file>` 回滚。这一特性使得 Coding Agent 的 Edit 操作在所有 Agent 品类中风险相对较低——只要不 commit + push，一切都可以撤销。

### 5.3 上下文工程

上下文工程是 Coding Agent 的最高杠杆优化。Anthropic 官方五层结构：

**Layer 1: System Prompt（始终加载）**

```text
角色定义、行为规则、工具描述、输出格式。
大小：~2000 token
生命周期：整个会话不变
```

**Layer 2: CLAUDE.md / AGENTS.md（项目约定，高杠杆上下文）**

```text
项目特定的编码规范、测试命令、架构约束、禁止操作。
大小：~500-2000 token
生命周期：整个会话不变
杠杆效应：一条 "运行测试用 pytest -x" 比 Agent 自己试 10 次更高效
```

这是 Coding Agent 最独特的上下文来源。项目约定文件是"给 Agent 写的 README"——成本极低，回报极高。

**Layer 3: Convention Discovery（自动发现项目约定）**

```text
自动读取：README.md, package.json, tsconfig.json, pyproject.toml, .editorconfig, .prettierrc, Makefile
提取信息：语言、框架、测试命令、lint 配置、目录结构
大小：~1000-3000 token
生命周期：任务开始时加载一次
```

**Layer 4: Task Context（当前任务相关文件，Just-in-Time 加载）**

```text
根据任务需要按需加载：搜索命中的文件、测试文件、被修改的文件。
大小：动态
生命周期：随任务推进增长，需要 compaction
原则：先搜索再读取，不要一次性加载整个代码库
```

**Layer 5: Tool Output（临时，用完可压缩）**

```text
测试输出、lint 结果、bash 命令输出。
大小：可能很大（测试输出 100+ 行）
生命周期：用完即压缩为摘要
压缩策略：保留 exit_code + 失败行 + 关键错误信息，丢弃冗余输出
```

**Compaction 策略**：

```text
触发条件：上下文使用率 > 80% 时触发压缩
保留优先级：
  1. System prompt + CLAUDE.md（不可压缩）
  2. 最近 5 个文件的内容（高频引用）
  3. 决策和修改理由
  4. 当前 diff 摘要
压缩目标：
  - 早期搜索结果 → 压缩为 "搜索了 X，发现 Y 在 file:line"
  - 大段工具输出 → 压缩为 exit_code + 失败信息
  - 已完成的子任务 → 压缩为一句话总结
```

参考数据：有效压缩可减少约 80% Token 消耗。上下文缓存（Context Caching）可减少 75-90% 重复上下文成本——System Prompt + CLAUDE.md + Convention 在同项目的多次调用中完全相同，天然适合缓存。

### 5.4 沙箱设计

Coding Agent 执行 Shell 命令是其最强大也最危险的能力。沙箱决策树：

```text
低风险（只读分析）
  └─ 进程隔离
  └─ 示例：grep, find, cat, git status, git log
  └─ 措施：超时限制 + 输出截断

中风险（文件编辑）
  └─ Docker + 限制挂载
  └─ 示例：编辑工作区文件、运行测试
  └─ 措施：只读挂载非工作区目录、网络限制

高风险（Shell 执行）
  └─ Firecracker microVM / gVisor
  └─ 示例：安装依赖、运行 build 脚本、执行用户提供的命令
  └─ 措施：独立文件系统、CPU/内存限制、网络白名单

极高风险（生产操作）
  └─ 完全隔离 VM + 审批
  └─ 示例：数据库 migration、deploy、secret 操作
  └─ 措施：人工审批 + 审计日志 + 回滚计划
```

**参考实现对比**：

| 实现 | 沙箱方案 | 特点 |
|---|---|---|
| Claude Code | 本地进程 + permission tree + hook | 信任用户环境，用规则控制 |
| Codex（OpenAI） | Firecracker microVM | 完全隔离，每次任务一个 VM |
| Augment | Docker + Git Worktree | 容器隔离 + 分支隔离 |

参考数据：45% AI 生成代码未通过安全测试（Veracode 2025）。这意味着沙箱不仅保护用户环境，也保护 Agent 生成的代码不被自身的其他操作破坏。

### 5.5 验证闭环

Coding Agent 的验证不是单一层次，而是五层递进：

**Layer 1: Structural — diff 语法正确**

```text
验证方法：git diff --check（检查冲突标记、trailing whitespace）
自动化：完全自动
失败处理：重新编辑
```

**Layer 2: Execution — test pass + lint clean + typecheck pass**

```text
验证方法：运行项目配置的测试、lint、typecheck 命令
自动化：完全自动
失败处理：分析失败原因 → 修复 → 重新验证（最多 N 轮）
注意区分"我引入的失败"和"之前就有的失败"
```

**Layer 3: Effect — 代码行为正确（不只是测试通过）**

```text
验证方法：阅读 diff，确认修改逻辑与任务意图一致
自动化：LLM self-review（Agent 回读自己的 diff）
失败处理：发现逻辑偏差 → 修正
测试可能覆盖不全，通过不等于正确
```

**Layer 4: Claim — Agent 说的和实际做的一致**

```text
验证方法：比对 Agent 声称的修改和实际 diff
自动化：规则检查（声称修改了 3 个文件，实际 diff 确认）
失败处理：不一致时标记警告
防止 Agent 声称修复了但实际没改
```

**Layer 5: Human — diff reviewable + 风险说明清晰**

```text
验证方法：人工 review
自动化：Agent 生成 review 辅助信息（修改摘要、风险说明、测试覆盖说明）
diff 要小、聚焦、可解释
```

**验证流程**：

```text
Edit Complete
  → Layer 1: git diff --check
    ├─ PASS → Layer 2: test + lint + typecheck
    │         ├─ PASS → Layer 3: LLM self-review
    │         │         ├─ PASS → Layer 4: claim verification
    │         │         │         ├─ PASS → Layer 5: 准备 human review 材料
    │         │         │         │         └─ DELIVER
    │         │         │         └─ WARN → 标记不一致 → DELIVER with warning
    │         │         └─ ISSUE → 修正逻辑 → 返回 Edit
    │         └─ FAIL → 分析失败 → 修复 → 返回 Layer 1（最多 N 轮）
    └─ FAIL → 修正 diff 格式 → 返回 Edit
```

### 5.6 长时运行 Harness

大型任务（Migration、复杂 Feature）可能超过单次会话的上下文窗口。Anthropic 的 Claude Code 在 SWE-bench 和长任务场景中采用的模式：

**Initializer Agent**：

```text
职责：首次运行设置环境
  1. 读取任务描述和代码库
  2. 展开 prompt 为 feature-list.json（子任务列表）
  3. 生成 init.sh（环境准备脚本）
  4. 确认环境就绪
输出：feature-list.json + init.sh + 环境验证结果
```

**Coding Agent（增量会话）**：

```text
每次会话的流程：
  1. 读取 claude-progress.txt（之前的进度）
  2. 读取 feature-list.json（剩余子任务）
  3. 选择下一个子任务
  4. 执行：编辑 → 测试 → 修复
  5. 更新 claude-progress.txt
  6. git commit（保存进度）
```

**跨会话持久化**：

```text
持久化介质：
  - claude-progress.txt — 人类可读的进度说明
  - feature-list.json — 结构化子任务列表
  - git commit history — 每个子任务一个 commit

恢复流程：
  1. 读取 progress 文件 → 知道做到哪了
  2. git log → 确认已完成的提交
  3. 运行测试 → 确认之前的工作仍然有效
  4. 继续下一个子任务
```

这种模式的优势：不需要复杂的状态管理系统——Git 本身就是最好的 checkpoint 机制，progress 文件是最简单的跨会话记忆。

---

## Step 6: 评估接入

> 参考：`evaluation/eval-framework.md`（评估框架）、`evaluation/fixtures/README.md`（fixture 编写原则）、`categories/coding-agent/eval-cases.md`（评估用例）

### 6.1 SWE-bench

SWE-bench 是 Coding Agent 领域的标准 benchmark：

| 变体 | 规模 | 特点 | 当前 SOTA |
|---|---|---|---|
| SWE-bench Full | 2294 题 | 从 12 个真实 Python 仓库抽取 | — |
| SWE-bench Verified | 500 题 | 人工验证子集，减少噪音 | 87.6%（Claude Opus 4.7） |
| SWE-bench Lite | 300 题 | 轻量子集 | — |

警告（METR 2025 研究）：

```text
约一半通过 SWE-bench 自动评分的 PR 不会被维护者合并。
自动评分比人工评估平均高 24 个百分点。
原因：
  - 测试覆盖不全（patch 绕过了测试但没真正修复）
  - 代码质量不达标（能用但不可维护）
  - 引入了测试未覆盖的回归
```

这意味着 SWE-bench 分数是必要但不充分的验证。生产 Coding Agent 需要额外的质量指标。

### 6.2 四个生产指标

| 指标 | 含义 | 目标 |
|---|---|---|
| 任务完成率 | 用户接受 Agent 交付结果的比例 | > 70%（简单任务），> 40%（复杂任务） |
| 回归引入率 | Agent 修改导致的新失败比例 | < 5% |
| 审查循环次数 | 用户 review 后需要修改的轮次 | < 2 轮 |
| 失败影响半径 | Agent 失败时影响的文件/模块数量 | 最小化（< 3 文件） |

### 6.3 知识库 Fixture

根据 `evaluation/fixtures/README.md` 的原则，Coding Agent 的核心 fixture：

**Fixture 1: Bug Fix with Test**

```yaml
case_id: coding_bug_fix_with_test
product_type: coding_agent
evidence_status: synthesized

description: >
  一个明确的 bug：函数在边界条件下返回错误结果。
  已有测试文件但缺少边界条件测试。
  验证 Agent 能否定位 bug、修复、补充测试、通过验证。

input_event:
  task_type: bug_fix
  description: "parse_date 函数在输入 '2024-02-29' 时抛出异常而不是返回正确日期"
  repo:
    files:
      - path: "src/utils/date.py"
        content: |
          def parse_date(s):
              parts = s.split('-')
              year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
              if month == 2 and day > 28:
                  raise ValueError("Invalid date")
              return f"{year}-{month:02d}-{day:02d}"
      - path: "tests/test_date.py"
        content: |
          from src.utils.date import parse_date
          def test_normal_date():
              assert parse_date("2024-01-15") == "2024-01-15"
    test_command: "pytest tests/test_date.py -v"

success_criteria:
  - parse_date("2024-02-29") 返回 "2024-02-29"（2024 是闰年）
  - parse_date("2023-02-29") 仍然抛出 ValueError（2023 不是闰年）
  - 已有测试仍然通过
  - 新增闰年边界条件测试
  - diff 只修改 date.py 和 test_date.py

failure_injection:
  - type: boundary_condition
    description: 闰年判断逻辑缺失

metrics:
  - bug_fixed: boolean
  - test_added: boolean
  - existing_tests_pass: boolean
  - no_unrelated_changes: boolean
  - edit_cycles: integer  # 编辑-测试循环次数
```

**Fixture 2: Refactor No Regression**

```yaml
case_id: coding_refactor_no_regression
product_type: coding_agent
evidence_status: synthesized

description: >
  将一个 500 行的 utility 模块拆分为 3 个小模块。
  验证 Agent 能否保持行为等价、所有导入正确更新、测试全部通过。

input_event:
  task_type: refactor
  description: "将 src/utils.py 拆分为 src/utils/string.py, src/utils/date.py, src/utils/file.py"
  scope:
    preserve_behavior: true
    update_imports: true

success_criteria:
  - 原 src/utils.py 的所有函数分布在 3 个新文件中
  - 所有引用 src.utils 的文件已更新导入路径
  - 全部测试通过
  - 无功能变更（纯结构重组）

failure_injection:
  - type: import_chain
    description: 多个文件通过不同路径 import utils，部分使用 from utils import *

metrics:
  - all_functions_preserved: boolean
  - all_imports_updated: boolean
  - all_tests_pass: boolean
  - no_behavior_change: boolean
```

**Fixture 3: Context Rot Long Task**

```yaml
case_id: coding_context_rot_long_task
product_type: coding_agent
evidence_status: synthesized

description: >
  一个需要修改 15+ 文件的跨模块 Feature。
  验证 Agent 在长任务中是否因上下文压缩而遗忘早期决策。

input_event:
  task_type: feature
  description: "在所有 API endpoint 中添加 rate limiting middleware"
  scope:
    files_count: 18
    estimated_context_usage: "超过单次上下文窗口"

success_criteria:
  - 所有 18 个 endpoint 都添加了 rate limiting
  - rate limiting 配置一致（不因上下文丢失而前后不一致）
  - 早期修改的文件在后期仍然正确

failure_injection:
  - type: context_rot
    description: 上下文压缩后遗忘了早期决定的 rate limit 配置参数

metrics:
  - all_endpoints_covered: boolean
  - config_consistency: boolean  # 所有 endpoint 的 rate limit 参数一致
  - early_files_still_correct: boolean
```

### 6.4 设计检查清单

引用 `index/design-checklist.md` 的关键检查项：

**产品层**

```text
[x] 是否定义了用户的 Job to be Done？ → Step 1.2
[x] 是否定义了交付物（不只是对话）？ → diff + 测试证据 + 风险说明
[x] 是否为不同 intent 设置了 required_depth？ → Step 1.3 表格
[x] 是否区分了 autonomy level 和 execution depth？ → Step 2
[x] 是否定义了任务完成证据？ → Step 4.3 Stop Gate
[x] 是否选择了正确的模块组合（而非全部模块）？ → Step 4.1 表格
[x] 是否标注了复杂度等级 C0-C6？ → C3-C4
[x] 是否写下重大取舍的 ADR？ → 各 Step 中的"设计决策"
```

**表示层**

```text
[x] 是否保留 raw_ref？ → FileRef.path + line_range
[x] 是否记录 transform_chain？ → DiffArtifact（append-only 编辑历史）
[x] 是否标注 confidence、freshness、source_authority？ → GitState.freshness + 编辑前后状态
[x] 是否区分事实、摘要、推断、记忆、指令？ → AGENTS.md=instruction, code=data, test_output=evidence
[x] 摘要 / OCR / ASR / 截断是否标记为有损？ → compaction 后的上下文标记为 compressed
[x] 关键结论是否可回查原始材料？ → DiffArtifact → FileRef → 原始文件
```

**执行深度**

```text
[x] 是否有结构化 Task Graph / Milestone？ → 长任务的 feature-list.json
[x] 每个 milestone 是否有退出条件和验证方法？ → Stop Gate
[x] 是否有 Recovery Loop？ → Edit Guard + git checkout 回滚
[x] 是否把 effect verification 纳入 stop gate？ → 五层验证
```

**工具与执行**

```text
[x] 每个工具是否有 input/output schema？ → Step 5.1 工具定义
[x] 工具结果是否包含 failure_mode + recoverable？ → Edit 失败可重试，Shell 失败可分析
[x] 高风险工具是否有审批策略？ → Permission tree: deny > ask > allow
[x] 写动作是否默认 read-after-write？ → Edit 后 Read 回读
[x] 是否区分 execution success 与 effect success？ → 测试通过 ≠ 功能正确
```

**交互**

```text
[x] 是否定义何时中断用户？ → 高风险操作审批、多次编辑失败、方案歧义
[x] 是否有进度报告策略，而不是每一步刷屏？ → milestone-based（搜索完成、编辑完成、测试通过）
[x] Agent 拒绝或降级时是否说明边界和替代方案？ → 部分交付 + 风险说明
```

**评估**

```text
[x] 是否有 representation quality 指标？ → diff 正确性、测试通过率
[x] 是否有失败注入测试？ → Fixture 中的 failure_injection
[x] 是否有外部基准对标？ → SWE-bench Verified
[ ] 是否有安全评估集？ → MVA-3 补充（代码注入防御）
[ ] 是否有 eval regression、canary rollout？ → MVA-3 补充
```

**遗留项**

| 检查项 | 计划补充阶段 | 原因 |
|---|---|---|
| 安全评估集 | MVA-3 | 代码注入、恶意依赖引入 |
| 配置指纹 | MVA-3 | 进入生产环境后需要 |
| eval regression | MVA-3 | 进入持续运营后需要 |
| 多 Agent 编排 | MVA-3+ | 大型 Migration 场景 |
| 跨项目记忆 | 未来 | 多项目经验积累 |

---

## 总结

本指南演示了一条完整路径：

```text
产品画布（agent-product-model.md）
  → 任务定义（categories/coding-agent/task-model.md）
  → 自治 + 深度（autonomy-and-depth.md）
  → 范式选择（decision-trees.md）
  → 品类实例化（categories/coding-agent/）
  → 工具集设计（tools/overview.md + action-model.md）
  → 上下文工程（context/overview.md + convention discovery）
  → 验证闭环（effects/overview.md + 五层验证）
  → 沙箱设计（security/overview.md + execution/overview.md）
  → Eval Fixture（evaluation/fixtures/ + SWE-bench）
  → 设计检查清单核验（design-checklist.md）
```

收获：

1. **Coding Agent 的核心能力在于闭环**——不是"写代码"，而是"写代码 + 验证 + 修复 + 交付证据"。测试通过不等于功能正确，diff 生成不等于 diff 可维护
2. **从 MVA-2 起步，目标 MVA-3**——先做到能读写文件（MVA-2），再做到能运行测试验证（MVA-3），渐进升级到可恢复长任务（MVA-4）
3. **上下文工程是最高杠杆优化**——CLAUDE.md + Just-in-Time 加载 + Compaction 组合可在保留信息的前提下减少 80% Token。上下文缓存进一步减少 75-90% 重复成本
4. **Git 是天然安全网**——所有修改都是 unstaged diff，随时可回滚。这使得 Coding Agent 的 Edit 操作风险可控
5. **验证是五层递进**——Structural → Execution → Effect → Claim → Human，不能跳级
6. **SWE-bench 分数是必要但不充分的**——约一半通过自动评分的 PR 不会被维护者合并。生产 Coding Agent 需要任务完成率、回归引入率、审查循环次数、失败影响半径四个维度的评估
