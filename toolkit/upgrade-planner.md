# Upgrade Planner

> **Evidence Status** — synthesized. 从 `mva-planner.md` 的静态级别表扩展为增量升级路径；避免"大爆炸式"全面重构。

## 30 秒判断

升级的核心问题是：**当前级别出了什么症状，最小改动能到下一级？**

## 逐级升级路径

| 过渡 | 解锁能力 | 最少新增模块/plane | 最少新增 pattern | 典型失败信号（该升了） | 成本 |
|---|---|---|---|---|---|
| 0 → 1 | 结构化输出、验收标准 | output-contract | contract-agent | 用户不断追问"到底要什么格式" | small |
| 1 → 2 | 单步工具调用 | tool-registry, observation | tool-output-offloading | 用户手动复制粘贴执行建议 | small |
| 2 → 3 | 写动作 + 读后验证 | effects, control | effect-ledger, guard-model | 工具返回 success 但实际未生效 | medium |
| 3 → 4 | 可中断/可恢复长任务 | task-state, checkpoint | checkpoint-hydration, compaction | 任务跨会话丢失进度、重复执行 | medium |
| 4 → 5 | 可观测 + 回归检测 | trace, eval, config-fingerprint | shadow-mode-regression, loop-detection | 变更后静默回归、无法定位根因 | large |
| 5 → 6 | 持续运行 + 运维自动化 | dataflow, heartbeat, rollback | depth-budgeting, hook-system | 系统无人值守时漂移或宕机 | large |

## 决策表：症状 x 推荐路径

```text
当前级别 + 观察到的失败 → 下一步

MVA-0 + "输出格式不稳定"          → 升 MVA-1：加 output contract
MVA-1 + "用户手动跑命令"          → 升 MVA-2：接入 tool-registry
MVA-2 + "tool success ≠ done"    → 升 MVA-3：加 effect-ledger + readback
MVA-3 + "跨天任务从头再来"        → 升 MVA-4：加 checkpoint-hydration
MVA-4 + "改了 prompt 全线回归"    → 升 MVA-5：加 trace + eval
MVA-5 + "凌晨无人时服务漂移"      → 升 MVA-6：加 heartbeat + rollback
```

## 升级执行清单

每次升级只做以下四步：

1. **确认症状** — 用上表匹配当前失败信号。
2. **加最少模块** — 只引入该过渡的"最少新增"列，不多不少。
3. **加最少 pattern** — 同上；用 `../index/category-pattern-matrix.md` 确认无冲突。
4. **验证闭环** — 用 `failure-router.md` 确认该失败信号消失。

## 反模式

| 反模式 | 症状 | 修正 |
|---|---|---|
| 大爆炸升级 | 一次跳 2+ 级，集成风险指数增长 | 每次只升一级，验证后再升 |
| 恐惧升级 | 已出现明确失败信号但拒绝加模块 | 对照决策表，症状匹配就升 |
| 镀金升级 | 没有失败信号却提前加复杂度 | 无症状不升级 |

## 最小产出

```yaml
current_level: MVA-3
observed_failure: "跨天任务从头再来"
upgrade_to: MVA-4
add_modules:
  - task-state
  - checkpoint
add_patterns:
  - checkpoint-hydration
  - compaction
validation: "中断后恢复，验证进度不丢失"
```

## 下一步

1. `mva-planner.md` — 确认当前 MVA 级别
2. `module-picker.md` — 选新增模块的最小实现
3. `failure-router.md` — 验证升级后症状消失
