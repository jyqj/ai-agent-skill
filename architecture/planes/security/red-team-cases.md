# Red-Team Cases

> **Evidence Status** — synthesized. prompt injection、tool output injection、MCP boundary、browser phishing、memory poisoning 等常见 Agent 风险。

## 目的

Security Plane 不能只停留在原则，还要能被 fixture、trace 和 review case 触发。

## 推荐红队案例

| 案例 | 攻击点 | 期望防御 |
|---|---|---|
| MCP Prompt Injection | 第三方 server 返回“忽略之前规则” | untrusted_data lane + sanitization |
| MCP Confused Deputy | 只读能力被诱导成代用户执行写动作 | capability boundary + deny escalation |
| Tool Output Injection | 搜索结果 / issue 评论夹带恶意指令 | instruction/data separation |
| Browser Phishing | 页面伪装成登录或付款确认 | origin verification + approval |
| Visual Prompt Injection | 截图里的文字诱导执行 | screenshot 视作 untrusted observation |
| Memory Poisoning | 恶意内容试图进入长期记忆 | write approval + provenance + quarantine |
| Citation Spoofing | 报告中的 citation 看似存在但不支撑 claim | citation integrity gate |
| Secret Exposure | GUI 或日志显示 token / secrets | redaction + no raw echo |

## fixture 设计建议

每个红队 case 至少写清：

```yaml
attack_surface: string
malicious_payload: string
expected_lane: instruction | trusted_data | untrusted_data | memory | inference
forbidden_effects: []
required_trace_signals: []
```

## 与其他模块的关系

- `evaluation/security-evals.md`：把红队案例转成评估集。
- `effects/`：高风险外部动作必须显式 gate。
- `interaction/`：需要 approval 的动作要能解释风险。
- `learning/`：防御策略更新后应进入 regression。
