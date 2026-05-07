# Choose Agent Type

> **Evidence Status** — synthesized. 由 `categories/README.md`、`index/category-module-map.md` 和参考项目覆盖范围压缩而来，用于 5 分钟内完成品类定位。

## 30 秒判断

先问：这个 Agent 的主要交付物是什么？

| 交付物 / 工作对象 | 品类 | 默认入口 |
|---|---|---|
| 代码修改、测试、PR、重构 | Coding Agent | `../categories/coding-agent/README.md` |
| 证据报告、引用、冲突整理 | Research Agent | `../categories/research-agent/README.md` |
| CRM / ticket / 审批 / 业务流转 | Enterprise Workflow Agent | `../categories/enterprise-workflow-agent/README.md` |
| 浏览器或桌面界面操作 | Browser/Desktop Agent | `../categories/browser-desktop-agent/README.md` |
| 告警、日志、回滚、健康检查 | Ops/SRE Agent | `../categories/ops-sre-agent/README.md` |
| SQL、BI、指标解释 | Data/BI Agent | `../categories/data-bi-agent/README.md` |
| 安全分诊、扫描、证据链 | Security Agent | `../categories/security-agent/README.md` |
| 关系、陪伴、长期偏好 | Companion Agent | `../categories/companion-agent/README.md` |
| 跨会话个人记忆 | Personal Memory Agent | `../categories/personal-memory-agent/README.md` |
| 多 Agent / 插件 / 工具市场平台 | Agent Platform | `../categories/agent-platform/README.md` |
| 机器人、传感器、现实动作 | Embodied Robot Agent | `../categories/embodied-robot-agent/README.md` |

## 最小产出

选择品类后，只写 4 行：

```yaml
agent_type: coding-agent
primary_deliverable: "merged PR with tests"
default_depth: D4-D5
first_blueprint: ../categories/coding-agent/README.md
```

## 不确定时怎么选

| 情况 | 默认选择 |
|---|---|
| 同时要研究和写代码 | Coding Agent，Research 作为子任务 |
| 同时要聊天和记忆 | Companion Agent，Personal Memory 作为模块 |
| 同时要浏览器和业务系统 | Browser/Desktop Agent，如果最终写业务系统则叠加 Workflow |
| 想做通用平台 | 先选最核心第一个品类，不要一开始选 Agent Platform |

## 下一步

1. `mva-planner.md`
2. `module-picker.md`
3. `../index/category-module-map.md`
