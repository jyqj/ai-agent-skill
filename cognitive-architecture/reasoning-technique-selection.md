> **已迁移**：本文件已迁移至 `../paradigms/reasoning-technique-selection.md`。以下内容保留为存档，权威版本请查阅迁移目标。

# Reasoning Technique Selection

> **Evidence Status** — synthesized. Gulli (2025) *Agentic Design Patterns* Ch17 + reasoning-modes.md 互补。

> **与 reasoning-modes.md 的关系**：reasoning-modes.md 描述推理的认知基础（演绎/归纳/溯因/类比/因果/反事实）。本文聚焦 **LLM 推理技术的工程选择**——给定任务特征，选择哪种推理技术实现。

## 推理技术全景

```text
                    ┌─── CoT (Chain-of-Thought)
                    │       └─── ToT (Tree-of-Thought)
     单 Agent ──────┤
                    ├─── Self-Correction (反思精化)
                    ├─── PAL (Program-Aided Language)
                    └─── ReAct (Reasoning + Acting)

                    ┌─── CoD (Chain of Debates)
     多 Agent ──────┤       └─── GoD (Graph of Debates)
                    └─── MASS (Multi-Agent System Search)

     训练时 ────────── RLVR (RL with Verifiable Rewards)
```

## 技术详解

### 1. Chain-of-Thought (CoT)
- **机制**：分解复杂问题为中间推理步骤序列
- **优势**：透明、可审计、通用性强
- **适用**：多步推理、算术、常识推理、符号操作
- **限制**：线性路径，无法回溯

### 2. Tree-of-Thought (ToT)
- **机制**：在 CoT 基础上探索多个分支，形成树形推理结构
- **优势**：支持回溯、自纠正、全局最优搜索
- **适用**：策略规划、复杂决策、多约束满足
- **成本**：比 CoT 高 N 倍（N = 分支因子）

### 3. Self-Correction
- **机制**：生成 → 内部评审 → 识别缺陷 → 精化 → 输出
- **优势**：内建质量控制，减少幻觉
- **适用**：内容生成、代码编写、任何质量敏感输出
- **限制**：多轮精化增加延迟和成本

### 4. PAL (Program-Aided Language)
- **机制**：LLM 生成代码 → 执行代码 → 将结果转为自然语言
- **优势**：精确计算、确定性结果
- **适用**：数学问题、数据操作、逻辑操作、需要精确计算的任何任务
- **依赖**：需要代码执行环境（沙箱）

### 5. ReAct (Reasoning + Acting)
- **机制**：Thought → Action → Observation → Thought...（交错循环）
- **优势**：融合推理与环境交互，动态适应
- **适用**：需要工具交互、信息检索、多轮环境反馈的任务
- **注意**：循环可能不收敛 → 需要最大步数限制

### 6. Chain of Debates (CoD)
- **机制**：多个模型/Agent 提出方案 → 相互批评 → 反论证 → 共识
- **优势**：减少单一偏差，增强鲁棒性
- **适用**：主观判断、有争议的问题、需要多视角的决策
- **成本**：N 个参与者 × M 轮辩论

### 7. Graph of Debates (GoD)
- **机制**：论点为节点、关系为边的非线性网络，支持动态分支和自适应合并
- **优势**：处理高度复杂的争论，结论源于最强支持的论点集群
- **"良好支持"定义**：地面真实 + 搜索验证 + 多模型共识
- **适用**：科学争议、复杂策略评估、多源信息综合

### 8. MASS (Multi-Agent System Search)
- **机制**：自动化 MAS 设计优化，三阶段——块级提示 → 拓扑 → 系统编排
- **优势**：自动发现最优多 Agent 配置
- **适用**：大规模 MAS 系统设计、Agent 组合优化

### 9. RLVR (RL with Verifiable Rewards)
- **机制**：训练时通过可验证答案（数学、代码测试）的奖励信号，训练"推理模型"
- **特征**：可变"思考时间"——困难问题自动分配更长推理链
- **产物**：推理模型（如 o1、DeepSeek-R1）
- **注意**：训练时技术，不是推理时可选的技术

## 选择决策树

```text
任务需要精确计算？
  ├─ 是 → PAL
  └─ 否 → 任务需要工具交互？
              ├─ 是 → ReAct
              └─ 否 → 需要多视角验证？
                        ├─ 是 → 参与者 ≤ 3？
                        │         ├─ 是 → CoD
                        │         └─ 否 → GoD
                        └─ 否 → 问题有唯一正确答案？
                                  ├─ 是 → 问题复杂度高？
                                  │         ├─ 是 → ToT
                                  │         └─ 否 → CoT
                                  └─ 否 → 质量敏感？
                                            ├─ 是 → Self-Correction
                                            └─ 否 → CoT (default)
```

## Scaling Inference Law

核心原则：模型性能随推理时计算资源增加而可预测提升。

| 维度 | 投入更多 | 预期收益 |
|---|---|---|
| 推理步数 | 更长 CoT | 更准确的中间推导 |
| 分支数 | 更多 ToT 分支 | 更高概率找到最优路径 |
| 精化轮次 | 更多 Self-Correction 迭代 | 更高输出质量 |
| 工具调用轮次 | 更多 ReAct 循环 | 更完整的信息收集 |

**约束**：收益递减 + 成本线性增长 → 需要与 Cost Plane 协调设定上限。

## 与 Plane 的设计影响

| Plane | 影响 |
|---|---|
| Cost | 技术选择直接决定推理成本（ToT >> CoT，CoD >> 单 Agent） |
| Execution | PAL 需要沙箱；ReAct 需要工具接口 |
| Prompting | 不同技术需要不同 prompt 结构（CoT 需要示例链、ReAct 需要工具描述） |
| Orchestration | CoD/GoD/MASS 需要多 Agent 编排 |
| Observability | 推理步骤必须记入 trace 以支持审计 |

## 参考

- Gulli, A. (2025). *Agentic Design Patterns*, Ch17: Reasoning Techniques.
- Wei et al. (2022). "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"
- Yao et al. (2023). "Tree of Thoughts: Deliberate Problem Solving with Large Language Models"
- Yao et al. (2023). "ReAct: Synergizing Reasoning and Acting in Language Models"
- `reasoning-modes.md` — 推理的认知基础（演绎/归纳/溯因/类比/因果/反事实）
- `paradigms/reasoning-paradigms.md` — 推理的组织方式
