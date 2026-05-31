# Frozen Snapshot Pattern

> **Evidence Status** — grounded. 提炼自 Hermes Agent 的 `tools/memory_tool.py` 实现，已在记忆系统中验证。

## 问题

Agent 的持久化数据（记忆、配置、偏好）需要注入系统提示（System Prompt）。但这里存在一个矛盾：

- Mid-session 修改会破坏提示缓存（Prompt Caching），导致每次修改都重新计算系统提示，成本高昂。
- 而用户期望修改"立即生效"。

这两个需求直接冲突。

## 解法：分离注入状态和持久化状态

冻结快照（Frozen Snapshot）的核心思路是：**系统提示里用的是会话启动时的快照，写入操作立即持久化到磁盘，但不改动当前会话的系统提示**。用户的修改在下次会话自动生效。

```python
class MemoryManager:
    def __init__(self):
        self._frozen_snapshot = None  # 系统提示用
        self._live_entries = []       # 实时数据

    def load(self):
        self._live_entries = self._read_file(MEMORY_MD)
        self._frozen_snapshot = self._render(self._live_entries)

    def format_for_system_prompt(self) -> str:
        return self._frozen_snapshot  # 返回冻结的，不是实时的

    def add(self, content: str) -> dict:
        self._live_entries.append(content)
        self._write_file(MEMORY_MD, self._live_entries)
        return {"success": True, "note": "Visible in next session"}
```

## 权衡

这个模式用"下次生效"换来了三个好处：prompt caching 不被打断、实现简单、无上下文重算成本。代价是工具响应需要向用户解释"已保存，下次会话生效"，这是有意为之的设计取舍。如果你的场景要求修改必须实时可见，那这个模式不适用，需要考虑上下文重算或增量注入方案。

## 适用场景

任何注入系统提示的持久化数据都适合用这个模式：用户记忆与偏好、技能配置的启用/禁用、环境事实等。

## 参考实现

Hermes Agent `tools/memory_tool.py`
