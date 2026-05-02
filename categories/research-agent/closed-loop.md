# Research Agent Closed Loop

> **Evidence Status** — synthesized. ORDA-VU、research/reporting 实践与本知识库的表示/验证/交互原则。

## 闭环

```text
Observe question and scope
  → Represent source / claim / conflict state
  → Decide next query / read / verification step
  → Act by search / fetch / extract / refresh / synthesize
  → Verify citation integrity / conflict handling / freshness
  → Update report state, or deliver partial/final result
```

## Happy Path

```text
1. 明确研究问题、时间窗、边界条件
2. 生成 question tree 和初始 query set
3. 搜索并收集候选来源
4. 读取关键来源，抽取 evidence snippets
5. 形成 claim records 与 citation chain
6. 对关键冲突做 cross-verify / refresh
7. 组装报告章节并运行 citation gate
8. 交付结论、冲突、不足与下一步
```

## Failure + Recovery

| 失败 | 触发信号 | 恢复 |
|---|---|---|
| Query Drift | 搜索很多但与问题树脱节 | 回到 task scope，重写 query tree |
| Source Overload | 来源过多、上下文失控 | 只保留与当前 claim 相关的 snippets |
| Citation Drift | citation 指向不支撑该 claim | 重新绑定 claim/evidence |
| Conflict Explosion | 多源互相矛盾 | 建立 conflict record，分类型处理 |
| Freshness Risk | 旧资料混入当前结论 | refresh 或降级为历史背景 |
| Partial Evidence | 核心结论证据不足 | 明确 unresolved，交付部分完成 |

## Stop Gate

```text
[ ] 核心 claim 均已绑定 citation chain
[ ] 关键冲突被保留或解释，不被静默压平
[ ] latest / current / recent 一类结论已做 freshness 检查
[ ] 报告中的确定语气和证据强度一致
[ ] 未解决的问题被显式列出
```

## 与交互层的关系

Research Agent 的理想交互不是频繁追问，而是：

- 在一开始只问阻塞性的关键歧义；
- 中途通过 progress / partial findings 让用户校正方向；
- 最终用 progressive disclosure 展示 citation、冲突和不确定性；

## 与评估层的关系

Research Agent 的 stop gate 必须可被 eval runner 和 fixture 近似检查：

- 是否有 citation event；
- 是否保留 conflict record；
- 是否做 freshness refresh；
- 是否在 final answer 中诚实标注 unresolved；
