# OpenClaw Plugin System

> **Evidence Status** — grounded. OpenClaw src/plugin-sdk/ + extensions/ 源码分析。

## Manifest-First Discovery

每个 extension 通过 `openclaw.plugin.json` 声明：
- Plugin ID 和版本
- Capability domains（provider / channel / memory / media / tools）
- Setup hints 和 onboarding flow
- Auth defaults 和 dependency declarations

## Plugin SDK Boundaries

| 允许 | 禁止 |
|------|------|
| `openclaw/plugin-sdk/*` subpath | `src/**` core internals |
| 本地 `api.ts` facade | `src/plugin-sdk-internal/**` |
| 本地 `runtime-api.ts` | 其他 extension `src/**` |

## Capability Provider Pattern

- Provider plugin：声明 auth methods + model catalog
- Channel plugin：声明 transport + allowlist policy
- Memory plugin：声明 search/store interface
- Tool plugin：声明 tool schema + handler via PluginToolFactory

## Plugin 加载

```
Startup → Scan manifest files → Match capabilities → Conditional load → Runtime registry
```

470+ plugin-sdk 文件，462 plugin loader 文件。
