# Stateful Agent Starter Kit

> **Evidence Status** — synthesized. 基于 verified-tool-agent 参考骨架扩展，增加 checkpoint 持久化、WorldStateSnapshot TTL 管理和跨轮次恢复能力。

## 定位

MVA-4 / MVA-5 级别的参考骨架。在 verified-tool-agent 的基础上增加以下概念映射；代码仅用于说明，不是生产状态管理方案：

| 能力 | 说明 | 对应 Plane |
|---|---|---|
| Checkpoint 持久化 | 每步执行后保存状态到磁盘，支持中断后恢复 | `state/` |
| WorldStateSnapshot | 外部对象快照 + TTL + 过期刷新 | `world-state/` |
| 上下文压缩 | 恢复时生成 compact summary 而非重放全量 trace | `context/` |
| 中断恢复 | 从上次 checkpoint 继续执行，跳过已完成步骤 | `recovery/` |

## 核心数据对象

```text
TaskCheckpoint          ← 可持久化的任务进度快照
WorldStateSnapshot      ← 带 TTL 的外部对象状态
StateStore              ← checkpoint 的存取层
StatefulAgent           ← 带状态的 Agent 运行时
```

## 文件结构

```text
stateful-agent/
├── README.md           ← 本文件
├── models.py           ← 数据模型：TaskCheckpoint、WorldStateSnapshot 等
├── state_store.py      ← checkpoint 持久化存取
├── tools.py            ← 工具注册（含 check_world_state）
├── effects.py          ← 效果验证（含 world_state_match）
├── agent_runtime.py    ← StatefulAgent：带 checkpoint 和 world-state 的运行时
└── main.py             ← CLI 入口
```

## 与 verified-tool-agent 的差异

| 维度 | verified-tool-agent | stateful-agent |
|---|---|---|
| 状态持久化 | 无，内存中运行 | 每步 checkpoint 到磁盘 |
| 中断恢复 | 不支持 | 从 checkpoint 恢复，跳过已完成步骤 |
| 外部状态 | 不感知 | WorldStateSnapshot + TTL + 自动刷新 |
| 上下文管理 | 完整 trace | 恢复时用 compact summary |
| 验证类型 | contains / file_exists / exit_code | 增加 world_state_match |
| 工具 | read_file / edit_file / run_test | 增加 check_world_state |

## 关键设计决策

### Checkpoint 策略

每步执行后自动 checkpoint。任务成功完成后删除 checkpoint。

```text
step 1 → checkpoint(step=1) → step 2 → checkpoint(step=2) → ... → 成功 → 删除 checkpoint
                                                                    → 失败 → 保留 checkpoint → 可恢复
```

### World State TTL

每次行动前检查目标对象的快照是否过期。过期则自动刷新。

```text
action.args.world_state_target = "service_status"
  → 查找该 target 的最新 snapshot
  → 如果 (now - observed_at) < freshness_ttl → 复用
  → 否则 → 调 check_world_state 重新观察
```

### 上下文压缩

恢复时不重放全量 trace，而是生成 compact summary：

```text
"Steps executed: 3. Effects: 2 verified, 1 failed."
```

这避免了恢复后上下文窗口被历史 trace 填满。

## 可选参考运行

```bash
# 首次运行
python3 main.py task.json /path/to/workspace

# 中断后恢复（自动从 checkpoint 继续）
python3 main.py task.json /path/to/workspace

# 强制从头开始
python3 main.py task.json /path/to/workspace --no-resume
```

## 适合的场景

- 多步骤文件修改 + 测试验证
- 需要检查外部服务状态后再行动
- 长任务可能因超时或错误中断
- 需要跨轮次保持进度

## 不适合的场景

- 简单一次性任务（用 verified-tool-agent）
- 需要 LLM 决策（用 react-llm-agent 或在此基础上扩展）
- 多 Agent 协作（需要 orchestration 层，超出本骨架范围）

## 相关文档

- `../verified-tool-agent/README.md` — 基础骨架
- `../../architecture/planes/state/overview.md` — Task State 设计
- `../../architecture/planes/world-state/overview.md` — World State 设计
- `../../architecture/planes/world-state/causal-model.md` — 因果世界模型扩展
- `../../architecture/planes/recovery/overview.md` — 恢复策略
- `../../architecture/planes/context/overview.md` — 上下文管理
- `../../design-space/methodology/minimum-viable-agent.md` — MVA 阶梯
