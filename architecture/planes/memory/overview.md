# Memory Engine
>
> **所属域**：2. Cognition & Continuity — 跨会话持续性
>
> **Evidence Status** — grounded. Nocturne、MemPalace、Naga、Generic Agent 等系统对长期记忆、审计、技能提炼的实现；this repository 对”记忆是可追溯主张而不是现实本身”的统一抽象。

**Principle Refs**: BR-02, BDI-01 — 记忆随时间退化可过期，信念需从观察而非假设构建。

## 定义

Memory Engine 管理跨会话、跨任务的持续性。记忆是产品特性，不是数据库特性——它影响 Agent 的未来行为。

记忆层保存的是：
- 稳定主张；
- 来源指针；
- 用户偏好与约束；
- 项目约定；
- 已验证技能；
- 失效与更正历史。

记忆条目必须标注来源和有效期，不应视为实时状态。

## 与 Context / World State 的区别

| 维度 | Context | Memory | World State |
|---|---|---|---|
| 生命周期 | 当前窗口 | 跨会话持久化 | 外部对象的当前或近期状态 |
| 本质 | 当前注意力预算 | 历史主张资产 | 可刷新的状态快照 |
| 主要问题 | context rot | 污染、过期、隐私 | stale、冲突、最终一致性 |
| 使用方式 | 装配 | 检索 / 写入 / 审计 / 失效 | read / refresh / verify |

## 模块接口

**输入**：Agent Kernel 的记忆写入候选、用户的记忆管理操作、eval / skill feedback
**输出**：相关记忆、记忆审计、修订历史
**配置**：记忆分层、写入审批、召回排序、敏感度、失效策略

## 记忆分层

| 层 | 生命周期 | 示例 | 写入策略 |
|---|---|---|---|
| Working | 当前上下文 | 正在处理的任务信息 | 自动（由 Context 管理） |
| Session | 单次会话 | 当前对话历史 | 自动 |
| Project | 项目生命周期 | 构建命令、目录约定、SOP | 半自动 + provenance |
| Long-term | 持久 | 用户偏好、关系、惯例 | 候选 → 确认 → provenance |
| Skill | 持久 | 成功执行路径、脚本、模板 | 提炼 → 验证 → 修订追踪 |

## 写入策略

```text
新信息产生 → 候选筛选（值得记吗？）
    ↓
标注 provenance（来源、时间、上下文、相关 raw ref）
    ↓
分类（哪一层？敏感度？是否长期有效？）
    ↓
确认（用户审批 / 自动写入 / 跳过）
    ↓
持久化 → 审计日志 → 失效 / 纠正规则
```

## 关键规则

- 永远不把一次性情绪写成长期偏好。
- 敏感信息需要显式确认。
- 删除 = 物理删除 + 不再用于推理。
- 记忆条目必须有 provenance、freshness / review policy、confidence。
- Skill 记忆必须支持修订追踪、停用和回滚。

## 设计模式

| 模式 | 说明 | 详见 |
|---|---|---|
| Layered Memory | 按生命周期和稳定性分层 | `../../../design-space/patterns/layered-memory.md` |
| Skill Crystallization | 从成功任务中提炼技能 | `../../../design-space/patterns/skill-crystallization.md` |

## 参考实现

- **Nocturne Memory**：第一人称记忆、审计链、Disclosure Routing，见 `projects/memory-systems/nocturne-memory/`
- **MemPalace**：Knowledge Graph 记忆、宫殿架构、MCP 工具、Benchmarks，见 `projects/memory-systems/mempalace/`
- **NagaAgent**：GRAG 记忆（Graph-RAG 混合），见 `projects/companion-agents/naga-agent/memory-grag.md`
- **Generic Agent**：从成功任务提炼 Skill，见 `projects/general-agents/generic-agent/self-evolution.snippet.md`
