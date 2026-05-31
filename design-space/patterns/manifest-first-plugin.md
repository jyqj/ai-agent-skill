# Manifest-First Plugin Discovery

> **Evidence Status** — grounded. OpenClaw 125 extensions manifest-driven 实现。

## 模式定义

插件通过声明式 manifest 文件（如 `plugin.json`）声明 capability，runtime 在启动时扫描 manifest 决定加载策略，避免 import-time side effects。

## 核心流程

```
Manifest Scan → Capability Matching → Conditional Load → Runtime Registration
```

## 与 Code-Registration 的对比

| 维度 | Code Registration | Manifest-First |
|------|-------------------|---------------|
| 发现时机 | import-time | 启动时扫描 |
| 副作用 | 可能有 | 无（声明式） |
| 边界强制 | 靠约定 | SDK subpath + facade |
| 条件加载 | 运行时判断 | manifest 声明 requires |
| 规模 | <50 工具 | 100+ extensions |

## Plugin SDK Boundaries

清晰的 public/internal 分离：
- 插件只能 import `<system>/plugin-sdk/*` subpath
- 本地 `api.ts` / `runtime-api.ts` facade 暴露受限 API
- 禁止访问 core src/ 或其他 extension src/

## 实现参考

| 项目 | manifest | 规模 |
|------|----------|------|
| OpenClaw | openclaw.plugin.json | 125 extensions |
| VSCode | package.json contributes | 1000+ extensions |
| Chrome | manifest.json | 100K+ extensions |

## 适用条件

- 插件数量预期 >30
- 需要 capability-based 条件加载
- 需要强制 SDK 边界防止 core 耦合
