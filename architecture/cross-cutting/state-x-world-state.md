# State x World State 交叉设计

> **Evidence Status** — synthesized.
> 知识库映射: Cognition (Plane — State) x World Modeling (Plane — World State) x Action&Effect (Plane — Effects)

## 为什么需要这篇文档

Agent 运行时维护两种状态：**Task State**（任务做到哪一步）和 **World State**（外部对象当前是什么样）。大多数架构把它们视为独立关注点，但生产系统中最棘手的 bug 恰恰发生在两者的交界处：Agent 的任务计划假设了某个外部条件，而这个条件在执行时已经改变。

典型场景：
- Agent 读取 CRM ticket 状态并制定修改计划，执行修改时 ticket 已被其他用户手动关闭
- Browser Agent 基于 DOM 快照规划点击序列，页面在执行前已被异步更新
- Ops Agent 查询告警状态后制定修复方案，告警在修复执行前已自动恢复

这些问题不是单纯的"过期缓存"问题——它们是 Task State 与 World State 之间的**一致性裂缝**。本文档系统性地识别这些裂缝的模式，提供一致性策略矩阵和缓解方案。

---

## 交叉点识别

| 交叉点 | State 侧关注 | World State 侧关注 | 冲突/张力 | 设计要求 |
|--------|------------|-------------------|----------|---------|
| 计划制定 | 基于当前信息制定任务步骤 | 信息快照有 TTL，可能过期 | 规划延迟 vs 信息新鲜度 | 规划时刷新关键依赖 |
| 写前读取 | 任务准备执行写操作 | 读取时的世界状态可能已失效 | 执行速度 vs 一致性保证 | 写前强制刷新 |
| 多步执行 | 步骤间有依赖和顺序 | 外部状态在步骤间可能变化 | 事务完整性 vs 世界动态性 | 步骤间一致性检查点 |
| 检查点恢复 | 从 checkpoint 恢复执行 | checkpoint 中的 world_refs 可能已过期 | 快速恢复 vs 状态准确性 | 恢复时验证全部 world_refs |
| 多 Agent 协作 | 多个 Agent 操作同一任务 | Agent A 的读取结果在 Agent B 写入后失效 | 并行效率 vs 写冲突 | 乐观锁 / 版本门控 |
| 效果验证 | 标记任务步骤为"已完成" | 外部效果需要回读确认 | 进度感知 vs 效果真实性 | 任务完成度绑定效果验证 |

---

## 一致性裂缝分类

### 按时序分类

| 裂缝类型 | 描述 | 检测难度 | 典型后果 |
|---------|------|---------|---------|
| **Stale-Read** | 基于过期的 WorldStateSnapshot 做决策 | 中（TTL 可检测） | 操作前提不成立，动作无效或有害 |
| **Write-After-Read** | 读取状态后、写入前，状态被外部改变 | 高（无原生检测） | 覆盖他人修改、产生冲突 |
| **Phantom Completion** | 任务状态标记完成，但世界状态未达标 | 中（需回读验证） | 虚假交付，用户需重做 |
| **Checkpoint Drift** | checkpoint 中的 world_refs 在恢复时已过期 | 低（恢复时可检查） | 恢复后基于旧信息继续，级联错误 |
| **Plan Obsolescence** | 规划阶段的假设在执行阶段不再成立 | 高（需持续监控） | 整个计划失效，需要 replan |

### 按参与者分类

| 场景 | 描述 | 缓解策略 |
|------|------|---------|
| 单 Agent + 单用户 | Agent 自己的读写之间世界变化 | TTL + refresh-before-write |
| 单 Agent + 多用户 | 其他用户在 Agent 操作间修改对象 | 版本检查 + 冲突检测 |
| 多 Agent + 共享对象 | Agent A 读取后 Agent B 写入，Agent A 的快照失效 | 乐观锁 + 版本门控执行 |
| Agent + 外部系统 | 外部系统异步更新对象状态 | 事件订阅 + 变更检测钩子 |

---

## 一致性策略矩阵

### 按操作类型选择策略

| 操作类型 | 默认策略 | 实现方式 | 适用场景 |
|---------|---------|---------|---------|
| 只读分析 | allow_if_recent | 检查 TTL，未过期直接使用 | 低风险查询、报告生成 |
| 低风险写入 | refresh_before_write | 写前刷新关键对象快照 | 更新描述、添加标签 |
| 高风险写入 | version_gated_write | 刷新 + 版本/etag 比对 + 条件写入 | 状态变更、金额修改 |
| 不可逆操作 | pessimistic_lock | 获取锁 → 刷新 → 验证 → 执行 → 释放 | 删除、部署、资金转移 |
| 多步事务 | saga_with_checkpoints | 每步检查一致性 + 补偿栈 | 跨系统工作流 |

### 乐观 vs 悲观方案对比

| 维度 | 乐观方案（版本检查） | 悲观方案（锁） |
|------|-------------------|---------------|
| 吞吐 | 高（无阻塞） | 低（持锁期间独占） |
| 冲突处理 | 事后检测，失败时 replan | 事前预防，锁超时风险 |
| 适用场景 | 冲突概率低的资源 | 不可逆操作、高竞争资源 |
| Agent 适配性 | 好（Agent 天然异步） | 差（Agent 执行时间不可预测） |
| 推荐用于 | 大多数 Agent 写操作 | 删除、部署、资金操作 |

---

## 缓解模式

### 模式 1: Refresh-Before-Write

最基础的一致性保障。在执行写操作前，强制刷新相关 WorldStateSnapshot。

```text
Task State: 准备执行 write_action
  → 识别 write_action 依赖的 world_refs
  → 逐一刷新 world_refs（重新读取外部状态）
  → 比对刷新后状态与计划假设
  → 一致 → 执行写操作
  → 不一致 → 中止，触发 replan 或请求用户确认
```

### 模式 2: Version-Gated Execution

在 refresh-before-write 基础上增加版本门控，防止刷新与写入之间的微小窗口内发生变更。

```yaml
version_gate:
  target_object: crm.ticket.12345
  expected_version: etag:abc123    # 刷新时获取
  condition: version == expected    # 写入时验证
  on_mismatch: abort_and_replan
```

### 模式 3: Change-Detection Hooks

对关键外部对象注册变更监听，当对象状态变化时主动通知 Agent，而非依赖 Agent 主动刷新。

```text
Agent 订阅 world_object.change_event
  → 事件到达时更新本地 WorldStateSnapshot
  → 检查受影响的 open steps
  → 受影响步骤标记为 needs_revalidation
  → 下次执行前重新评估步骤前提条件
```

### 模式 4: Saga with Consistency Checkpoints

多步执行流程中，每个步骤完成后检查后续步骤的前提条件是否仍然成立。

```text
Step 1: Execute → Verify Effect → Checkpoint
  → 检查 Step 2 的 preconditions 是否仍成立
  → 成立 → 继续 Step 2
  → 不成立 → 暂停，评估是否 replan 或 compensate Step 1
Step 2: Execute → Verify Effect → Checkpoint
  → 检查 Step 3 的 preconditions...
```

---

## 常见错误与案例

### 错误 1: 计划制定后不刷新就执行

**表现**: Agent 在规划阶段读取世界状态，执行阶段直接使用规划时的快照
**后果**: 规划到执行可能间隔数秒到数分钟，期间外部状态可能已变化
**修正**: 执行写操作前，至少对关键依赖对象执行 refresh-before-write

### 错误 2: 把 Task State 的"已完成"等同于外部效果已达成

**表现**: Agent 调用工具成功后立即标记步骤为完成，不做回读验证
**后果**: Phantom Completion——任务显示 100% 完成，但外部对象状态未改变
**修正**: 步骤完成标记必须绑定 EffectRecord 的 verification_status，而非 ToolCall 的 success

### 错误 3: Checkpoint 恢复时不验证 world_refs

**表现**: 从 checkpoint 恢复后直接继续执行下一步
**后果**: checkpoint 中保存的世界状态引用可能已过期，恢复后的执行基于错误假设
**修正**: 恢复流程必须包含 "Refresh stale world refs" 步骤（State Plane 恢复流程已定义此步骤）

### 错误 4: 多 Agent 场景下无冲突检测

**表现**: Agent A 和 Agent B 同时读取同一对象，各自基于自己的快照执行写操作
**后果**: 后写入者覆盖先写入者的修改，或产生不一致状态
**修正**: 共享对象必须使用版本门控写入；写入冲突时进入仲裁流程而非静默覆盖

---

## 设计启发

1. **Task State 和 World State 是两个独立的真相来源。** Task State 记录"Agent 认为自己做到了哪一步"，World State 记录"外部世界实际是什么样"。两者的不一致是常态，而非异常。
2. **写操作是一致性裂缝的高发区。** 读操作容忍一定的陈旧度，但写操作基于错误前提可能造成不可逆后果。写前刷新是最小成本的安全网。
3. **TTL 是必要但不充分的。** TTL 能检测已知的时间维度过期，但无法捕获 TTL 内的外部变更。高风险操作需要版本门控或锁。
4. **Checkpoint 是时间胶囊——恢复时必须解冻。** checkpoint 中的 world_refs 是快照时间点的真相，恢复时必须重新验证。
5. **乐观策略优先于悲观策略。** Agent 执行时间不可预测，持锁时间过长会成为瓶颈。大多数场景下，版本检查 + 冲突重试优于锁。
6. **事件驱动优于轮询。** 当外部系统支持变更通知时，change-detection hooks 比定期刷新更及时、更节省资源。
7. **多 Agent 场景下，共享对象是天然的竞争点。** 不要假设"Agent 不会同时操作同一对象"——设计时就要考虑并发写入的冲突路径。

---

## 与知识库的映射

| 本文档章节 | 映射到的 Plane / 文档 | 关系说明 |
|-----------|---------------------|---------|
| 一致性裂缝分类 | `architecture/planes/state/overview.md` | Task State 与 World State 的分层定义 |
| 一致性裂缝分类 | `architecture/planes/world-state/overview.md` | WorldStateSnapshot 的 TTL 和刷新策略 |
| Stale-Read / Write-After-Read | `architecture/planes/world-state/overview.md` — 常见失败 | Stale Snapshot 和 State Conflict 条目 |
| Phantom Completion | `architecture/planes/effects/overview.md` — Ghost Success | 工具成功但状态未变的验证缺失 |
| Checkpoint Drift | `architecture/planes/state/overview.md` — 恢复流程 | "Refresh stale world refs" 步骤 |
| Saga 模式 | `architecture/planes/recovery/overview.md` | partial_effect 的 compensation stack |
| 多 Agent 冲突 | `architecture/planes/orchestration/shared-world-model.md` | 共享世界模型的一致性管理 |
| Version-Gated Execution | `architecture/planes/world-state/overview.md` — etag / optimistic lock | 乐观锁方案的实现基础 |
