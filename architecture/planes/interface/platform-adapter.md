# Platform Adapter Pattern


> **Evidence Status** — synthesized. 通用运行时模块来自多个参考项目的统一抽象。

## 问题

Agent 需要接入多个消息平台（Telegram/Discord/Slack/WhatsApp）：
- 每个平台 API 不同
- 消息格式不同
- 媒体处理不同
- 会话模型不同

## 解法

**抽象适配器 + 统一消息事件**：

```python
@dataclass
class MessageEvent:
    text: str
    message_type: MessageType  # TEXT|PHOTO|VOICE|DOCUMENT
    source: SessionSource      # platform, chat_id, user_id, thread_id
    media_urls: List[str]      # 本地缓存路径
    reply_to_message_id: Optional[str] = None
    auto_skill: Optional[str] = None

class BasePlatformAdapter(ABC):
    @abstractmethod
    async def connect(self) -> bool:
        """连接平台"""
        ...

    @abstractmethod
    async def send(self, chat_id: str, content: str) -> SendResult:
        """发送文本"""
        ...

    async def send_image(self, chat_id: str, image_url: str) -> SendResult:
        """发送图片（可选实现）"""
        ...

    async def send_voice(self, chat_id: str, audio_path: str) -> SendResult:
        """发送语音（可选实现）"""
        ...
```

## 网关架构

```python
class GatewayRunner:
    def __init__(self):
        self.adapters: Dict[Platform, BasePlatformAdapter] = {}
        self._running_agents: Dict[str, AIAgent] = {}  # 按会话缓存
        self._session_store = SessionStore()

    async def start(self):
        # 并行启动所有适配器
        tasks = [adapter.connect() for adapter in self.adapters.values()]
        await asyncio.gather(*tasks)

        # 启动消息循环
        await self._message_loop()

    async def _handle_message(self, event: MessageEvent):
        session_key = build_session_key(event.source)

        # 重用缓存的 Agent（保持 prompt caching）
        agent = self._running_agents.get(session_key)
        if not agent:
            agent = AIAgent(session_id=session_key, ...)
            self._running_agents[session_key] = agent

        response = await agent.chat(event.text)
        await self._route_response(event.source, response)
```

## 会话键生成

```python
def build_session_key(source: SessionSource, config: SessionConfig) -> str:
    parts = [source.platform, source.chat_id]

    # 按用户隔离（可选）
    if config.group_sessions_per_user:
        parts.append(source.user_id)

    # 按线程隔离（Discord/Slack）
    if config.thread_sessions_per_user and source.thread_id:
        parts.append(source.thread_id)

    return ":".join(parts)
```

## 媒体缓存

```python
async def _cache_media(self, url: str, media_type: str) -> str:
    """下载媒体到本地，返回本地路径。"""
    cache_dir = get_cache_dir() / media_type
    cache_dir.mkdir(exist_ok=True)

    filename = hashlib.md5(url.encode()).hexdigest()
    local_path = cache_dir / filename

    if not local_path.exists():
        content = await self._download(url)
        local_path.write_bytes(content)

    return str(local_path)
```

**为什么缓存**：
- CDN URL 短期有效
- 视觉工具需要本地路径
- 避免重复下载

## 交付路由

```python
def _resolve_delivery(job: dict) -> Optional[dict]:
    deliver = job.get("deliver", "local")

    if deliver == "origin":
        return {"platform": origin["platform"], "chat_id": origin["chat_id"]}
    if deliver == "local":
        return None  # 本地文件
    if ":" in deliver:
        platform, chat_id = deliver.split(":", 1)
        return {"platform": platform, "chat_id": chat_id}
    # 平台家庭频道
    return {"platform": deliver, "chat_id": os.getenv(f"{deliver.upper()}_HOME")}
```

## 权衡

| 优点 | 缺点 |
|-----|------|
| 统一接口 | 每个平台有特殊 edge case |
| 按会话缓存 Agent | 内存占用随会话增长 |
| 媒体本地化 | 需要清理过期缓存 |

## 适用场景

- 多平台 Agent
- 统一会话管理
- 跨平台消息投递

## 来源

Hermes Agent `gateway/run.py`, `gateway/platforms/`
