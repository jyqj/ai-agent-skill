# 多模型异构系统

> **Evidence Status** — theoretical
> 当前 Agent 架构知识库假设 Agent = 一个模型 + Harness。但生产 Agent 越来越多地采用多模型协作架构。本目录补充这一维度。

## 为什么一个 Agent 需要多个模型

单模型架构在以下场景会触碰天花板：

| 瓶颈 | 说明 | 多模型解法 |
|---|---|---|
| 成本 | 所有步骤都用大模型，token 成本线性放大 | 小模型处理简单步骤，大模型只在关键节点介入。Planner-Executor 分离可减少推理成本达 45%（Claude Code/Cursor 实践） |
| 延迟 | 大模型推理慢，串行步骤多则总延迟高 | 轻量模型并行处理低复杂度子任务 |
| 同源偏差 | 同一个模型既生成又验证，容易自洽但不正确 | 独立 Critic 模型做异源校验。Agent-as-a-Judge 多模型辩论使人类不一致率从 31% 降至 0.3% |
| 模态覆盖 | 文本模型无法处理图像、音频、视频 | 专用 VLM / ASR 模型负责对应模态 |
| 精确计算 | LLM 不擅长数值计算、约束求解 | 符号引擎 / 传统 ML 做精确部分（Hermes 的 SQL 引擎、Coding Agent 的编译器验证） |
| 安全隔离 | Guard 逻辑和生成逻辑耦合时易被绕过 | 独立 Guard 模型做输入/输出防护 |
| 环境预测 | 长期规划需要预测未来状态 | 专用 World Model 做状态转移模拟 |

## 常见角色

一个多模型 Agent 内部可能包含以下角色：

- **Planner** -- 大型推理模型，负责任务分解和高层规划
- **Critic / Judge** -- 独立小模型，异源验证 Planner 输出
- **Embedder** -- 专用 embedding 模型，负责检索和语义匹配
- **Vision** -- VLM，处理图像理解、GUI 识别等
- **Tool Router** -- 微调小模型，快速选择工具
- **Guard** -- 独立防护模型，输入/输出安全检查
- **World Model** -- 模拟环境动态，预测未来状态

## 本目录回答的问题

| 问题 | 文件 |
|---|---|
| 如何给不同模型分配角色？ | `model-role-allocation.md` |
| 多个模型意见不一致怎么办？ | `confidence-aggregation.md` |
| 什么时候需要显式世界模型？ | `world-models.md` |
| LLM 和符号系统如何混合？ | `neuro-symbolic-hybrid.md` |

## 与其他模块的关系

- `../planes/cost/model-routing.md` -- 侧重成本维度的模型路由；本目录侧重架构维度的角色分配
- `../planes/orchestration/` -- 多 Agent 间编排；本目录侧重单 Agent 内的多模型编排
- `../planes/representation/` -- 多源观察的融合；本目录扩展到多模型输出的融合
- `../planes/control/` -- Policy Engine 是一种符号系统，与 neuro-symbolic 混合相关
- `../planes/security/` -- Guard 模型是安全架构的一部分

## 延伸阅读

- `model-role-allocation.md`
- `confidence-aggregation.md`
- `world-models.md`
- `neuro-symbolic-hybrid.md`
- `../planes/cost/model-routing.md`
- `../planes/orchestration/overview.md`
