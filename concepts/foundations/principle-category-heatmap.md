# 哲学原则 × 品类违反概率热力图

> **Evidence Status** — synthesized. 基于 28 条哲学原则和 14 个品类的交叉分析。

本热力图帮助品类架构师快速定位"我这类 Agent 最容易违反哪些原则"。

---

## 为什么需要这张图

`concepts/foundations/PRINCIPLE-INDEX.md` 列出了 28 条原则和它们对应的 ORDA-VU 阶段。但不同品类的 Agent 违反不同原则的概率差异很大——Coding Agent 最容易违反 IS-02（工具成功 ≠ 世界成功），Companion Agent 最容易违反价值对齐原则。逐条审查所有原则效率低下；这张热力图让你在设计和评审阶段直接聚焦高风险区域。

---

## 热力图

**标注说明**

- **H** = 高违反风险（需要优先防护）
- **M** = 中等风险
- **L** = 低风险
- **—** = 不适用或极低风险

### Bounded Rationality (BR-)

| ID | 原则 | Coding | Research | Browser | Workflow | Companion | Creative | Security | Ops/SRE | Data/BI | Memory | Embodied | Platform |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BR-01 | 显式资源预算 | H | H | M | M | L | M | M | M | M | L | M | H |
| BR-02 | 上下文腐烂 | H | H | M | M | H | H | L | M | M | H | M | M |
| BR-03 | 满意解优于最优解 | M | H | L | M | L | H | L | M | M | L | M | L |
| BR-04 | 并行任务资源竞争 | M | L | M | H | L | L | L | H | M | L | M | H |
| BR-05 | 递归深度失控 | H | M | M | H | L | M | M | H | M | L | L | H |

### BDI & Active Inference (BDI-)

| ID | 原则 | Coding | Research | Browser | Workflow | Companion | Creative | Security | Ops/SRE | Data/BI | Memory | Embodied | Platform |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BDI-01 | 信念从观察构建 | M | H | H | M | M | M | H | H | H | M | H | L |
| BDI-02 | 验证即信念修正 | H | M | H | H | L | L | M | H | M | L | H | M |
| BDI-03 | 意图跨步持久可修正 | M | M | M | H | M | M | L | H | L | M | H | M |
| BDI-04 | 观察选择性偏差 | M | H | H | M | H | M | H | M | H | H | M | L |
| BDI-05 | 信念惯性抵抗修正 | M | H | M | M | H | M | M | M | H | H | M | L |

### Intentional Stance (IS-)

| ID | 原则 | Coding | Research | Browser | Workflow | Companion | Creative | Security | Ops/SRE | Data/BI | Memory | Embodied | Platform |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| IS-01 | 操作表示非现实 | M | H | H | M | M | M | M | M | H | H | H | L |
| IS-02 | 工具成功 ≠ 世界成功 | H | M | H | H | L | L | M | H | M | L | H | M |
| IS-03 | 地图-领地分离 | M | H | M | M | L | L | M | M | H | M | H | L |
| IS-04 | 拟人化导致错误归因 | L | M | L | L | H | H | L | L | L | M | H | L |
| IS-05 | 多 Agent 意图不可透明假设 | L | L | L | M | L | L | M | M | L | L | M | H |

### Embodiment & Situation (EM-)

| ID | 原则 | Coding | Research | Browser | Workflow | Companion | Creative | Security | Ops/SRE | Data/BI | Memory | Embodied | Platform |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EM-01 | 工具是认知延伸 | H | M | H | M | L | M | M | M | M | L | H | M |
| EM-02 | 能力 = 模型 × Harness | M | M | M | M | M | H | M | M | M | L | H | H |
| EM-03 | 环境约束行动空间 | M | L | H | M | L | L | H | H | M | L | H | H |
| EM-04 | 工具组合产生涌现行为 | H | M | H | H | L | M | H | M | M | L | H | M |
| EM-05 | 感知缺陷不可自知 | L | M | H | L | M | M | M | M | M | L | H | L |

### Metacognition (MC-)

| ID | 原则 | Coding | Research | Browser | Workflow | Companion | Creative | Security | Ops/SRE | Data/BI | Memory | Embodied | Platform |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MC-01 | 表达不确定性 | M | H | M | M | M | M | H | M | H | M | H | L |
| MC-02 | 自我监控与策略切换 | H | M | H | H | M | M | M | H | M | M | H | M |
| MC-03 | 知道不知道什么 | M | H | M | M | M | M | H | M | H | M | M | L |
| MC-04 | 置信度校准误差 | M | H | M | M | H | H | H | M | H | M | M | L |

### Value Alignment (VA-)

| ID | 原则 | Coding | Research | Browser | Workflow | Companion | Creative | Security | Ops/SRE | Data/BI | Memory | Embodied | Platform |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VA-01 | 价值漂移 | L | L | L | L | H | M | L | L | L | H | L | L |
| VA-02 | 短期指令 vs 长期利益 | M | M | L | M | H | M | M | M | M | H | M | M |
| VA-03 | 偏好过拟合 | L | L | L | L | H | M | L | L | L | H | L | L |
| VA-04 | 多层价值源冲突解决 | M | L | L | H | H | H | M | M | L | M | M | H |

---

## 品类高风险原则速查

为每个品类提取所有 H 标注，方便直接查阅。

### Coding Agent
BR-01, BR-02, BR-05, BDI-02, IS-02, EM-01, EM-04, MC-02

### Research Agent
BR-01, BR-02, BR-03, BDI-01, BDI-04, BDI-05, IS-01, IS-03, MC-01, MC-03, MC-04

### Browser/Desktop Agent
BDI-01, BDI-02, BDI-04, IS-01, IS-02, EM-01, EM-03, EM-04, EM-05, MC-02

### Enterprise Workflow Agent
BR-04, BR-05, BDI-03, IS-02, EM-04, MC-02, VA-04

### Companion Agent
BR-02, BDI-04, BDI-05, IS-04, VA-01, VA-02, VA-03, VA-04

### Creative Agent
BR-02, BR-03, EM-02, IS-04, MC-04, VA-04

### Security Agent
BDI-01, EM-03, EM-04, MC-01, MC-03, MC-04

### Ops/SRE Agent
BR-04, BR-05, BDI-01, BDI-02, BDI-03, IS-02, EM-03, MC-02

### Data/BI Agent
BDI-01, BDI-04, BDI-05, IS-01, IS-03, MC-01, MC-03, MC-04

### Personal Memory Agent
BR-02, BDI-04, BDI-05, IS-01, VA-01, VA-02, VA-03

### Embodied Robot Agent
BDI-01, BDI-02, BDI-03, IS-01, IS-02, IS-03, EM-01, EM-02, EM-03, EM-04, EM-05, MC-01, MC-02

### Agent Platform
BR-01, BR-04, BR-05, EM-02, EM-03, IS-05, VA-04

---

## 使用指南

1. **找到你的品类对应的列**——或直接使用上方"品类高风险原则速查"。
2. **关注所有标注 H 的行**——这些是你需要优先在架构中防护的原则。
3. **对照 `concepts/foundations/PRINCIPLE-INDEX.md`** 了解每条原则的详细内容和运行时义务。
4. **对照 `categories/<type>/design-decisions.md`** 检查是否已有对应的防护措施。
5. **如果某个 H 原则没有对应防护**——这就是你的架构盲区，需要补充设计决策或增加 eval fixture。

---

## 方法论说明

本热力图基于以下分析维度综合判断违反概率：

- **任务特征**：长任务 vs 短任务、写操作 vs 只读操作、确定性 vs 模糊性
- **环境特征**：沙箱 vs 生产、单工具 vs 多工具、可验证 vs 不可验证
- **交互特征**：单轮 vs 多轮、单用户 vs 多用户、短期 vs 长期关系
- **风险后果**：违反后的影响严重性（安全、数据、用户信任）

每个 H 标注意味着"该品类的典型使用场景中，如果不做专门防护，此原则有较高概率被违反"。M 和 L 不代表可以忽略，只代表相对优先级较低。

---

## 延伸阅读

- `./PRINCIPLE-INDEX.md` — 28 条原则完整定义与运行时义务
- `./value-and-alignment.md` — VA 系列原则的哲学基础
- `../../categories/README.md` — 品类索引与成熟度
- `../../toolkit/review-checklist.md` — 架构评审 checklist
- `./principle-obligation-eval-map.md` — 原则 → 义务 → eval 映射
