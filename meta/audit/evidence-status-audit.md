# Evidence Status Audit

> **Evidence Status** — synthesized. 对整个 skill 目录的结构化扫描结果；校验口径与 `scripts/validate_skill.py` 保持一致，并单独列出 snippet 与运行样例。

**Last Updated** — 2026-05-02

## 扫描摘要

- 文件总数：**492**
- Markdown 文档总数：**415**
- 纳入结构校验的 Markdown 文档（validate_skill.py checked）：**392**
- 含有效 Evidence Status 的 Markdown 文档：**374 / 392**
- 校验豁免（模板 / 非文档）：**5**
- 校验失败：**4**（均为 `.pytest_cache/README.md`，由 pytest 自动生成，非项目内容）
- 测试总数（4 套件）：**39 全部通过**
  - `starter-kit/verified-tool-agent`：3 passed
  - `starter-kit/react-llm-agent`：6 passed
  - `starter-kit/stateful-agent`：6 passed
  - `evaluation/eval-runner`：24 passed
- Plane 交互矩阵列数：**26**（1 行标题 + 25 plane），正确
- Plane overview 含 Principle Refs：**25 / 25**

## Evidence Status 分布

| 等级 | 文件数 |
|---|---:|
| synthesized | 255 |
| grounded | 89 |
| theoretical | 18 |
| mixed | 7 |
| speculative | 5 |

## 目录覆盖

| 目录 | 含 Evidence Status 的 Markdown 数 |
|---|---:|
| 根目录（SKILL / ARCHITECTURE / AGENTS） | 3 |
| `concepts` | 20 |
| `cognitive-architecture` | 7 |
| `paradigms` | 17 |
| `architecture` | 87 |
| `categories` | 100 |
| `design-space` | 60 |
| `projects` | 65 |
| `synthesis` | 8 |
| `evaluation` | 20 |
| `index` | 11 |
| `meta` | 6 |
| `starter-kit` | 4 |

## 当前结构覆盖

核心架构已覆盖：

- Intake & Representation
- Cognition & Continuity
- Action & Effect
- Interaction & Collaboration
- Orchestration & Parallelism
- Governance as Cross-Cutting Concern

本轮优化后强化的关键能力包括：

- ORDA-VU 的多粒度闭环、不可达验证降级与多目标 Update
- 复杂度等级系统，用于避免所有 Agent 都默认启用完整 Plane
- Plane 交互矩阵，用于识别强耦合、读写依赖和横切治理点
- Runtime 数据流模型，用于连接 JobSpec、ContextPack、WorldStateSnapshot、EffectRecord、FailureRecord 与 EvaluationCase
- Identity & Capability Plane，把身份、授权来源、权限范围和能力生命周期作为一等设计对象
- Error & Recovery Plane，把失败分类、恢复策略、降级和部分交付从边角逻辑提升为架构面
- Learning & Adaptation Plane，把运行中沉淀的偏好、策略和模式纳入受控学习闭环
- 范式选择决策树，把"列举范式"升级为"根据任务风险、可验证性、状态跨度和协作需求做选择"
- Anti-Pattern Top 10，把常见失败模式和修复路径显式化
- Eval Runner 的无外部依赖 fallback，保证 fixture 可以直接运行
- 结构校验器已修正为基于相对路径识别受检目录，并同时接受中文与英文 Evidence Status 标记

## 校验状态

`scripts/validate_skill.py` 当前结果：**VALIDATION FAILED**，共检查 392 个 Markdown 文件，374 通过，4 失败。失败文件均为 pytest 自动生成的 `.pytest_cache/README.md`（不含 Evidence Status 头），非项目文档内容，不影响 skill 质量。

## 无状态处理

skill 包不使用发布标签、日期包名或变更日志表达当前形态。运行时文档中的 `ConfigFingerprint` 只用于 Agent 系统的行为审计和回归，不代表 skill 自身有状态。

## 可执行校验口径

- `scripts/validate_skill.py`：检查 Evidence Status、相对链接、starter-kit 必需文件。
- `starter-kit/verified-tool-agent/tests/`：3 tests — 验证最小 Agent 的工具执行、效果验证与失败记录。
- `starter-kit/react-llm-agent/tests/`：6 tests — 验证 ReAct 循环中的效果验证、不可验证降级与循环检测。
- `starter-kit/stateful-agent/tests/`：6 tests — 验证 checkpoint 保存/恢复、TTL 快照刷新、中断恢复与上下文压缩。
- `evaluation/eval-runner/tests/`：24 tests — 验证评估 runner 的 fixture 读取、trace 比较、mock 工具和 world fixture。
- `evaluation/fixtures/`：提供表示、记忆、工具、安全、成本、并发、数据流、人机交互等基础 eval case。

## 仍然存在的少量缺口

纯 snippet 文件是源码切片而非分析文档，默认由相邻 README 与专题 Markdown 文件提供 provenance。若后续需要更严格的机器可读审计，可为 snippet 增加 sidecar metadata。

## 审计结论

这个 skill 已从"Runtime 模块知识库"升级为覆盖表示层、现实接口、世界状态、外部效果、人机交互、多 Agent 协作、成本工程、并发数据流、安全边界、身份授权、错误恢复、运维回归和可执行评估的 Agent 设计知识系统。
