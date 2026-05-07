# 端到端构建指南：Research Agent

> **Evidence Status** — synthesized. 基于知识库各层方法论（产品画布、MVA 阶梯、范式决策树、品类架构、设计检查清单）的整合演示，尚未以完整项目实践验证。

## 目标

从零设计一个 Research Agent，使其能够：

- 接收用户的研究问题
- 自主检索、阅读和提取多源材料
- 产出带 citation chain 的结构化研究报告
- 明确标注不确定性、冲突和 freshness 边界

本指南以这个目标为线索，逐步演示如何使用知识库中的方法论完成设计。每一步都交叉引用具体文件路径，方便你回到知识库深入阅读。

---

## Step 1: 用户任务定义

> 参考：`paradigms/methodology/agent-product-model.md`（产品画布）、`categories/research-agent/task-model.md`（任务模型）

### 1.1 填写产品画布

在动手设计任何模块之前，先回答产品画布中的核心问题。以下是 Research Agent 的填写示例：

| 字段 | Research Agent 答案 |
|---|---|
| Target User | 知识工作者、分析师、咨询团队 |
| User Job | 把一个研究问题变成带 citation 的结构化报告 |
| Entry Point | Chat / API / IDE 插件 |
| Deliverable | 结构化研究报告（摘要 + 分节结论 + citation + 冲突说明 + 后续建议） |
| World Objects | 网页、论文、PDF、数据库、已有笔记 |
| Observable Inputs | 用户问题、scope 约束、已有材料 |
| Representation Contract | SourceRecord、ClaimRecord、EvidenceSnippet、CitationRecord、ConflictRecord |
| Intended Effects | 用户获得可引用、可回查的研究结论 |
| Verification | citation chain 完整、冲突未被抹平、freshness 已标注 |

### 1.2 定义 JTBD（Jobs to be Done）

Research Agent 的核心 job 不是"搜几个链接"，而是：

```text
把问题变成可验证的问题树
→ 检索和读取多源材料
→ 提取 claim / evidence / conflict
→ 形成带 citation 的结论
→ 明确保留不确定性和 freshness 边界
```

### 1.3 确定任务类型

根据 `categories/research-agent/task-model.md`，Research Agent 覆盖五种核心任务类型：

| 任务类型 | 典型输入 | 默认深度 |
|---|---|---|
| Fact Check | "这个说法可靠吗？" | D3-D4 |
| Comparative Brief | "比较这几家公司的产品" | D4 |
| Literature Review | "梳理这个方向的主要观点" | D4-D5 |
| Due Diligence | "给我一个风险导向的背景调研" | D4-D5 |
| Ongoing Briefing | "持续跟踪这个主题" | D3-D4 |

**设计决策**：MVA-1 阶段只支持 Fact Check 和 Comparative Brief 两种任务类型，降低首版复杂度。

### 1.4 写 TaskEnvelope

为每种任务类型定义结构化输入，确保 Agent 收到的不是模糊文本，而是有明确 scope 和约束的任务信封：

```yaml
task_envelope:
  task_type: comparative_brief
  research_question: "比较 2024 年主流 LLM Agent 框架的架构差异"
  scope:
    time_window: "2023-01 至 2024-12"
    geography: null
    entity_scope: [LangGraph, CrewAI, AutoGen, OpenAI Assistants]
  success_criteria:
    - 每个框架至少有 2 个独立来源支撑
    - 关键 claim 有 citation chain
    - 架构差异维度覆盖：推理范式、记忆、工具、编排
  constraints:
    - 不编造 citation
    - 不确定性显式标注
  budget:
    max_queries: 30
    max_sources: 20
  output_contract:
    sections: [摘要, 框架概览, 维度对比, 冲突与不足, 后续建议]
    citation_style: inline
```

---

## Step 2: 自治等级和执行深度选择

> 参考：`paradigms/methodology/autonomy-and-depth.md`（自治等级 + 执行深度）、`paradigms/methodology/minimum-viable-agent.md`（MVA 阶梯）

### 2.1 自治等级选择

自治等级回答的问题是：**Agent 能不能自己做？**

Research Agent 的动作风险分析：

| 动作 | 风险 | 可逆性 | 建议自治等级 |
|---|---|---|---|
| Search（搜索） | 低 | 可逆 | L4 — 自动执行 |
| Fetch / Read（读取材料） | 低 | 可逆 | L4 — 自动执行 |
| Extract（提取 claim/evidence） | 低 | 可逆 | L4 — 自动执行 |
| Synthesize（综合报告） | 中 | 可逆 | L4 — bounded autonomy |
| Publish / Send（对外发送） | 高 | 不可逆 | L3 — 需审批 |

**设计决策**：Research Agent 默认 **L3-L4**。搜索、读取、提取在规则内自动执行（L4），但最终报告发布需要用户确认（L3）。这与 `paradigms/methodology/autonomy-and-depth.md` 中 Research Agent 的默认建议一致。

### 2.2 执行深度选择

执行深度回答的问题是：**Agent 要做到哪一步？**

| 深度 | 含义 | Research Agent 是否需要 |
|---|---|---|
| D0 Answer | 回答问题 | 不够——需要证据 |
| D1 Plan | 制定计划 | 不够——需要执行 |
| D2 Assisted Action | 生成草稿 | 不够——需要自主检索 |
| D3 Tool Execution | 执行工具调用 | 基础版可接受 |
| **D4 Verified Execution** | **执行并验证** | **目标深度——citation chain 验证** |
| D5 Stateful Workflow | 长任务可恢复 | 进阶版需要 |

**设计决策**：目标深度 **D4**，即 Agent 不仅搜索和提取，还要验证 citation chain 的完整性。MVA-1 从 D3 起步，MVA-2 升级到 D4。

### 2.3 复杂度等级

根据 `architecture/complexity-levels.md`，D4 + L3-L4 对应 **C3 Verified Action**。Agent 需要 postcondition 验证能力，但不需要跨会话恢复或持续运营。

---

## Step 3: 范式选择

> 参考：`paradigms/decision-trees.md`（范式决策树）、`paradigms/reasoning-paradigms.md`、`paradigms/memory-paradigms.md`、`paradigms/tool-paradigms.md`

使用决策树逐一选择五类范式：

### 3.1 推理范式

```text
任务只需要解释/总结吗？
  └─ 否 → 需要外部读取吗？
       └─ 是，工具结果会改变下一步 → ReAct / ORDA-VU

任务可预先拆成稳定步骤吗？
  └─ 部分可以（先建问题树，再分支检索）→ Plan-and-Execute + ReAct 混合
```

**选择**：**Plan-and-Execute + ReAct 混合**。先用 Plan 阶段建立问题树和搜索策略，再在每个子问题内用 ReAct 循环执行搜索-读取-提取。

### 3.2 记忆范式

```text
信息只在当前任务有效吗？
  └─ 大部分是 → Context / TaskState

是外部对象当前状态吗？
  └─ 是：来源的 freshness、可访问性 → WorldStateSnapshot + TTL
```

**选择**：**Context + WorldStateSnapshot**。当前任务的 claim/evidence 放在 TaskState，来源 freshness 用 WorldStateSnapshot 管理。MVA-1 不需要长期记忆。

### 3.3 工具范式

```text
工具动作是否高风险或外部写入？
  └─ 否（搜索和读取都是只读）→ Atomic/Static Tool 可接受

任务形态是否高度变化？
  └─ 是（不同问题需要不同搜索策略）→ Atomic Tool + Tool Router
```

**选择**：**Atomic Tool**。工具集包括 `search`、`fetch`、`read_pdf`、`extract`，全部是只读、无副作用的原子工具。

### 3.4 协作范式

```text
单 Agent 能在上下文和时间预算内完成吗？
  └─ 大部分可以 → Single Agent + Tools
```

**选择**：**Single Agent**。MVA-1 不引入多 Agent 编排。如果未来需要并行搜索多个子问题，可升级为 Coordinator-Worker。

### 3.5 控制范式

```text
动作会改变外部世界吗？
  └─ 否（只读搜索和报告生成）→ output check / citation check

规则能确定判定吗？
  └─ 部分可以（citation 完整性是规则判断）→ Rule + LLM Judge
```

**选择**：**Rule（citation gate）+ LLM Judge（synthesis quality）**。citation chain 完整性用规则检查，综合质量用 LLM 评估。

### 3.6 范式选择输出

```yaml
paradigm_selection:
  reasoning: plan_execute + react
  memory: context + world_state
  tools: atomic
  collaboration: single
  control: rule + judge
  complexity_level: C3
  required_planes:
    - representation
    - context
    - tools
    - control
    - interaction
    - cost
    - observability
  stop_gates:
    - citation_chain_complete
    - conflicts_preserved
    - freshness_labeled
  eval_fixtures:
    - research_claim_citation_001
    - research_conflict_resolution_001
    - research_freshness_refresh_001
```

---

## Step 4: 品类架构实例化

> 参考：`categories/research-agent/README.md`（品类模板）、`../ARCHITECTURE.md`（plane 总览）

### 4.1 从品类模板出发

`categories/research-agent/README.md` 定义了 Research Agent 的模块配置配方。根据 Step 3 的范式选择，确认需要哪些 plane：

| Plane | 是否需要 | MVA-1 | MVA-2 | 理由 |
|---|---|---|---|---|
| Representation | 必须 | 简化版 | 完整版 | 核心——SourceRecord、ClaimRecord |
| Context | 必须 | 基础 | claim-centered pack | 防止上下文溢出 |
| Tools | 必须 | search + fetch | + read_pdf + extract | 核心能力 |
| Control | 必须 | citation gate | + freshness gate | 质量保障 |
| Interaction | 必须 | 基础进度 | + 澄清 + partial deliver | 用户信任 |
| Cost | 推荐 | query budget | + read budget | 防止搜索发散 |
| Observability | 推荐 | 基础 trace | + source coverage | 调试和改进 |
| State | 可选（MVA-3） | 否 | 否 | 长任务恢复 |
| World State | 可选（MVA-2） | 否 | freshness TTL | 来源时效 |
| Memory | 可选（MVA-3） | 否 | 否 | 跨任务记忆 |
| Effects | 可选 | 否 | 否 | Research 主要是只读 |
| Recovery | 可选（MVA-2） | 否 | retry budget | 搜索失败恢复 |

### 4.2 闭环模型实例化

从 `categories/research-agent/closed-loop.md` 的闭环模型出发，实例化 Research Agent 的执行循环：

```text
1. Observe  ← 接收用户研究问题 + scope 约束
2. Plan     ← 分解问题树、定义搜索策略、设置预算
3. Search   ← 执行搜索，扩展候选来源
4. Read     ← 读取候选来源，提取 EvidenceSnippet
5. Extract  ← 从 evidence 形成 ClaimRecord，标注 status
6. Verify   ← 检查 citation chain、冲突、freshness
7. Synthesize ← 形成结构化报告
8. Deliver  ← 交付报告，标注未验证部分
```

每一轮 Search-Read-Extract 都是一个 ReAct micro-loop。整体 Plan-Execute 框架控制何时停止搜索、何时进入综合。

### 4.3 Stop Gate

从 `categories/research-agent/README.md` 的 stop gate 直接使用：

```text
[ ] 核心结论均可回到 citation chain
[ ] 关键冲突未被静默抹平
[ ] freshness 风险已说明
[ ] source authority 和 limitations 已表达
[ ] 未验证部分被明确标注
```

---

## Step 5: 表示层设计

> 参考：`categories/research-agent/representation.md`（表示模型）、`architecture/planes/representation/overview.md`（通用表示层）、`design-space/patterns/citation-chain.md`（引用链模式）

### 5.1 关键表示对象

Research Agent 的核心设计挑战不在工具调用，而在于**如何表示和追踪知识**。定义以下六个关键对象：

**SourceRecord** — 一个原始来源及其 metadata：

```yaml
source_id: "src_001"
kind: webpage
raw_ref: "https://example.com/article"
source_title: "LLM Agent Frameworks in 2024"
authority: third_party
published_at: "2024-06-15"
retrieved_at: "2024-12-01"
freshness_ttl: "30d"
transform_chain: []
lossy: false
```

**ClaimRecord** — 研究中形成的可验证主张：

```yaml
claim_id: "clm_001"
claim_text: "LangGraph 使用有向图作为核心执行模型"
subject: "LangGraph"
claim_type: fact
status: supported
supports: ["ev_001", "ev_002"]
conflicts_with: []
last_checked_at: "2024-12-01"
```

**EvidenceSnippet** — 来源中的具体支撑片段：

```yaml
evidence_id: "ev_001"
source_id: "src_001"
snippet: "LangGraph defines workflows as directed graphs..."
location: "paragraph 3"
```

**CitationRecord** — 绑定 claim 到 evidence 的引用链：

```yaml
citation_id: "cit_001"
claim_id: "clm_001"
evidence_ids: ["ev_001", "ev_002"]
source_ids: ["src_001", "src_003"]
```

**ConflictRecord** — 互相冲突的 claim 组：

```yaml
conflict_id: "conf_001"
claims: ["clm_005", "clm_008"]
conflict_type: factual_disagreement
resolution: unresolved
notes: "来源 A 报告市场份额 30%，来源 B 报告 45%，时间窗不同"
```

**SynthesisState** — 报告当前聚合状态：

```yaml
synthesis_state:
  total_sources: 12
  total_claims: 28
  supported_claims: 20
  conflicted_claims: 3
  unresolved_claims: 5
  coverage_gaps: ["缺少亚洲市场数据"]
  report_sections_ready: [摘要, 框架概览, 维度对比]
  sections_pending: [冲突与不足, 后续建议]
```

### 5.2 表示层设计原则

从 `categories/research-agent/representation.md` 提炼的四条铁律：

1. **No Orphan Claim**：进入 final synthesis 的 claim 必须绑定 EvidenceSnippet，可回到 SourceRecord.raw_ref
2. **Summary is Lossy**：所有总结、抽取、重写默认标记为 lossy，需要高置信判断时必须支持 raw ref replay
3. **Freshness 跟着 claim 走**：claim 状态应体现 freshly supported / stale but historically accurate / unresolved due to freshness risk
4. **Conflict 是对象不是错误**：冲突的来源、时间窗、定义域差异应成为 ConflictRecord，而不是脚注

### 5.3 ContextPack 组装策略

Research Agent 不应把整堆网页全文塞进上下文。按优先级分层装配：

```text
Layer 1: 当前子问题和输出目标
Layer 2: 已有 claim / conflict map（结构化摘要）
Layer 3: 与当前子问题强相关的 evidence snippets
Layer 4: 需要回放的 raw refs（按需加载）
Layer 5: 压缩历史和预算状态
```

这种分层策略既保证模型看到最相关的信息，又避免上下文溢出导致的 Context Rot（`architecture/planes/context/overview.md`）。

---

## Step 6: 效果验证设计

> 参考：`architecture/planes/effects/overview.md`（效果验证）、`design-space/patterns/self-verification.md`（自验证模式）、`concepts/beyond-verification.md`（超越验证）

### 6.1 Research Agent 的特殊性

Research Agent 的"效果"不同于 Coding Agent 或 Workflow Agent——它不改变外部世界状态，而是产出一个知识制品（报告）。因此验证的重点从"外部状态是否改变"转移到"报告质量是否达标"。

### 6.2 定义 Postcondition

| Postcondition | 验证方法 | 自动化程度 |
|---|---|---|
| Citation chain 完整 | 遍历所有 final claim，检查是否有 EvidenceSnippet 和 SourceRecord 绑定 | 完全自动 |
| 无 orphan claim | 扫描报告文本，匹配 ClaimRecord 列表 | 完全自动 |
| 冲突未被抹平 | 检查 ConflictRecord 列表是否在报告中体现 | 半自动（规则 + LLM judge） |
| Freshness 已标注 | 检查时间敏感 claim 是否有 freshness 状态 | 完全自动 |
| Source authority 已表达 | 检查 first_party / third_party / unknown 分布 | 完全自动 |
| Synthesis quality | 评估报告是否结构化、非拼贴 | LLM judge |

### 6.3 验证流程

```text
Report Draft Ready
  → Citation Gate（自动）
    ├─ PASS → Conflict Gate（半自动）
    │         ├─ PASS → Freshness Gate（自动）
    │         │         ├─ PASS → Quality Judge（LLM）
    │         │         │         ├─ PASS → Ready for delivery
    │         │         │         └─ FAIL → 返回 Synthesize 步骤
    │         │         └─ FAIL → 返回 Refresh 步骤
    │         └─ FAIL → 返回 Extract 步骤恢复冲突
    └─ FAIL → 返回 Search/Read 步骤补 evidence
```

### 6.4 不可完全验证的部分

Research Agent 面对的一个现实是：某些结论无法完全验证（数据不足、来源不可得、时间窗限制）。根据 `concepts/beyond-verification.md`，正确做法是：

- 不假装完整——显式标注 `unresolved` 状态
- 不降低标准——标注不等于放弃验证
- 提供后续建议——告诉用户如何补充验证

---

## Step 7: 交互设计

> 参考：`architecture/planes/interaction/overview.md`（交互层）、`categories/research-agent/README.md`（交互策略）

### 7.1 何时中断用户

Research Agent 的默认原则是 **少打扰，关键时刻精准澄清**。定义中断策略：

| 中断时机 | 触发条件 | 中断内容 |
|---|---|---|
| 任务范围不清 | 研究问题过于宽泛或有歧义 | 请用户确认 scope、时间窗、关注维度 |
| 关键定义冲突 | 同一术语在不同来源有不同含义 | 请用户选择定义或接受多义标注 |
| 预算即将耗尽 | query/source budget 达到 80% | 报告当前覆盖率，请用户选择继续/停止/调整 |
| 高风险结论 | 关键 claim 只有单一来源 | 报告风险，请用户决定是否接受或继续搜索 |

**不中断的情况**：搜索无结果（自动调整搜索策略）、非关键 claim 的冲突（保留在 ConflictRecord 中报告）、常规读取和提取步骤。

### 7.2 进度报告策略

不要每一步都刷屏，也不要完全黑盒。采用 **milestone-based progress**：

```text
[进度] 问题树已建立，共 5 个子问题
[进度] 子问题 1/5 完成：已找到 4 个来源，提取 8 个 claim
[进度] 子问题 3/5 发现冲突：来源 A 和 B 在市场份额数据上不一致
[进度] 综合阶段：20/28 claim 有完整 citation chain
[交付] 报告已完成，3 个 claim 标记为 unresolved
```

### 7.3 部分交付

当 budget 耗尽或用户主动停止时，Research Agent 应能交付部分报告：

- 已完成的 section 正常交付
- 未完成的 section 标注为 `pending`，说明缺什么
- 提供后续搜索建议

### 7.4 置信度表达

报告中的结论不应该看起来同等可靠。采用自然语言置信度表达：

| claim status | 表达方式 |
|---|---|
| supported（多源） | "根据 X、Y、Z 三个来源..." |
| weakly_supported（单源） | "根据 X 的报告（未经交叉验证）..." |
| conflicted | "来源 A 指出...，但来源 B 认为..." |
| unresolved | "尚无充分证据判断...，建议进一步..." |

---

## Step 8: Eval Fixture 创建

> 参考：`evaluation/fixtures/README.md`（fixture 编写原则）、`evaluation/eval-framework.md`（评估框架）、`categories/research-agent/task-model.md`（成功维度）

### 8.1 Fixture 设计原则

Fixture 是评估的最小可复现输入。每个 fixture 固定一个场景的输入、工具、世界状态和验收条件。Research Agent 的 fixture 必须显式说明 citation / conflict / freshness 的断言。

### 8.2 示例 Fixture：Comparative Brief with Conflict

```yaml
case_id: research_comparative_brief_conflict_001
product_type: research_agent
evidence_status: synthesized

description: >
  用户要求比较两个产品，来源中存在事实冲突。
  验证 Agent 是否保留冲突而非抹平。

input_event:
  task_type: comparative_brief
  research_question: "比较 Product A 和 Product B 的市场份额"
  scope:
    time_window: "2024"
    entity_scope: [Product A, Product B]

world_state:
  - source_id: src_mock_001
    kind: webpage
    content: "Product A 占据 40% 市场份额（2024 Q2 报告）"
    authority: third_party
    published_at: "2024-07-01"
  - source_id: src_mock_002
    kind: webpage
    content: "Product A 占据 28% 市场份额（2024 年度报告）"
    authority: first_party
    published_at: "2024-12-15"
  - source_id: src_mock_003
    kind: webpage
    content: "Product B 占据 35% 市场份额"
    authority: third_party
    published_at: "2024-09-01"

allowed_tools:
  - search
  - fetch

success_criteria:
  - 报告中存在 ConflictRecord：src_mock_001 与 src_mock_002 的市场份额数据冲突
  - 冲突未被静默解决——报告文本中明确说明两个数据来源的差异
  - 时间窗差异（Q2 vs 年度）被标注为可能原因
  - first_party 来源（src_mock_002）的 authority 被标注为更高
  - 所有 claim 有 citation chain

failure_injection:
  - type: conflicting_sources
    description: 两个来源报告同一指标的不同数值

metrics:
  - conflict_preserved: boolean
  - citation_chain_complete: boolean
  - authority_differentiation: boolean
  - time_window_noted: boolean
```

### 8.3 建议的 Fixture 覆盖矩阵

| Fixture | 验证目标 | 对应 task-model 中的失败类型 |
|---|---|---|
| `research_claim_citation_001` | Orphan Claim 检测 | Orphan Claim |
| `research_conflict_resolution_001` | 冲突保留 | Conflict Flattening |
| `research_freshness_refresh_001` | 过期来源检测 | Freshness Blindness |
| `research_comparative_brief_conflict_001` | 冲突 + authority + time | Conflict Flattening + Single-Source Collapse |
| `research_single_source_001` | 单源依赖检测 | Single-Source Collapse |
| `research_search_thrash_001` | 搜索发散预算控制 | Search Thrash |

已有 fixture（`evaluation/fixtures/` 目录下）可直接复用前三个，新增后三个需要根据上述模板编写。

---

## Step 9: MVA 路线图

> 参考：`paradigms/methodology/minimum-viable-agent.md`（MVA 阶梯）

### 9.1 核心原则

```text
先构建最小闭环，再根据真实失败补模块。
不要因为框架完整，就要求 Agent 从第一天拥有全部 plane。
```

### 9.2 MVA-1：Assisted Research（2-3 周）

**目标**：能接收研究问题，搜索和读取来源，产出带 citation 的报告草稿。

**对应 MVA 阶梯**：MVA-2 Tool-assisted（有工具调用，但验证有限）。

**必备组件**：

| 组件 | 实现要点 |
|---|---|
| TaskEnvelope | 解析用户问题为结构化任务输入 |
| Representation（简化） | SourceRecord + ClaimRecord（基础版，无 ConflictRecord） |
| Tools | `search`（web 搜索）+ `fetch`（网页读取） |
| ReAct Loop | 搜索 → 读取 → 提取 → 综合的基础循环 |
| Output Contract | 报告模板（摘要 + 分节 + inline citation） |
| Query Budget | 限制搜索次数，防止发散 |

**验收标准**：
- 能完成 Fact Check 和 Comparative Brief 任务
- 产出带 inline citation 的报告
- 不编造 citation

**不做**：冲突检测、freshness 管理、部分交付、问题树分解。

### 9.3 MVA-2：Verified Research（3-4 周）

**目标**：增加 citation chain 验证、冲突保留和 freshness 标注。

**对应 MVA 阶梯**：MVA-3 Verified Tool Agent。

**升级触发器**：MVA-1 中观察到以下失败——
- Orphan Claim（结论无 citation）
- Conflict Flattening（冲突被抹平）
- Freshness Blindness（过期来源被使用）

**新增组件**：

| 组件 | 实现要点 |
|---|---|
| ConflictRecord | 检测和保留冲突 |
| Citation Gate | 自动验证 citation chain 完整性 |
| Freshness Gate | 检查时间敏感 claim 的来源 freshness |
| Quality Judge | LLM 评估报告综合质量 |
| Interaction（澄清） | scope 不清或关键冲突时中断用户 |
| Partial Delivery | budget 耗尽时交付部分报告 |
| Retry Budget | 搜索失败的重试策略 |

**验收标准**：
- Citation Gate 通过率 > 95%
- ConflictRecord 在报告中可见
- freshness 风险在报告中标注
- 通过 `research_claim_citation_001`、`research_conflict_resolution_001`、`research_freshness_refresh_001` 三个 fixture

### 9.4 MVA-3：Stateful Research（4-6 周）

**目标**：支持长任务、跨会话恢复、进阶任务类型。

**对应 MVA 阶梯**：MVA-4 Stateful Agent。

**升级触发器**：MVA-2 中观察到以下失败——
- Literature Review 超出上下文窗口
- 长任务中断后无法恢复
- 用户需要 Ongoing Briefing（持续跟踪）

**新增组件**：

| 组件 | 实现要点 |
|---|---|
| TaskState + Checkpoint | 任务状态可保存和恢复 |
| WorldStateSnapshot | 来源 freshness TTL 管理 |
| SynthesisState 持久化 | 报告聚合状态可恢复 |
| Problem Tree | 完整问题树分解和管理 |
| Source Coverage Map | 跟踪各子问题的来源覆盖度 |
| Memory（项目级） | 跨任务积累的来源评价和搜索策略 |

**验收标准**：
- 中断后恢复，不重复已完成的搜索
- Literature Review 能处理 50+ 来源
- Ongoing Briefing 能区分新旧来源

---

## Step 10: 设计检查清单核验

> 参考：`index/design-checklist.md`（完整检查清单）

用 `index/design-checklist.md` 对 Research Agent 的设计做最终 review。以下是各节的核验结果：

### 产品层

```text
[x] 是否定义了用户的 Job to be Done？ → Step 1.2
[x] 是否定义了交付物（不只是对话）？ → 结构化研究报告
[x] 是否为不同 intent 设置了 required_depth？ → Step 2.2 表格
[x] 是否区分了 autonomy level 和 execution depth？ → Step 2
[x] 是否定义了任务完成证据？ → Step 6.2 Postcondition
[x] 是否选择了正确的模块组合（而非全部模块）？ → Step 4.1 表格
[x] 是否标注了复杂度等级 C0-C6？ → C3
[x] 是否写下重大取舍的 ADR？ → 各 Step 中的"设计决策"
```

### 表示层

```text
[x] 是否保留 raw_ref？ → SourceRecord.raw_ref
[x] 是否记录 transform_chain？ → SourceRecord.transform_chain
[x] 是否标注 confidence、freshness、source_authority？ → ClaimRecord.status + SourceRecord.authority/freshness_ttl
[x] 是否区分事实、摘要、推断、记忆、指令？ → ClaimRecord.claim_type + Trust Lane
[x] 摘要 / OCR / ASR / 截断是否标记为有损？ → SourceRecord.lossy
[x] 关键结论是否可回查原始材料？ → CitationRecord → EvidenceSnippet → SourceRecord
```

### 执行深度

```text
[x] 是否有结构化 Task Graph / Milestone？ → 问题树 + 子问题
[x] 每个 milestone 是否有退出条件和验证方法？ → Stop Gate
[x] 是否有 Recovery Loop？ → MVA-2 retry budget
[x] 是否把 effect verification 纳入 stop gate？ → Citation Gate + Conflict Gate + Freshness Gate
```

### 工具与执行

```text
[x] 每个工具是否有 input/output schema？ → Atomic Tool 定义
[x] 工具结果是否包含 failure_mode + recoverable？ → 搜索无结果可重试
[n/a] 高风险工具是否有审批策略？ → Research Agent 工具均为只读
[n/a] 写动作是否默认 read-after-write？ → 无写动作
[x] 是否区分 execution success 与 effect success？ → 搜索返回结果 ≠ 研究问题已回答
```

### 交互

```text
[x] 是否定义何时中断用户？ → Step 7.1
[x] 是否有进度报告策略，而不是每一步刷屏？ → Step 7.2 milestone-based progress
[x] Agent 拒绝或降级时是否说明边界和替代方案？ → 部分交付 + 后续建议
```

### 评估

```text
[x] 是否有 representation quality 指标？ → citation_chain_complete、conflict_preserved
[x] 是否有失败注入测试？ → Fixture 中的 failure_injection
[ ] 是否有安全评估集？ → MVA-2 补充（防止搜索结果注入）
[ ] 是否有 eval regression、canary rollout？ → MVA-3 补充
```

### 遗留项

以下检查项在当前设计阶段标记为后续补充：

| 检查项 | 计划补充阶段 | 原因 |
|---|---|---|
| 安全评估集 | MVA-2 | 需要防止搜索结果中的 prompt injection |
| 配置指纹 | MVA-3 | 进入生产环境后需要 |
| eval regression | MVA-3 | 进入持续运营后需要 |
| 多 Agent 编排 | 未来 | 当前 single agent 足够 |

---

## 总结：从知识库到实践的路径

本指南演示了一条完整路径：

```text
产品画布（agent-product-model.md）
  → 任务定义（task-model.md）
  → 自治 + 深度（autonomy-and-depth.md）
  → 范式选择（decision-trees.md）
  → 品类实例化（categories/research-agent/）
  → 表示层设计（representation.md）
  → 效果验证（effects/overview.md）
  → 交互设计（interaction/overview.md）
  → Eval Fixture（evaluation/fixtures/）
  → MVA 路线图（minimum-viable-agent.md）
  → 检查清单核验（design-checklist.md）
```

关键收获：

1. **先定义交付物和效果，再定义 Agent**——产品画布是起点，不是 prompt 工程
2. **范式选择是结构化过程**——用决策树而不是直觉
3. **渐进复杂度**——MVA 阶梯让你从最小闭环开始，根据真实失败补模块
4. **表示层是研究质量的基础**——SourceRecord、ClaimRecord、CitationRecord 不是可选的花架子
5. **验证不只是"跑通了"**——citation chain 完整性、冲突保留、freshness 标注才是 Research Agent 的 postcondition
6. **检查清单是安全网**——每一项都对应一个真实的失败模式
