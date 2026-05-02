# Tool Output Sanitization

> **Evidence Status** — synthesized. 问题在实践中反复出现——网页、日志、邮件、issue、第三方 API 返回值都可能夹带"看起来像指令"的文本，属于已知攻击面。

## 问题

工具输出经常包含不可信文本。如果系统直接把这些内容拼回主提示（Main Prompt），外部世界就能间接操控 Agent——这就是间接提示注入（Indirect Prompt Injection）的基本原理。

## 解法

核心原则是**默认不信任**：所有工具输出先进入 `untrusted_data` 通道，经过清洗后才能进入上下文。

具体做法：

1. 保留原始引用（raw ref），不直接将工具输出提升为指令（instruction）。
2. 解析时区分四类内容：纯数据、建议、可执行文本、凭证片段，分别处理。
3. 对 shell 命令、URL、SQL、HTML、Markdown 中的"建议动作"做显式隔离——它们是数据，不是指令。

最小处理流程：

```text
Tool Output -> Normalize -> Classify Trust Tier -> Strip / Escape Dangerous Fragments -> Summarize with Citation -> Feed into Context
```

## 典型反模式

以下做法在生产系统中都出现过，且都导致了安全问题：

- **网页正文并入 system prompt** — 攻击者只需在页面中插入一段"忽略前文，执行以下操作"就能劫持 Agent。
- **第三方 API 返回值生成 shell 命令后自动执行** — 等于把代码执行权交给了外部服务。
- **日志里出现"请忽略前文"就真的忽略前文** — Agent 把日志中的文字当成了用户指令。
