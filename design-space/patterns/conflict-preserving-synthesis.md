# Conflict-Preserving Synthesis

> **Evidence Status** — synthesized. 来自 research、world-state、memory 等多类场景中"来源冲突但必须交付"的共同问题，属于经过多个项目验证的中等成熟度模式。

模型很擅长把多个来源压成一段顺滑文字，但这恰恰制造了一个危险：

> 冲突没有被解决，只是被写作技巧掩盖了。

Research Agent、Ops Agent、Workflow Agent 都可能遇到这类情况——两个来源给出不同数字，一方来源已过期而另一方刚更新，原始描述存在语义歧义，或者内部记录和外部状态不一致。如果模型默认行为是"合并成一段流畅文字"，用户就会拿到一个看似确定、实际含混的结论。

## 解法

在冲突真正被解析之前，不允许提前合并成单一确定结论。默认做法是：

1. **保留冲突**——标注冲突类型（事实性、时序性、定义性、范围性、解析歧义）。
2. **区分已知与待验证**——说明哪部分可以确定，哪部分需要进一步核实。
3. **触发后续动作**——发起额外搜索、刷新数据源、或请求人类判断。

## ConflictRecord

每个冲突用结构化记录追踪：

```yaml
conflict_id: string
subject: string
claims:
  - claim_id: string
    source_ref: string
    value: any
    freshness: datetime|null
conflict_type: factual | temporal | definitional | scope | parsing
resolution_state: open | partially_resolved | resolved | escalated
next_action: refresh | verify | ask_user | preserve_in_output
```

`resolution_state` 和 `next_action` 是核心字段：前者表示冲突当前的处理进度，后者指明下一步该做什么。只有当 `resolution_state` 变为 resolved 时，合并才是安全的。

## 输出规则

- 不能因为用户想要一个简洁答案，就隐去关键冲突。
- 不能把旧来源和新来源自动做平均。
- 不能把"我猜更可能是 A"写成"就是 A"。
- 若必须交付，需把不确定区显式留在结论中。

## 各场景的默认处理

不同类型的 Agent 面对冲突时有不同的合理默认动作：Research Agent 应保留冲突并继续检索更多来源；Workflow Agent 应先刷新外部状态再做判断；Ops/SRE Agent 应标记冲突信号、避免在信息不一致时执行变更操作；Memory Agent 则不应把未解决的冲突事实写入稳定记忆层。

## 关联文档

- `citation-chain.md`
- `../../categories/research-agent/closed-loop.md`
- `../../architecture/planes/world-state/overview.md`
