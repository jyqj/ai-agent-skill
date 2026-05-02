# BDI、主动推断与 ORDA-VU 的认识论根基

> **Evidence Status** — theoretical

## 核心论点

ORDA-VU（Observe → Represent → Decide → Act → Verify → Update）不是凭经验拼凑的循环，而是两个认识论传统的工程化综合：BDI 模型提供了"信念-欲望-意图"的决策框架，主动推断提供了"通过最小化预测误差来理解世界"的感知框架。理解这些根基，才能理解 ORDA-VU 为什么比 ReAct 多出了 Represent 和 Verify，以及为什么这两步不是可选的优化而是结构性的必要。

## 1. BDI 模型

### 起源

BDI（Belief-Desire-Intention）模型由 Michael Bratman 在 1987 年提出，后被 Anand Rao 和 Michael Georgeff 在 1990 年代形式化为 Agent 架构。它认为理性 Agent 的行为由三个心智状态驱动：

- **Belief（信念）**：Agent 对世界当前状态的认知。不一定正确，可能过期，可能不完整。
- **Desire（欲望）**：Agent 希望世界变成什么样。可以有多个，可以冲突。
- **Intention（意图）**：Agent 承诺要去做的事情。意图是从欲望中经过审慎选择后形成的行动计划。

### BDI 的关键洞察

BDI 模型最重要的贡献不是这三个概念本身，而是它们之间的关系：

1. **信念约束意图**：你不会去做你认为不可能的事（除非信念更新了）
2. **意图产生承诺**：一旦形成意图，Agent 不会在每一步都重新审视所有选项（这就是 satisficing 在规划层的体现）
3. **意图驱动信念更新**：你会主动观察与当前意图相关的信息（选择性注意）
4. **信念-欲望冲突需要调解**：当你发现"世界不是你以为的样子"时，需要重新评估哪些欲望还可行

## 2. ORDA-VU 与 BDI 的映射

| BDI 组件 | ORDA-VU 阶段 | 工程化实体 |
|---|---|---|
| Belief（信念） | Observe → Represent | World State、Representation、EvidenceRef |
| Desire（欲望） | 外部输入 | TaskEnvelope 中的 success criteria |
| Intention（意图） | Decide | 当前 plan、选定的 action |
| 行动 | Act | Tool invocation、API call |
| 信念修正 | Verify → Update | Effect Verification、World State 更新 |

### 关键对应

**Observe + Represent = 信念的形成过程**

BDI 原始论文中，Belief 是一个给定的起点。但在实际 Agent 系统中，信念不是天上掉下来的——它需要从原始观察中经过采样、解析、结构化才能形成。ORDA-VU 的 Represent 步骤把这个过程显式化了：

- 观察到一个网页（Observe）
- 解析 HTML、提取关键信息、标注来源和时效（Represent）
- 此时 Agent 才真正"持有"了一个可用的信念

**Decide = 从欲望到意图的过渡**

BDI 中最复杂的部分是 deliberation（审慎）：从多个可能的欲望中选择一个可行的，形成承诺。在 ORDA-VU 中，这对应 Decide 阶段——结合目标（TaskEnvelope）、当前信念（World State）、资源约束（Depth Budget、Token Budget）和风险评估来选择下一步行动。

**Verify + Update = 信念修正循环**

BDI 模型承认信念可能是错的，但没有给出系统性的修正机制。ORDA-VU 通过 Verify 和 Update 填补了这个空白：行动之后，显式检查"世界是否按预期改变了"，然后更新信念（World State）。

## 3. 主动推断与自由能原理

### Friston 的框架

Karl Friston 的主动推断（Active Inference）提供了另一个视角：Agent 的核心目标是**最小化预测误差**（或更精确地说，最小化自由能）。

简单来说：

1. Agent 持有一个世界模型（generative model），用它来预测"接下来会观察到什么"
2. 当实际观察与预测不匹配时，产生预测误差（prediction error）
3. Agent 有两种方式消除误差：
   - **感知推断**：更新世界模型以匹配观察（"我对世界的理解错了"）
   - **主动推断**：行动以改变世界使其匹配预测（"世界不是我期望的样子，我要改变它"）

### 主动推断与 ORDA-VU 的映射

| 主动推断概念 | ORDA-VU 对应 | 说明 |
|---|---|---|
| 世界模型 | World State + Representation | Agent 对外部世界的结构化认知 |
| 预测 | intended_effect（Act 阶段声明的预期效果） | "我认为这个行动会导致什么结果" |
| 观察 | Observe + Sense/Verify | 行动后回读实际状态 |
| 预测误差 | Verify 阶段发现的偏差 | 预期效果 vs 实际效果 |
| 感知推断 | Update（修正 World State） | "原来世界不是我以为的样子" |
| 主动推断 | Act（改变世界） | "我要让世界变成我期望的样子" |

### Effect Ledger 是预测误差的记录

在主动推断框架下，Effect Ledger 获得了新的理论意义：它不仅是"做了什么的日志"，更是"预测与现实之间差距的系统性记录"：

```text
Effect Ledger 条目：
  action: 修改文件 X 的第 42 行
  intended_effect: 第 42 行变为 "new_value"
  actual_effect: 第 42 行确实变为 "new_value"
  prediction_error: 0（匹配）

Effect Ledger 条目：
  action: 调用 API 创建用户
  intended_effect: 用户被创建，返回 user_id
  actual_effect: API 返回 200，但回读发现用户不存在
  prediction_error: 高（API 成功但效果未实现）
```

当累积的预测误差超过阈值时，Agent 应该触发更深层的策略调整——这连接到 `metacognition.md` 中的策略层元认知。

## 4. 为什么 ORDA-VU 比 ReAct 多了 Represent 和 Verify

ReAct（Reason + Act）的循环是：Thought → Action → Observation → Thought → ...

对比 ORDA-VU：Observe → Represent → Decide → Act → Verify → Update

差异在两个关键步骤：

### Represent：观察不等于信念

ReAct 隐含假设观察结果可以直接使用。但在生产系统中，原始观察到可用信念之间有一段需要显式处理的转换：

- 一个网页的 HTML 不等于"网页的内容"——需要解析、去噪、提取关键信息
- 一个 API 的 JSON 返回不等于"系统的状态"——需要判断返回值的可靠性、新鲜度、是否完整
- 一段日志不等于"发生了什么"——需要关联、过滤、归因

如果跳过 Represent，Agent 就会把原始数据直接当作事实使用，这是 Context Rot 和幻觉的温床。

### Verify：行动不等于效果

ReAct 隐含假设行动的 Observation 直接反映了行动的效果。但在生产系统中：

- `git commit` 返回 exit code 0 不等于 commit 真的存在
- API 返回 200 不等于数据真的写入了
- 文件写入成功不等于写入的内容是正确的

Verify 步骤把"工具说成功了"和"现实确实改变了"之间的鸿沟显式化。这是 `representation-and-effects.md` 中"效果边界"的循环实现。

### 理论依据的总结

- BDI 解释了为什么需要 Represent：信念不是给定的，需要从观察中构建
- 主动推断解释了为什么需要 Verify：Agent 需要检查预测误差来更新世界模型
- 两者共同解释了为什么 ORDA-VU 是六步而不是三步：省略的步骤不是冗余，而是把隐含假设变成了显式检查

## 5. 实践启发

### World State 是 Belief 的工程化

不要把 World State 当成"缓存"。它是 Agent 的信念系统——Agent 基于它做决策。设计 World State 时要考虑：

- **来源追溯**：每个字段从哪来？经过了什么转换？
- **时效管理**：什么时候过期？过期后怎么处理？
- **冲突处理**：多个来源给出不同值时怎么办？
- **缺口标记**：哪些字段是未知的？未知意味着什么？

### intended_effect 是预测的显式化

在 Act 阶段声明 intended_effect 不是"文档"，而是后续 Verify 阶段的基准线。没有 intended_effect，Verify 就无从比较。

### 预测误差累积需要报警

如果 Agent 的行动反复与预期不符，这不只是"效果验证失败"——它可能意味着 Agent 的世界模型（World State）已经严重偏离现实，需要更大范围的信念修正。

## 延伸阅读

- ORDA-VU 的工程实现：`../../architecture/kernel/agent-loop.md`
- 表示边界与效果边界：`../representation-and-effects.md`
- World State 设计：`../../architecture/planes/state/` 目录
- Effect Ledger：`../../architecture/planes/effects/` 目录
- 元认知与策略调整：`./metacognition.md`
- 有界理性与满意解：`./bounded-rationality.md`
- 范式选择与路由：`../../paradigms/paradigm-routing.md`
