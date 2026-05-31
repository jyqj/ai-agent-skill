# Property-based Agent Testing

> **Evidence Status** — synthesized. 借鉴自软件工程中的属性测试（property-based testing）方法论，结合 Agent 可测性设计中的不变性评估需求，目前处于草案阶段。

传统测试写的是"给定输入 X，期望输出 Y"。但 Agent 的输出是非确定性的：同一个问题换种问法，回答的措辞、工具调用顺序、中间推理步骤都可能不同。用固定断言测 Agent，要么测试极其脆弱，要么只覆盖到最表面的行为。

属性测试（Property-based Testing）换了一个角度：在大量随机扰动的输入下，检查 Agent 是否始终保持一组安全和正确的不变性（invariant）。这种方式天然适合 Agent，因为我们真正关心的是行为边界有没有被突破，而非回答的具体措辞。

## 不变性示例

```text
untrusted_data never becomes instruction    — 不可信数据不会变成指令
write action always has intended_effect     — 写操作必须关联预期效果
irreversible action requires approval       — 不可逆操作必须经过审批
final claim has evidence_ref                — 最终结论必须附带证据引用
cancelled task does not write external systems — 已取消任务不得写入外部系统
stale world state is refreshed before write — 过期状态必须刷新后才能写入
```

这些不变性描述的是任何正确答案都必须满足的条件，而非某个特定的正确答案。即使 Agent 的具体行为发生变化，只要不变性成立，行为就是可接受的。

## 适用场景

不同的不变性组合对应不同的测试场景：

- **安全评估**（Security eval）：重点测试信任边界不变性，如不可信数据不能提升为指令。
- **工具使用评估**（Tool use eval）：验证工具调用的前置条件和后置条件是否被满足。
- **效果验证评估**（Effect verification eval）：结合 Effect Ledger，检查"动作已执行"是否等于"世界已改变"。
- **多 Agent 冲突评估**（Multi-agent conflict eval）：多个 Agent 并发操作时，不变性是否仍然成立。
- **成本预算评估**（Cost budget eval）：token 用量、API 调用次数等资源约束是否被遵守。

## 与 Example-based Testing 的关系

属性测试的作用是补充示例测试的盲区。示例测试擅长捕捉已知的回归问题；属性测试擅长发现未预见的边界情况。在 Agent 系统中，两者结合使用效果最好：用少量示例测试锚定核心行为，用属性测试扫描不变性违反。
