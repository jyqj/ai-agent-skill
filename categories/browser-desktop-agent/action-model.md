# Browser / Desktop Agent Action Model

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

## 动作分类

| 动作 | 风险 | Precondition | Postcondition | Verification |
|---|---|---|---|---|
| navigate | safe | URL 在 allowlist | 页面加载完成 | URL 匹配+DOM 就绪 |
| click | safe/check | 元素可见可点击 | 预期状态变化 | DOM+截图 |
| type/fill | check | 元素可编辑 | 值已填入 | 回读匹配 |
| submit | check/approval | 表单验证通过 | 成功响应 | 确认页/后端验证 |
| screenshot | safe | 无 | 图像生成 | 非空 |
| download | check | 磁盘空间 | 文件存在 | hash/内容校验 |

## 操作安全

- **origin allowlist：** 只在白名单域操作。
- **凭证隔离：** 密码不经 DOM 明文传递。
- **防钓鱼：** 检查当前 URL 是否预期域。
- **速率控制：** 操作间隔 ≥ 500ms。
