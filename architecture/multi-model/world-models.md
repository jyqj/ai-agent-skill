# 显式世界模型

> **Evidence Status** — mixed
> 来源：model-based RL（Dreamer, MuZero）、LLM Agent 的 inner monologue / planning 实践、robotics sim-to-real 领域、game AI 状态预测；生产系统中"先预测再行动"的工程需求。

## 1. 什么是世界模型

世界模型 (World Model) 是 Agent 内部对"动作如何改变环境状态"的预测能力。

```text
World State: 环境现在是什么样（快照）
World Model: 如果我做动作 A，环境会变成什么样（预测）
```

不是所有 Agent 都需要显式世界模型。很多 Agent 用 observe-act 循环就够了 -- 做一步，看一步。但当以下条件成立时，显式世界模型变得必要。

## 2. 何时需要显式世界模型

| 条件 | 说明 | 示例 |
|---|---|---|
| 试错成本高 | 每次行动的代价大，不能"做了再看" | 生产环境部署、金融交易 |
| 需要多步规划 | 当前动作影响远期状态 | 游戏策略、项目排期 |
| 环境不可逆 | 某些动作无法撤销 | 数据删除、邮件发送 |
| 环境反馈慢 | 观察动作效果需要等待较长时间 | 营销活动效果、代码部署后监控 |
| 需要并行评估 | 同时比较多个方案的预期效果 | 架构设计、策略选择 |
| 物理交互 | 需要预测物理世界的变化 | 机器人操控、自动驾驶 |

## 3. 世界模型的实现方式

### 3.1 LLM 内隐世界知识

最简单的方式：直接让 LLM 做"如果...会怎样"的推理。

```text
Prompt: "如果我在生产环境执行 DROP TABLE users，会发生什么？"
LLM:    "所有用户数据将永久丢失，依赖该表的服务将崩溃..."
```

| 优点 | 缺点 |
|---|---|
| 零额外成本 | 预测精度不可控 |
| 覆盖面广 | 幻觉风险 |
| 灵活 | 不擅长精确数值预测 |

适用场景：常识推理、粗略风险评估、方案比较。

### 3.2 专用模拟器

用领域特定的模拟器做精确预测：

| 领域 | 模拟器类型 | 示例 |
|---|---|---|
| 物理操控 | 物理引擎 | MuJoCo, Isaac Sim, PyBullet |
| 游戏 | 游戏状态模拟器 | 棋类引擎、Atari 模拟器 |
| 网络/基础设施 | 拓扑模拟器 | ns-3, Mininet |
| 金融 | 风险模型 | Monte Carlo 模拟 |

### 3.3 轻量预测模型

介于 LLM 推理和专用模拟器之间的中间方案：

```yaml
lightweight_predictor:
  input: current_state + proposed_action
  output: predicted_next_state + confidence
  model_type: small_ml_model | rule_based | statistical
  training_data: historical_state_transitions
  update_frequency: online | daily | weekly
```

### 3.4 混合方案

生产系统常用多种方式组合：

```text
LLM 做高层推理：  "这个方案大方向可行"
模拟器做精确验证：  "具体参数下结果是 X"
轻量模型做快速筛选："这 10 个方案中，3 个值得深入评估"
```

## 4. 与 World State Plane 的区别和连接

| 维度 | World State Plane | World Model |
|---|---|---|
| 关注点 | 当前状态快照 | 状态转移预测 |
| 数据来源 | 观察（tool readback, sensor） | 模型推理 / 模拟 |
| 时态 | 现在 | 未来（条件性） |
| 刷新方式 | 从环境读取 | 从模型计算 |
| 可靠性 | 取决于观察新鲜度 | 取决于模型准确度 |

连接关系：

```text
World State (当前状态)
    ↓ 作为输入
World Model (预测)
    ↓ 输出预测状态
Decide (选择动作)
    ↓ 执行动作
World State (刷新，获取实际状态)
    ↓ 与预测对比
World Model (校准，更新模型)
```

## 5. 世界模型的校准

模型预测和实际观察之间的差异需要被系统性追踪：

```yaml
prediction_record:
  prediction_id: string
  predicted_state: object
  actual_state: object | null  # 动作执行后观察到的
  prediction_error: float | null
  model_version: string
  context: object
  timestamp: datetime
```

### 校准策略

| 策略 | 说明 |
|---|---|
| 在线校准 | 每次预测-观察对都更新模型参数 |
| 批量校准 | 定期用累积数据重新训练/微调 |
| 异常检测 | 当预测误差突然增大时触发告警 |
| 领域切换检测 | 当任务进入模型未覆盖的领域时降低置信度 |

## 6. 与 ORDA-VU 的关系

ORDA-VU 循环（Observe-Represent-Decide-Act-Verify-Update）中，世界模型参与两个阶段：

### Decide 阶段：What-If 分析

```text
Decide:
  候选动作 A → World Model → 预测状态 A'
  候选动作 B → World Model → 预测状态 B'
  候选动作 C → World Model → 预测状态 C'
  → 选择预测结果最优的动作
```

### Verify 阶段：预测验证

```text
Verify:
  执行动作 A 后，观察实际状态 A_actual
  对比 A_actual 与预测 A'
  差异大 → 世界模型需要校准
  差异小 → 世界模型可信度提升
```

## 7. 品类映射

| Agent 品类 | 世界模型形态 | 典型精度要求 |
|---|---|---|
| Embodied Robot | 物理引擎 + 传感器融合 | 毫米级精度 |
| Game Agent | 游戏规则引擎 + 状态预测 | 状态精确匹配 |
| Enterprise Workflow | 业务流程模型 + SLA 预测 | 流程级正确性 |
| Coding Agent | AST 分析 + 编译器 + 测试 | 编译通过 + 测试通过 |
| Ops / SRE Agent | 基础设施拓扑 + 负载模型 | 趋势正确性 |
| Browser Agent | DOM 状态预测 + 页面加载模型 | 元素级可用性 |

## 8. 反模式

| 反模式 | 风险 |
|---|---|
| 过度信任世界模型 | 模型预测不等于现实，高风险场景仍需实际验证 |
| 不校准 | 模型预测精度随时间衰减而不自知 |
| 用 LLM 做精确数值预测 | LLM 不擅长精确计算，该用模拟器时别省 |
| 世界模型覆盖范围外仍使用 | 越界预测的置信度应大幅降低 |

## 延伸阅读

- `../planes/world-state/overview.md` -- World State Plane 的当前状态管理
- `../planes/world-state/causal-model.md` -- 因果模型与世界模型的关系
- `model-role-allocation.md` -- World Model 作为独立角色的分配
- `neuro-symbolic-hybrid.md` -- 模拟器属于符号系统的一种
- `../../concepts/decision-frameworks.md` -- 决策框架中的预测需求
