# NagaAgent


> **Evidence Status** — grounded. 本目录下的架构、memory、prompt、execution 分析。

## 基本信息

- **类型**：companion-agent
- **项目定位**：全栈 companion agent，集成对话、记忆、语音、虚拟形象和 MCP 工具。
- **学习来源**：本地项目分析文档。
- **推荐入口**：README → prompt-system.md / memory-grag.md / execution-layer.md。

## 模块覆盖

| 模块 | 覆盖程度 | 证据文件 | 可复用模式 |
|---|---|---|---|
| interface | 深 | README.md | multi-modal gateway |
| representation | 中 | README.md / prompt-system.md | voice / avatar / event representation |
| context | 中 | prompt-system.md | layered prompt |
| memory | 深 | memory-grag.md | GRAG memory |
| tools | 中 | mcp-skills.md | MCP registry |
| orchestration | 中 | execution-layer.md | heartbeat / service split |

## 关键发现

- Companion 场景中，表示层（语音、形象、情绪表达）的设计权重远高于纯 chat agent：用户感知到的"智能"很大程度来自表示而非推理。
- 人格、关系和情绪必须分层管理（四层 prompt：基础人格 → 关系记忆 → 情境上下文 → 实时补充），混在一起会导致人格漂移。
- 主动性需要 heartbeat 事件机制驱动，而不能只靠被动的对话循环。agent 必须能在没有用户输入时也触发行为（如主动问候、定时检查）。

> **二次元超能 AI 助手框架**，集对话、记忆、工具调用、语音交互、虚拟形象于一身的智能体系统。

---

## 项目定位

NagaAgent 是一个**全栈智能体系统**，体现三个维度的创新：

1. **技术创新**：自动 GRAG（五元组知识图谱）、流式工具调用、事件驱动心跳
2. **设计创新**：4 通道 Live2D 动画、多模态口型同步、热补丁更新
3. **理念创新**：拟人化 SOUL 日志、分布式思维的叙事化

---

## 核心公式

```
NagaAgent = 微服务 + 分层 Prompt + GRAG 记忆 + 流式工具循环 + 主动心跳
```

---

## 架构速览

```
┌──────────────────────────────────────────────────────────┐
│          Electron/PyQt5 前端 (Vue 3 + Vite)              │
└────────┬──────────────┬───────────────┬──────────────────┘
         │              │               │
    ┌────▼─────┐  ┌──────▼──┐  ┌──────▼────┐
    │ API :8000│  │Agent:8001│  │Voice:5048 │
    │ 对话引擎  │  │任务编排  │  │TTS/ASR    │
    └────┬─────┘  └──────┬──┘  └───────────┘
         │               │
    ┌────▼────────────────▼────┐
    │   MCP Server :8003        │
    │  工具注册 / 并行调度       │
    └────┬─────────────────────┘
         │
    ┌────▼──────────────────────────────┐
    │  MCP Agents（可插拔）              │
    │ 天气|搜索|抓取|视觉|启动器|攻略   │
    └────┬──────────────────────────────┘
         │
    ┌────▼──────┐      ┌──────────┐
    │  Neo4j    │      │OpenClaw  │
    │  知识图谱  │      │Gateway   │
    └───────────┘      └──────────┘
```

---

## 核心文件索引

| 模块 | 路径 | 核心功能 |
|------|------|--------|
| 分层 Prompt | `system/prompts/tier{1-4}/` | 四层上下文组装 |
| Prompt 装配 | `system/config.py` | `build_system_prompt()`, `build_context_supplement()` |
| 工具循环 | `apiserver/agentic_tool_loop.py` | Agentic Tool Loop (max 5 轮) |
| 意图路由 | `apiserver/intent_router.py` | Nano 模型快速分类 |
| 上下文压缩 | `apiserver/context_compressor.py` | 6 分区压缩，100k token 触发 |
| 记忆系统 | `summer_memory/` | GRAG 五元组 + 任务管理器 |
| MCP 注册 | `mcpserver/mcp_registry.py` | 自动扫描 + 动态加载 |
| 心跳系统 | `agentserver/dogtag/` | 事件驱动 + 主动思考 |

---

## 差异化特点

| 特性 | NagaAgent | 其他框架 |
|------|----------|---------|
| **工具调用** | 文本代码块（所有 API 兼容） | 依赖 OpenAI Function Calling |
| **知识图谱** | 自动五元组 + Neo4j | 向量 RAG |
| **心跳机制** | 事件驱动 v3 | 无或轮询 |
| **上下文压缩** | 6 分区 + 跨会话继承 | 简单滑窗 |
| **拟人化设计** | SOUL.md 自维护日志 | 无 |

---

## 子文档

- `./architecture.md` - 微服务架构详解
- `./prompt-system.md` - 四层 Prompt 系统
- `./memory-grag.md` - GRAG 记忆系统
- `./execution-layer.md` - 执行层设计
- `./mcp-skills.md` - MCP 和技能系统
- `./patterns.md` - 可复用设计模式
