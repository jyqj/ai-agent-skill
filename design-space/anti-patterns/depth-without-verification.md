# Depth Without Verification

> **Evidence Status** — synthesized. 本知识库中相关模块的失败模式总结。


## 定义

执行很深、步骤很多，但没有测试、readback、postcondition。

## 典型表现

- Agent 连续执行 10+ 步工具调用，中间没有任何断言或 readback；
- 前序步骤返回空结果或错误码，后续步骤仍基于假设继续执行；
- 最终输出看起来完整，但中间关键步骤实际已失败；
- 调试时需要逐步回放整条链路才能定位首个出错点。

## 风险

- 多步执行中前序步骤的失败被后续步骤掩盖，最终错误与根因相距甚远。
- 错误在链路中逐步放大：一个错误的中间结果被后续步骤当作正确输入反复引用。
- 无法做部分重试——缺少 checkpoint 意味着任何修复都需要从头重跑。
- 长链路的最终输出置信度无法评估，因为没有中间验证点提供证据。

## 修复

把 execution depth 与 verification depth 绑定。

## 评审问题

```text
这个设计的单一事实来源是什么？
失败时能否重放？
是否有明确的 gate、trace 和 stop condition？
```
