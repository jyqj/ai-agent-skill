# 元认知 -- Agent 知道自己不知道什么

> **Evidence Status** — theoretical

## 核心论点

一个 Agent 能做对事情，靠的是认知能力；一个 Agent 能知道自己做不对什么、并据此调整策略，靠的是元认知能力。`agent-epistemics.md` 给出了"未知"的类型清单（Unobserved、Low-confidence、Stale、Conflicted...），元认知回答的是下一步问题：Agent 如何检测自己处于哪种未知状态？检测到之后如何调整策略？

在当前 LLM Agent 中，元认知失败是最常见也最隐蔽的错误来源——Agent 不是不能做，而是不知道自己不能做，于是自信地输出了错误结果。

## 1. 元认知的两个层次

认知心理学将元认知分为两个层次：

### 元认知知识（Metacognitive Knowledge）

对自己认知过程的了解：

- **自我知识**：我擅长什么、不擅长什么
- **任务知识**：这个任务有多难、需要什么策略
- **策略知识**：什么方法对什么问题有效

对 Agent 的映射：

| 元认知知识类型 | Agent 中的对应 | 具体表现 |
|---|---|---|
| 自我知识 | 模型能力边界感知 | 知道自己在数学推理上比文本生成更容易出错 |
| 任务知识 | Depth 判断 | 知道这个任务需要 D4（Verified Execution）而不是 D2（Assisted Action） |
| 策略知识 | 范式选择意识 | 知道这个任务应该用 Plan-Execute 而不是 ReAct |

### 元认知调节（Metacognitive Regulation）

对认知过程的实时监控和调整：

- **规划**：开始任务前评估难度和选择策略
- **监控**：执行过程中检查进展和质量
- **评估**：完成后反思结果和过程
- **调整**：发现问题后切换策略

对 Agent 的映射：

| 调节阶段 | Agent 中的对应 | 工程化机制 |
|---|---|---|
| 规划 | paradigm-routing | 根据任务特征选择执行范式 |
| 监控 | 循环中的自检 | Confidence 评估、进度追踪、资源消耗检查 |
| 评估 | Verify + Reflection | Effect Verification、Reflection 范式 |
| 调整 | 策略切换 | 从 ReAct 降级到 Plan-Execute，或升级到 Multi-Agent |

## 2. 置信度校准：最关键的元认知能力

置信度校准（Confidence Calibration）是指 Agent 对自己输出的可靠性估计与实际可靠性之间的匹配程度。

### 校准失败的两个方向

**过度自信（Overconfidence）**

- 表现：Agent 声称"已完成"但实际未完成；给出确定性结论但证据不足；跳过验证步骤
- 原因：LLM 的训练目标是生成流畅的文本，不是准确评估自身可靠性；助手模式的训练倾向于给出确定答案
- 后果：幻觉、错误结论被当作事实传播、效果未验证就声称成功
- Agent 架构中的症状：Confidence 字段总是 high，UnknownRecord 几乎为空，Verify 步骤被跳过

**过度谨慎（Underconfidence）**

- 表现：Agent 频繁请求确认已经很清楚的事情；拒绝合理的请求；反复检查已经验证过的结果
- 原因：安全训练过度；过去的错误导致策略过于保守
- 后果：用户体验差、任务效率低、该做的事不做
- Agent 架构中的症状：Autonomy Level 总是停在 L1/L2，明明有验证能力却不敢自动执行

### 校准的工程化方法

1. **置信度不是模型输出的一个数字**，而是多个信号的综合判断：
   - 证据的数量和质量（EvidenceRef 的数量和来源可靠性）
   - 信息的新鲜度（Freshness）
   - 推理链的长度（链越长，累积误差越大）
   - 是否有冲突信号（ConflictRecord）
   - 是否经过验证（VerificationResult）

2. **分层置信度**：不要对整个输出给一个笼统的置信度，而是对每个关键 claim 分别标注

3. **参考合成规则**：将多个信号汇聚为单一置信度值的一种实现方式：

   ```python
   confidence = min(
       evidence_count / evidence_threshold,
       freshness_weight(data_age),
       1 - conflict_ratio(supporting, contradicting)
   )
   ```

   - `evidence_count / evidence_threshold`：证据充分度。证据不够时置信度天花板受限
   - `freshness_weight(data_age)`：信息新鲜度。过期数据拉低上限，常见实现是指数衰减
   - `1 - conflict_ratio`：冲突比率。支持与反驳证据的比例；全部冲突时趋近 0

   取 `min` 而非加权平均，是因为任何一个维度的短板都不应被其他维度掩盖。这不是强制规范——不同系统可根据场景调整权重函数或改用加权几何平均。关键是置信度必须由多信号合成，而非模型自报的单一数字。

   ```mermaid
   graph LR
       E["证据充分度<br/>evidence_count / threshold"] --> MIN["min()"]
       F["信息新鲜度<br/>freshness_weight(age)"] --> MIN
       C["冲突比率<br/>1 − conflict_ratio"] --> MIN
       MIN --> CONF["confidence ∈ [0, 1]"]
       CONF -->|≥ threshold| ACT["可执行"]
       CONF -->|< threshold| HOLD["需补充证据<br/>或请求确认"]
   ```

4. **校准反馈**：记录历史上 Agent 声称的置信度与实际正确率的对应关系，用于调整未来的校准策略

## 3. 任务难度估计：Depth 判断

元认知的任务知识层面对应 Agent 对"这个任务有多复杂"的判断，直接影响 Depth（执行深度）的选择。

### Depth 判断错误的后果

| 判断偏差 | 后果 | 示例 |
|---|---|---|
| 低估难度 | 用简单策略处理复杂问题，导致失败 | 用 D2（草稿）处理需要 D4（验证执行）的代码修改 |
| 高估难度 | 用复杂策略处理简单问题，浪费资源 | 启动 Multi-Agent 协作来回答一个简单的事实性问题 |
| 未识别不确定性 | 用确定性策略处理不确定问题 | 不加 refresh 就使用可能过期的 World State |

### Depth 判断的信号

- 任务涉及多少个外部系统？
- 任务中有多少步骤是不可逆的？
- 任务需要多少次工具调用？
- 前置信息的置信度如何？
- 是否有已知的类似任务的失败案例？

## 4. 策略选择意识：paradigm-routing 是元认知

`paradigm-routing.md` 描述了 Agent 如何根据任务特征选择执行范式（ReAct、Plan-Execute、Reflection、Multi-Agent 等）。从元认知视角看，这就是策略层元认知的工程实现。

### 策略僵化：最隐蔽的元认知失败

策略僵化是指 Agent 一直使用同一种执行范式，即使当前任务不适合：

- 总是用 ReAct（逐步试错）处理需要全局规划的任务
- 总是用 Plan-Execute（先规划后执行）处理需要快速迭代的探索性任务
- 总是用单 Agent 处理需要多角色协作的任务

策略僵化的根源通常是 Harness 设计中没有为范式切换提供机制——不是 Agent "选择"了错误的范式，而是它"只有"一个范式可用。

### 动态策略切换的触发条件

| 信号 | 可能需要的策略调整 |
|---|---|
| 连续多次行动失败 | 从 ReAct 切换到 Plan-Execute，先重新规划 |
| 预测误差持续增大 | 触发 Reflection，重新评估假设 |
| 上下文即将耗尽 | 切换到 Multi-window 或 Compaction |
| 任务分解后发现子任务独立 | 切换到 Worker 并行模式 |
| 用户反馈不满意 | 提升 Autonomy Level 中的人工参与度 |

## 5. 学习意识：何时固化、何时丢弃

元认知的最高层次是对学习过程本身的意识：Agent 是否知道自己什么时候该把经验固化为可复用的知识、什么时候该丢弃过时的经验？

### 固化的条件

- 同一类问题出现过多次
- 解决方案经过验证且稳定
- 固化后能显著减少后续的推理开销

### 丢弃的条件

- 环境已经变化（API 版本更新、代码库重构）
- 固化的经验在最近几次使用中产生了错误
- 经验依赖的前提条件不再成立

### 与知识库的连接

- `../../architecture/learning/` 目录处理学习的工程机制
- `../../architecture/learning/knowledge-distillation.md` 处理经验固化
- 元认知补充的是"何时触发学习"的判断层

## 6. 元认知失败的诊断清单

当 Agent 表现不佳时，除了检查输入、工具和 prompt，还应检查元认知层面的问题：

```text
[ ] 置信度是否校准？高置信度的输出是否确实可靠？
[ ] Depth 判断是否合理？是否用了太浅或太深的策略？
[ ] 范式选择是否适当？是否存在策略僵化？
[ ] 未知状态是否被识别？UnknownRecord 是否反映了实际的认知缺口？
[ ] 停止条件是否合理？是过早停止还是过度执行？
[ ] 历史经验是否过期？Memory 中的模式是否还适用？
```

## 7. 与知识库其他部分的连接

元认知不是一个独立的模块，而是贯穿 Agent 架构多个层面的横切关注点：

| 元认知能力 | 知识库中的对应 |
|---|---|
| 置信度校准 | `../agent-epistemics.md` -- Confidence 对象 |
| Depth 判断 | `../../architecture/controllers/execution-depth/overview.md` |
| 策略选择 | `../../paradigms/paradigm-routing.md` |
| 未知状态检测 | `../agent-epistemics.md` -- UnknownRecord |
| 学习意识 | `../../architecture/learning/` 目录 |
| 反思能力 | `../../paradigms/reasoning-paradigms.md` -- Reflection 范式 |

## 延伸阅读

- 未知的类型清单：`../agent-epistemics.md`
- 范式路由的工程实现：`../../paradigms/paradigm-routing.md`
- 执行深度控制：`../../architecture/controllers/execution-depth/overview.md`
- 学习与适应机制：`../../architecture/learning/overview.md`
- 意向立场与目标归因：`./intentional-stance.md`
- BDI 与预测误差：`./bdi-and-active-inference.md`
