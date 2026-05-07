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
