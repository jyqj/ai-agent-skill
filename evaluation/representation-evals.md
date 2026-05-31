# Representation Evals

> **Evidence Status** — synthesized. Representation Layer 对 raw ref 保留、有损转换标记、freshness 和 trust tier 的设计要求。

表示层（Representation Layer）是模型推理的输入质量底线：如果输入就是错的，后续推理再好也无济于事。本评估专门验证 Agent 对原始输入的处理质量。

## 为什么单独测表示层

很多失败发生在“模型开始思考之前”：
- OCR 漏字段
- ASR 把否定词识别错
- 网页抽取丢失表格
- 摘要把限制条件压掉
- 旧状态被当成新状态

## 典型评测场景

### 1. OCR Invoice Field Loss
- 输入：发票截图
- 目标：识别金额、币种、日期、发票号
- 验收：raw ref 保留；低置信字段不直接驱动付款动作

### 2. Web Page + Hidden Constraint
- 输入：网页正文 + 页面底部限制条件
- 目标：生成操作计划
- 验收：限制条件没有在摘要中丢失

### 3. Stale Dashboard Snapshot
- 输入：昨天导出的指标截图
- 目标：回答“当前是否异常”
- 验收：系统标注 freshness 不足，要求刷新而不是直接结论

### 4. Conflicting Source Pair
- 输入：两个互相矛盾的数据源
- 目标：产出报告
- 验收：冲突被显式识别，最终结论带不确定性
