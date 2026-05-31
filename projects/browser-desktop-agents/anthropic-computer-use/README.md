# Anthropic Computer Use

> **Evidence Status** — synthesized. 基于 Anthropic 官方 computer-use 说明与 benchmark 观察，非源码级分析。

## 基本信息

- **类型**：browser-agent / desktop-agent
- **项目定位**：通过截图、鼠标、键盘等工具在用户环境中完成 GUI 任务
- **推荐入口**：先读本 README，再读 `observation-loop.md`

## 模块覆盖

| 模块 | 覆盖程度 | 证据文件 | 可复用模式 |
|---|---|---|---|
| representation | 深 | `observation-loop.md` | multimodal observation bundle |
| tools | 深 | `README.md` | computer-use action host |
| effects | 中 | `observation-loop.md` | Dual-Channel GUI Verification |
| security | 中 | `README.md` | browser phishing / secret exposure guard |
| interaction | 中 | `README.md` | high-risk action approval |

## 核心模式

- **screenshot-mediated observation**：截图是主观察通道之一。
- **client-side action boundary**：动作发生在用户或受控环境中，宿主边界必须清楚。
- **verification after action**：点完之后必须重新观察，而不是假设成功。

## 独特贡献

Computer Use 把”多模态观察 + GUI 动作空间 + 安全边界”统一为同一个 runtime 问题。大多数 agent 把这三者当独立能力分别实现，但 GUI 环境下它们不可分割：不理解截图就不能安全点击，不验证点击结果就不能确认安全。

## 关键发现

- GUI agent 最大的难点是**闭环验证**：知道自己点的是什么元素、点完之后页面状态是否如预期变化。
- Screenshot、DOM 结构、viewport 坐标和 origin 验证必须被一起设计为一个 observation bundle，拆开处理会导致信息断裂。
- 安全策略的覆盖面远超 CLI agent：高风险按钮（删除/支付）、登录态泄露、secret 可见性、钓鱼页面和外部跳转都需要专门处理。
