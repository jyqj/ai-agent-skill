# Human-Agent Interaction Plane
>
> **所属域**：6. Coordination — Human-Agent 交互
>
> **Evidence Status** — synthesized. Autonomy Level、Control Policy、Approval、Memory Feedback、Progress Reporting 等实践需求；本知识库把人机交互从”审批按钮”提升为独立运行时层。

**Principle Refs**: MC-01, EM-03 — 必须向用户显式传达不确定性；用户本身也是环境约束的一部分

## 1. 定义

Interaction Plane 负责 Agent 与用户之间的中断、确认、审批、纠错、教学、进度报告、拒绝解释和信任升级。

它回答的问题不是“用户能不能批准”，而是：

```text
用户何时需要被打扰？
Agent 该暴露多少信息？
用户如何纠正 Agent？
用户如何逐步授权更高自治？
Agent 如何说不并保持可理解？
```

## 2. InteractionEvent 类型

| 类型 | 触发器 | 输出 |
|---|---|---|
| progress | milestone、长任务、等待外部系统 | 简短进度 + 下一步 |
| clarification | 关键歧义、目标不完整 | 单个最关键问题或候选项 |
| approval_request | 高风险、不可逆、越权边缘 | 影响说明 + 选项 + 默认安全行为 |
| correction | 用户指出错误 | 更新 state / memory / plan |
| teaching | 用户表达偏好或规则 | proposed MemoryRecord / SkillRecord |
| budget_choice | 成本或时间接近阈值 | 质量-成本选项 |
| refusal | 不安全、不合规、不可验证 | 清楚原因 + 安全替代方案 |
| escalation | Agent 无法可靠完成 | 转人工或交付部分结果 |
| completion | 完成或部分完成 | 结果 + 证据 + 剩余不确定性 |

## 3. 交互原则

| 原则 | 含义 |
|---|---|
| Minimal Sufficient Interruption | 只问阻塞当前决策的最小问题 |
| Progressive Disclosure | 默认简洁，允许展开证据和 trace |
| User Control Surface | 用户可以暂停、取消、改目标、限制工具、调整预算 |
| Trust Calibration | 不假装确定，不隐藏风险，不过度打扰 |
| Teachability | 用户纠正应进入可审计状态，而不是只影响当前回复 |
| Refusal with Boundary | 拒绝要说明边界，不用空泛道歉替代设计 |

当原则之间发生冲突时，以用户对风险的知情权为最高优先级。例如 Trust Calibration 要求披露不确定性，而 Minimal Sufficient Interruption 要求减少打扰——此时应优先保证风险信息送达用户，再考虑精简交互形式。

## 4. 和其他模块的关系

| 模块 | 关系 |
|---|---|
| Control | approval_request 由 policy 触发，但 UX 由 Interaction 设计 |
| Memory | teaching / correction 可能生成 MemoryRecord，但需 provenance 和审批 |
| State | 用户取消、改目标、选择预算会改变 TaskCheckpoint |
| Cost | 预算接近上限时触发 budget_choice |
| Effects | 不可逆 effect 需要 approval 或 human_confirm |
| Observability | 每次交互写入 InteractionEvent 和 TraceEvent |

## 5. Stop Gate 中的交互检查

```text
是否有用户必须知道的风险？
是否有不可验证但可能影响交付的部分？
是否有用户纠正尚未应用？
是否有 pending approval？
是否有预算、范围或安全降级？
```

## 6. 子文件导航

| 文件 | 内容 | 关注点 |
|---|---|---|
| `intent-alignment.md` | 意图漂移检测、认知负载管理、多利益方冲突 | 用户意图与 Agent 理解的持续对齐 |
| `interruption.md` | 中断策略和时机选择 | 何时打扰用户、何时自主决策 |
| `progress-report.md` | 进度报告的设计 | 长任务中如何保持用户知情 |
| `teaching.md` | 用户教学与纠正 | 用户偏好和规则如何进入 Agent 状态 |
| `trust-escalation.md` | 信任升级的工程机制 | 阶段划分、升降级条件、授权范围 |
| `trust-dynamics.md` | 信任建设的理论框架 | 信任演化路径、破坏修复、品类差异、过度信任 |
| `cognitive-load.md` | 认知负荷与交互设计 | 输出信息密度、审批复杂度、进度频率、错误层次化 |
| `ux-patterns.md` | 具体的 UX 交互模式 | Progress Card、Approval Block、Evidence Drawer 等 |

## 7. 外部参考

- `../../../design-space/patterns/progressive-disclosure.md`
