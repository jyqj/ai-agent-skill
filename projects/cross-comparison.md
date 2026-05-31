# Agent 项目通用横向对比

> **Evidence Status** — synthesized. 基于 8 个参考项目的横向综合。

## 对比范围

| 编号 | 项目 | 定位 | 语言 |
|------|------|------|------|
| CC | Claude Code | 生产级 CLI coding agent | TypeScript |
| CX | Codex CLI | 本地沙箱 coding agent | Rust + TypeScript |
| HM | Hermes Agent | 多平台通用 agent | TypeScript |
| GA | GenericAgent | 极简通用 agent | TypeScript |
| WP | Warp | Agentic 开发平台 | Rust |
| OC | OpenCode | 多形态 agent 框架 | TypeScript (Effect.js) |
| TR | Trellis | Multi-platform Agent Harness | TypeScript + Python |
| OW | OpenClaw | Personal AI Gateway | TypeScript |

---

## 1. 架构范式

| 项目 | 范式 | 核心循环 |
|------|------|---------|
| CC | Runtime 工程 | Query → Tool → Compress 闭环 |
| CX | 安全即能力 | Sandbox → Guardian → Execute |
| HM | Gateway + 学习循环 | Platform Adapter → Agent → Skill Curator |
| GA | 极简 Generator | Prompt → Generate → Verify |
| WP | Agent 即贡献者 | Skill → Agent → Orchestrate |
| OC | 可组合 Runtime | Effect Service → Layer → Stream |
| TR | 工作流 Harness | Breadcrumb → Task → Spec Inject |
| OW | Gateway 控制平面 | Manifest → Channel → Session |

---

## 2. Plugin / 工具注册

| 维度 | CC | CX | HM | GA | WP | OC | TR | OW |
|------|----|----|----|----|----|----|----|----|
| 注册方式 | 内置+MCP | 内置+AGENTS.md | AST 动态发现 | 显式 9 工具 | SkillProvider 枚举 | Effect DI | AI_TOOLS Registry | Manifest-First |
| 工具数 | 60+ | ~10 | 40+ | 9 | 多 Agent | ~20 | 14 平台×N | 125 extensions |
| 边界 | Hook | 沙箱 | check_fn TTL | 无 | Profile | Zod schema | 占位符中立化 | SDK facade |

---

## 3. 权限 / 安全模型

| 维度 | CC | CX | HM | GA | WP | OC | TR | OW |
|------|----|----|----|----|----|----|----|----|
| 模型 | permissionMode+Hook | Guardian LLM(0-100) | 三层审批 | 无 | Profile+原因枚举 | deny>ask>allow | 隐式(Hook控制) | ACP+DM Pairing |
| 沙箱 | 无 | Seatbelt/Landlock | 无 | 无 | 云容器+PTY | 无 | 无 | Docker/SSH/OpenShell |
| 凭证 | 会话级缓存 | 无 | 多 credential pool | 无 | 企业 override | 系统级配置 | 无 | Session-scoped auth |

---

## 4. 上下文 / 压缩

| 维度 | CC | CX | HM | GA | WP | OC | TR | OW |
|------|----|----|----|----|----|----|----|----|
| 策略 | 5 层渐进 | 2 阶段 rollout | 迭代预算(4维) | 截断 | Skill 注入 | 3 层 Prune | JSONL spec inject | Context Engine |
| 特色 | 熔断器 | 后台异步 | FTS5 记忆 | 极简 | 无压缩 | Effect Stream | Breadcrumb per-turn | Prepared facts |

---

## 5. 记忆 / 持久化

| 维度 | CC | CX | HM | GA | WP | OC | TR | OW |
|------|----|----|----|----|----|----|----|----|
| 机制 | MEMORY.md 3 scope | StateDb+rollout | SQLite FTS5 | 4 层分级 | Diesel+SQLite | SQLite WAL | Journal 轮转(2000行) | Memory plugin slot |
| 跨会话 | Session fork | 两阶段管道 | Frozen snapshot | Action-Verified | ResumePayload | Task fork | task.json 持久 | LanceDB vector |

---

## 6. 多 Agent / 编排

| 维度 | CC | CX | HM | GA | WP | OC | TR | OW |
|------|----|----|----|----|----|----|----|----|
| 模式 | Fork/Spawn/Teammate | spawn_agent+深度限制 | Kanban Worker | 无 | RunAgents+ThirdParty | Task Tool 递归 | 4 sub-agent+dispatch mode | Multi-agent routing |
| 上下文传递 | 消息+指令 | send_input | 摘要返回 | 无 | 事件+生命周期 | 摘要返回 | Hook push / Pull-based | Session isolation |

---

## 关键差异总结

1. **Trellis 是唯一的 "不运行 Agent 的 Agent 项目"**：它是 Harness 层，为 14 个 IDE 提供统一工作流
2. **OpenClaw 是唯一的 "Gateway 控制平面"**：Agent 在独立进程，Gateway 只做调度
3. **OpenClaw 的 plugin 规模最大**：125 extensions，远超其他项目
4. **Trellis 的 breadcrumb per-turn 是独特的状态管理模式**：其他项目都靠一次性注入或内存
5. **OpenClaw 和 Hermes 都有 multi-channel**，但 OpenClaw 是 DM-first（个人助手），Hermes 是多用户

## 与知识库的关联

- Trellis 补充了 `patterns/hook-system.md`、`patterns/harness-container.md`、`patterns/milestone-gated-execution.md`
- OpenClaw 补充了 `patterns/tool-registry.md`、`patterns/credential-pool-failover.md`、`patterns/layered-memory.md`
- 两者共同补充了 `patterns/subagent.md`（push vs pull context）
- 新模式：`platform-adapter-registry`、`manifest-first-plugin`、`gateway-control-plane`、`channel-adapter`、`prepared-runtime-facts`
