# 神经-符号混合架构

> **Evidence Status** — mixed
> 来源：neuro-symbolic AI 研究（Garcez et al., Kautz 2022）、coding agent 中 AST/compiler 与 LLM 的协作实践、enterprise agent 中规则引擎与 LLM 的集成经验、RAG + 数据库查询的生产模式。

## 1. 为什么需要混合

LLM 和符号系统各有擅长和不擅长：

| 能力 | LLM | 符号系统 |
|---|---|---|
| 模糊匹配 | 强 | 弱 |
| 自然语言理解 | 强 | 弱 |
| 精确推理 | 弱 | 强 |
| 约束满足 | 弱 | 强 |
| 可解释性 | 弱 | 强 |
| 泛化到新场景 | 强 | 弱 |
| 一致性保证 | 弱 | 强 |
| 常识推理 | 强 | 弱 |

单独使用任何一方都会在另一方的能力域出现短板。混合架构的目标是让每个组件做它最擅长的事。

## 2. 混合模式

### 2.1 LLM 理解 + 规划器执行

典型代表：Coding Agent

```text
用户需求（自然语言）
    ↓
LLM: 理解意图，生成代码草案
    ↓
AST 分析: 检查语法正确性、类型一致性
    ↓
编译器/解释器: 精确验证可执行性
    ↓
测试框架: 验证行为正确性
    ↓
LLM: 根据测试结果修正
```

LLM 负责"从模糊到结构化"的翻译，符号系统负责"结构化后的精确验证"。

### 2.2 LLM 意图识别 + 规则引擎合规检查

典型代表：Enterprise Workflow Agent

```text
用户请求: "帮我给这个客户退款 $5000"
    ↓
LLM: 识别意图 = refund, 金额 = 5000, 对象 = customer_id
    ↓
规则引擎:
  - 金额 > $1000 → 需要主管审批
  - 客户状态 = VIP → 允许快速通道
  - 本月退款总额 > $10000 → 触发风控审查
    ↓
LLM: 将规则引擎的决定翻译为自然语言回复用户
```

### 2.3 LLM 交互 + 数据库精确查询

典型代表：Data / BI Agent

```text
用户: "上个季度哪个产品线增长最快？"
    ↓
LLM: 理解问题，生成 SQL
    ↓
SQL 引擎: 精确执行查询，返回数据
    ↓
LLM: 解释结果，生成可视化建议
    ↓
图表库: 精确渲染图表
```

关键点：LLM 生成的 SQL 可能有错，需要 schema validation 和 dry-run 验证。

### 2.4 LLM 高层规划 + 传统 ML 数值预测

典型代表：Ops / SRE Agent

```text
LLM: "根据告警模式，这看起来像内存泄漏"
    ↓
时序模型: 预测内存使用趋势，预计 2 小时后 OOM
    ↓
LLM: "建议立即重启 Pod 并排查内存分配"
    ↓
规则引擎: 检查操作权限和变更窗口
    ↓
LLM: 生成变更单并通知相关人员
```

## 3. 接口设计：神经和符号之间的桥梁

LLM 的输出是自然语言文本，符号系统的输入通常是结构化数据。**结构化输出**是关键桥梁。

### 3.1 结构化输出的形式

| 形式 | 适用场景 | 可靠性 |
|---|---|---|
| JSON Schema 约束 | 工具调用参数、API 请求 | 高（有 schema 验证） |
| YAML 配置 | 规则引擎输入、工作流定义 | 中（需要额外验证） |
| SQL / 查询语言 | 数据库查询 | 中（需要 dry-run） |
| 代码 (Python/JS) | 计算逻辑、数据处理 | 中（需要沙箱执行） |
| DSL | 领域特定操作 | 高（如果 DSL 设计良好） |

### 3.2 接口契约

```yaml
neural_to_symbolic_interface:
  input_format: json_schema | yaml | sql | code
  validation:
    schema_check: true
    dry_run: true | false
    sandbox: true | false
  error_handling:
    on_parse_failure: retry_with_feedback | escalate
    max_retries: 3
    feedback_template: "输出不符合要求: {error}. 期望格式: {schema}"
```

### 3.3 反向接口：符号到神经

符号系统的输出也需要回传给 LLM：

```text
规则引擎输出: { "decision": "deny", "reason": "amount_exceeds_limit", "limit": 1000 }
    ↓
LLM 接收结构化结果，翻译为自然语言或下一步行动
```

## 4. 与 Control Plane 的关系

Control Plane 的 Policy Engine 就是一种符号系统：

```text
LLM (生成候选动作)
    ↓
Policy Engine (符号系统，检查约束)
    ↓ allow / deny / ask
LLM (根据政策决定执行或解释)
```

Policy Engine 的规则通常是:
- 手动编写的业务规则
- 从合规文档中提取的约束
- 从历史事故中学到的安全边界

这是最普遍的神经-符号混合场景之一。

## 5. 与 Tool Paradigms 的关系

`code-as-tool` 模式的实质就是 LLM 调用符号计算：

| Tool Paradigm | 神经-符号混合的体现 |
|---|---|
| API-as-tool | LLM 生成 API 参数，API 做精确操作 |
| Code-as-tool | LLM 生成代码，解释器/编译器做精确执行 |
| DB-as-tool | LLM 生成查询，数据库做精确检索 |
| Shell-as-tool | LLM 生成命令，Shell 做精确执行 |

每种工具调用都是一次"神经 → 结构化输出 → 符号执行 → 结果回传 → 神经解释"的循环。

## 6. 设计决策检查清单

- [ ] 哪些步骤需要精确性？→ 用符号系统
- [ ] 哪些步骤需要灵活性？→ 用 LLM
- [ ] 神经到符号的接口是否有 schema 验证？
- [ ] 符号系统的错误信息是否能被 LLM 理解并修正？
- [ ] 是否有 fallback：当结构化输出持续失败时怎么办？
- [ ] 符号系统的规则更新流程是否独立于模型更新？

## 7. 反模式

| 反模式 | 症状 | 改进 |
|---|---|---|
| 让 LLM 做精确计算 | 数值错误、逻辑不一致 | 生成代码让解释器算 |
| 让规则引擎处理自然语言 | 大量模板匹配规则，维护成本高 | 用 LLM 做意图识别 |
| 没有 schema 验证 | LLM 输出格式不稳定导致下游崩溃 | 加 JSON Schema 约束 |
| 不给 LLM 反馈 | 结构化输出错误时直接失败 | 将错误信息回传让 LLM 修正 |
| 符号规则硬编码在 prompt 中 | 规则更新需要改 prompt | 将规则外部化为配置 |

## 延伸阅读

- `model-role-allocation.md` -- 符号系统可以视为一种特殊的"角色"
- `world-models.md` -- 物理引擎/模拟器是典型的符号世界模型
- `../planes/control/overview.md` -- Policy Engine 作为符号系统
- `../planes/tools/tool-use.md` -- 工具调用作为神经-符号接口
- `../../concepts/harness-engineering.md` -- Harness 设计中的符号约束
