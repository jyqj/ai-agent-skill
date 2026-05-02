# Browser / Desktop Agent Closed Loop

> **Evidence Status** — synthesized. 品类蓝图与设计模板的综合整理，结合 ORDA-VU 闭环与评估维度。

## 核心循环

```text
1. Observe: 截图 + DOM/A11y + 页面状态
2. Represent: 结构化页面 + 可操作元素 + 任务进度
3. Decide: 下一步操作 + 预期结果 + 失败回退
4. Act: 执行 GUI 操作
5. Verify: 双通道验证（DOM + 视觉 + 可选后端）
6. Update: 更新进度 → 继续/重试/升级
```

## Stop Gate

```text
[ ] 最终目标已达成（不仅是最后一步操作成功）
[ ] 截图+DOM 双通道确认
[ ] 关键操作有后端效果验证
[ ] 无未处理弹窗/错误
[ ] 操作轨迹已记录
```

## 常见失败

| 失败 | 恢复 |
|---|---|
| 元素定位失败 | 等待 → 替代 selector → 视觉定位 |
| CAPTCHA | 升级到人工 |
| 登录失效 | 重新登录 → checkpoint 续执行 |
