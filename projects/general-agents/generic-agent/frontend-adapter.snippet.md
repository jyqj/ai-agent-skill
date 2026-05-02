# 多前端统一架构

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> 核心模式：**队列协议 + 适配层解耦**

## 三层架构

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 1: Protocol Adapter (协议适配)                           │
│  ├─ Streamlit: st.chat_input / session_state                  │
│  ├─ WeChat: WxBotClient HTTP                                   │
│  ├─ Telegram: python-telegram-bot                              │
│  ├─ QQ: qq-botpy WebSocket                                     │
│  ├─ 钉钉: dingtalk-stream                                      │
│  ├─ 企业微信: wecom_aibot_sdk                                  │
│  └─ 飞书: lark-oapi                                            │
└─────────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────────┐
│ Layer 2: Unified Facade (统一门面)                             │
│  ├─ AgentChatMixin (可选继承)                                  │
│  ├─ async send_text() 多态                                     │
│  └─ run_agent() 流程复用                                       │
└─────────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────────┐
│ Layer 3: Agent Engine (核心引擎)                               │
│  ├─ agentmain.GeneraticAgent                                   │
│  ├─ put_task() + display_queue                                 │
│  └─ agent_runner_loop                                          │
└─────────────────────────────────────────────────────────────────┘
```

## 队列协议

```python
# agentmain.py
def put_task(self, query, source="user", images=None):
    '''非阻塞入队，返回独立输出队列'''
    display_queue = queue.Queue()
    self.task_queue.put({
        "query": query,
        "source": source,
        "images": images or [],
        "output": display_queue
    })
    return display_queue
```

**消息类型**：

| 类型 | 格式 | 场景 |
|-----|------|------|
| 增量 | `{'next': str}` | 流式输出中 |
| 完成 | `{'done': str}` | 任务完成 |
| 超时 | 无消息 | 处理中 |

## AgentChatMixin 抽象

```python
class AgentChatMixin:
    label = "Chat"
    source = "chat"
    split_limit = 1500      # 消息分割限制
    ping_interval = 20      # 心跳间隔

    async def send_text(self, chat_id, content, **ctx):
        '''子类必须实现'''
        raise NotImplementedError

    async def run_agent(self, chat_id, text, **ctx):
        '''统一流程'''
        dq = agent.put_task(text, source=self.source)
        last_ping = time.time()

        while True:
            try:
                item = await asyncio.to_thread(dq.get, True, 3)
            except queue.Empty:
                if agent.is_running and time.time() - last_ping > self.ping_interval:
                    await self.send_text(chat_id, "⏳ 处理中...")
                    last_ping = time.time()
                continue

            if 'next' in item:
                await self.send_text(chat_id, item['next'])
            if 'done' in item:
                await self.send_text(chat_id, item['done'])
                break
```

## 渠道特化示例

### WeChat 消息格式转换

```python
def _strip_md(t):
    '''WeChat 特定的 Markdown 简化'''
    # 代码块截断
    t = re.sub(r'(`{3,})[\s\S]*?\1', _trunc_code, t)
    # 链接文字化
    t = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', t)
    # 列表化
    t = re.sub(r'^\s*[-*+]\s+', '• ', t, flags=re.M)
    return t
```

### Telegram HTML 转换

```python
def _to_html(t):
    '''Telegram HTML 格式'''
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'\*(.+?)\*', r'<i>\1</i>', t)
    t = re.sub(r'`(.+?)`', r'<code>\1</code>', t)
    return t
```

### 飞书卡片消息

```python
def _card(text):
    return json.dumps({
        "config": {"wide_screen_mode": True},
        "elements": [{"tag": "markdown", "content": text}]
    })
```

## 多模态输入

```python
# 通用媒体标记格式
"[image: image.jpg]\n[File: source: /path/to/image.jpg]"

# 传递给 Agent
dq = agent.put_task(
    f"{text}\n\n{media_description}",
    source="feishu",
    images=[file_path, ...]
)
```

## 新渠道集成清单

```
1. Protocol Adapter (必需)
   ├─ init()
   ├─ receive_message(callback)
   ├─ send_text(chat_id, text)
   └─ download_media() [可选]

2. 继承 AgentChatMixin (推荐)
   ├─ async send_text() 实现
   └─ run_agent() 调用

3. 权限控制 (推荐)
   ├─ ALLOWED 白名单
   └─ public_access() 检查

4. 主循环 (必需)
   ├─ Thread(agent.run, daemon=True).start()
   └─ while True: receive_loop()
```
