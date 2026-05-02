# Verified Tool Agent Starter Kit

> **Evidence Status** — synthesized. ORDA-VU、Effects、Tool Registry、Stop Gate、最小 eval 需求。


## 这个骨架展示什么

> **参考性说明**：该目录中的代码是 reference skeleton，只用于展示 TaskEnvelope、ToolRegistry、EffectRecord、TraceEvent 等对象如何串联；不是完整 LLM agent、框架模板或生产实现。

```text
TaskEnvelope
→ ActionSpec
→ ToolRegistry
→ EffectRecord
→ Verification
→ FailureRecord / RecoveryAction
→ TraceEvent
→ Final summary
```

这是一个 reference runtime skeleton。你可以借鉴 `agent_runtime.py` 中的对象流，把 rule-based planner 替换为你自己的模型决策；落地时需要重做权限、安全、错误恢复和测试。

## 文件说明

| 文件 | 作用 |
|---|---|
| `models.py` | TaskEnvelope、ActionSpec、EffectRecord、FailureRecord、RunResult 等对象 |
| `tools.py` | read_file / edit_file / run_test 等示例工具和注册表 |
| `effects.py` | contains / file_exists / exit_code 一类验证函数 |
| `agent_runtime.py` | 主执行循环：represent → act → verify → failure_record → stop gate |
| `main.py` | 从 JSON task 运行 |
| `tests/test_runtime.py` | 最小回归测试 |

## 可选参考运行

```bash
python3 starter-kit/verified-tool-agent/main.py path/to/task.json
python3 -m unittest discover -s starter-kit/verified-tool-agent/tests -p 'test_*.py'
```

## 示例 task

```json
{
  "goal": "Replace hello with world and verify it.",
  "actions": [
    {
      "tool": "edit_file",
      "args": {"path": "note.txt", "old_text": "hello", "new_text": "world"},
      "intended_effect": "note.txt contains world",
      "verification": {"kind": "contains", "path": "note.txt", "value": "world"}
    }
  ]
}
```

## 与主知识库的对应关系（代码对象仅作参考映射）

| 代码对象 | 知识库对应 |
|---|---|
| `TaskEnvelope` | `architecture/runtime-data-model.md` |
| `EffectRecord` | `architecture/planes/effects/overview.md` |
| `FailureRecord` | `architecture/planes/recovery/overview.md` |
| `TraceEvent` | `architecture/planes/observability/overview.md` |
| `ToolRegistry` | `design-space/patterns/tool-registry.md` |
| `VerificationSpec` | `design-space/patterns/self-verification.md` |
