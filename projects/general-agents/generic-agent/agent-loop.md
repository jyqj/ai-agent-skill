# Agent Loop 核心循环

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> 文件：`agent_loop.py` (~100行)

## 执行流程

```
感知 → 推理 → 执行 → 记忆 → 循环
```

## 关键代码

### 主循环结构 (L45-98)

```python
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_input}
]
turn = 0
while turn < handler.max_turns:
    turn += 1
    if turn % 10 == 0:
        client.last_tools = ''  # 每10轮重置工具描述

    response_gen = client.chat(messages=messages, tools=tools_schema)
    response = yield from response_gen  # 流式输出

    # 提取工具调用
    tool_calls = [
        {'tool_name': tc.function.name,
         'args': json.loads(tc.function.arguments),
         'id': tc.id}
        for tc in response.tool_calls
    ] if response.tool_calls else [{'tool_name': 'no_tool', 'args': {}}]

    # 串行执行工具
    for tc in tool_calls:
        outcome = yield from handler.dispatch(tc['tool_name'], tc['args'], response)

        if outcome.should_exit:
            exit_reason = {'result': 'EXITED', 'data': outcome.data}
            break
        if not outcome.next_prompt:
            exit_reason = {'result': 'CURRENT_TASK_DONE', 'data': outcome.data}
            break

    # 准备下轮消息
    next_prompt = handler.turn_end_callback(response, tool_calls, tool_results, turn, ...)
    messages = [{"role": "user", "content": next_prompt, "tool_results": tool_results}]
```

### 工具调度器 (L18-29)

```python
class BaseHandler:
    def dispatch(self, tool_name, args, response, index=0):
        method_name = f"do_{tool_name}"  # 约定优于配置
        if hasattr(self, method_name):
            args['_index'] = index
            # 三阶段回调
            yield from try_call_generator(self.tool_before_callback, tool_name, args, response)
            ret = yield from try_call_generator(getattr(self, method_name), args, response)
            yield from try_call_generator(self.tool_after_callback, tool_name, args, response, ret)
            return ret
        elif tool_name == 'bad_json':
            return StepOutcome(None, next_prompt=args.get('msg', 'bad_json'))
        else:
            yield f"未知工具: {tool_name}\n"
            return StepOutcome(None, next_prompt=f"未知工具 {tool_name}")
```

### StepOutcome 协变出口 (L5-8)

```python
@dataclass
class StepOutcome:
    data: Any              # 工具返回值
    next_prompt: str = ""  # 下轮提示（None=任务完成）
    should_exit: bool = False  # 强制退出
```

## 设计模式

| 模式 | 实现 | 价值 |
|-----|------|-----|
| **生成器链** | `yield from` | 无缓冲流式输出 |
| **约定发现** | `do_{name}` | 零配置工具注册 |
| **协变出口** | `StepOutcome` | 工具控制流走向 |
| **三阶段钩子** | before/do/after | 无侵入扩展点 |

## 轮次控制策略

```python
# ga.py:507-511
if turn % 35 == 0:
    next_prompt += "\n\n[DANGER] 已连续执行第 {turn} 轮。必须ask_user。"
elif turn % 7 == 0:
    next_prompt += "\n\n[DANGER] 已连续执行第 {turn} 轮。禁止无效重试。"
```

## 极简消息传递（第二轮审计补充）

主循环每轮只向 LLM 发送 **最新一轮的 user 消息**（含 tool_results），而非累积完整历史。
历史由 `_get_anchor_prompt()` 以摘要形式注入，loop 本身不承担状态管理职责。

```python
# 每轮只传最新消息，不累积
messages = [{"role": "user", "content": next_prompt, "tool_results": tool_results}]
# 上下文由 anchor prompt 提供，而非 messages 数组增长
```

这把上下文管理从循环层剥离到记忆层，换来两个好处：
1. 单轮 token 消耗可预测，不随对话长度线性增长
2. 压缩/遗忘策略完全由 memory-layers 控制，loop 保持无状态

---

## no_tool 行为矫正层（第二轮审计补充）

当 LLM 未返回 tool_calls 时，dispatch 接收 `tool_name='no_tool'`，`do_no_tool` 承担行为矫正：

```python
def do_no_tool(self, args, response):
    text = response.content or ""
    # 1. 空回复 → 强制重试
    if not text.strip():
        return StepOutcome(None, next_prompt="[系统] 回复为空，请重新思考后调用工具。")
    # 2. 包含代码块但未执行 → 纠正
    if "```" in text and not any_tool_called:
        return StepOutcome(None, next_prompt="[系统] 检测到代码块但未调用执行工具。请用 run_code 执行。")
    # 3. 虚假完成声明 → 拦截
    if _looks_like_premature_done(text):
        return StepOutcome(None, next_prompt="[系统] 任务未验证完成。请先验证再调用 task_done。")
    # 4. 正常文本输出 → 继续
    return StepOutcome(None, next_prompt=text)
```

**设计意图**：LLM 倾向于"说话而不行动"或宣称完成而不验证。矫正层将这些退化行为拦截在 loop 内部。

---

## _done_hooks 后置任务链（第二轮审计补充）

`task_done` / `EXITED` 退出后，loop 不直接返回，而是检查 `_done_hooks` 回调列表：

```python
# agent_loop.py 退出段
if exit_reason:
    for hook in handler._done_hooks:
        yield from hook(exit_reason, response, turn)
    return exit_reason
```

典型 hook 包括：自动触发 `start_long_term_update`（记忆结算）、Langfuse trace 关闭、BBS 结果回传。
hook 按注册顺序串行执行，任一 hook 可通过返回值阻止后续 hook 运行。
