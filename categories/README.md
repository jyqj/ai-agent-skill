# Agent Categories

> **Evidence Status** — synthesized. 品类索引，覆盖 11 个 Agent 品类。

## 品类层在主干中的位置

```text
concepts/       Agent 是什么
paradigms/      有哪些根本不同的做法
categories/     某类 Agent 的完整设计
architecture/   通用模块怎么设计
projects/       真实项目怎么实现
```

品类文档不应该只是"模块配方清单"。一个成熟的品类架构至少回答：

```text
1. 用户模型：谁用、信任如何建立、交互心智是什么
2. 任务模型：任务类型、成功定义、失败分类
3. 表示模型：这个品类的关键对象、freshness、trust
4. 行动模型：读/写/验证动作、前置/后置条件
5. 闭环模型：happy path、failure path、stop gate、verification
6. 设计决策：沙箱、并发、上下文、记忆、控制、运维
7. 评估用例：品类专属 eval cases 和指标
8. 实现映射：参考项目中每个模块怎么落地
```

## 当前成熟度

> **CC = Category Coverage**，衡量品类文档的完整程度（CC0-CC4）。与 `architecture/blueprint.md` 中的运行时成熟度 A0-A5 是不同维度。

| 品类 | 入口 | 成熟度 | 说明 |
|---|---|---|---|
| Coding Agent | `coding-agent/README.md` | CC4 | 完整样板 |
| Research Agent | `research-agent/README.md` | CC4 | 完整样板 |
| Enterprise Workflow Agent | `enterprise-workflow-agent/README.md` | CC3-CC4 | 已升级：任务/表示/行动/闭环/决策/eval/实现 |
| Browser/Desktop Agent | `browser-desktop-agent/README.md` | CC3-CC4 | 已升级：双通道验证/安全/benchmark 映射 |
| Ops/SRE Agent | `ops-sre-agent/README.md` | CC3 | 已升级：多 Agent 诊断/信号关联/缓解闭环 |
| Data/BI Agent | `data-bi-agent/README.md` | CC3 | 已升级：Text-to-SQL/语义层/SQL 安全 |
| Companion Agent | `companion-agent/README.md` | CC3 | 已升级：三层记忆/人格一致性/安全边界 |
| Security Agent | `security-agent/README.md` | CC3 | 已升级：自身安全/证据链/MITRE 映射 |
| Personal Memory Agent | `personal-memory-agent/README.md` | CC3 | 已升级：三层存储/矛盾检测/隐私控制 |
| Embodied Robot Agent | `embodied-robot-agent/README.md` | CC2-CC3 | 已升级：安全层级/LLM+控制分离/Sim-to-Real |
| Agent Platform | `agent-platform/README.md` | CC3 | 已升级：协议栈/多租户/版本管理 |

## 品类模板

新建或升级品类时使用：

- `../meta/templates/category-architecture-template.md`
- `coding-agent/` 和 `research-agent/` 作为 CC4 样板
- 其他品类作为 CC3 样板

## 验证类型说明

不同品类的效果验证方式不同。工程型品类（Coding、Ops/SRE）主要使用客观 postcondition 验证；关系/创造型品类（Companion、Creative）需要扩展验证语义。详见：

- `../concepts/beyond-verification.md` — 超越验证：审美、情感、创造性任务
- `../evaluation/subjective-eval.md` — 主观性任务评估框架

## 旧单页入口

历史单页文件保留为兼容入口，指向对应目录。
