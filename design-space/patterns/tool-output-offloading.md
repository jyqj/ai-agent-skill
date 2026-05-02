# Tool Output Offloading

> **Evidence Status** — synthesized. 来自多个 Agent 项目在处理大输出时的共同实践，属于工程层面的成熟模式。

Agent 调用工具后经常收到大量输出——测试日志、网页全文、代码搜索结果、PDF 表格，动辄数千 token。把这些内容原样塞进上下文窗口，有用信息会被淹没在噪声中，后续推理质量随之下降，这就是上下文腐化（context rot）。

## 核心思路

解法很直接：设定一个内联预算（inline budget），超过预算的输出写入外部存储，上下文中只保留摘要、关键片段和一个可回溯的引用。

```python
def normalize_tool_output(output, budget):
    if token_count(output.text) <= budget.inline_limit:
        return InlineObservation(output.text)
    ref = artifact_store.write(output.text)
    summary = summarize(output.text, max_tokens=budget.summary_limit)
    return OffloadedObservation(summary=summary, raw_ref=ref, truncated=True)
```

这段逻辑的关键不在于摘要算法本身，而在于几条必须遵守的约束：

- **截断透明**：observation 必须明确标注是否经过截断，模型需要知道自己看到的不是完整信息。
- **引用可读**：artifact 引用必须能被后续工具调用读取，否则卸载就变成了丢弃。
- **摘要不等于证据**：摘要可以辅助推理，但不能作为最终结论的依据；需要精确信息时，必须回溯原始数据。
- **错误优先**：关键错误行应优先保留在内联部分，即使总量超过预算也不应被摘要掉。

最后一点尤为重要：如果一段 500 行的测试日志里有 3 行失败信息，这 3 行的价值远超其余 497 行。内联预算的分配应该是语义感知的，而不是简单截断前 N 行。
