# 多平台网关

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> 来源：`gateway/run.py`, `gateway/platforms/`

## 网关架构

```python
class GatewayRunner:
    def __init__(self, config: GatewayConfig):
        self.adapters: Dict[Platform, BasePlatformAdapter] = {}
        self._running_agents: Dict[str, AIAgent] = {}  # session_key → agent
        self._agent_cache: Dict[str, tuple] = {}       # 缓存代理实例
        self._pending_messages: Dict[str, str] = {}    # 中断时排队
        self._session_store = SessionStore(config.sessions_dir)

    async def start(self):
        # 并行启动所有适配器
        tasks = [adapter.connect() for adapter in self.adapters.values()]
        await asyncio.gather(*tasks)

        # 启动 cron 调度器
        self._cron_task = asyncio.create_task(self._run_cron_scheduler())

        # 主消息循环
        await self._message_loop()
```

**洞察**：单一 asyncio 循环驱动所有平台。代理缓存按会话保存，保持前缀缓存跨消息不变。

---

## 平台适配器接口

```python
class BasePlatformAdapter(ABC):
    def __init__(self, config: PlatformConfig, platform: Platform):
        self._message_handler: Optional[MessageHandler] = None
        self._active_sessions: Dict[str, asyncio.Event] = {}  # 中断事件
        self._pending_messages: Dict[str, MessageEvent] = {}  # 排队消息
        self._background_tasks: set[asyncio.Task] = set()

    @abstractmethod
    async def connect(self) -> bool:
        """连接平台。"""
        pass

    @abstractmethod
    async def send(self, chat_id: str, content: str) -> SendResult:
        """发送文本消息。"""
        pass

    async def send_image(self, chat_id: str, image_url: str) -> SendResult:
        """发送图片（可选实现）。"""
        ...

    async def send_voice(self, chat_id: str, audio_path: str) -> SendResult:
        """发送语音（可选实现）。"""
        ...
```

**洞察**：抽象接口强制核心方法。后台任务集合在网关关闭时批量取消。SendResult 带 retryable 标记。

---

## 消息规范化

```python
@dataclass
class MessageEvent:
    text: str
    message_type: MessageType = MessageType.TEXT  # TEXT|PHOTO|VOICE|DOCUMENT
    source: SessionSource = None  # platform, chat_id, user_id, thread_id
    media_urls: List[str] = field(default_factory=list)  # 本地缓存路径
    media_types: List[str] = field(default_factory=list)
    reply_to_message_id: Optional[str] = None  # 链式回复
    auto_skill: Optional[str] = None  # 主题绑定技能

    def is_command(self) -> bool:
        return self.text.startswith("/")
```

**洞察**：统一表示屏蔽平台差异。media_urls 为本地路径（已缓存），避免 CDN 短期有效期。

---

## 会话键生成

```python
def build_session_key(source: SessionSource, config: SessionConfig) -> str:
    """生成会话隔离键。"""
    parts = [source.platform, source.chat_id]

    # 按用户隔离（可选）
    if config.group_sessions_per_user:
        parts.append(source.user_id)

    # 按线程隔离（Discord/Slack）
    if config.thread_sessions_per_user and source.thread_id:
        parts.append(source.thread_id)

    # Signal UUID 别名解析
    if source.platform == "signal":
        parts[2] = _resolve_signal_uuid(source.user_id)

    # WhatsApp LID 映射
    if source.platform == "whatsapp":
        parts[2] = _resolve_whatsapp_lid(source.user_id)

    return ":".join(parts)
```

**洞察**：多粒度隔离支持。Signal/WhatsApp 特殊处理避免 ID 漂移。

---

## 会话上下文注入

```python
def build_session_context_prompt(context: SessionContext, redact_pii: bool) -> str:
    lines = [
        "## Current Session Context",
        f"**Source:** {platform} ({description})",
        f"**Channel Topic:** {context.source.chat_topic}",
        f"**Connected Platforms:** {', '.join(platforms)}",
        "**Delivery options:**",
        "- \"origin\" → Back to this chat",
        "- \"local\" → Save to files",
        "- \"telegram\" → Home channel",
    ]

    # PII 安全模式：Telegram/WhatsApp/Signal 哈希 ID
    if redact_pii and context.source.platform in _PII_SAFE_PLATFORMS:
        user_id = _hash_id(user_id)

    return "\n".join(lines)
```

**洞察**：动态提示让 LLM 知晓上下文和交付选项。PII 区分平台：提及系统（Discord）需原始 ID。

---

## Cron 交付路由

```python
def _resolve_delivery_target(job: dict) -> Optional[dict]:
    deliver = job.get("deliver", "local")

    if deliver == "origin":
        # 返回任务来源
        return {"platform": origin["platform"], "chat_id": origin["chat_id"]}

    if deliver == "local":
        # 本地文件
        return None

    if ":" in deliver:
        # 显式目标：platform:chat_id
        platform, chat_id = deliver.split(":", 1)
        return {"platform": platform, "chat_id": resolve_channel_name(chat_id)}

    # 平台家庭频道
    home = os.getenv(f"{deliver.upper()}_HOME_CHANNEL")
    return {"platform": deliver, "chat_id": home}
```

**洞察**：四元组路由（origin/local/platform/explicit）。支持人类友好标签映射。

---

## 人机协作回调

```python
def approval_callback(cli, command: str, description: str) -> str:
    with cli._approval_lock:  # 序列化并发请求
        timeout = config.get("approvals", {}).get("timeout", 60)
        response_queue = queue.Queue()

        cli._approval_state = {
            "command": command,
            "description": description,
            "choices": ["once", "session", "always", "deny"],
            "response_queue": response_queue,
        }
        cli._approval_deadline = time.monotonic() + timeout
        cli._app.invalidate()  # 刷新 TUI

        while True:
            try:
                return response_queue.get(timeout=1)
            except queue.Empty:
                if time.monotonic() > cli._approval_deadline:
                    return "deny"  # 超时默认拒绝
```

**洞察**：线程锁防止并发竞争。队列解耦 TUI 和代理线程。超时降级安全（拒绝而非批准）。

---

## SQLite 会话存储

```python
class SessionStore:
    def __init__(self, sessions_dir: Path):
        self._db_path = sessions_dir / "sessions.db"
        self._fallback_json = sessions_dir / "sessions.json"

    def get_session(self, session_key: str) -> Optional[SessionEntry]:
        try:
            # 优先 SQLite
            db = SessionDB()
            return SessionEntry.from_dict(db.get_session(session_key))
        except Exception:
            # 降级 JSONL
            return self._get_from_jsonl(session_key)

    def save_session(self, entry: SessionEntry):
        # 双写确保可迁移
        try:
            SessionDB().save_session(entry.to_dict())
        except Exception:
            self._save_to_jsonl(entry)
```

**洞察**：SQLite 优先（分析、导出），JSONL 降级（无依赖）。双写确保可迁移性。
