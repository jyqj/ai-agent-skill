# OpenClaw Skill Registry

> **Evidence Status** — grounded. OpenClaw skills/ + VISION.md 分析。

## 三层 Skill

| 层 | 来源 | 数量 | 管理 |
|----|------|------|------|
| Bundled | OpenClaw core | 55 | 代码内置 |
| ClawHub | 社区发布 | 开放 | Registry 发现 |
| Workspace | 用户自定义 | 任意 | 本地目录 |

## Skill 加载

```
Manifest Discovery → Filter by agent allowlist → Load prompt templates → Register tools → Inject context
```

## ClawHub

- 官方 plugin/skill 发布平台
- Provenance tracking
- Security review（可选）
- 新 skill 优先发布到 ClawHub，不直接进 core

## 设计原则

- 核心保持精简
- 可选能力通过 plugin/skill 提供
- Bundle-style plugin（稳定外部 surface）优先于 code plugin
