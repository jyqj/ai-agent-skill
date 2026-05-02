# ReAct LLM Agent Starter Kit

> **Evidence Status** — synthesized. 本页来自 starter-kit 的参考代码、测试用例和本 skill 的最小闭环设计要求。

## 这个 starter 展示什么

> **参考性说明**：该目录中的代码只展示 ReAct 循环、工具调用和效果验证如何连接；API 封装、错误处理、权限和安全策略都不是生产实现。

一个真正调用 LLM 的 ReAct (Reasoning + Acting) Agent，实现完整的闭环：

```text
TaskEnvelope
  -> LLM observe + reason
  -> tool_use decision (with intended_effect + verification_method)
  -> execute tool           -- produces ExecutionResult
  -> _verify_effect()       -- SEPARATE step: readback / test / none
  -> EffectRecord           -- verification_status set by verify, NOT by tool status
  -> update context
  -> loop or finalize
```

> **IS-02 原则**：工具返回 `status: "success"` 只说明工具本身没报错，不等于预期的世界状态变化已经发生。
> 验证必须通过独立的 readback（重读文件）、test（运行测试命令）等方式确认。

Agent 在每一步中：
1. 观察当前状态和历史工具结果
2. 由 LLM 推理并决定下一步动作（含 intended_effect 和 verification_method）
3. 执行工具调用 -> 得到 ExecutionResult
4. **独立验证**：根据 verification_method 调用 readback/test 确认效果
5. 将结果反馈给 LLM，决定继续还是结束

## 与 verified-tool-agent 的区别

| | verified-tool-agent | react-llm-agent |
|---|---|---|
| 决策方式 | 预定义动作序列（JSON 配置） | LLM 实时推理决策 |
| 执行计划 | 静态，运行前确定 | 动态，每步根据上下文调整 |
| 工具选择 | 由配置指定 | 由 LLM 自主选择 |
| 错误处理 | stop 或 continue | LLM 诊断失败原因并调整策略 |
| 依赖 | 纯标准库 | 标准库 + anthropic SDK |

## 文件说明

| 文件 | 作用 |
|---|---|
| `models.py` | TaskEnvelope, EffectRecord (with verification_method), TraceEvent, Decision (with intended_effect/postconditions/verification_method), RunResult |
| `tools.py` | read_file / edit_file / run_command 工具及 ToolRegistry（含 schema 生成） |
| `llm.py` | Claude API 调用封装，system prompt 包含 ORDA-VU 闭环思想 |
| `agent_runtime.py` | ReAct 主循环 + stop gate + 循环检测 + effect ledger + `_verify_effect()` 独立验证 |
| `main.py` | CLI 入口 |

## 可选参考运行

如果只是阅读 skill，不需要运行代码。若要本地试跑这个参考样板，需要安装 anthropic SDK：

```bash
pip install anthropic
```

设置 API Key：

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

参考运行：

```bash
# 在当前目录下执行任务
python3 main.py "Read main.py and add a docstring to the main function"

# 指定工作目录
python3 main.py "List all Python files and count total lines" /path/to/project
```

## 与知识库的对应关系（代码对象仅作参考映射）

| 代码对象 | 知识库对应 |
|---|---|
| `TaskEnvelope` | `architecture/runtime-data-model.md` |
| `EffectRecord` | `architecture/planes/effects/overview.md` |
| `TraceEvent` | `architecture/planes/observability/overview.md` |
| `ToolRegistry` | `design-space/patterns/tool-registry.md` |
| `Decision` | `architecture/kernel/agent-loop.md` |
| `ReactAgent` (stop gate) | `architecture/planes/control/overview.md` |
| System prompt (ORDA-VU) | `architecture/lifecycle.md` |
