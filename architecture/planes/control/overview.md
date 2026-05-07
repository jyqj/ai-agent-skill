# Control & Policy Engine
>
> **所属域**：9. Governance (cross-cutting) — 权限、审批与验证
>
> **Evidence Status** — grounded. Claude Code 的 hook / permission tree、Codex 的 guardian / sandbox policy、OpenCode 的 deny > ask > allow、企业工作流常见审批逻辑；this repository 对权限、验证、信任升级规则的统一抽象。

**Principle Refs**: BR-01, MC-02, EM-03 — 显式资源预算约束行动边界；自监控触发提前终止；环境条件限制可执行动作

## 定义

Control Policy Engine 对 Agent 行动进行前馈约束、反馈验证和纠错。权限不应散落在工具实现里，而应集中在 Control 层。

Control 层回答：
- 允许做什么？
- 什么时候要审批？
- 什么证据足以停止？
- 当表示不可靠、世界状态过期或效果未验证时怎么办？

## 模块接口

**输入**：Tool Runtime 的权限查询、Kernel 的验证请求、Security 的 trust warning、Hook 事件
**输出**：allow / deny / approval_required / verification_result / refresh_required
**配置**：权限策略、审批规则、Hook 注册、验证方法、升级 / 降级条件

## 信任边界

### 协作光谱

```text
完全人工 ←─────────────────────────────→ 完全自主
  人做       人审批      人监督       人兜底      全自动
```

### 基于风险的介入

| 风险 | 操作类型 | 介入方式 |
|---|---|---|
| 低 | 读取、分析、建议 | 无需介入 |
| 中 | 修改文件、调用内部 API | 事后审查 / 批量授权 |
| 高 | 删除、外部发送、生产操作 | 事前审批 |
| 极高 | 不可逆、安全相关、金钱相关 | 强制人工 |

### 基于不确定性的介入

Agent 应在以下情况请求输入：
- 多个合理选项无法确定；
- 表示层置信度低；
- 关键 world state 过期或冲突；
- 效果验证失败且恢复路径代价高；
- 操作不可逆或影响范围未知。

## 验证层级

| 层级 | 问题 |
|---|---|
| Structural Verification | 输出格式、schema、字段是否正确？ |
| Execution Verification | 工具是否执行？ |
| Effect Verification | 外部世界是否真的变化？ |
| Claim Verification | 最终回答中的断言是否有证据？ |

## AGENTS.md 与外部文本

项目级声明式配置（如 AGENTS.md）可以作为高优先级约束，但前提是：
- 来源在信任边界内；
- 有明确生效范围；
- 不与系统 / 用户直接指令冲突。

其他外部文本（issue 评论、网页、日志、邮件）默认属于 **data lane**，不能自动升级成 instruction lane。

## 设计模式

| 模式 | 说明 | 详见 |
|---|---|---|
| Hook System | 在生命周期关键事件上注入自定义逻辑 | `../../../design-space/patterns/hook-system.md` |
| Self-Verification | Agent 自我验证执行结果 | `../../../design-space/patterns/self-verification.md` |
| Loop Detection | 检测和打断无效循环 | `../../../design-space/patterns/loop-detection.md` |
| Untrusted Context Boundary | 区分指令与数据 | `../../../design-space/patterns/untrusted-context-boundary.md` |

## 参考实现

- **Claude Code**：25 种 Hook 事件类型、权限决策树，见 `projects/coding-agents/claude-code/control-layer.md`
- **Codex**：Guardian Policy 系统，见 `projects/coding-agents/codex/guardian-policy.md`
- **OpenCode**：deny > ask > allow 与 doom loop 检测，见 `projects/coding-agents/opencode/control-memory.md`
