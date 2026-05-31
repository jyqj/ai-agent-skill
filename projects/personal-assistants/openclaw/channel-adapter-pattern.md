# OpenClaw Channel Adapter

> **Evidence Status** — grounded. OpenClaw src/channels/ 源码分析。

## 20+ 渠道

WhatsApp, Telegram, Slack, Discord, Google Chat, Signal, iMessage, IRC, Microsoft Teams, Matrix, Feishu, LINE, Mattermost, Nextcloud Talk, Nostr, Synology Chat, Tlon, Twitch, Zalo, WeChat, QQ, WebChat

## Adapter 结构

每个渠道 plugin 实现：
- Message transport（Bot API / Webhook / WebSocket）
- Account metadata（name, avatar, capabilities）
- Allowlist policy
- Turn management

## DM-First Security

- 默认 `dmPolicy="pairing"`：未知发送者收到配对码
- `dmPolicy="open"` 需要显式 opt-in + allowlist
- 配对通过 `openclaw pairing approve <channel> <code>`

## Runtime Dispatch

```
Inbound → resolveMessageChannel() → Channel-specific parsing → Agent → Outbound delivery
```
