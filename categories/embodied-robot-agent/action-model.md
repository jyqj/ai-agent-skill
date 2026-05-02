# Embodied Robot Agent Action Model

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

## 动作层级

```text
LLM 层: "把杯子放桌上" → [navigate, pick, place]
Skills 层: pick → [approach, pre-grasp, grasp, lift, verify]
Control 层: grasp → 力控/位控
```

## 安全约束（不可覆盖）

- 力矩 < 安全阈值
- 末端速度 < 安全阈值（人类附近更低）
- 碰撞检测 → 立即停止
- 禁区不可进入
- Emergency Stop 最高优先级
