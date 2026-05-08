# 多模型适配层

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> 文件：`llmcore.py` (~957行)

## 后端类型

| 后端 | 触发条件 | 实现类 | 特性 |
|-----|---------|-------|------|
| Claude Native | `native` + `claude` | `NativeClaudeSession` | 原生工具调用、思维链、Prompt Caching、Extended Thinking |
| OpenAI Native | `native` + `oai` | `NativeOAISession` | 原生函数调用、Prompt Caching |
| Claude via Proxy | `claude` (无native) | `ClaudeSession` | OpenAI 兼容 |
| OpenAI Compatible | `oai` | `LLMSession` | chat/responses API |
| Mixin Fallback | `mixin` | `MixinSession` | 轮询重试 + 指数退避、多后端故障转移 |

## 动态后端发现

```python
# agentmain.py:46-63
for k, cfg in mykeys.items():
    if 'native' in k and 'claude' in k:
        llm_sessions.append(NativeToolClient(NativeClaudeSession(cfg=cfg)))
    elif 'native' in k and 'oai' in k:
        llm_sessions.append(NativeToolClient(NativeOAISession(cfg=cfg)))
    elif 'claude' in k:
        llm_sessions.append(ToolClient(ClaudeSession(cfg=cfg)))
    elif 'oai' in k:
        llm_sessions.append(ToolClient(LLMSession(cfg=cfg)))
    elif 'mixin' in k:
        llm_sessions.append(MixinSession(all_sessions, cfg))
```

## 消息格式转换

### Claude → OpenAI

```python
def _msgs_claude2oai(msgs):
    result = []
    for m in msgs:
        if m['role'] == 'assistant':
            # tool_use 块 → tool_calls
            tool_calls = []
            for b in m.get('content', []):
                if b.get('type') == 'tool_use':
                    tool_calls.append({
                        "id": b.get("id", ""),
                        "type": "function",
                        "function": {
                            "name": b.get('name', ''),
                            "arguments": json.dumps(b.get('input', {}))
                        }
                    })
            result.append({"role": "assistant", "content": text, "tool_calls": tool_calls})

        elif m['role'] == 'user':
            # tool_result 块 → 独立 tool 消息
            for b in m.get('content', []):
                if b.get('type') == 'tool_result':
                    result.append({
                        "role": "tool",
                        "tool_call_id": b.get("tool_use_id", ""),
                        "content": b.get('content', '')
                    })
    return result
```

## 工具定义转换

```python
def openai_tools_to_claude(tools):
    '''OpenAI → Claude 工具定义'''
    result = []
    for t in tools:
        if 'input_schema' in t:
            return tools  # 已是 Claude 格式
        fn = t.get('function', t)
        result.append({
            'name': fn['name'],
            'description': fn.get('description', ''),
            'input_schema': fn.get('parameters', {"type": "object", "properties": {}})
        })
    return result
```

## 上下文压缩

### 历史标签压缩

```python
def compress_history_tags(history, keep_recent=10, force=False):
    '''压缩旧消息中的长标签'''
    for i, m in enumerate(history[:-keep_recent]):
        for b in m.get('content', []):
            if b.get('type') == 'tool_result':
                b['content'] = _trunc_str(b['content'], max_len=800)
            # 压缩 <thinking>, <history>, <key_info> 等
```

### 动态截断

```python
def trim_messages_history(history, context_win):
    cost = sum(len(json.dumps(m)) for m in history)

    if cost > context_win * 3:
        compress_history_tags(history, keep_recent=4, force=True)
        target = context_win * 3 * 0.6

        while len(history) > 5 and cost > target:
            history.pop(0)
            # 清理孤立的 tool_result
            while history and history[0].get('role') != 'user':
                history.pop(0)
```

## 上下文优化策略

### Peer Hint（行为引导）

```python
# agentmain.py — agent.peer_hint = True 时启用
# 每轮结束后追加行为建议，引导 agent 调整方向
```

### History Folding（历史折叠）

```python
# llmcore.py — 每 5 轮触发 compress_history_tags
# 旧标签压缩 + 摘要折叠，释放上下文空间
# 无文本输出时自动注入 thinking → tool_use 块
```

### 工具库缓存

```python
# ToolClient._prepare_tool_instruction
if self.auto_save_tokens and self.last_tools == tools_json:
    # 工具库未变，节省 tokens
    instruction = "\n### 工具库状态：持续有效\n"
else:
    instruction = f"### 可用工具库\n{tools_json}"
    self.last_tools = tools_json

if self.total_cd_tokens > 9000:
    self.last_tools = ''  # 超过阈值，下次完整注入
```

## 流式 SSE 解析

```python
def _parse_openai_sse(lines):
    content_blocks = []
    current_text = ""

    for line in lines:
        if line.startswith("data: "):
            data = json.loads(line[6:])
            delta = data['choices'][0].get('delta', {})

            if 'content' in delta:
                current_text += delta['content']
                yield delta['content']

            if 'tool_calls' in delta:
                # 收集工具调用
                for tc in delta['tool_calls']:
                    content_blocks.append({
                        "type": "tool_use",
                        "id": tc.get('id'),
                        "name": tc['function'].get('name'),
                        "input": json.loads(tc['function'].get('arguments', '{}'))
                    })

    return content_blocks
```

## MixinSession 负载均衡

```python
class MixinSession:
    def _raw_ask(self, *args, **kwargs):
        base = self._pick()  # 当前主 session

        for attempt in range(self._retries + 1):
            idx = (base + attempt) % len(self._sessions)
            gen = self._sessions[idx].raw_ask(*args, **kwargs)

            try:
                result = yield from gen
                if not is_error(result):
                    if attempt > 0:
                        self._cur_idx = idx  # 切换成功
                        self._switched_at = time.time()
                    return result
            except Exception:
                pass

            # 指数退避
            delay = min(30, self._base_delay * (1.5 ** attempt))
            time.sleep(delay)
```

---

## 双客户端架构（第二轮审计补充）

适配层提供两种客户端包装，对应两种协议风格：

| 客户端 | 协议 | 适用后端 | 工具传递方式 |
|--------|------|---------|-------------|
| **ToolClient** | 文本协议 | ClaudeSession, LLMSession | 工具定义序列化为 JSON 文本注入 system prompt |
| **NativeToolClient** | 原生协议 | NativeClaudeSession, NativeOAISession | 工具定义通过 API 原生 `tools` 参数传递 |

```python
class ToolClient:
    def chat(self, messages, tools):
        # 工具库 → 文本指令，拼入 system prompt
        instruction = self._prepare_tool_instruction(tools)
        messages[0]['content'] = instruction + messages[0]['content']
        return self.session.raw_ask(messages)

class NativeToolClient:
    def chat(self, messages, tools):
        # 工具库 → API 原生参数
        return self.session.raw_ask(messages, tools=tools)
```

**设计权衡**：文本协议兼容任意 OpenAI 兼容端点（含本地 Ollama），但无法利用模型原生工具调用能力；
原生协议支持 Claude extended thinking、结构化 tool_use 块，但要求端点完整实现 tool_calls API。

---

## _fix_messages 消息修复器（第二轮审计补充）

LLM 返回的消息常存在格式异常，`_fix_messages` 在发送前进行修复：

```python
def _fix_messages(messages):
    fixed = []
    for m in messages:
        # 1. 空 content 补充占位（某些 API 拒绝 null content）
        if m.get('content') is None:
            m['content'] = ""
        # 2. 连续同角色消息合并（API 要求 user/assistant 交替）
        if fixed and fixed[-1]['role'] == m['role']:
            fixed[-1]['content'] += "\n" + m['content']
            continue
        # 3. 孤立 tool_result 补充 assistant 占位
        if m['role'] == 'tool' and (not fixed or fixed[-1]['role'] != 'assistant'):
            fixed.append({"role": "assistant", "content": "[tool call]"})
        fixed.append(m)
    return fixed
```

**必要性**：不同后端对消息格式的容忍度差异极大。Claude 要求严格交替，OpenAI 允许连续 tool 消息。
修复器统一处理，使上层 loop 不必关心后端差异。
