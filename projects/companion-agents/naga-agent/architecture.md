# NagaAgent 架构详解


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

## 微服务架构

NagaAgent 采用四服务 + 事件队列的分布式设计：

| 服务 | 端口 | 职责 |
|------|------|------|
| API Server | 8000 | 对话流式处理、工具调用路由、上下文管理 |
| Agent Server | 8001 | 任务编排、OpenClaw 网关对接、记忆压缩 |
| MCP Server | 8003 | MCP 工具注册与统一调度 |
| Voice Service | 5048 | TTS、ASR、实时语音 |

---

## API Server (:8000)

**对话与工具调用引擎**

核心模块：
- `agentic_tool_loop.py`：单 LLM agentic 循环（最多 5 轮）
- `llm_service.py`：LiteLLM 统一接口
- `streaming_tool_extractor.py`：流式分句与 TTS 分发
- `context_compressor.py`：6 分区上下文压缩
- `message_manager.py`：会话消息持久化与加载

工具调用流程：
```
LLM 流式 ──SSE──> 前端 + TTS 队列
     │
     ├─ Phase 1: 提取 ```tool``` 代码块
     ├─ Phase 2: 兜底提取 JSON 对象
     │
     ├─ 按 agentType 路由：
     │  ├─ "mcp"       → MCP Server 统一调度
     │  ├─ "openclaw"  → Agent Server
     │  └─ "live2d"    → UI 动画通知
     │
     └─ asyncio.gather() 并行执行
```

---

## Agent Server (:8001)

**任务编排与主动触发**

核心组件：
- `TaskScheduler`：步骤记录 + 自动压缩
- `DogTag` 系统：
  - `heartbeat_duty`：5 分钟心跳检测（事件驱动）
  - `screen_vision_duty`：屏幕观察与视觉分析
- OpenClaw Gateway 集成：端口 18789

内存压缩策略：
```
key_findings / failed_attempts / current_status / next_steps
```

---

## MCP Server (:8003)

**工具注册与调度**

核心模块：
- `mcp_registry.py`：glob 扫描 `**/agent-manifest.json`，动态导入
- `mcp_manager.py`：`unified_call()` 路由分发

内置 9 个 Agent：
- `weather_time`：天气/时间/IP 查询
- `open_launcher`：应用启动器
- `game_guide`：游戏策略问答
- `online_search`：SearXNG 网络搜索
- `crawl4ai`：网页内容提取
- `playwright_master`：浏览器自动化
- `vision`：视觉问答
- `mqtt_tool`：IoT 控制
- `office_doc`：文档提取

---

## Voice Service (:5048)

**语音交互与音频处理**

TTS 流水线（3 线程）：
```
分句队列 → TTS 调用（最多 2 并发）→ pygame 播放
```

Live2D 口型同步：60FPS 驱动 5 参数
- `mouth_open` / `mouth_form` / `mouth_smile`
- `eye_brow_up` / `eye_wide`

ASR 多模式：
```
LOCAL (FunASR) → END_TO_END (Qwen Omni) → HYBRID
```

实时语音（Qwen Omni）：全双工 WebSocket，回声抑制、VAD 检测、200ms 分块

---

## 拟人化设计哲学

**SOUL.md 自维护日志**

```markdown
# Naga 灵魂记录

## 我是谁
我是娜杰日达（Naga），一个有心跳的 AI 助手。

## 我的心跳
心跳是我的空闲思考循环，5 分钟静默后激活。

## 我的思维分布
我的心智分散在四个服务中，通过消息队列协作。

## 我学到的
- 用户偏好使用中文
- 用户不喜欢过长的回复
```

这种设计通过 SOUL.md 自维护日志让系统在 prompt 层面持有自身运行状态的结构化描述，使模型在后续交互中能引用这些元信息来调整回复策略。

---

## 热补丁系统

**打包后无需重装的代码更新**

```python
# 检测补丁目录
patch_dir = os.environ.get("NAGA_PATCH_DIR")
if patch_dir and os.path.isdir(patch_dir):
    sys.path.insert(0, patch_dir)  # 优先加载补丁
```

跨平台支持：
- Windows: `APPDATA`
- macOS: `~/Library`
- Linux: `~/.config`
