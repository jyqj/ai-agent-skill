# 多 Agent 死锁——当所有 Agent 都选择"最合理"的行动

> **Evidence Status** — grounded. 来自 MAST 分类法论文（NeurIPS 2025，1600+ 标注跟踪）和 ReputAgent 协调死锁研究。

---

## 场景

多个 LLM Agent 需要协作完成任务，各自独立决策后协调执行。

## 设计选择

- 采用"Bag of Agents"模式：多个独立 Agent 各自决策然后合并结果
- 无全局排序/优先级协议
- 无显式 leader election
- 每个 Agent 使用相同模型和相似 prompt

## 预期

多个 Agent 各自给出建议，合并后质量更高。

## 实际结果

### 系统性协调失败

MAST 研究（NeurIPS 2025）在 7 个主流 MAS 框架上收集 1600+ 标注跟踪，识别出 14 种独特失败模式。其中协调失败占 36.94%。关键发现：失败通常源于系统设计而非 LLM 自身。

> 来源: arxiv 2503.13657

### 趋同推理导致死锁

独立的 Agent 因使用相同模型，倾向于选择相同的"合理"行动。在需要互补选择的场景中（例如多角色分工、资源分配），这种趋同直接导致冲突。小组中死锁率高达 100%。

> 来源: ReputAgent

### "Bag of Agents"的 17 倍错误率

"Bag of Agents"模式——多个 Agent 独立执行后合并——的错误率是结构化编排的 17 倍。独立性假设在需要协调的任务上彻底失效。

> 来源: Towards Data Science

### 级联失败的指数级放大

单一 Agent 的错误输出传递给下游 Agent，触发盲重试。在 500 job/min 的负载下，每个 job 3 次额外重试 = 10 分钟内 15,000 次可避免的调用。

> 来源: Galileo

## 根因分析

**相同模型 + 相似 prompt = 相似决策。这不是随机的，是系统性的。**

- **趋同推理（Convergent Reasoning）**：相同模型的参数权重决定了在给定相似输入时，输出分布高度相似。当多个 Agent 面对同一个问题时，它们倾向于选择概率最高的同一个"合理"行动——而不是互补的不同行动
- **无仲裁机制**：当多个 Agent 选择冲突的行动时，没有人决定"谁让步"。系统停滞或进入活锁
- **隐式协调假设**：设计者假设 Agent 会"自然"分工，就像人类团队一样。但人类有社会规范、组织层级和即时沟通，LLM Agent 没有
- **缺少 Circuit Breaker**：级联失败 + 盲重试 = 指数级负载放大。一个 Agent 的错误不会被隔离，而是传播到整个系统

趋同推理的可视化：

```
Agent A (GPT-4, prompt P) -> 决策: "选方案 X"
Agent B (GPT-4, prompt P) -> 决策: "选方案 X"
Agent C (GPT-4, prompt P) -> 决策: "选方案 X"

需要的是: A->X, B->Y, C->Z (互补)
得到的是: A->X, B->X, C->X (趋同 -> 冲突)
```

## 教训

### 多 Agent 系统必须有显式协调协议

不能假设 Agent 会"自然"协调。需要显式的机制：

- **Leader election**：某个 Agent 被指定为协调者，负责分配任务和解决冲突
- **Priority protocol**：每个 Agent 有明确的优先级，冲突时高优先级的 Agent 的决策胜出
- **Turn-taking**：Agent 按顺序行动，而不是并行行动后尝试合并

### 增加决策多样性

使用不同模型或不同 prompt 避免趋同推理：

```yaml
agent_a:
  model: claude-3.5-sonnet
  role: "保守分析师，优先考虑风险"
agent_b:
  model: gpt-4
  role: "创新探索者，优先考虑机会"
agent_c:
  model: gemini-pro
  role: "实用主义者，优先考虑可行性"
```

不同模型 + 不同角色 prompt = 不同的决策分布 = 更高概率产生互补建议。

### "Bag of Agents"只适用于独立子任务

当子任务之间没有依赖时（例如并行翻译不同章节），Bag of Agents 是有效的。但当任务需要协调（例如资源分配、多角色分工），必须用 Coordinator-Worker 模式。

### Agent 间通信需要保护机制

- **Circuit breaker**：下游 Agent 连续 N 次收到异常输入时，停止处理并上报
- **Exponential backoff**：重试间隔指数增长，防止负载雪崩
- **死锁检测**：周期性检查是否有 Agent 组在互相等待

### 输入完整性检查

每个 Agent 的输入应有 integrity check：如果输入已损坏或不符合预期格式，拒绝处理而不是传播错误。"垃圾进垃圾出"在多 Agent 系统中会被放大为"垃圾进灾难出"。

---

## 关联文件

- `../../paradigms/collaboration-paradigms.md` — 协作范式
- `../../architecture/planes/orchestration/communication.md` — Agent 间通信
- `../../architecture/planes/concurrency/overview.md` — 并发和死锁
- `../../design-space/patterns/worker-orchestration.md` — Worker 编排模式
