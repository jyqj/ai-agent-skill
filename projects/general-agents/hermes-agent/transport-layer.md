# Provider 格式转换层

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> 来源：`hermes_cli/providers/transports/`

## ProviderTransport ABC

每个 LLM Provider 的请求/响应格式不同，Transport 层负责双向转换：

```python
class ProviderTransport(ABC):
    @abstractmethod
    def format_request(self, messages: List[dict], tools: List[dict], **kwargs) -> dict:
        """将标准消息格式转换为 Provider 专有请求体。"""
        ...

    @abstractmethod
    def parse_response(self, raw: dict) -> NormalizedResponse:
        """将 Provider 专有响应转换为标准 NormalizedResponse。"""
        ...

    @abstractmethod
    def parse_stream_chunk(self, chunk: bytes) -> Optional[StreamDelta]:
        """解析流式 chunk 为标准增量。"""
        ...
```

---

## 四种实现

| Transport | Provider | 关键差异 |
|-----------|----------|---------|
| **OpenAITransport** | OpenAI, Azure, 兼容端点 | tool_calls 数组、function_call 格式 |
| **AnthropicTransport** | Anthropic Claude | content blocks、tool_use/tool_result 块 |
| **GoogleTransport** | Gemini | functionCall/functionResponse、parts 数组 |
| **BedrockTransport** | AWS Bedrock | 包装层，内部按模型委托到 Anthropic/Meta transport |

```python
class AnthropicTransport(ProviderTransport):
    def format_request(self, messages, tools, **kwargs):
        return {
            "model": kwargs["model"],
            "messages": self._convert_messages(messages),
            "tools": self._convert_tools(tools),     # input_schema 格式
            "max_tokens": kwargs.get("max_tokens", 8192),
            "system": kwargs.get("system_prompt", ""),
        }

    def parse_response(self, raw) -> NormalizedResponse:
        # content blocks → 统一 tool_calls + text
        return NormalizedResponse(
            text=self._extract_text(raw["content"]),
            tool_calls=self._extract_tool_calls(raw["content"]),
            usage=Usage(input=raw["usage"]["input_tokens"],
                        output=raw["usage"]["output_tokens"]),
            stop_reason=raw["stop_reason"],
        )
```

---

## NormalizedResponse

所有 Transport 输出统一为 NormalizedResponse，上层代码无需感知 Provider 差异：

```python
@dataclass
class NormalizedResponse:
    text: str                           # 文本内容
    tool_calls: List[ToolCall]          # 标准化工具调用
    usage: Usage                        # token 用量
    stop_reason: str                    # stop / tool_use / max_tokens / content_filter
    raw: Optional[dict] = None          # 原始响应（调试用）
    thinking: Optional[str] = None      # extended thinking 内容（仅 Claude）
```

**设计意图**：Transport 层是 Provider 多样性的唯一吸收点。新增 Provider 只需实现一个 Transport，
不影响 agent loop、工具调度、错误恢复等上层逻辑。
