# <Category Name> Architecture

> **Evidence Status** — <level>. <projects, evals, observed systems>


## 1. Core Job

<这个 Agent 被用户雇来完成什么工作？交付物是什么？>

## 2. 用户模型

| 用户 | 心智模型 | 信任建立方式 | 默认交互 |
|---|---|---|---|
| | | | |

## 3. 任务模型

| 任务类型 | 默认深度 | 默认自治 | 成功定义 | 失败模式 |
|---|---|---|---|---|
| | | | | |

## 4. 表示模型

| 表示对象 | 含义 | Freshness | Trust | Raw Ref |
|---|---|---|---|---|
| | | | | |

## 5. 行动模型

| 动作 | 工具/接口 | 风险 | Preconditions | Postconditions | Verification |
|---|---|---|---|---|---|
| | | | | | |

## 6. 闭环模型

```text
Observe → Represent → Decide → Act → Verify → Update
```

### Happy Path

<步骤>

### Failure + Recovery

<失败分类与恢复>

### Stop Gate

```text
[ ] <完成条件>
```

## 7. 品类特有设计决策

| 决策 | 默认 | 升级触发器 |
|---|---|---|
| 沙箱/执行环境 | | |
| 并发策略 | | |
| 上下文策略 | | |
| 记忆策略 | | |
| 控制策略 | | |
| 运维策略 | | |

## 8. 模块配置

| 模块 | 品类特化配置 | 通用参考 |
|---|---|---|
| Representation | | `../../architecture/planes/representation/overview.md` |
| Context | | `../../architecture/planes/context/overview.md` |
| Tools | | `../../architecture/planes/tools/overview.md` |
| Effects | | `../../architecture/planes/effects/overview.md` |

## 9. Eval Cases

| Case | 目标 | 必备断言 |
|---|---|---|
| | | |

## 10. Reference Implementations

| 项目 | 学习点 | 入口 |
|---|---|---|
| | | |
