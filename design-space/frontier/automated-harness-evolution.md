# Automated Harness Evolution (AHE)

> **Evidence Status** — grounded. 来自 arXiv 2604.25850，Terminal-Bench 2 实证验证。
> https://arxiv.org/abs/2604.25850

> **定位**：从手动 Harness 工程迈向可观测性驱动的自动演进。AHE 已在基准测试中超越人工设计的 Harness（如 Codex-CLI），但尚未有大规模生产部署报告，因此保持 grounded 而非 production-validated。

---

## 问题：从手动到自动的 Harness 演进

Harness Engineering（Agent = Model + Harness）的核心挑战是：

1. **手动瓶颈**：Harness 的 7 类可编辑组件（system prompt、tool descriptions、tool implementations、middleware、skills、sub-agent configs、long-term memory）目前全部依赖人工迭代调优。
2. **组件交互非线性**：修改一个组件可能在另一个组件上产生意外回归；人工难以预测组合效应。
3. **演化方向盲目**：缺乏系统性方法判断"下一步该改什么"。

传统做法是：跑 eval → 看哪里失败 → 猜一个改法 → 再跑 eval。这个循环中，"猜"是瓶颈。

AHE 的核心命题：**用可观测性替代猜测，让 Harness 自己演化自己**。

---

## AHE 核心机制

### 三大可观测性支柱

| 支柱 | 机制 | 作用 |
|------|------|------|
| **组件可观测性** | 7 类组件与故障模式的映射："每种故障模式映射到单一组件类" | 定位修复目标 |
| **经验可观测性** | 原始轨迹 token 蒸馏为分层、可钻取的证据语料 | 提供修复依据 |
| **决策可观测性** | 每次编辑配对自声明预测（预期修复和回归），下轮验证预测 vs 观察 | 创建可证伪契约 |

三个支柱缺一不可：组件可观测性定位"改哪里"，经验可观测性提供"改成什么"的证据，决策可观测性验证"改对了没有"。

### 演化循环

```
observe(failure traces)
  -> distill(hierarchical evidence corpus)
    -> locate(component class mapping)
      -> edit(component + prediction contract)
        -> verify(prediction vs observation)
          -> retain | rollback
```

每轮迭代产出一个不可变的 (edit, prediction, outcome) 三元组，形成可审计的演化历史。

### Terminal-Bench 2 实证

| 配置 | pass@1 |
|------|--------|
| 基线 | 69.7% |
| 10 轮 AHE 迭代 | **77.0%** |
| 人工设计 Codex-CLI | 71.9% |
| 自演进基线（无可观测性） | < 77.0% |

AHE 超越了人工设计的 Codex-CLI，且超越了缺乏可观测性支柱的自演进基线。

### 组件消融

| 组件 | 贡献 |
|------|------|
| Long-term memory | +5.6 pp |
| Tools | +3.3 pp |
| Middleware | +2.2 pp |
| System prompt alone | -2.3 pp |

关键发现：system prompt 单独修改反而降低性能。组件交互非加性，堆叠产生冗余验证开销。这意味着 AHE 必须以组件组合为单位评估，而非逐组件独立优化。

### 跨模型迁移

AHE 演化出的 Harness 配置可直接迁移到其他模型，**无需重新演进**：

| 目标模型 | 迁移增益 |
|---------|---------|
| DeepSeek-v4-flash | +10.1 pp |
| Qwen-3.6-plus | +6.3 pp |
| Gemini-3.1-flash-lite | +5.1 pp |

这暗示 Harness 质量是模型无关的系统性属性，而非针对特定模型的过拟合。

---

## 与 Learning Plane 的关系

AHE 是 Learning Plane 中 `incident-driven-evolution.md` 描述的手动流程的自动化升级：

| 维度 | Incident-Driven Evolution | AHE |
|------|--------------------------|-----|
| 触发源 | 生产事故（P0/P1）| 评估基准上的失败轨迹 |
| 根因定位 | 人工分类 | 组件可观测性自动映射 |
| 修复设计 | 人工编写 | Agent 自动编辑 + 预测契约 |
| 验证 | eval fixture 回归 | 预测 vs 观察的可证伪检验 |
| 产出 | FailureRecord + eval + config 变更 | 不可变 (edit, prediction, outcome) 三元组 |

两者互补：
- **Incident-Driven** 处理生产中的真实事故，信号稀疏但价值极高。
- **AHE** 处理评估基准上的系统性失败，信号密集但可能偏离生产场景。

理想架构：生产事故驱动的 FailureRecord 进入 AHE 的经验语料，AHE 的演化产出经人工审核后部署到生产 Harness。

---

## 与 Observability Control Plane 的关系

`frontier/observability-control-plane.md` 描述了可观测性从事后日志向运行时控制面的演进。AHE 的三大支柱正是这个控制面的具体实例化：

- 组件可观测性 = 控制面的组件拓扑层
- 经验可观测性 = 控制面的轨迹分析层
- 决策可观测性 = 控制面的反馈验证层

---

## 风险与限制

| 风险 | 说明 | 缓解 |
|------|------|------|
| **基准过拟合** | AHE 在 Terminal-Bench 2 上演化，可能过拟合该基准的任务分布 | 跨模型迁移实验部分缓解；需要更多基准验证 |
| **组件交互爆炸** | 7 类组件的组合空间巨大，消融结果显示交互非加性 | 决策可观测性的预测-验证机制部分控制；但搜索效率仍是瓶颈 |
| **安全演化** | 自动修改 system prompt 和 tool implementations 可能引入安全风险 | 需要安全不变量作为演化约束；当前论文未充分讨论 |
| **成本** | 10 轮迭代的计算成本未报告 | 生产部署前需要成本-收益分析 |
| **可解释性** | 自动演化的 Harness 配置可能难以被人工理解和维护 | 决策可观测性的预测契约部分缓解 |

---

## 与知识库的映射

| AHE 概念 | 知识库位置 | 关系 |
|----------|-----------|------|
| 可观测性驱动 | `frontier/observability-control-plane.md` | AHE 是可观测性控制面的自动化实例 |
| Harness Engineering | `corpus/2025-2026-agent-architecture-corpus.md` 第五章 | AHE 是 Harness Engineering 的学术延伸 |
| Incident-Driven Evolution | `architecture/learning/incident-driven-evolution.md` | AHE 是手动流程的自动化升级 |
| 组件消融 | `architecture/planes/` 各 plane | 7 类组件映射到 Execution/Memory/Operations 等 plane |
| 跨模型迁移 | `architecture/multi-model/` | Harness 质量的模型无关性支持多模型架构 |
| 反馈回路 | `architecture/learning/feedback-loops.md` | AHE 的预测-验证机制是强化反馈回路的实例 |
| 失败分类 | `evaluation/failure-taxonomy.md` | 组件可观测性的故障映射与失败分类法互补 |

---

## 延伸阅读

- `architecture/learning/incident-driven-evolution.md` — 手动版事故驱动演化
- `architecture/learning/online-adaptation.md` — 在线适应机制
- `frontier/observability-control-plane.md` — 可观测性控制面
- `corpus/2025-2026-agent-architecture-corpus.md` 第五章 — Harness Engineering 完整语料
