# Guides

> **Evidence Status** — synthesized. 基于知识库各层文档的方法论整合，尚未经过完整项目实践验证。

## 定位

知识库提供了从哲学基础到运行时 plane 的完整理论体系，但缺少"从知识到实践"的落地桥梁。`guides/` 目录填补这一空白：每篇指南以一个具体 Agent 为例，端到端地演示如何使用知识库中的方法论、模板和检查清单来完成设计。

## 与其他目录的关系

| 目录 | 回答什么 | guides 如何引用 |
|---|---|---|
| `concepts/` | Agent 是什么 | 指南解释"为什么选这个概念" |
| `paradigms/` | 有哪些做法 | 指南演示"用决策树选出范式" |
| `categories/` | 某类 Agent 的完整架构 | 指南从品类模板出发实例化 |
| `architecture/` | 运行时模块如何设计 | 指南选择必要 plane 并配置 |
| `evaluation/` | 如何验收 | 指南创建 eval fixture |
| `index/` | 检查清单和导航 | 指南用 checklist 做最终 review |

## 目录

| 指南 | 描述 |
|---|---|
| `build-research-agent.md` | 从零设计一个能产出可引用研究报告的 Research Agent，端到端演示知识库使用方法 |
