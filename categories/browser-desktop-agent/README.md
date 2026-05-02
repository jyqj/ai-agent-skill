# Browser / Desktop Agent Architecture

> **Evidence Status** — grounded. Claude Computer Use、OpenAI Operator、Browser Use (81K+ stars)、WebMCP、Playwright 生态、WebVoyager/OSWorld benchmark。

## Core Job

在网页或桌面界面中完成真实用户级操作，交付可验证的任务结果：

```text
理解任务 → 感知界面 → 规划操作 → 执行 GUI 交互 → 验证效果 → 异常恢复
```

核心挑战："点击提交按钮返回 200 不等于订单真的创建了。"

## 用户模型

| 用户 | 心智模型 | 信任建立方式 | 默认交互 |
|---|---|---|---|
| 知识工作者 | 数字助手 | 任务正确、不破坏数据 | 描述任务 → 观察 → 确认 |
| 运营人员 | 批量操作工具 | 准确高效可回滚 | 任务队列+进度面板 |
| 非技术用户 | 操作代理 | 透明可见可中断 | 自然语言 → 实时预览 |

## 任务模型

| 任务 | 默认深度 | 完成定义 |
|---|---|---|
| 信息提取 | D3-D4 | 结构化数据 + 来源标记 |
| 表单填写 | D4 | 字段正确 + 提交验证 |
| 多步导航 | D4-D5 | 流程完成 + 最终状态验证 |
| 跨网站比较 | D4 | 多源结构化对比 |
| 批量操作 | D5 | 全部项处理 + 每项验证 |

## 表示模型

```text
DOM/AccessibilityTree、Screenshot、BoundingBox、PageState、
FormFieldState、ElementSelector、ActionHistory、NetworkState
```

双通道验证：DOM 状态 + 截图视觉 + 可选后端回读。

## 行动模型

| 动作 | 示例 | 风险 |
|---|---|---|
| Navigate | goto URL、click link | safe |
| Read | extract text、screenshot | safe |
| Input | type、select、check | check |
| Submit | click submit、confirm | check/approval |

## 品类特有设计决策

| 决策 | 默认建议 |
|---|---|
| 感知 | DOM + 截图双通道；A11y tree 优先，视觉兜底 |
| 沙箱 | 隔离浏览器 profile；独立 cookie jar |
| 安全 | origin allowlist、防钓鱼、防 DOM prompt injection |
| 等待 | 智能等待（DOM 稳定 + network idle），非固定 sleep |
| 定位 | 多策略降级：test-id > aria > CSS > XPath > 坐标 |

## 参考实现

| 参考 | 学习点 |
|---|---|
| Claude Computer Use | screenshot-action loop、Zoom Action |
| OpenAI Operator/CUA | 任务规划、安全约束 |
| Browser Use (81K★) | DOM+视觉混合、89% WebVoyager |
| WebMCP | 网站作为结构化工具协议 |
| Browserbase/Steel | 云托管浏览器基础设施 |

## 延伸：主观性任务的验证

本品类的部分任务涉及主观判断，标准效果验证可能不够：

- `../../concepts/beyond-verification.md` — 超越 postcondition 的验证方式
- `../../evaluation/subjective-eval.md` — 主观性任务的评估框架
