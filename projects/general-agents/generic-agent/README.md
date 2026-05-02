# GenericAgent 参考实现


> **Evidence Status** — grounded. 本目录下的 snippet 分析与 README。

## 基本信息

- **类型**：general-agent
- **项目定位**：极简自进化 agent 框架，强调少工具、强记忆、技能固化。
- **学习来源**：仓库 README 与专题 snippet。
- **推荐入口**：README → agent-loop.snippet.md / memory-layers.snippet.md / self-evolution.snippet.md。

## 模块覆盖

| 模块 | 覆盖程度 | 证据文件 | 可复用模式 |
|---|---|---|---|
| learning | 深 | self-evolution.snippet.md | skill-crystallization |
| memory | 深 | memory-layers.snippet.md | layered-memory |
| tools | 中 | tool-system.snippet.md | atomic tools |
| interface | 中 | frontend-adapter.snippet.md | frontend adapter |
| orchestration | 浅 | agent-loop.snippet.md | minimal loop |

## 独特贡献

GenericAgent 用 9 个原子工具 + ~100 行 agent loop 证明了一个反直觉的命题：**agent 的能力上限不取决于预置了多少工具，而取决于它能否从执行中学习**。成功路径自动固化为 Skill，能力随使用有机生长——这是”最小 viable agent”的极致表达。

## 关键发现

- 能力边界可以动态生长：`code_run` 一个工具就能覆盖无限多的操作空间，关键在于学会后固化为 Skill。
- “No Execution, No Memory”——记忆层只写入经过行动验证的信息，禁止存储推理过程和假设，直接避免了记忆污染。
- 极简 runtime（~3K 行代码）也能展示完整 Agent 闭环，说明复杂性应在运行时生长而非编译时堆砌。

**仓库**：https://github.com/lsdefine/GenericAgent

## 核心公式

```
GenericAgent = 9 原子工具 + ~100 行 Agent Loop + 5 层记忆系统 + 自我进化
```

## 架构亮点

| 维度 | 设计 | 独特价值 |
|-----|------|---------|
| **极简工具集** | 9 个原子工具 | 能力通过 code_run 动态扩展，不预设 |
| **分层记忆** | L0-L4 五层 | 行动验证原则，只存成功执行的信息 |
| **自我进化** | Skill 自动固化 | 执行路径 → 可复用 SOP/脚本 |
| **多前端** | 7+ 渠道适配 | 统一队列协议，渠道解耦 |

## 文件索引

| 文件 | 主题 |
|-----|------|
| [agent-loop.snippet.md](agent-loop.snippet.md) | 核心循环 (~100行) |
| [memory-layers.snippet.md](memory-layers.snippet.md) | L0-L4 五层记忆系统 |
| [tool-system.snippet.md](tool-system.snippet.md) | 9 原子工具 + 动态扩展 |
| [self-evolution.snippet.md](self-evolution.snippet.md) | Skill 固化机制 |
| [frontend-adapter.snippet.md](frontend-adapter.snippet.md) | 多前端统一架构 |
| [llm-adapter.snippet.md](llm-adapter.snippet.md) | 多模型适配层 |

## 关键洞察

### 1. 能力边界：不预设，靠进化

GenericAgent 不像传统框架预置大量工具，而是：
- 启动时仅 9 个原子工具
- 通过 `code_run` 动态安装依赖、编写脚本
- 成功执行的路径自动固化为 Skill

这实现了**能力的有机生长**，而非**能力的预设堆叠**。

### 2. 记忆哲学：No Execution, No Memory

记忆层只写入**经过行动验证**的信息：
- 禁止存储推理过程、假设、通用常识
- 禁止存储易变状态（时间戳、PID、Session ID）
- 只存环境特异性事实和经验验证的 SOP

### 3. 工具发现：约定优于配置

```python
# 工具名 → 方法名
tool_name = "code_run"
method = getattr(handler, f"do_{tool_name}")  # do_code_run()
```

无需注册表，通过命名约定自动发现。

### 4. 协变出口：next_prompt 控制流

```python
StepOutcome(data, next_prompt, should_exit)
# next_prompt=None → 任务完成，退出循环
# should_exit=True → 强制退出（如 ask_user）
```

工具返回值决定循环走向，而非外部状态机。

### 5. 上下文压缩：梯级策略

**基于轮数触发**：

| 轮次 | 动作 |
|-----|------|
| 每 10 轮 | 重新注入全局记忆 |
| 第 7 轮 | 提示策略转变（引导 agent 调整方向） |
| 第 35 轮 | 强制 ask_user（要求人工介入） |
| 第 40 轮 | 循环退出 |

**基于上下文大小触发**：

| 条件 | 动作 |
|-----|------|
| 超过 context_win×3 | 压缩旧消息标签，释放上下文空间 |
