# Feature List Progress

> **Evidence Status** — synthesized. 源自多个项目中 Agent 过早宣布完成的共同问题，是一种轻量的进度追踪约定。

Agent 在长任务中容易犯两个错误：过早宣布完成，或者忘记哪些子任务还没做。特性列表进度（Feature List Progress）是一个简单的对策：用结构化的任务列表跟踪每个子目标的状态，并且限制 Agent 只能更新状态，不能修改目标定义。

## 机制

任务列表由用户或系统定义 `title` 和 `success_criteria`，Agent 不可删除或改写这些字段。Agent 能做的是更新 `status`、填写 `evidence` 和添加 `notes`。完成一个特性前必须填写 evidence——这迫使 Agent 拿出证据而不是仅凭"感觉做完了"来标记完成。

```json
{
  "features": [
    {
      "id": "F1",
      "title": "Add login validation",
      "status": "in_progress",
      "success_criteria": ["invalid email rejected"],
      "evidence": []
    }
  ]
}
```

最终的 Stop Gate 会检查所有 required feature 的状态，只有全部满足退出条件才允许交付。这从机制上杜绝了"遗漏子任务"和"无证据完成"两类问题。
