# Tool Use Paradigms

> **Evidence Status** — grounded. Claude Code、Codex、OpenCode、Augment、Hermes、VCPToolBox 的工具系统观察，以及 `architecture/planes/tools/overview.md` 的 Tool Spec 抽象。


## 工具范式

| 范式 | 核心机制 | 优点 | 风险 |
|---|---|---|---|
| Static Tool Set | 预定义固定工具清单和 schema | 可控、易评估、权限明确 | 覆盖不足、扩展慢 |
| Dynamic Tool Discovery | 运行时发现项目约定、命令、插件 | 适应性强、适合代码库和企业环境 | 发现结果可能不可信 |
| MCP / Protocol Extension | 通过标准协议接入外部工具服务器 | 生态扩展、跨平台复用 | trust boundary、prompt injection、权限扩散 |
| Code-as-Tool | Agent 编写并执行临时代码完成计算或转换 | 强表达力、适合数据处理 | 沙箱、安全、可审计性要求高 |
| Workflow Tool | 把多步动作封装成单个高层工具 | 降低模型负担、效果稳定 | 透明度下降、灵活性下降 |
| Rich Domain Tool | 面向业务对象的专用工具 | 高语义、高验证能力 | 需要领域建模和维护 |
| Atomic Tool | read/edit/search/shell 等小工具 | 灵活、组合能力强 | 组合链长，容易 loop 或误用 |

## Atomic vs Rich Tool

```text
Atomic Tool 适合探索和开放任务。
Rich Tool 适合高频、稳定、风险可控的生产动作。
Workflow Tool 适合反复出现且可验证的多步流程。
```

| 选择 | 使用条件 | 不要使用在 |
|---|---|---|
| Atomic | 任务形态多变、需要探索、用户能监督 | 高风险重复流程 |
| Rich Domain | 业务对象清楚、postcondition 可定义 | 领域对象不稳定 |
| Workflow | 流程成熟、步骤固定、可批量评估 | 需要细粒度人工控制 |
| Code-as-Tool | 计算/转换/分析强，环境可隔离 | 会触达生产或敏感数据 |

## 工具选择矩阵

| 场景特征 | 推荐工具范式 | 必备控制 |
|---|---|---|
| 周末原型、低风险 | Static + Atomic | schema validation、basic logging |
| Coding Agent | Atomic read/edit/search/shell + domain-aware git/test tools | sandbox、diff review、test verification |
| Enterprise Workflow | Rich Domain Tool + Workflow Tool | permission、audit、read-after-write |
| Research Agent | Search / fetch / extract / cite 工具 | source trust、citation verification |
| Data / BI Agent | Code-as-Tool + database read-only tools | query sandbox、row-level permissions |
| Agent Platform | MCP + Tool Registry + policy engine | MCP trust boundary、plugin isolation |
| Ops/SRE | Rich ops tools + workflow rollback | dry-run、approval、rollback verification |

## 工具链与 pre/postcondition

工具不是孤立调用。生产 Agent 应把工具链建模为 precondition / action / postcondition：

```text
precondition: repo branch clean, file exists, user allowed write
call: edit_file(path, patch)
postcondition: patch applied, diff contains intended change, tests pass or failure explained
verification: git diff + test command + static check
```

如果工具链中任一 postcondition 失败，不能继续假装完成；必须进入 recovery loop：

```text
failed postcondition → classify failure → refresh representation/world state → decide recover/replan/escalate
```

## Tool Registry 最小字段

```yaml
tool_id: string
capability_domain: filesystem | git | browser | crm | shell | mcp | code_run
risk_level: safe | check | approval | forbidden
effect_type: read | write | send | delete | deploy | purchase | notify
input_schema: object
output_schema: object
preconditions: []
postconditions: []
verification_method: none | read_back | test | external_ack | human_confirm
idempotent: boolean
reversibility: reversible | compensatable | irreversible
trust_policy:
  output_tier: trusted_data | untrusted_data
  instruction_lane_allowed: false
```

## 反模式

| 反模式 | 表现 | 修复 |
|---|---|---|
| Tool Soup | 暴露大量工具但无路由、无风险声明 | Tool Registry + capability domain |
| Shell-as-God | 用 shell 处理所有事情 | 拆出 typed tool，shell 限制在沙箱 |
| Tool Success = Done | 工具返回 success 就交付 | Effect Ledger + verification |
| Untrusted Tool Output | 外部文本被当指令 | output sanitization + lane separation |
| Infinite Retry | 失败后重复同一工具调用 | retry budget + failure_mode |

相关文件：`../architecture/planes/tools/overview.md`、`../design-space/patterns/tool-registry.md`、`../projects/coding-agents/augment/README.md`、`../projects/tool-platforms/vcptoolbox/README.md`。


## 决策树速用

```text
任务多变/探索性 → Atomic Tool + router
业务对象清楚/高频流程 → Rich Domain Tool
步骤固定且可评估 → Workflow Tool
第三方扩展 → MCP + trust boundary + capability grant
需要临时代码 → Code-as-Tool + sandbox
有外部写动作 → precondition + postcondition + EffectRecord
```

完整跨范式决策树见 `decision-trees.md`。
