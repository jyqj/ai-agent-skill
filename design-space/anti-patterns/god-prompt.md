# God Prompt

> **Evidence Status** — synthesized. 本知识库中相关模块的失败模式总结。


## 定义

把所有系统规则、工具说明、策略、安全边界、输出格式都塞进一个巨大 system prompt。

## 典型表现

- system prompt 超过数千 token，包含角色设定、工具列表、输出格式、安全规则、业务逻辑等所有内容；
- 修改一条安全策略需要在一整段文本中定位并手动编辑；
- 不同规则之间出现矛盾（如”永远不要拒绝用户”与”禁止执行危险操作”同时存在）；
- 新增功能只能往 prompt 末尾追加段落。

## 风险

- prompt 膨胀导致指令之间相互冲突，模型选择性遗忘尾部或中部规则。
- 行为异常时无法定位是哪条规则被忽略或被覆盖，调试成本极高。
- 单一 prompt 无法按场景动态加载，所有任务都承担全量指令的上下文开销。
- 版本管理困难：一次改动可能无意间影响多个不相关的行为。

## 修复

PromptContract、Policy、Tool Spec、ContextPack、Security Gate 分离。

## 评审问题

```text
这个设计的单一事实来源是什么？
失败时能否重放？
是否有明确的 gate、trace 和 stop condition？
```
