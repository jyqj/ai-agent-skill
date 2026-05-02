# Research Agent Action Model

> **Evidence Status** — synthesized. research workflow、citation systems、search/fetch/read/synthesize 的通用闭环。

## 动作类型

| 动作 | 作用 | Preconditions | Postconditions | Verification |
|---|---|---|---|---|
| Search | 发现候选来源 | 明确当前子问题 | source candidates 增加 | source diversity / relevance |
| Fetch / Open | 获取 raw material | source chosen | raw ref + metadata | fetch success + parse status |
| Parse / Extract | 形成 snippets / claims 候选 | raw ref 可读 | new EvidenceSnippet / ClaimRecord | confidence + replayability |
| Refresh | 检查 freshness | 主题时间敏感或 source 过期 | source / claim 时间更新 | refresh trace |
| Cross-Verify | 比对多源 | claim importance 足够高 | claim status 更新 | support/conflict map |
| Synthesize | 形成章节或报告 | claim set 已有 citation chain | report section ready | citation integrity check |
| Publish / Send | 对外扩散 | 用户授权、风险说明 | report delivered | delivery ack / audit |

## 默认动作顺序

```text
question framing
  → search
  → fetch/read
  → extract evidence and claims
  → cross-verify / refresh
  → synthesize with citations
  → final integrity check
```

## 关键 gate

### Citation Gate

任何高价值段落在进入最终报告前都需要：

```text
claim present
+ evidence bound
+ raw ref available
+ citation renderable
```

### Conflict Gate

若某个核心结论存在冲突，默认动作不是“写一个平滑段落”，而是：

```text
preserve conflict
→ decide whether to search more / refresh / label unresolved
```

### Freshness Gate

当任务涉及“最新”“当前”“近期”一类问题时，final claim 前应检查：

- source 是否在任务可接受时间窗内；
- 更旧的资料是否被标记为历史背景而非当前事实；
- 是否需要 refresh query；

## 不同输出的行动差异

| 输出 | 行动重点 |
|---|---|
| Fact check | authority + direct support + counterevidence |
| Comparative brief | 维度统一 + 时间窗统一 + 不同来源口径对齐 |
| Literature review | 主题聚类 + 观点谱系 + conflict mapping |
| Ongoing briefing | refresh + delta extraction + stale source handling |

## 高风险动作

Research Agent 通常是低外部效果场景，但以下动作应被视为高风险：

- 把报告自动发送到外部渠道；
- 代表用户联系外部主体；
- 付费抓取、登录受限系统、触发合规敏感检索；
- 对高影响结论做看起来确定的断言但证据不足；

## 关联文档

- `closed-loop.md`
- `../../evaluation/research-agent-evals.md`
- `../../design-space/frontier/agentic-rag-and-citation-loops.md`
