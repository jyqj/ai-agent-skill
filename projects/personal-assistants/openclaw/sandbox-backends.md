# OpenClaw Sandbox Backends

> **Evidence Status** — grounded. OpenClaw src/agents/sandbox/ + AGENTS.md。

## 四种后端

| 后端 | 隔离级别 | 适用场景 |
|------|---------|---------|
| Local | 无隔离 | 主 session（信任用户） |
| Docker | 容器级 | 非 main session 默认 |
| SSH | 远程 | node-host 场景 |
| OpenShell | 终端级 | macOS/Linux |

## 配置

```
agents.defaults.sandbox.mode: "non-main"
```

默认允许：bash, process, read, write, edit, sessions_list/history/send/spawn
默认拒绝：browser, canvas, nodes, cron, discord, gateway

## Security Audit

- Channel account metadata audit
- Exec surface audit（dangerous bins detection）
- Workspace skill escape detection
- Plugin trust model
