# Agent Loop 核心实现

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> 来源：`run_agent.py`

## 循环架构

```python
# 同步单线程循环，双重边界控制
while api_call_count < self.max_iterations and self.iteration_budget.remaining > 0:
    response = client.chat.completions.create(model=model, messages=messages, tools=tool_schemas)

    if response.tool_calls:
        # 可选并发执行（仅当安全时）
        if _can_parallelize(tool_calls):
            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(handle_function_call, tool_calls))
        else:
            results = [handle_function_call(tc) for tc in tool_calls]

        messages.extend(tool_result_messages(results))
        api_call_count += 1
    else:
        return response.content
```

**洞察**：循环本身是"笨"的，判断在模型。同步设计简化调试，并发通过 ThreadPoolExecutor 可选启用。

---

## 迭代预算模型

```python
class IterationBudget:
    """线程安全的迭代预算，支持 consume/refund。"""
    def __init__(self, max_iterations: int):
        self._lock = threading.Lock()
        self._remaining = max_iterations

    def consume(self, n: int = 1) -> bool:
        with self._lock:
            if self._remaining >= n:
                self._remaining -= n
                return True
            return False

    def refund(self, n: int = 1):
        """便宜操作（如 execute_code）可退还预算。"""
        with self._lock:
            self._remaining += n
```

**洞察**：Refund 机制让程序化工具调用不消耗预算。预算可跨父子代理共享。

---

## 预算压力注入

```python
# 在 70%/90% 阈值注入警告到最后一个工具结果
if budget_ratio >= 0.9:
    last_tool_result["_budget_warning"] = "CRITICAL: 90% budget consumed. Wrap up immediately."
elif budget_ratio >= 0.7:
    last_tool_result["_budget_warning"] = "CAUTION: 70% budget consumed. Plan to conclude soon."
```

**洞察**：警告注入工具结果 JSON 而非独立消息，保护消息交替不变性，不失效 prompt caching。

---

## 上下文压缩触发

```python
# 两阶段检查：预检 + 精确
if _estimate_prompt_tokens(messages) >= compression_threshold:
    # 预检通过，执行 API 调用
    response = client.chat.completions.create(...)

    # 精确检查（使用实际 usage）
    actual_tokens = response.usage.prompt_tokens
    if actual_tokens >= compression_threshold:
        messages = compress_context(messages)
        compression_retries += 1
        if compression_retries > 3:
            raise ContextOverflowError("Compression failed after 3 attempts")
```

**洞察**：预检避免浪费 API 调用，精确检查使用实际 token 数。重试上限防止无限循环。

---

## 两阶段压缩

```python
def compress_context(messages: list) -> list:
    # Phase 1: 轻量剪枝（无 LLM）
    pruned = _prune_old_tool_results(messages)

    # Phase 2: LLM 总结（仅在必要时）
    if _estimate_tokens(pruned) > target_tokens:
        summary = _llm_summarize(pruned[head_protected:tail_start])
        pruned = pruned[:head_protected] + [summary_message] + pruned[tail_start:]

    # 清理孤立的 tool_call/tool_result 对
    return _sanitize_tool_pairs(pruned)
```

**洞察**：头部保护系统提示，尾部保护最近 ~20K tokens。总结保留前次压缩内容，增量更新而非重新总结。

---

## 多格式推理提取

```python
def _extract_reasoning(response) -> Optional[str]:
    """尝试 4 个来源提取推理内容。"""
    # 1. 直接字段
    if hasattr(response, 'reasoning'):
        return response.reasoning

    # 2. 替代字段名
    for field in ['thinking', 'thought', 'rationale']:
        if hasattr(response, field):
            return getattr(response, field)

    # 3. 结构化数组（DeepSeek 格式）
    if response.content and isinstance(response.content, list):
        for block in response.content:
            if block.get('type') == 'thinking':
                return block.get('thinking')

    # 4. 内联标签（<thinking>...</thinking>）
    if '<thinking>' in response.content:
        return _extract_thinking_tags(response.content)

    return None
```

**洞察**：兼容多提供商（OpenAI/Anthropic/DeepSeek/OpenRouter），去重和组合多个来源。
