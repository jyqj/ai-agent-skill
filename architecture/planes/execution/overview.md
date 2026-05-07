# Execution Engine
>
> **所属域**：4. Action & Effect — 实际执行宿主
>
> **Evidence Status** — grounded. Codex、Claude Code、Hermes、Augment 等系统对 sandbox、timeout、host abstraction 的实现；this repository 对”执行成功 != 效果成功”的统一抽象。

**Principle Refs**: IS-02, EM-01 — 执行返回 ≠ 世界状态确认，工具是认知延伸需隔离管理。

Agent 的价值最终通过执行实现——但执行环境的隔离、超时和失败处理决定了系统是否安全可靠。10 步操作中每步 99% 成功率，整体只有 90%。

## 定义

Execution Engine 管理工具实际运行的沙箱环境：Shell 命令、代码执行、文件操作、远程调用、浏览器动作、设备控制。

Execution 层负责的是**把动作送进宿主环境**，不是替任务宣布完成。

## 模块接口

**输入**：Tool Runtime 的执行请求（host + command + args）
**输出**：原始执行结果（由 Observation Normalizer 标准化）
**配置**：沙箱策略、超时、资源限制、网络策略、回放/重试策略

## 沙箱设计

| 维度 | 配置项 |
|---|---|
| 文件系统 | workspace 边界、只读区域、临时目录 |
| 网络 | 域名白名单、出口代理、完全隔离 |
| 资源 | CPU / 内存限制、磁盘配额 |
| 时间 | 单次命令超时、总任务超时 |
| 权限 | 禁止 sudo、限制系统调用、最小凭证 |
| 外设 | 浏览器 / 机器人 / GUI 的最小控制集 |

## 可靠性

单步 99% 成功率，10 步后只有 90.4%。Execution Engine 的设计必须假设失败是常态：

- 每次执行都有 timeout；
- 失败返回 failure_mode + recoverable + suggested_recovery；
- 幂等操作可以 retry；
- 非幂等操作要有 rollback / compensation；
- 写动作默认需要后续 verification。

## 关键区分

| 结果 | 含义 |
|---|---|
| execution_success | 宿主执行完成，例如进程退出码为 0 |
| tool_success | 工具返回符合约定的 observation |
| effect_success | 外部世界达到 postcondition |

前三者不一定同时成立。

## 设计模式

| 模式 | 详见 |
|---|---|
| Execution Environment | `execution-env.md` |
| Effect Ledger | `../../../design-space/patterns/effect-ledger.md` |

## 参考实现

- **Claude Code**：进程隔离、超时控制，见 `projects/coding-agents/claude-code/execution-layer.md`
- **Codex**：完全沙箱化的执行环境，见 `projects/coding-agents/codex/`
- **Hermes Agent**：多 backend 执行环境，见 `projects/general-agents/hermes-agent/execution-env.md`
- **Augment**：Sidecar 进程隔离，见 `projects/coding-agents/augment/README.md`
