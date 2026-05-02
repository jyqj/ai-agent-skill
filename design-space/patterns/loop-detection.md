# Loop Detection

> **Evidence Status** — synthesized. 多个 Agent 框架和生产系统中反复出现的问题，属于公认的 Agent 可靠性挑战。

## 问题

Agent 可能反复调用同一工具、修改同一文件、尝试同一失败路径，形成死循环（Doom Loop）。这不仅浪费资源，还会让用户失去信任。循环通常不是因为 Agent "笨"，而是因为它没有机制回顾自己最近做了什么。

## 解法

记录最近若干步的行为签名（Action Signature），检测重复模式，并触发对应的干预策略。

```python
def detect_loop(trace, window=5):
    sigs = [s.signature for s in trace.last(window)]
    if len(set(sigs)) == 1: return 'same_action_loop'
    if repeated_error(trace.last(window)): return 'same_error_loop'
    if oscillating_edits(trace.last(window)): return 'edit_oscillation'
    return None
```

检测到循环后，不同类型需要不同的干预方式：

- **同工具同参数反复失败** — 禁止相同步骤，强制要求新策略。继续重试只会得到同样的错误。
- **同文件来回修改**（编辑振荡） — 回滚到最近的 checkpoint，要求 Agent 先解释修改意图再动手。
- **测试失败反复修** — 降低修复范围，先定位最小失败用例，而不是反复尝试大范围修改。
- **搜索反复无结果** — 换关键词、换搜索策略，或直接请求用户澄清。
