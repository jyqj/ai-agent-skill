> **已合并**：本反模式的完整内容已合并至 `top-10.md`。以下内容保留为存档。

# Trust Everything

> **Evidence Status** — synthesized. 本知识库中相关模块的失败模式总结。


## 定义

网页、邮件、issue、tool output、memory、summary 全都放在同一可信上下文。

## 典型表现

- 用户输入、网页内容、工具返回值、邮件正文共享同一信任级别；
- 没有对 tool output 做 schema 校验或内容过滤；
- prompt injection 载荷可以通过 issue 标题、网页摘要等路径进入决策流程；
- Agent 直接执行从不可信来源提取的指令（如”请运行以下命令”）。

## 风险

- 不可信来源的指令被当作系统指令执行，prompt injection 无法防御。
- 攻击面随接入数据源数量线性增长，任一来源被污染即可劫持 Agent 行为。
- 无法区分”模型自己的判断”和”被外部内容诱导的判断”，事后审计无从入手。
- 工具返回的恶意或畸形数据直接参与后续推理，导致级联错误。

## 修复

Trust lanes + tool-output sanitization + untrusted context boundary。

## 评审问题

```text
这个设计的单一事实来源是什么？
失败时能否重放？
是否有明确的 gate、trace 和 stop condition？
```
