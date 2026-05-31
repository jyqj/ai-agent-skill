# AI Agent Architecture Skill

> **Evidence Status** — synthesized. 项目入口页。

Agent 架构知识库与评审工具，用于设计、诊断和评审 Agent 产品。仓库内代码均为 reference-only。

**从 [START-HERE.md](START-HERE.md) 开始。**

## 顶层文件职责

| 文件 | 职责 |
|---|---|
| [START-HERE.md](START-HERE.md) | 唯一入口：按构建、诊断、升级、评审和 AI 使用分流 |
| [SKILL.md](SKILL.md) | AI 加载用速查卡：核心判断、故障入口、证据规则 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 深度参考：产品公式、ORDA-VU、运行时模块和数据资产 |
| [index/mainline-map.md](index/mainline-map.md) | 主干地图：知识层级和系统阅读路线 |
| [AGENTS.md](AGENTS.md) | 维护规则：目录归属、工作约束、自检流程 |

## 三层入口的选择

| 你是 | 用途 | 入口 |
|---|---|---|
| 有明确任务（构建/诊断/升级/评审） | 最短路径直达 | [START-HERE.md](START-HERE.md) |
| Agent 出了问题，按症状查 | 故障定位 + 核心规则 | [SKILL.md](SKILL.md) |
| 想系统了解架构全貌 | 深度阅读 | [ARCHITECTURE.md](ARCHITECTURE.md) → [index/mainline-map.md](index/mainline-map.md) |
| AI 助手加载本 skill | 最小成本意图路由 | [index/ai-routing-pack.md](index/ai-routing-pack.md) |

## 规模概览

当前覆盖：9 域 25 Plane、12 条设计原则、21 个失败案例、53 个设计模式（含 7 个生产验证级）、7 个品类工具、6 个源码级项目对照。

## 使用原则

- 先走 `START-HERE.md`，不要从目录树开始读。
- 具体代码只作为架构映射参考，不能当生产实现。
- 关键结论优先回到 `projects/`、`synthesis/`、`evaluation/` 或真实 trace。
