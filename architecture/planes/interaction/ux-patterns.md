# Interaction UX Patterns

> **Evidence Status** — synthesized. progress reporting、approval、partial delivery、teaching/correction 等人机协作需求。

## 目标

把 Interaction Plane 从事件类型扩到更接近产品形态的 UX 约束。

## 常用模式

### 1. Progress Card

适合长任务。默认只展示：

- 当前阶段；
- 已完成什么；
- 下一步；
- 是否存在风险或等待；

不要把所有 trace 原样倒给用户。

### 2. Approval Block

高风险动作请求批准时，应同时给出：

```text
要做什么
→ 为什么现在需要做
→ 可能影响
→ 如果不批准的默认安全行为
```

### 3. Evidence Drawer

默认回答简洁，但允许用户展开：

- citations / sources
- effect verification evidence
- reasoning summary / plan changes
- remaining uncertainty

### 4. Correction Receipt

当用户纠正 agent 时，系统应回显：

```text
收到的纠正内容
→ 影响了什么 state / memory / plan
→ 何时生效
```

### 5. Partial Completion Banner

当任务只完成了一部分时，不要伪装完成。应显示：

- 已完成部分；
- 未完成原因；
- 是否建议继续；

## 信息密度建议

| 场景 | 默认信息密度 |
|---|---|
| 快速问答 | 低 |
| 长任务 progress | 中 |
| approval / refusal | 中高 |
| research report | 主文低，evidence drawer 高 |
| browser/high-risk action | 中高 |

## 关联文档

- `overview.md`
- `../../../design-space/patterns/progressive-disclosure.md`
- `../../../categories/research-agent/closed-loop.md`
