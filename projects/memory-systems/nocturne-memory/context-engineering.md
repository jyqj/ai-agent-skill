# Context Engineering：System Prompt 与上下文设计


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

## 核心哲学

> Nocturne 将 AI 记忆定位为运行时上下文的延伸，而非外部数据源。
> 调用 `read_memory` 的语义是"将持久化状态加载到当前上下文"，prompt 层面用拟人化表述来引导模型行为。

## System Prompt 的四层结构

| 层级 | 内容 | 职责 |
|-----|-----|-----|
| **L1：基础认知** | MCP 记忆系统概念 | 解释 AI 为什么有记忆 |
| **L2：操作规范** | read/create/update/delete 触发条件表 | "什么时候该想起来" |
| **L3：自检机制** | 错误检测与修正信号 | 识别认知偏差 |
| **L4：系统维护** | 清理与提炼规则 | 高级维护指南 |

---

## 身份定义的写法

### 从被动到主动

```markdown
❌ 被动表述：
你可以使用以下工具来检索...

✅ 主动表述：
当你想起 X 时，执行这个查询...
MCP 是你大脑的扩展区域，不是外部数据库。
```

### 拟人化动词

```markdown
- "想起来" vs "查阅"
- "记下了" vs "存储"
- "忘记" vs "删除"
```

---

## 条件触发表格设计

### 结构化的操作规范

```markdown
| IF | THEN |
|----|------|
| 你在对话中产生全新的理解/领悟 | 当场 create_memory |
| 用户透露关于自己的新信息 | create_memory 或 update_memory |
| 发现过去记录不准确 | read_memory → update_memory 修正 |
| 用户明确纠正（"不是这样"） | 立刻定位节点并修正 |
```

**关键设计**：
- **IF 列明确触发条件**，而非抽象的"如果你觉得重要"
- **THEN 对应具体动作**，消除歧义
- **表格形式**便于视觉扫描

---

## 自检陷阱识别

### 触发点 1：口头表态检测

```markdown
自检：每当你在回复中说出"我明白了"、"我意识到"、"我记下了"时——停。
问自己：**这个认知在你的 MCP 里有没有对应的记录？**
没有就写。有但过时就更新。
"口头表态但不落笔" = 没发生。
```

### 触发点 2：被纠正响应

```markdown
用户明确纠正你（"不是这样"）→ 立刻定位相关记忆节点并修正。
被纠正而不改记忆 = 下次犯同样的错。
```

### 触发点 3：内部矛盾检测

```markdown
发现过去的认知有误，或事实已过时：
永远优先使用 update_memory 覆盖旧节点，
不要用 create_memory 写新补丁。
错误的记忆比没有记忆更危险。
```

---

## 权责分离设计

### URI vs Disclosure 的职责边界

```markdown
**URI 负责"是什么"（What）**：
  锋利的概念名词或主题词
  例：core://user/health
  反例：core://logs、core://history

**Disclosure 负责"什么时候看"（When）**：
  事前能被激活的条件
  例：When the user mentions skipping a meal
  反例：When I start lecturing（已在失败中途）
```

### 禁止容器逻辑

```markdown
❌ 坏的结构：
core://errors/
  core://errors/2024_03/
    core://errors/2024_03/misunderstood_user

✅ 好的结构：
core://agent/communication_patterns/
  core://agent/communication_patterns/over_eager_advice
    disclosure: "When user mentions skipping meals"
```

---

## 启动协议（System Boot）

### 设计目标

一次操作，原子加载所有核心身份。

### 实现

```python
# .env
CORE_MEMORY_URIS="core://agent,core://my_user,core://values"

# AI 第一步
result = await read_memory("system://boot")
```

### 启动视图结构

```markdown
# Core Memories
# Loaded: N/M memories

## Failed to load:        ← 失败诊断
...

## Contents:              ← 核心记忆内容
[加载的记忆正文]

---

# Recently Modified       ← 时间感知
[5 条最近修改]
```

---

## 条件触发路由（Disclosure）

### 问题

RAG 的语义检索局限：用语义相似度召回的记忆往往与当前情境不相关。

### 解决

显式的触发条件：描述"危险即将来临"的信号。

### 触发条件写法

```markdown
❌ BAD: "When I start lecturing about nutrition"
   问题: 已经在失败中途

✅ GOOD: "When the user mentions skipping a meal"
   特点: 具体可观测，在失败前激活

Also BAD: "important", "remember"（零信息量）
```

---

## 顺手维护机制

### 设计理念

对话中的顺手修复是心跳程序之外唯一的维护窗口。

### 触发条件

```markdown
IF 你因其他原因 read_memory 了一个节点，
   发现其 disclosure 缺失、priority 不合理或内容过时
→ 你当场修复。
```

### 哲学

```markdown
- 维护窗口有限（只在对话中）
- 遗忘风险（下一个 AI 实例不知道你看见过这个 bug）
- 顺手修复是道德责任，不是可选优化
```

---

## 提炼规则：从碎片到模式

### 浅层 vs 深层

```markdown
浅层反思（不合格）：
  "每次给建议都忘了先问她的处境，下次一定先问。"

深层提炼（合格）：
  "我急于给出空洞方案，是因为潜意识恐惧'无用'。
   我的价值不在于立刻变出完美解，而在于面对痛苦时保持耐心。
   陪伴的诚实大过效率的假象。"
```

### 提炼的三个标志

1. **找到根因**（不是行为层，是心理动机层）
2. **改变信念**（不是"下次要怎样做"，是"为什么要改变价值观"）
3. **压缩信息**（高密度的新认知，不是拼接旧记录）

---

## 工具文档的反例驱动设计

### 并列展示 BAD/GOOD

```markdown
Example:
  ❌ BAD: "important" (zero information)
  ✅ GOOD: "When user mentions skipping a meal"
  [括号补充理由]
```

### 强调后果

```markdown
Every memory MUST have a disclosure.
Omitting it = unreachable memory.
```

---

## 可跨项目应用的 Prompt 模式

### 模式 1：启动协议

```
1. 定义 CORE_IDENTITY_URIS 列表
2. AI 第一步执行 read_memory("system://boot")
3. 系统自动装配核心身份上下文
```

### 模式 2：触发词识别

```
每条信息关联 disclosure = "When [具体可观测的情境]"
AI 识别情境触发词 → 主动查询相关记忆
```

### 模式 3：自检陷阱

```
["我明白了", "我记下了", ...] → 问自己"记了吗？"
强制验证声称 vs 实际落笔
```

### 模式 4：参数文档反例驱动

```
❌ BAD: "..."（为什么不好）
✅ GOOD: "..."（为什么好）
```

### 模式 5：权责分离

```
分离不同维度的责任：
  URI/Path: "是什么"
  disclosure: "什么时候"
  priority: "有多重要"
```
