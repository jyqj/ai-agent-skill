# Knowledge Fitness Loop — 反馈机制设计

> **Evidence Status** — theoretical. 知识库自身尚未实际运行此反馈循环；设计基于 meta/audit 审计结果和 evaluation/eval-meta 的元评估思路。

## 1. 为什么知识库需要反向验证

这个知识库的核心主张之一是：Agent 必须做 effect verification——"工具返回 success 不等于任务完成"。但知识库自身缺少对等机制：

- **68% 的文件是 synthesized**，0% 是 production-validated。内容大多来自跨项目抽象，未经过使用者在真实场景中的验证。
- **内容与实践之间没有闭环**。知识库被读取后，没有结构化方式回收"哪些内容有用、哪些误导、哪些缺失"。
- **Evidence Status 只升不降**。缺少降级触发机制，过时内容可能长期保持高 status。

如果 Agent 需要 read-after-write 来验证效果，知识库也需要 read-after-use 来验证知识的有效性。Knowledge Fitness Loop 就是这个机制。

## 2. 反馈如何影响 Evidence Status 升降级

反馈是 Evidence Status 变更的**证据来源之一**，不是自动触发器。流程如下：

```text
使用者提交反馈
  → 反馈归档到 meta/feedback/reports/
  → 维护者分析反馈，判断证据质量
  → 如果构成升级/降级依据，更新目标文件的 Evidence Status
  → 更新 meta/audit/evidence-status-audit.md 中的分布数据
```

升降级的具体标准见 `evidence-upgrade-criteria.md`。

### 升级路径示例

一位使用者在生产环境中按照 `design-space/patterns/self-verification.md` 设计了效果验证，反馈报告包含具体项目、架构决策和结果数据。如果类似反馈累计达到升级门槛，该文件可以从 synthesized 升级为 grounded 或 prototype-validated。

### 降级路径示例

多位使用者反馈 `paradigms/reasoning-paradigms.md` 中的某个范式对比在实践中产生误导——按推荐选择了范式 A，但在该场景下范式 B 明显更优。维护者确认后，可以对该部分标注修正说明或降级相关 claim。

## 3. 反馈收集流程

### 3.1 提交方式

- **结构化反馈**：按 `feedback-template.md` 填写，提交到 `meta/feedback/reports/` 目录，文件名格式 `YYYY-MM-DD-<project-slug>.md`。
- **轻量反馈**：在相关文件的 issue 或 PR 中标注 `[feedback]` 标签，维护者定期归档。

### 3.2 反馈内容要求

最低要求：
1. 使用了哪个文件或模块
2. 在什么场景下使用
3. 结果是什么（有用 / 缺失 / 误导）

完整反馈还应包含：项目类型、Agent 品类、具体架构决策、效果数据。详见 `feedback-template.md`。

## 4. 反馈分析流程

```text
1. 收到反馈后，维护者在 7 天内完成初步分类：
   - 标记为 useful / missing / misleading / outdated
   - 关联到具体文件路径

2. 按季度汇总分析：
   - 哪些文件被高频引用且评价为 useful → 升级候选
   - 哪些文件被多次标记为 misleading → 降级候选或修正
   - 哪些主题反复出现 missing → 新文件创建候选

3. 维护者根据 evidence-upgrade-criteria.md 判断是否变更 Evidence Status

4. 变更记录写入 meta/feedback/changelog.md（按季度维护）
```

## 5. 归档结构

```text
meta/feedback/
├── README.md                        ← 本文件：设计思路
├── feedback-template.md             ← 结构化反馈模板
├── evidence-upgrade-criteria.md     ← Evidence Status 升降级标准
├── changelog.md                     ← 反馈驱动的变更记录（按季度）
└── reports/                         ← 归档的反馈报告
    └── YYYY-MM-DD-<slug>.md
```

## 6. 与其他模块的关系

| 模块 | 关系 |
|---|---|
| `meta/audit/evidence-status-audit.md` | 反馈分析结果反映到审计报告的 Evidence Status 分布 |
| `meta/guide.md` | guide 中引用本机制，说明反馈入口 |
| `evaluation/eval-meta/README.md` | eval-meta 评估评估框架，本机制评估知识库内容本身；互补 |
| `AGENTS.md` | 维护者工作约束中新增反馈处理职责 |
| `SKILL.md` Provenance / Trust 规则 | 反馈是 Evidence Status 变更的证据来源之一 |

## 7. 设计约束

- 反馈不自动触发任何变更。所有 Evidence Status 变更必须经过维护者判断。
- 匿名反馈可以接受，但有具体项目和数据的反馈权重更高。
- 反馈不替代项目分析。如果反馈涉及新项目的深度学习，应走 `meta/guide.md` 中的"新项目学习流程"。
- 反馈报告本身也有 Evidence Status，默认标注为 grounded（基于使用者的一手经验）。
