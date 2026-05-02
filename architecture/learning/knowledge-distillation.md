# Knowledge Distillation

> **Evidence Status** — grounded. Voyager skill library 从长 trace 中提炼 executable skill；Generic Agent 在 self-evolution 中将冗长执行记录压缩为可复用函数。直接存储原始 trace 既浪费 token 又降低命中精度。

## 问题

一次成功的复杂任务可能产生 30+ 步 trace，但其中包含：

- 试错步骤（走错路又退回来）
- 环境探索（`ls`、`grep` 等信息收集）
- 重复验证（多次运行同一测试）
- 上下文特定的路径、变量名、配置值

直接将整条 trace 当作 skill 使用会导致：过长无法放入 context、过于特定无法泛化、包含错误路径误导后续决策。

知识蒸馏（Knowledge Distillation）的目标是将长 trace 压缩为短小、泛化、可验证的 skill candidate。

## 蒸馏管道（Distillation Pipeline）

```text
raw_trace (30+ steps)
  → step classification          # 分类每一步的角色
  → critical path extraction     # 提取关键路径
  → precondition induction       # 归纳前置条件
  → verification distillation    # 提炼验证方法
  → skill candidate              # 输出候选 skill
```

### Step 1: 步骤分类

将 trace 中每一步标记为以下类型之一：

| 类型 | 定义 | 蒸馏动作 |
|---|---|---|
| Decision（决策步） | 选择方案、确定策略 | 保留，提取决策依据 |
| Execution（执行步） | 实际修改文件、调用工具 | 保留核心操作，丢弃探索性尝试 |
| Verification（验证步） | 运行测试、检查输出 | 提炼为验证条件 |
| Exploration（探索步） | 搜索文件、阅读文档 | 转化为前置条件描述 |
| Backtrack（回退步） | 撤销错误尝试 | 丢弃，但记录为 anti-pattern |

### Step 2: 关键路径提取

从分类结果中提取最短成功路径：

```yaml
critical_path:
  - step: "识别问题根因在 X 模块"
    type: decision
    evidence: "错误日志指向 X.ts:42"
  - step: "修改 X 模块的 Y 函数"
    type: execution
    detail: "将条件判断从 A 改为 B"
  - step: "运行相关测试确认修复"
    type: verification
    command: "npm test -- --grep X"
```

### Step 3: 前置条件归纳

从 exploration 步骤中归纳出 skill 适用的前置条件：

```yaml
preconditions:
  - "项目使用 TypeScript >= 5.0"
  - "存在 X 模块且暴露 Y 接口"
  - "测试框架为 vitest 或 jest"
```

### Step 4: 验证方法提炼

从 verification 步骤中提炼出可复用的验证方法，去除硬编码值：

```yaml
verification:
  - method: "运行受影响模块的单元测试"
    success_criteria: "全部通过，无新增 warning"
  - method: "检查修改点的类型安全"
    success_criteria: "tsc --noEmit 无错误"
```

## 自动 vs 人工辅助蒸馏

| 维度 | 自动蒸馏 | 人工辅助蒸馏 |
|---|---|---|
| 适用场景 | 高频重复任务、模式清晰 | 低频复杂任务、首次出现的问题类型 |
| 优势 | 速度快、无需人工介入 | 泛化质量高、能捕捉隐性知识 |
| 风险 | 可能保留无关步骤、过拟合特定 trace | 人工成本高、主观偏差 |
| 推荐策略 | 自动蒸馏 + 人工审核 | 仅用于高价值 / 高风险 skill |

## 蒸馏质量评估

| 指标 | 计算方式 | 合格阈值 |
|---|---|---|
| 压缩比 | 原始步骤数 / 蒸馏后步骤数 | >= 3x |
| 泛化度 | 在不同项目上的适用率 | >= 0.5 |
| 完整性 | 按蒸馏 skill 执行能否复现成功 | 100%（必须通过 replay 验证） |
| 无害性 | 是否引入 anti-pattern 或有害路径 | 零容忍 |

## 关联文档

- `overview.md` — 学习类型总览
- `skill-governance.md` — 蒸馏产物进入 skill 库后的治理与冲突检测
- `safety-guardrails.md` — 蒸馏产物的安全审查
- `../../design-space/patterns/skill-crystallization.md` — 结晶模式
