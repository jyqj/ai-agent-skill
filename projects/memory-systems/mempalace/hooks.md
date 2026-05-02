# Auto-Save Hooks 设计


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> **两层保护：定期保存 + 压缩前紧急保存**

## 两个 Hook

| Hook | 触发时机 | 职责 | 阻止行为 |
|------|---------|------|---------|
| **Save Hook** | 每 15 条人类消息 | 定期 checkpoint | 有条件：达阈值时 |
| **PreCompact Hook** | 上下文即将压缩 | 紧急保存 | 总是阻止 |

## 工作流

### Save Hook（Stop 事件）

```
User msg → AI response → Stop 事件触发
                              │
                    ┌─────────▼─────────┐
                    │  数人类消息       │
                    └─────────┬─────────┘
                              │
         ┌────────────────────┴────────────────────┐
         │                                         │
    < 15 since                               ≥ 15 since
     last save                                last save
         │                                         │
     echo "{}"                              Block AI:
         │                              {"decision": "block",
      正常 stop                          "reason": "AUTO-SAVE..."}
         │                                         │
         │                              AI 保存到 palace
         │                                         │
         │                              尝试第二次 stop
         │                                         │
         │                         Hook 看 stop_hook_active=true
         │                                         │
         └─────────────────────────→ echo "{}" (通过)
```

### PreCompact Hook

```
Context window 满 → 即将压缩
           │
    Hook 总是返回:
{"decision": "block",
 "reason": "COMPACTION IMMINENT..."}
           │
       AI 保存一切
           │
      压缩继续进行
```

## 配置

### Claude Code

```json
// .claude/settings.local.json
{
  "hooks": {
    "Stop": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "/path/to/hooks/mempal_save_hook.sh",
        "timeout": 30
      }]
    }],
    "PreCompact": [{
      "hooks": [{
        "type": "command",
        "command": "/path/to/hooks/mempal_precompact_hook.sh",
        "timeout": 30
      }]
    }]
  }
}
```

### Codex CLI

```json
// .codex/hooks.json
{
  "Stop": [{
    "type": "command",
    "command": "...",
    "timeout": 30
  }],
  "PreCompact": [{
    "type": "command",
    "command": "...",
    "timeout": 30
  }]
}
```

## 关键设计细节

### 无限循环防护

```bash
# stop_hook_active 标志
# block 一次 → AI 保存 → 再 stop → 标志为 true → hook 放通

if [[ "$STOP_HOOK_ACTIVE" == "true" ]]; then
    echo "{}"  # 放通，不再 block
    exit 0
fi
```

### 状态文件

```
~/.mempalace/hook_state/
  ├── ${session_id}_last_save    # 上次保存时的消息计数
  ├── ${session_id}_msg_count    # 当前消息计数
  └── hook.log                   # 触发日志
```

### Block Reason 驱动 AI 行为

Hook 返回的 `reason` 是 AI 看到的系统消息：

```json
{
  "decision": "block",
  "reason": "AUTO-SAVE: 15+ messages since last checkpoint. Please:\n1. Call mempalace_diary_write with session summary\n2. Call mempalace_add_drawer for important exchanges\n3. Call mempalace_kg_add for new facts"
}
```

AI 根据这个指令主动调用 MCP 工具保存。

## AI 如何分类保存

| 维度 | AI 决策 |
|-----|--------|
| **Wing** | 根据主题（wing_user / wing_team / wing_code） |
| **Room** | 根据内容类型（diary / decisions / meetings） |
| **Hall** | 根据信息性质（hall_facts / hall_events） |
| **格式** | 可选用 AAAK 压缩日记 |

## 保存的 Drawer 结构

```python
{
    "wing": "wing_myproject",
    "room": "architecture-decisions",
    "source_file": "session_abc123",
    "added_by": "claude",
    "filed_at": "2026-04-15T14:30:00",
}
```

## 成本模型

| 项目 | 成本 |
|-----|------|
| Hook 执行 | $0（本地 bash + Python） |
| AI 保存时间 | 几秒（组织记忆，使用已加载上下文） |
| 存储增长 | 线性（原文存储，无总结丢失） |

## 设计权衡

| 选择 | 理由 |
|-----|------|
| **AI 决定分类** | AI 有上下文，知道什么重要 |
| **Hook 只做计数** | 简单可靠，不依赖 LLM |
| **两层保护** | 定期 + 紧急，不遗漏 |
| **15 条消息阈值** | 平衡打断频率 vs 保存充分 |
| **Block 而非直接调用 MCP** | 让 AI 有机会组织和决策 |
