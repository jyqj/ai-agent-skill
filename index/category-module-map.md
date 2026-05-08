# Product to Module Map

> **Evidence Status** — synthesized. 跨项目观察归纳。

| 产品 | 必备模块 | 可选模块 | 默认深度 | 重点风险 | 品类入口 |
|---|---|---|---|---|---|
| Coding Agent | Representation, Context, Tools, Execution, Control, State, World State, Effects, Observability, Depth Controller | Memory, Orchestration, Learning, Operations (Warp 证明 Operations 对 agent-driven 项目很关键) | D5 | 误改代码、危险命令、未验证效果 | `../categories/coding-agent/README.md` |
| Research Agent | Representation, Context, Tools, Control, Observability, Cost, Interaction | Memory, Orchestration, State, Operations | D4-D5 | citation drift、来源不可信、freshness blindness、冲突被抹平 | `../categories/research-agent/README.md` |
| Personal Memory Agent | Representation, Memory, Context, Control, Observability, State | Tools, World State, Learning | D3-D4 | 记忆污染、隐私、错误用户建模 | `../categories/personal-memory-agent.md` |
| Enterprise Workflow Agent | Interface, Representation, Tools, Control, State, World State, Effects, Observability, Depth Controller | Orchestration, Memory, Operations | D4-D5 | 越权、错误执行、审计缺失、状态过期 | `../categories/enterprise-workflow-agent.md` |
| Browser/Desktop Agent | Interface, Representation, Tools, Control, World State, Effects, Observability | Memory, Orchestration, Operations | D5 | DOM/截图不一致、坐标漂移、点击成功但任务失败 | `../categories/browser-desktop-agent.md` |
| Ops/SRE Agent | Interface, Representation, Tools, Control, State, World State, Effects, Observability, Operations | Orchestration, Memory | D5-D6 | 误报、误操作、回滚失败 | `../categories/ops-sre-agent.md` |
| Security Agent | Representation, Tools, Control, Observability, Operations | Memory, Orchestration | D4-D5 | 漏洞误判、越权扫描、secret 泄露 | `../categories/security-agent.md` |
| Companion Agent | Representation, Context, Memory, Interface, Control | Tools, State, Orchestration | D2-D4 | 角色漂移、越界建议、记忆泄露 | `../categories/companion-agent.md` |
| Agent Platform | 全部模块 | Marketplace, Distributed Execution | D5-D6 | 插件安全、权限、稳定性、回归 | `../categories/agent-platform.md` |
| Creative Agent | Representation, Context, Memory, Interface, Control, Interaction | Tools, Orchestration, Learning | D2-D4 | 风格漂移、版权侵权、创意枯竭、审美偏差、多模态不一致 | `../categories/creative-agent/README.md` |
| Data/BI Agent | Representation, Context, Tools, Control, World State, Observability, Cost | Memory, Orchestration, Operations | D4-D5 | SQL 注入、数据泄露、统计误导、语义歧义、查询失控 | `../categories/data-bi-agent/README.md` |
| Embodied Robot Agent | Representation, Tools, Control, State, World State, Effects, Observability, Depth Controller | Memory, Orchestration, Learning, Operations | D5-D6 | 物理伤害、传感器失效、Sim-to-Real 漂移、紧急停止失败、环境误判 | `../categories/embodied-robot-agent/README.md` |
| Financial Agent | Representation, Tools, Control, State, World State, Effects, Observability, Cost, Recovery, Depth Controller | Memory, Orchestration, Operations | D5-D6 | 未授权交易、滑点失控、合规违规、闪崩、肥手指 | `../categories/financial-agent/README.md` |
| Education Agent | Representation, Context, Memory, Interface, Control, Interaction | Tools, State, Orchestration, Learning | D2-D4 | 教授错误内容、难度不匹配、失去学习动力、评估偏差、隐私泄露 | `../categories/education-agent/README.md` |

## 品类 × Plane 配置矩阵

> 从"必备/可选模块"到"25 个 plane 各自要不要启用"的具体映射。开发者看了能回答：**我的品类至少要启用哪些 plane？**
>
> `●` = 必选（品类核心依赖，缺失即无法交付），`○` = 推荐（显著提升质量或安全），`-` = 可选或不适用
>
> 矩阵依据：各品类 README 中的必备/可选模块、`architecture/complexity-levels.md` 中的 C0-C6 必备 plane、`plane-interaction-matrix.md` 中的强耦合链路。

### Intake & Representation

| Plane | Coding | Research | Browser/Desktop | Security | Companion | Data/BI | Ops/SRE | Enterprise Workflow | Creative | Education | Financial | Embodied Robot | Personal Memory | Agent Platform |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Interface | ○ | ○ | ● | ○ | ● | ○ | ● | ● | ● | ● | ○ | ● | ○ | ● |
| Representation | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● |

### Cognition & Continuity

| Plane | Coding | Research | Browser/Desktop | Security | Companion | Data/BI | Ops/SRE | Enterprise Workflow | Creative | Education | Financial | Embodied Robot | Personal Memory | Agent Platform |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Prompting | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● |
| Context | ● | ● | ● | ○ | ● | ● | ○ | ○ | ● | ● | ○ | ○ | ● | ● |
| Memory | ○ | ○ | ○ | ○ | ● | ○ | ○ | ○ | ● | ● | ○ | ○ | ● | ○ |
| State | ● | ○ | ● | ○ | ○ | ○ | ● | ● | ○ | ○ | ● | ● | ● | ● |
| World State | ● | ○ | ● | ○ | - | ● | ● | ● | - | - | ● | ● | - | ○ |

### Action & Effect

| Plane | Coding | Research | Browser/Desktop | Security | Companion | Data/BI | Ops/SRE | Enterprise Workflow | Creative | Education | Financial | Embodied Robot | Personal Memory | Agent Platform |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Tools | ● | ● | ● | ● | ○ | ● | ● | ● | ● | ○ | ● | ● | ○ | ● |
| Execution | ● | ○ | ● | ○ | - | ● | ● | ● | ● | ○ | ● | ● | - | ● |
| Effects | ● | - | ● | ○ | - | ○ | ● | ● | ○ | - | ● | ● | - | ● |

### Interaction & Collaboration

| Plane | Coding | Research | Browser/Desktop | Security | Companion | Data/BI | Ops/SRE | Enterprise Workflow | Creative | Education | Financial | Embodied Robot | Personal Memory | Agent Platform |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Interaction | ○ | ○ | ● | ● | ● | ○ | ● | ● | ● | ● | ○ | ○ | ○ | ● |
| Orchestration | ○ | ○ | ○ | ○ | - | ○ | ○ | ○ | ○ | ○ | ○ | ○ | - | ● |
| Concurrency | - | ○ | ○ | ○ | - | ○ | ○ | ○ | ○ | - | ● | ○ | - | ● |
| Dataflow | - | ○ | - | ○ | - | ○ | ○ | ○ | - | - | ● | ○ | - | ● |

### Governance & Evolution

| Plane | Coding | Research | Browser/Desktop | Security | Companion | Data/BI | Ops/SRE | Enterprise Workflow | Creative | Education | Financial | Embodied Robot | Personal Memory | Agent Platform |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Control | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● |
| Security | ○ | ○ | ● | ● | ○ | ● | ● | ● | ○ | ○ | ● | ○ | ● | ● |
| Identity-Capability | - | - | ○ | ● | ○ | ○ | ○ | ● | - | ○ | ● | - | ○ | ● |
| Recovery | ○ | ○ | ● | ○ | - | ○ | ● | ● | ○ | - | ● | ● | ○ | ● |
| Cost | ○ | ● | ○ | ○ | - | ● | ● | ○ | ○ | - | ● | ○ | - | ● |
| Observability | ● | ● | ● | ● | ○ | ● | ● | ● | ○ | ○ | ● | ● | ● | ● |
| Operations | ○ | ○ | ○ | ○ | - | ○ | ● | ● | - | - | ● | ● | - | ● |
| Learning-Adaptation | ○ | ○ | - | - | ○ | - | ○ | - | ● | ● | ○ | ○ | ○ | ○ |
| Economics | - | - | - | - | - | - | ○ | ○ | - | - | ● | - | - | ● |
| Explainability | ○ | ● | ○ | ● | ○ | ● | ● | ● | ○ | ● | ● | ● | ○ | ○ |
| Time | ○ | ● | ○ | ○ | - | ● | ● | ● | - | ○ | ● | ● | ● | ○ |

### 如何使用矩阵

1. **找到品类列**，筛选 `●` 行——这是启动开发的最小 plane 集合。
2. **看 `○` 行**，在 MVP 之后按优先级逐步启用。
3. **`-` 不代表绝对禁止**——如果你的具体场景需要，可以升级为 `○`。
4. **矩阵与 `complexity-levels.md` 交叉使用**：如果你的品类在某个 C 等级，也要检查该等级的必备 plane 是否已覆盖。
5. **矩阵与 `plane-interaction-matrix.md` 交叉使用**：启用一个 plane 时，检查它的强耦合链路中的其他 plane 是否也已启用。

### 品类 × 深度（D0-D6）典型区间

| 品类 | 典型深度 | 说明 |
|---|---|---|
| Coding Agent | D4-D5 | 必须验证（测试通过）；长任务需 checkpoint |
| Research Agent | D3-D5 | 检索和 citation 至少 D3；深度综述 D5 |
| Browser/Desktop Agent | D3-D5 | 信息提取 D3；表单提交 D4；批量操作 D5 |
| Security Agent | D4-D5 | 证据链和缓解验证是核心 |
| Companion Agent | D2-D4 | 无外部写动作；主要是对话+记忆 |
| Data/BI Agent | D3-D5 | 事实查询 D3；交叉分析/报表 D4-D5 |
| Ops/SRE Agent | D5-D6 | 持续运营和生产操作要求高深度 |
| Enterprise Workflow | D4-D5 | 跨系统写动作+审计+审批 |
| Creative Agent | D2-D5 | 单次生成 D2；多模态工作流 D4-D5 |
| Education Agent | D2-D4 | 教学对话 D2；自适应学习路径 D4 |
| Financial Agent | D5-D6 | 交易执行和风险监控要求最高深度 |
| Embodied Robot Agent | D5-D6 | 物理动作不可逆；安全绝对优先 |
| Personal Memory Agent | D3-D4 | 记忆写入需验证；检索需准确 |
| Agent Platform | D5-D6 | 多租户+持续运营+回归 |

## 使用方式

1. 先用 `../design-space/methodology/agent-product-model.md` 定义产品画布。
2. 再用本表确定默认模块组合。
3. 用上方品类 × Plane 矩阵确定具体 plane 的必选/推荐/可选。
4. 再进入品类入口补齐任务模型、表示模型、行动模型、闭环模型。
5. 最后用 `category-pattern-matrix.md` 选择横切模式。
