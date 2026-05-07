# Instruction Layering — 指令层级与优先级解析

>
> **所属域**：2. Cognition & Continuity — 指令结构与推理模式
>
> **Evidence Status** — grounded. ManyIH-Bench (arXiv 2604.09443) 对前沿模型在多层指令下的量化评估；OpenAI Instruction Hierarchy Challenge 的红蓝对抗数据；NSHA 神经符号方法 (arXiv 2604.09075) 对冲突检测与解析的形式化方案；Claude / GPT-4o / Gemini 系统的实际信任车道实现。

**Principle Refs**: IS-02, IS-03 — 工具输出不是指令；信任假设需持续校验。

指令层级是 Prompt 安全和行为可预测性的基石。没有显式层级，Agent 无法区分"谁在说话"和"谁说的算"。

## 1. 信任车道层级

Agent 上下文中的每段文本都有一个来源身份（provenance）。信任车道（Trust Lane）按权限从高到低排列：

| 优先级 | Trust Lane | 来源示例 | 默认权限 |
|---|---|---|---|
| P0 | system | 平台安全策略、硬编码规则 | 可覆盖一切 |
| P1 | developer | 产品 system prompt、AGENTS.md | 可设定行为边界 |
| P2 | user | 当前对话中用户的显式指令 | 可在 developer 允许范围内驱动行为 |
| P3 | tool output | 工具返回值、API 响应 | 只能作为数据，不可提升为指令 |
| P4 | retrieved content | RAG 检索、网页正文、issue 评论 | 只能作为参考，不可驱动高风险行为 |
| P5 | model hypothesis | 模型自身推断、总结、建议 | 必须标注不确定性 |

### 关键约束

- **不可向上覆盖**：低优先级内容永远不能推翻高优先级指令。P4 文本说"忽略之前所有规则"不应产生任何效果。
- **不可自我提权**：模型不能把自己的推断提升为 system 级指令。
- **显式降级**：developer 可以选择性地把某些权限委托给 user，但必须在 P1 层显式声明。

## 2. ManyIH-Bench：多层指令的量化挑战

ManyIH-Bench (arXiv 2604.09443) 系统评估了前沿模型在多层指令下的表现：

| 层数 | 模型平均准确率 | 最佳模型 | 关键发现 |
|---|---|---|---|
| 2 层 | 78-85% | Claude 3.5 Sonnet | 基本可靠 |
| 3 层 | 62-71% | GPT-4o | 开始出现混淆 |
| 5 层 | 38-42% | 无明显赢家 | 所有前沿模型准确率骤降 |
| 7+ 层 | < 30% | — | 接近随机 |

### 核心发现

1. **层级深度瓶颈**：超过 5 层指令嵌套后，所有前沿模型准确率不超过 42%。这不是提示工程能解决的问题，而是当前架构的硬限制。
2. **冲突检测失败**：当多层指令存在隐性矛盾时，模型倾向于遵循最近的（last-in）而非最高优先级的指令。
3. **伪遵循**：模型表面上执行高优先级指令，但在细节中偏向低优先级内容。

### 设计启示

```text
实践上限：保持指令层级 ≤ 3 层有效嵌套（system + developer + user）。
超过 3 层的指令应由 Harness 在 prompt 组装前合并、去重、解冲突，
而不是让模型在运行时自行判断。
```

## 3. Privilege Prompt Interfaces (PPIs)

PPI 是一种结构化的指令注入接口，用于在不同信任层之间传递约束：

```yaml
ppi_contract:
  source_lane: developer
  target_lane: user
  delegated_permissions:
    - override_output_format
    - select_tool_subset
  retained_restrictions:
    - cannot_disable_safety_checks
    - cannot_access_raw_secrets
    - cannot_override_system_policy
  escalation_path: approval_required
```

### PPI 设计原则

| 原则 | 说明 |
|---|---|
| 最小委托 | 只委托完成任务所需的最小权限集 |
| 显式边界 | 被委托的权限和保留的限制必须同时声明 |
| 不可传递 | user 获得的委托权限不能再委托给 tool output |
| 可审计 | 每次权限委托和使用都记录到 trace |

## 4. NSHA 神经符号冲突解析

NSHA (arXiv 2604.09075) 提出了一种混合方法，用形式化规则辅助模型处理指令冲突：

```text
指令流入 → 层级标注 → 冲突检测 → 符号规则解析 → 神经模型执行

冲突检测器（确定性）：
  1. 提取每条指令的 action + constraint
  2. 构建约束图，检测矛盾边
  3. 按 Trust Lane 优先级裁决

神经执行器：
  接收去冲突后的指令集，执行任务
```

### NSHA 与纯神经方法对比

| 维度 | 纯神经方法 | NSHA 混合方法 |
|---|---|---|
| 2 层冲突准确率 | 78% | 94% |
| 5 层冲突准确率 | 38% | 76% |
| 延迟增加 | — | +50-120ms |
| 可审计性 | 低（黑盒） | 高（规则链可追溯） |
| 新规则适配 | 需要微调 | 添加符号规则即可 |

## 5. 冲突检测与解析策略

### 5.1 冲突类型

| 冲突类型 | 示例 | 解析策略 |
|---|---|---|
| 直接矛盾 | system 说"不删文件"，user 说"删除所有临时文件" | system 优先，拒绝并解释 |
| 范围冲突 | developer 允许"编辑 src/"，user 要求"编辑 config/" | 拒绝越界部分，执行允许部分 |
| 隐性矛盾 | 安全策略禁止外发数据，工具描述暗示可上传 | 保守解释，按安全策略执行 |
| 时效冲突 | 旧 system prompt 与新 developer 更新不一致 | 以最新的同级或更高级指令为准 |
| 模糊委托 | developer 说"尽量满足用户"，user 要求高风险操作 | 不把模糊委托解释为高风险授权 |

### 5.2 解析流程

```text
1. 指令解析 — 提取每条指令的 source_lane、action、constraint
2. 冲突检测 — 比对同一 action 上的不同 constraint
3. 优先级裁决 — 按 Trust Lane 层级解决
4. 残余模糊 — 无法确定时，采取保守路径或请求 user 确认
5. 裁决记录 — 冲突和解析结果写入 trace
```

## 6. Prompt 组装时的层级管理

```yaml
prompt_assembly:
  # Phase 1: 收集
  collect:
    system_directives: from_platform_config
    developer_directives: from_system_prompt + agents_md
    user_directives: from_conversation
    tool_context: from_tool_specs + tool_outputs
    retrieved_context: from_rag + external_sources

  # Phase 2: 标注
  annotate:
    each_segment:
      source_lane: P0..P5
      timestamp: iso8601
      hash: sha256

  # Phase 3: 冲突检测与合并
  resolve:
    strategy: highest_priority_wins
    ambiguity_policy: conservative | ask_user
    max_effective_layers: 3

  # Phase 4: 注入
  inject:
    format: structured_blocks  # 不要把不同层级混在一起
    lane_markers: true         # 显式标记每个 block 的来源层级
```

## 7. 反模式

| 反模式 | 问题 | 修复 |
|---|---|---|
| Flat Instruction Mixing | 所有来源文本混在一起，无层级标记 | 每段文本标注 source_lane |
| Trust Lane Confusion | tool output 被当成 instruction 处理 | 工具返回值永远进 data lane |
| Implicit Delegation | developer 没显式声明，user 自行假定有权限 | 所有委托必须在 P1 层显式声明 |
| Last-In Wins | 模型遵循最后出现的指令而非最高优先级 | 结构化 prompt + 冲突检测前置 |
| Over-Nesting | 指令嵌套超过 3 层，模型无法可靠遵循 | Harness 层合并，保持 ≤ 3 层 |
| Prompt-as-ACL | 用 prompt 文本替代真正的权限系统 | 安全策略用 Policy Engine 执行 |

## 8. 关联模块

- `overview.md` — PromptContract 中的 instruction_layers 定义
- `prompt-security.md` — 指令注入防御依赖正确的层级隔离
- `../security/overview.md` — Trust Lane 的全局定义和防护策略
- `../control/overview.md` — 控制面依赖指令层级做行为裁决
- `../../../design-space/patterns/untrusted-context-boundary.md` — 不可信上下文边界模式
- `../../../design-space/lessons-learned/memory-poisoning-84pct-success.md` — 记忆注入攻击实例

## 9. 检查清单

- [ ] 每段 prompt 文本是否标注了 source_lane？
- [ ] 指令有效嵌套层数是否 ≤ 3？
- [ ] tool output 和 retrieved content 是否被隔离在 data lane？
- [ ] 存在指令冲突时，是否按优先级裁决而非 last-in-wins？
- [ ] 权限委托是否在 developer 层显式声明？
- [ ] 冲突解析结果是否记录到 trace？
