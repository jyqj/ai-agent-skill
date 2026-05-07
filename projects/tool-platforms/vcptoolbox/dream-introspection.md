# AgentDream 梦系统 - AI 内省架构

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

## 核心理念

> 让 AI 拥有安全的内省能力：在隔离的梦境中重新审视记忆，发现清醒时被线性思维掩盖的深层关联，然后由人类管理员对改动进行最终决策。

## 系统架构

```
┌─────────────────────────────────────────────┐
│        AgentDream.js (核心引擎)              │
├─────────────────────────────────────────────┤
│ ① 记忆采集 ← DreamWaveEngine (涟漪浪潮)     │
│ ② 梦提示词组装 (dreampost.txt 模板)         │
│ ③ 梦叙事生成 (VCP API 调用)                 │
│ ④ 梦操作处理 (processToolCall)              │
│ ⑤ 梦日志持久化 (dream_logs/*.json)          │
│ ⑥ VCPInfo 实时广播                          │
└─────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────┐
│  管理面板审批系统 (DreamManager.vue)         │
│  routes/admin/dream.js                       │
└─────────────────────────────────────────────┘
```

## 梦的生命周期

### 1. 触发机制
```javascript
// 自动触发
时间窗口: 凌晨 1-6 点
频率: 8 小时一次
概率: 60% 在窗口内触发

// 手动触发
action: "triggerDream", agent_name: "Nova"
```

### 2. 记忆采集 (DreamWaveEngine V8)
```
Phase 1: 近期涟漪 (≤7天)
  └→ 种子采样 → L1共振桥梁 → L2下探

Phase 2: 中期涟漪 (7~90天)
  └→ 独立联想流程

Phase 3: 深渊浪潮 (>90天)
  └→ 所有向量融合 → 深远记忆召回
```

### 3. 三类梦操作

```javascript
// DiaryMerge - 合并日记
command: "DiaryMerge",
sourceDiaries: ["file:///a.txt", "file:///b.txt"],
newContent: "合并后内容\nTag: 标签1, 标签2"

// DiaryDelete - 删除日记
command: "DiaryDelete",
targetDiary: "file:///c.txt",
reason: "内容与 a.txt 重复"

// DreamInsight - 梦感悟
command: "DreamInsight",
referenceDiaries: ["file:///a.txt"],
insightContent: "梦感悟正文\nTag: 梦感悟"
```

### 4. 审批机制

```
AI 生成操作
    ↓
记录到 dream_logs/*.json
(status: "pending_review")
    ↓
管理员在面板查看
├── 梦叙事
├── 操作详情
└── 源日记对比
    ↓
┌─────────────────┐
│ ✅ 批准          │ → 执行实际文件操作
├─────────────────┤
│ ❌ 拒绝          │ → 仅标记状态
└─────────────────┘
```

### 5. 梦日志结构
```json
{
  "dreamId": "dream-2026-02-18-Nova-a1b2c3d4",
  "agentName": "Nova",
  "timestamp": "2026-02-18T02:15:00Z",
  "dreamNarrative": "我在梦中看到...",
  "dreamTree": {
    "recent": { "seeds": [], "resonanceL1": [], "cascadeL2": [] },
    "mid": { "seeds": [], "cascadeL1": [] },
    "deep": { "recalls": [] }
  },
  "operations": [{
    "operationId": "op-1",
    "type": "merge",
    "sourceDiaries": ["..."],
    "sourceContents": { "...": "原文内容" },
    "newContent": "...",
    "status": "pending_review"
  }]
}
```

## 安全边界设计

### 三层防护

1. **AI 写，AI 读不了**: 梦操作仅记录 JSON，AI 无法直接修改文件
2. **异步批准**: 所有操作先入队，管理员审批后再执行
3. **自动读取源文件**: 系统补充源日记内容，供审批时对比

### 防并发梦
```javascript
let isDreamingInProgress = false

async function triggerDream(agentName) {
  if (isDreamingInProgress) return { status: 'busy' }
  isDreamingInProgress = true
  try { ... } finally { isDreamingInProgress = false }
}
```

### 梦状态持久化
```javascript
// 跨重启恢复
DREAM_STATE_FILE = 'dream_schedule_state.json'
lastDreamTimestamps = Map<agentName, timestamp>
```

## 设计启示

1. **信任量化**: 采用「生成→审批→执行」三阶段流程
2. **隔离空间**: 梦境独立于日常对话，保护清醒状态的稳定性
3. **格式一致**: 所有操作都通过 DailyNoteWrite，保持系统一致性
4. **递归记忆**: 梦本身成为可检索的持久记忆，支持「梦的梦」

## 应用场景

- **日记整理**: 自动识别重复、合并冗余
- **记忆感悟**: 发现跨时间维度的隐藏联系
- **人机协作**: AI 提议，人类决策
- **知识演进**: 梦记录成为新的知识源
