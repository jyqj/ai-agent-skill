# Channel Adapter

> **Evidence Status** — grounded. OpenClaw 20+ 渠道适配 + Hermes 35+ platform adapter。

## 模式定义

将异构消息渠道（WhatsApp/Telegram/Discord/Slack/iMessage 等）统一为标准的 inbound/outbound 接口，通过 per-channel adapter 处理渠道特定逻辑。

## 核心接口

```
ChannelInboundMessage {
  targetId, fromAccountId, timestamp, body, attachments?, metadata?
}
ChannelOutboundReply {
  targetId, body?, attachments?, edited?, reactions?
}
```

## 适配层

| 层 | 职责 |
|----|------|
| Transport | 渠道特定的消息收发（Bot API / Webhook / WebSocket） |
| Account Metadata | 渠道特定的用户信息（name, avatar, capabilities） |
| Allowlist Policy | DM/Group 访问控制 |
| Turn Management | 渠道特定的对话轮次处理 |

## DM-First Security (OpenClaw)

个人 assistant 场景：默认拒绝陌生人 DM，通过 pairing code 机制授权。
- `dmPolicy="pairing"` — 未知发送者收到配对码
- `dmPolicy="open"` — 需要显式 opt-in + allowlist

## 实现光谱

| 项目 | 渠道数 | 抽象层 |
|------|--------|--------|
| OpenClaw | 20+ | Plugin-based channel adapter |
| Hermes | 35+ | Platform adapter pattern |
| NagaAgent | 2 | 直接集成 |

## 风险

- 最小公约数：统一接口可能丢失渠道特定能力（reactions, threads, buttons）
- 维护成本：每个渠道 API 独立演化，adapter 需要持续更新
