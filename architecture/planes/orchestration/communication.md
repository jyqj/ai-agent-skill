# Agent Communication Protocol

> **Evidence Status** — synthesized. subagent、worker orchestration、output contract 等模式；本知识库对 Agent 间通信的统一协议抽象。

## 1. 为什么需要协议

多 Agent 协作不能只靠自然语言“你去做这个”。必须明确消息类型、权限范围、证据引用、世界状态引用、取消语义和冲突处理。

## 2. AgentMessage

```yaml
agent_message:
  message_id: msg_...
  conversation_id: conv_...
  sender_agent: coordinator
  receiver_agent: researcher
  message_type: task_request | observation | claim | plan | result | conflict | arbitration | heartbeat | cancel
  payload: object
  evidence_refs: []
  world_state_refs: []
  authority_scope: read_only | propose | act | verify | arbitrate
  ttl: duration|null
  correlation_id: string
```

## 3. 消息类型

| 类型 | 用途 | 必带字段 |
|---|---|---|
| task_request | 委派任务 | goal、scope、success_criteria |
| observation | 分享观察 | observation_refs、confidence |
| claim | 提出结论 | claim、evidence_refs |
| plan | 提出计划 | steps、risks、required_tools |
| result | 返回结果 | deliverable、verification_status |
| conflict | 报告冲突 | conflicting_refs、impact |
| arbitration | 仲裁决定 | decision、reason、authority |
| heartbeat | 长任务存活 | progress、blocked_on |
| cancel | 取消任务 | reason、compensation_needed |

## 4. 协议反模式

- Free-text Delegation：没有 success criteria。
- Evidence-free Result：worker 只说“完成了”。
- Authority Leak：read-only worker 被允许执行写动作。
- Silent Conflict：多个 Agent 结论冲突但 coordinator 直接合并。
