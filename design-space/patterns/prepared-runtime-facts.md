# Prepared Runtime Facts

> **Evidence Status** — grounded. OpenClaw prepared-runtime-facts 优化模式。

## 模式定义

在启动时或请求入口处一次性预计算频繁使用的运行时值（model refs, provider IDs, channel IDs, capability flags），通过 context 传递给下游消费者，避免 hot path 中的重复发现。

## 反模式：Request-Time Rediscovery

```
# 反模式：每次请求都重新发现
async function handleReply(message) {
  const providers = await loadAllPlugins();          // 全量加载
  const model = await resolveModelFromCatalog();     // 重复查询
  const channel = await getChannelPlugin(message);   // 重复解析
  // ... 使用
}
```

## 正确做法

```
# 启动时预计算
const runtimePlan = {
  provider: resolveProviderOnce(),
  model: resolveModelOnce(),
  channel: resolveChannelOnce(),
};

// Hot path 直接使用预计算值
async function handleReply(message, runtimePlan) {
  // 无需重复发现
}
```

## 适用条件

- Plugin/Provider 数量 >20
- Hot path 每秒处理 >10 请求
- 运行时值在 request 生命周期内不变

## 与缓存的区别

Prepared Runtime Facts 把发现推到更早的位置（启动/配置加载），从根本上消除 hot path 中的发现动作，而非在发现之后再缓存结果。
