# 构建 Browser Agent：最短路径

> **Evidence Status** — synthesized. 基于 `categories/browser-desktop-agent/`、Browser Use、Anthropic Computer Use、Stagehand 等分析压缩而来；这是操作清单，不是生产实现。

## 定位

Browser Agent 成功的判定标准是用户目标在网页/后端状态中确认达成：

```text
用户目标已在网页/后端状态中达成，并有 DOM / screenshot / readback 证据
```

完整品类设计见 `../categories/browser-desktop-agent/README.md`。

## 1. 先定任务边界

```yaml
agent_type: browser-desktop-agent
primary_deliverable: "verified browser workflow result"
allowed_domains: []
allowed_actions:
  - navigate
  - read_dom
  - screenshot
  - click
  - type
  - scroll
approval_required:
  - submit_form
  - purchase
  - send_message
  - irreversible_account_change
success_criteria:
  - target page state changed
  - confirmation or readback exists
  - sensitive data handling is explicit
```

先读：`../toolkit/choose-agent-type.md`、`../categories/browser-desktop-agent/task-model.md`。

## 2. 选择最小运行时

| 模块 | Browser Agent 最小要求 |
|---|---|
| Representation | PageState、DOM/AccessibilityTree、Screenshot、URL、FormFieldState |
| Context | 当前目标、页面快照、最近动作、失败原因 |
| Tools | navigate / query / click / type / screenshot / wait |
| Execution | browser profile、session、timeout、selector fallback |
| Control | domain allowlist、submit/purchase approval、PII policy |
| Effects | DOM + screenshot 双通道验证，必要时后端 readback |
| Recovery | stale element、modal、captcha、navigation failure、timeout |
| Observability | action trace、screenshot refs、selector refs |

## 3. Runtime loop

```text
intake task + allowed scope
  → observe DOM / screenshot / URL
  → represent PageState
  → choose next action
  → permission gate for risky action
  → execute GUI action
  → verify DOM + screenshot / readback
  → recover or ask user
  → final: result + evidence refs
```

关键边界：`click` 成功不等于任务成功；HTTP 200 不等于订单/表单真的完成。

## 4. 风险门控

```text
[ ] allowed_domains 是否限制？
[ ] 是否区分 read / type / submit / purchase？
[ ] 表单提交、支付、发消息是否需要 approval？
[ ] 截图是否可能包含敏感信息？
[ ] captcha / 登录 / 2FA 是否会转人工？
[ ] 页面状态是否有 freshness / stale policy？
```

先读：`../architecture/planes/control/overview.md`、`../architecture/planes/security/overview.md`。

## 5. Eval

Browser Agent eval 至少检查：

```text
[ ] action trace 顺序正确
[ ] DOM 与 screenshot 证据一致
[ ] submit 类动作前经过 gate
[ ] stale element / modal / timeout 有恢复路径
[ ] 最终状态有 confirmation 或 readback
[ ] 不把不可验证动作说成 verified
```

先读：`../evaluation/effect-evals.md`、`../evaluation/tool-use-evals.md`、`../evaluation/execution-depth-evals.md`。

## 6. 参考项目对照

| 设计问题 | 先对照 |
|---|---|
| 视觉与 DOM 表示 | `../projects/browser-desktop-agents/anthropic-computer-use/README.md` |
| browser action loop | `../projects/browser-desktop-agents/browser-use/architecture.md` |
| developer-friendly browser automation | `../projects/browser-desktop-agents/stagehand/architecture.md` |
| 通用 runtime contract | `../synthesis/local-agent-runtime-practices.md` |

## Stop Gate

```text
[ ] 用户目标对应的页面/后端状态已验证
[ ] 关键动作有 DOM 和 screenshot 或等价证据
[ ] 高风险动作未越过审批
[ ] 敏感信息处理方式已说明
[ ] 未完成、被阻塞或不可验证项已明确交付
```
