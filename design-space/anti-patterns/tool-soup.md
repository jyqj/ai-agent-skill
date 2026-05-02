# Tool Soup

> **Evidence Status** — synthesized. 本知识库中相关模块的失败模式总结。


## 定义

接入大量工具，但没有路由、权限、风险、precondition、postcondition。

## 典型表现

- 工具列表超过 20 个且全部在每次请求中注入 system prompt；
- 工具描述之间存在功能重叠（如同时有 `search_web` 和 `google_search`），模型随机选择；
- 没有根据任务类型动态加载工具子集；
- 高风险工具（如 `execute_shell`）与低风险工具（如 `get_time`）共享同一权限级别。

## 风险

- 工具描述占满上下文窗口，挤压用户指令和推理空间。
- 模型选错工具的概率随工具数量增加，尤其在功能描述相近时。
- 无差别暴露所有工具导致攻击面扩大，低权限任务也能触发高危操作。
- 工具间缺少 precondition/postcondition 约束，组合调用产生非预期副作用。

## 修复

Tool Registry + Tool Router + Control Gate + Effect Ledger。

## 评审问题

```text
这个设计的单一事实来源是什么？
失败时能否重放？
是否有明确的 gate、trace 和 stop condition？
```
