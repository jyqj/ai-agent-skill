# Tool Boundary Comparison

> **Evidence Status** — grounded. Claude Code、Codex、OpenCode、Augment、Hermes、VCPToolBox 项目分析。


## 对比维度

| 系统 | 工具注册 | 宿主分层 | 审批 / 风险 | 备注 |
|---|---|---|---|---|
| Claude Code | 集中工具体系 | 本地 + MCP | hooks + permission tree | 强调上下文 / 执行联动 |
| Codex | orchestrator + sandbox | 多平台沙箱 | guardian + approval | 安全与宿主隔离强 |
| OpenCode | schema + permissions | runtime abstraction | deny > ask > allow | framework 感强 |
| Augment | 4 层 host | remote/local/sidecar/mcp | hook lifecycle | 分层最清晰 |
| Hermes | registry + toolset | 多 backend | 三层审批 | gateway 能力强 |
| VCPToolBox | plugin manifest | 多运行时 + 分布式 | 依赖插件边界 | 平台化明显 |
| Warp | skill 作为元工具 | 终端原生 + 外部 agent | readiness-label + Oz review | 工具 = skill 指令 |

## 综合判断

- Augment 最强调宿主分层。
- Codex 最强调执行安全和审批升级。
- Claude Code / OpenCode 最强调 runtime 内部协同。
- Hermes / VCP 更适合看 gateway、toolset、插件平台视角。
- Warp 独特之处在于把 skill 作为元工具（不是 API 调用，而是可组合的指令文档），用 readiness label 做准入控制（不是运行时审批，而是任务级准入）。
