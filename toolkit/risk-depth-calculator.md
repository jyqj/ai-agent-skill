# Risk & Depth Calculator

> **Evidence Status** — synthesized. 从执行深度、自治等级、效果风险和控制 plane 中压缩出的复杂度判断工具。

## 30 秒判断

风险越高、效果越不可逆、世界状态越容易变化，需要的深度越高。

| 问题 | 低 | 中 | 高 |
|---|---|---|---|
| 是否写外部世界 | 只读 | 可撤销写 | 不可逆写 / 生产写 |
| 是否可验证 | 用户可看 | readback/test | 需要外部 ack / 传感器 |
| 状态跨度 | 单轮 | 多步 | 跨会话 / 长任务 |
| 失败成本 | 可忽略 | 需修复 | 金钱/安全/生产事故 |
| 自主权 | 建议 | 人审批执行 | Agent 自动执行 |

## 推荐深度

| 组合 | 推荐 |
|---|---|
| 只读 + 单轮 + 低失败成本 | D1-D2 |
| 多步分析 + 需要证据 | D3-D4 |
| 写文件/API + 可回读 | D4-D5 |
| 生产变更 / 金钱 / 安全 / 不可逆动作 | D5-D6 + approval |
| 持续监控和自动处置 | D6 + Operations + Recovery |

## 最小产出

```yaml
required_depth: D5
risk_reason:
  - "writes external system"
  - "requires read-after-write"
control_policy:
  approval_required_for:
    - delete
    - deploy
    - send_external
verification_required: true
```

## 深度不是越高越好

如果当前只是探索或原型，宁可保持 D3/D4，加上清晰的 `blocked / pending / unverifiable_by_agent` 状态，也不要假装做到 D6。

## 下一步

1. `module-picker.md`
2. `eval-planner.md`
3. `../index/maturity-ladders.md`
