# Start Here

> **Evidence Status** — synthesized.

## 这个 skill 是什么

Agent 开发过程中的参照系。做产品决策、模块装配、故障诊断、模式选择、评估设计或架构评审时，用它定位该看什么、该避免什么。不是教材，不用从头读完。

## 你现在要做什么？

### A. 构建一个新 Agent

四步走，每步有明确产出。

**第 1 步：选品类**（30 秒）

| 用户任务 | 品类 | 入口 |
|---|---|---|
| 写代码、修 bug、做 PR | Coding Agent | `categories/coding-agent/README.md` |
| 调研、出报告、做综述 | Research Agent | `categories/research-agent/README.md` |
| 操作浏览器或桌面 | Browser/Desktop Agent | `categories/browser-desktop-agent/README.md` |
| 企业流程审批执行 | Enterprise Workflow | `categories/enterprise-workflow-agent/README.md` |
| 长期陪伴、情感交互 | Companion Agent | `categories/companion-agent/README.md` |
| 运维告警、故障处置 | Ops/SRE Agent | `categories/ops-sre-agent/README.md` |
| 记忆管理、个人知识 | Memory Agent | `categories/personal-memory-agent/README.md` |
| 数据分析、BI 报表 | Data/BI Agent | `categories/data-bi-agent/README.md` |
| 不确定或上面没有 | `toolkit/choose-agent-type.md` 帮你判断 | |

**第 2 步：定深度和风险**（2 分钟）

回答三个问题，确定 MVA 级别：

```text
1. Agent 是否写入外部世界（文件、数据库、API、邮件）？
   不写         → MVA-2，专注表示和工具
   写但可撤销   → MVA-3，加效果验证
   不可逆写入   → MVA-4+，加审批和恢复

2. 效果能否立即回读验证？
   能（readback / test / ack） → 当前级别
   不能 → 升一级，加 unverifiable_by_agent 退化路径

3. 任务是否跨会话或长时间运行？
   不跨   → 当前级别
   跨会话 → MVA-4+，加 checkpoint 和 world-state refresh
```

产出：

```yaml
mva_level: MVA-3
required_depth: D4
risk_factors: ["writes external API", "needs read-after-write"]
```

MVA 阶梯全表和成本估算见 `toolkit/mva-planner.md`。

**第 3 步：选模块**（5 分钟）

用品类默认模块集作为起点：`index/category-module-map.md`。

不确定某个模块是否需要？三条判断规则：

- 有写动作 → 必须有 Effects + Control
- 有外部状态依赖 → 必须有 World State
- 有多步任务 → 必须有 State

其他模块暂缓，等失败触发再引入。详细选择器见 `toolkit/module-picker.md`。

**第 4 步：设计验收**（10 分钟）

用 `index/design-checklist.md` 过一遍。重点三个区域：

1. 产品层——任务定义、交付物、成功标准
2. 效果层——写动作是否有 postcondition 和验证方法
3. 安全层——信任边界是否区分指令、数据、工具输出

完整评估设计见 `toolkit/eval-planner.md`。

---

### B. 诊断一个已有 Agent

从症状出发：`toolkit/failure-router.md`。

常见症状速查也在 `SKILL.md` 的"问题诊断"表中。

### C. 做架构评审

`index/design-checklist.md` 做完整 review。

对照真实项目：`index/project-module-map.md`。

### D. AI 使用本 skill

先读 `index/ai-routing-pack.md`，按用户意图路由到最少必要文件。

---

## 深层知识库

上面四条路径足够启动。以下按需深入：

| 层 | 回答什么 | 入口 |
|---|---|---|
| 品类蓝图 | 某类 Agent 的完整设计 | `categories/README.md` |
| 架构底盘 | 9 域 25 plane、数据流、边界 | `architecture/README.md` |
| 范式选择 | 推理/记忆/工具/协作/控制怎么选 | `paradigms/README.md` |
| 设计模式 | 可复用做法与反模式 | `design-space/patterns/README.md` |
| 项目证据 | 真实项目怎么做 | `projects/README.md` |
| 评估体系 | 怎么验收和回归 | `evaluation/README.md` |
| 哲学基础 | 为什么必须这样设计 | `concepts/foundations/README.md` |

## 信任规则

阅读任何文件时留意顶部的 `Evidence Status`：

| 标记 | 可以怎么用 |
|---|---|
| production-validated | 可作为设计依据 |
| prototype-validated / grounded | 可参考，需在你的场景验证 |
| synthesized / mixed | 架构草案和 checklist，结合场景裁剪 |
| theoretical / speculative | 思考工具，不作为实现规范 |
