# Personal Memory Agent Design Decisions

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

| 决策 | 默认 | 升级触发 |
|---|---|---|
| 存储 | raw+structured+vector | 规模 → 分层 |
| 提取 | 对话后批量 | 实时 → 流式 |
| 检索 | 混合(语义+结构+时效) | 单策略不够 → 多路+重排 |
| 矛盾 | supersede(旧降权保留) | 否认 → retracted |
| 遗忘 | 事实 TTL+偏好衰减 | 存储压力 → 压缩 |
| 安全 | 不存密码/金融；危机不记忆 | — |
