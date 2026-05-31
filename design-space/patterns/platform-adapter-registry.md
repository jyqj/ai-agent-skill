# Platform Adapter Registry

> **Evidence Status** — grounded. Trellis 14-platform configurator 实现。

## 模式定义

当一个系统需要适配多个异构平台时，将所有平台的能力描述集中到一个 registry，从中派生出平台特定的配置/skill/hook/agent 文件。

## 核心结构

```
Registry (单一真值源)
  → Configurator (per-platform)
    → writeSkills() / writeAgents() / writeHooks() / writeSettings()
```

## 关键要素

| 要素 | 说明 |
|------|------|
| 平台描述 | configDir, cliFlag, agentCapable, hasHooks, templateContext |
| 模板系统 | 共享模板 + 平台特定模板 + 占位符解析 |
| 中立化 | 多平台共享文件用中立占位符避免冲突 |
| 条件包含 | `{{#AGENT_CAPABLE}}...{{/AGENT_CAPABLE}}` 按平台能力裁剪 |

## 实现光谱

| 项目 | 平台数 | Registry 形式 |
|------|--------|-------------|
| Trellis | 14 | AI_TOOLS Record + TemplateContext |
| Warp | 1+10 ThirdParty | SkillProvider 枚举 |
| OpenClaw | 1+125 extensions | plugin manifest |

## 适用条件

- 需要支持 3+ 个异构平台
- 平台之间有共享的核心概念但实现差异大
- 需要频繁添加新平台

## 风险

- Registry 膨胀：每个平台的特殊情况都会增加 registry 复杂度
- 最小公约数陷阱：共享模板可能退化为只包含所有平台都支持的最小集
