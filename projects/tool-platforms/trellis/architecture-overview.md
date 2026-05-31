# Trellis Architecture Overview

> **Evidence Status** — grounded.

## 三层架构

```
Layer 1: Registry (AI_TOOLS 单一真值源)
  ↓
Layer 2: Configurator (14 平台适配器，生成 skills/agents/hooks/settings)
  ↓
Layer 3: Execution (Task Lifecycle × Workflow State Machine)
```

## 核心公式

```
Trellis = Registry-Driven Config + Breadcrumb State Machine + Spec Curation Gate + Journal Persistence
```

## 执行模型

```
Phase 1 Plan → Phase 2 Execute → Phase 3 Finish
     │              │                │
  brainstorm    implement/check   update-spec
  + research    (sub-agent or     + commit
  + JSONL        inline)          + journal
   curation
```

## 量化特征

| 指标 | 数值 |
|------|------|
| 平台 | 14 |
| Phase | 3 |
| Steps | 13 |
| Workflow States | 6 |
| Shared Skills | 5 |
| Sub-agent Types | 4 |
| Task.py 子命令 | 16+ |
| TS LOC | ~12.7K |
| Python Scripts | 27 |
| Migration Manifests | 8+ |
