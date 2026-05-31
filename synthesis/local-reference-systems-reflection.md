# Local Reference Systems Reflection

> **Evidence Status** — grounded. 基于 `/Users/jin/Desktop/knode` 根目录中的 GenericAgent、Hermes Agent、NagaAgent、VCPToolBox、MemPalace、Nocturne Memory、Codex、Claude Code、OpenCode、Warp 等实际项目，以及本 skill `projects/` 下对应分析笔记的交叉对照。

## 目的

这份反思回答两个问题：**这些真实项目共同暴露出本 skill 在 Agent 开发指导上的哪些缺口？应该把哪些经验提升为稳定设计规则？**

结论：真实项目反复证明，Agent 架构的关键在于以下五点：

1. **任务入口是否变成可验证契约**；
2. **上下文、记忆、状态和世界效果是否分离**；
3. **工具执行是否有权限、审计、恢复和效果验证**；
4. **长期运行后是否有 skill / memory / eval 的治理闭环**；
5. **Agent 是否嵌入真实产品流程，而不是只作为聊天层外挂**。

## 本轮对照的本地项目

| 本地项目 | 在本 skill 中的映射 | 最强证据维度 | 对 skill 的反思 |
|---|---|---|---|
| `../../GenericAgent/README.md` | `../projects/general-agents/generic-agent/README.md` | 极简 loop、原子工具、skill crystallization | “少工具 + 强学习”比堆工具更重要；需要把 skill 生成纳入验证和退役治理。 |
| `../../hermes-agent/README.md` | `../projects/general-agents/hermes-agent/README.md` | gateway、tool registry、execution backend、learning loop | Gateway 是 runtime 边界；工具注册表和执行后端必须成为单一事实源。 |
| `../../NagaAgent/README.md` | `../projects/companion-agents/naga-agent/README.md` | 多模态入口、角色系统、GRAG 记忆、端侧产品化 | Companion Agent 的评估不能只看任务完成，还要看身份、情绪连续性和用户负担。 |
| `../../VCPToolBox/README.md` | `../projects/tool-platforms/vcptoolbox/README.md` | 插件生态、分布式工具、底层权限风险 | 工具平台必须把 capability、身份、权限和审计作为核心对象，不是插件目录附属品。 |
| `../../mempalace/README.md` | `../projects/memory-systems/mempalace/README.md` | 原文优先记忆、结构检索、benchmark | 记忆是 representation 问题；摘要不是默认答案，raw ref 和结构索引优先。 |
| `../../nocturne_memory/README.md` | `../projects/memory-systems/nocturne-memory/README.md` | disclosure routing、版本链、changeset 审计 | 记忆召回应由触发条件和审计约束驱动，而不是只靠相似度。 |
| `../../codex/README.md` | `../projects/coding-agents/codex/README.md` | 本地 coding agent、sandbox、policy、MCP | 高执行深度依赖 sandbox / guardian / approval，而不是模型能力本身。 |
| `../../claude code/package/README.md` | `../projects/coding-agents/claude-code/README.md` | 终端 agent、代码库理解、工具执行、git workflow | Coding Agent 的核心是代码库上下文 + 工具链可靠性 + git / test 验证闭环。 |
| `../../opencode/README.md` | `../projects/coding-agents/opencode/README.md` | 开源 coding agent、TUI / desktop、多语言包 | Agent 产品需要清晰的安装、更新、插件和 UI surface；runtime 不是唯一架构。 |
| `../../warp/README.md` | `../projects/coding-agents/warp/README.md` | terminal-native ADE、Oz pipeline、spec / readiness label | Agent 可成为贡献者；任务要先经过 readiness 和 spec contract，而不是直接执行。 |

## 升级后的设计判断

### 1. 任务入口：Prompt 不够，必须变成 Contract

Warp 的 issue → readiness label → spec → implement → review 流程说明，高质量 Agent 开发需要把任务入口结构化为：

```text
Intent → Readiness Gate → Spec / Contract → Execution Plan → Review Gate → Effect Verification
```

因此本 skill 的 `Design Checklist` 需要强制问：

- 任务是否有 readiness gate？
- 是否有 testable behavior / acceptance criteria？
- 是否记录 out-of-scope？
- 是否允许 Agent 在规格不足时协商，而不是硬做？

对应文件：
- `../design-space/patterns/contract-agent.md`
- `../design-space/patterns/milestone-gated-execution.md`
- `../categories/coding-agent/implementation-map.md`

### 2. 工具层：Tool schema 只是起点，capability ledger 才是安全边界

VCPToolBox、Codex、Claude Code、OpenCode 和 Hermes 都显示：工具一旦能读写文件、执行命令、控制浏览器或调用第三方 server，就必须显式建模：

```text
actor_user + agent_id + tool_id + capability_grant + audit_context + effect_record
```

因此工具设计不应只写 JSON Schema，还要写：

- preconditions / postconditions；
- reversibility；
- risk level；
- approval policy；
- read-after-write 或 external ack；
- failure_mode 与 recovery policy。

对应文件：
- `../architecture/planes/tools/overview.md`
- `../architecture/planes/identity-capability/overview.md`
- `../architecture/planes/effects/overview.md`
- `../design-space/patterns/effect-ledger.md`

### 3. 记忆层：不要把 memory 当长上下文

MemPalace 和 Nocturne Memory 从两个方向证明同一件事：

- MemPalace：原文保留 + 结构导航优先于过早摘要；
- Nocturne：disclosure 条件、版本链和审计比“召回相似片段”更关键。

因此本 skill 对记忆的默认建议应是：

```text
Memory = Raw Evidence + Structured Address + Disclosure Condition + Version / Audit + Expiry
```

不要把“无限上下文”或“自动摘要”误认为长期记忆。记忆写入必须区分：

- 事实；
- 用户偏好；
- 环境约定；
- 成功路径；
- 失败路径；
- 推断；
- 过期状态。

对应文件：
- `../architecture/planes/memory/overview.md`
- `../architecture/planes/representation/overview.md`
- `../synthesis/context-memory-state-boundaries.md`
- `../design-space/lessons-learned/infinite-context-as-memory.md`

### 4. 学习层：Skill crystallization 必须带治理，不然会污染

GenericAgent 和 Hermes 都强调 self-improving / skill creation，但真实系统的风险也很明显：一次偶然成功可能被固化为长期错误。

因此 skill 生成不能直接从“成功 trace”进入 active 状态，至少需要：

```text
candidate → replay / eval → scoped activation → monitored use → deprecate / rollback
```

Skill 记录必须包含：

- 适用项目 / domain / preconditions；
- 验证方法；
- do_not_use_when；
- expiry / invalidation trigger；
- 权限需求；
- 失败案例。

对应文件：
- `../design-space/patterns/skill-crystallization.md`
- `../architecture/learning/skill-governance.md`
- `../evaluation/eval-framework.md`

### 5. 产品层：Agent 越强，越需要 Operations Plane

根目录项目里，很多真正困难的问题并不在 agent loop：

- Warp 需要 readiness label、CI、Oz review、SME escalation；
- Hermes 需要 gateway、cron、plugins、checkpoints、diagnostics；
- NagaAgent 需要打包、登录、TTS、前端状态和多端配置；
- VCPToolBox 需要插件管理、分布式工具和管理员面板；
- Codex / Claude Code / OpenCode 需要安装、升级、认证、遥测、错误报告。

因此本 skill 应避免把 Agent 架构缩小为“模型 + 工具循环”。面向真实产品时，Operations / Interface / Observability 是主路径，不是后期补丁。

对应文件：
- `../architecture/planes/operations/overview.md`
- `../architecture/planes/interface/overview.md`
- `../architecture/planes/observability/overview.md`
- `../synthesis/execution-depth-across-agent-types.md`

## 对本 skill 的架构修正

| 旧倾向 | 修正后规则 |
|---|---|
| 先讲所有 plane | 先问用户 Job、required depth、risk，再选最小 plane set。 |
| 认为工具调用成功即可推进 | 所有写动作必须进入 effect ledger，并有 read-after-write / external ack。 |
| 把记忆当上下文扩展 | 记忆是带 provenance、trigger、version、expiry 的 representation。 |
| 把 skill 当 prompt 文件 | skill 是可治理资产：scope、eval、activation、retirement 缺一不可。 |
| 把安全当拒绝策略 | 安全是 identity + capability + audit + recovery 的运行时对象。 |
| 把 Agent 当单轮助手 | 真实产品里的 Agent 是 workflow participant，需要 operations gate。 |

## 使用这份反思的最短路线

当用户要求“根据真实项目完善 Agent 设计”时，优先按下面顺序回答或设计：

1. `../index/design-checklist.md`：先做完整性审查；
2. 本文件：对照本地真实项目的经验约束；
3. `../index/project-module-map.md`：按模块选择参考项目；
4. `../synthesis/tool-effect-verification.md`：检查工具成功与世界效果；
5. `../design-space/patterns/skill-crystallization.md`：检查长期学习是否会污染；
6. `../evaluation/eval-framework.md`：把设计转成 eval / replay / regression。

## 未解决问题

- 根目录项目覆盖 coding、memory、tool platform、companion 较强，但 enterprise workflow、data/BI、robotics 仍缺少同等深度的本地参考实现。
- 多 Agent 协作的真实冲突合并、共享 world state 仲裁和长期成本指标仍证据不足。
- Companion / persona 类 Agent 的主观体验评估仍弱于 coding agent 的 test / CI / review 评估。
