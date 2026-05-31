# Registry-Driven Configurator

> **Evidence Status** — grounded. Trellis AI_TOOLS registry 源码分析。

## 设计

`AI_TOOLS: Record<AITool, AIToolConfig>` 是 14 个平台的单一真值源。

## AIToolConfig 结构

| 字段 | 说明 |
|------|------|
| name | 平台显示名 |
| configDir | 配置目录（.claude / .codex / ...） |
| cliFlag | CLI 参数标识 |
| hasPythonHooks | 是否需要 Python hook |
| templateContext.agentCapable | 是否支持 sub-agent |
| templateContext.hasHooks | 是否支持 Hook |
| templateContext.cmdRefPrefix | 命令前缀（/trellis: / $ / ...） |

## 派生链

AI_TOOLS → configurator.configure() → writeSkills() + writeAgents() + writeHooks() + writeSettings()

## Template Placeholder Neutralization

多平台共享的 skill 文件用中立占位符替换平台特定前缀：
- `{{CMD_REF:start}}` → `"start (Trellis command)"`
- 确保 Codex 和 Gemini 生成同一份文件，避免 git 冲突

## 14 平台能力矩阵

| 平台 | Hook | Agent | Skill | Workflow |
|------|------|-------|-------|---------|
| Claude Code | Yes | Yes | Slash cmd | - |
| Cursor | Yes | Yes | Slash cmd | - |
| Codex | No | Yes | $ prefix | - |
| Kilo | No | No | - | Yes |
| OpenCode | Plugin | No | Plugin | - |

## 对知识库的贡献

- 补充了 `patterns/tool-registry.md`：registry 不注册工具，注册平台能力
- 新模式 `patterns/platform-adapter-registry.md`
