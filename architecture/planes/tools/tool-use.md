# Tool Use Pattern


> **Evidence Status** — synthesized. 通用运行时模块来自多个参考项目的统一抽象。

## 问题

Agent 需要调用工具完成真实动作，但工具调用容易出现参数错误、工具选错、结果不可读、权限越界。

## 解法

```text
Intent → Tool Selection → Schema Validation → Policy Check → Execute → Normalize → Verify
```

## 伪代码

```python
def use_tool(intent, candidate_tool, args, state):
    tool = registry.resolve(candidate_tool)
    args = tool.schema.validate(args)
    decision = policy.check(tool, args, state)
    if decision == 'deny': return Observation.denied(tool.id)
    if decision == 'ask': return ApprovalRequest(tool.id, args)
    raw = executor.run(tool, args)
    obs = normalizer.normalize(tool, raw)
    trace.record(tool.id, args, obs)
    return obs
```

## 设计要点

- 工具描述说明何时使用、何时不要使用。
- 工具输出结构化，包含 status、summary、evidence、error_type。
- 高风险工具必须经过 Policy Engine。
- 长输出应该 offload，只把摘要和引用放入上下文。
