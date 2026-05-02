# Embodied Robot Agent Closed Loop

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

```text
1. Perceive: 传感器 → 场景理解
2. Plan: LLM 高层 → skill 序列
3. Validate: 安全检查 → 可行性
4. Execute: 低层控制
5. Sense: 传感器回读 → 效果验证
6. Adapt: 成功→下一步 / 失败→重规划/求助
```

安全闭环嵌套在每一步：实时力/位监控 → 超阈值立即停止。
