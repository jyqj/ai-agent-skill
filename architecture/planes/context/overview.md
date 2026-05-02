# Context Engine
>
> **所属域**：2. Cognition & Continuity — 当前注意力预算
>
> **Evidence Status** — grounded. Claude Code、OpenCode、Nocturne 等系统对 compaction、disclosure、snapshot 的实现；this repository 对上下文预算与表示分层的统一抽象。

**Principle Refs**: BR-02, BR-01 — 上下文信息随时间退化，窗口受显式资源预算约束。

## 定义

上下文窗口是 Agent 的工作记忆——每个 token 都在购买注意力，不在窗口中的信息模型无法利用。Context Engine 的职责不是保存一切，而是决定哪些信息进入当前窗口、以什么语义和 trust tier 进入、哪些该压缩或原样保留、哪些该留在 memory / world state / raw refs 中按需回查。

## 核心问题

| 问题 | 表现 |
|---|---|
| Context Rot | 上下文填满后推理质量下降、早期退出、指令跟随下降 |
| Lost in the Middle | 中间位置的信息最容易被忽略 |
| Trust Collapse | 不同来源的内容被混成一段 prompt |
| Summary Overwrite | 有损摘要覆盖原始观察 |

## 模块接口

**输入**：Depth Controller 的 milestone、Representation 层的 observations、Memory 的相关主张、World State 快照、State Engine 的进度
**输出**：组装好的 Context Pack
**配置**：compaction 策略、offloading 阈值、progressive disclosure、trust lane policy

## Context Pack 装配

```yaml
context_pack:
  system_prompt: string
  goal_and_constraints: string
  current_milestone: string
  trusted_instructions: []
  normalized_observations: []
  world_state_snapshots: []
  relevant_memory: []
  progress_state: {}
  decision_log_summary: string
  available_tools: []
  recent_effects: []
  trust_warnings: []
```

## 管理策略

| 策略 | 说明 | 详见 |
|---|---|---|
| Compaction | 上下文满时智能压缩历史 | `../../../design-space/patterns/compaction.md` |
| Frozen Snapshot | 不可变的上下文快照，用于子代理或恢复 | `../../../design-space/patterns/frozen-snapshot.md` |
| Tool Output Offloading | 大输出写文件，上下文只保留摘要和 raw ref | `../../../design-space/patterns/tool-output-offloading.md` |
| Progressive Disclosure | 按需逐步展开信息 | `../../../design-space/patterns/progressive-disclosure.md` |
| Untrusted Context Boundary | 不可信内容与指令分离 | `../../../design-space/patterns/untrusted-context-boundary.md` |

## 产品差异化配置

| 产品 | Context 重点 | 典型配置 |
|---|---|---|
| Coding Agent | 代码文件、测试日志、diff | offloading > 200 行；保留路径和失败测试名 |
| Research Agent | 多来源文本与来源冲突 | 保留来源评级、问题树、证据表 |
| Enterprise Workflow | 外部对象状态和审批上下文 | 保留 object id、状态快照、权限上下文 |
| Browser/Desktop Agent | DOM + 截图 + UI 状态 | 多 lane：DOM / screenshot / user goal |
| Companion Agent | 人格定义不可压缩 | persona frozen；关系层 compaction |

## 参考实现

- **Claude Code**：4 阶段压缩（snip → micro → collapse → auto），见 `projects/coding-agents/claude-code/control-layer.md`
- **OpenCode**：Doom Loop 检测与上下文压缩联动，见 `projects/coding-agents/opencode/context-engineering.snippet.md`
- **Nocturne Memory**：Disclosure Routing 决定信息披露策略，见 `projects/memory-systems/nocturne-memory/context-engineering.md`
