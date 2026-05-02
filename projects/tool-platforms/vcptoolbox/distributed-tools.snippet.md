# VCPToolBox 分布式工具执行

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

## 星型网络拓扑

```
┌─────────────────────────────────────┐
│     VCP 主服务器 (WebSocketServer)   │
│                                     │
│  • 连接管理 (6 种客户端)             │
│  • 消息路由与调度                    │
│  • 插件管理 (本地 + 分布式)          │
│  • 文件获取服务 (FileFetcherServer)  │
└───────────────┬─────────────────────┘
                │
    ┌───────────┼───────────┬─────────────┐
    ▼           ▼           ▼             ▼
  Node-A      Node-B      Node-C      VCPChrome
 (GPU)       (Files)     (Crawler)   (Browser)
```

## 6 种客户端类型

| 类型 | 路径 | 用途 |
|------|------|------|
| VCPLog | `/VCPlog/VCP_Key=` | 日志订阅 |
| VCPInfo | `/vcpinfo/VCP_Key=` | 系统状态推送 |
| DistributedServer | `/vcp-distributed-server/VCP_Key=` | 远程工具节点 |
| ChromeObserver | `/vcp-chrome-observer/VCP_Key=` | 浏览器观察者 |
| ChromeControl | `/vcp-chrome-control/VCP_Key=` | 浏览器控制器 |
| AdminPanel | `/vcp-admin-panel/VCP_Key=` | Web 管理面板 |

## 节点注册流程

```javascript
// Step 1: 工具注册
{
  type: 'register_tools',
  data: {
    tools: [{
      name: 'video_generator',
      description: '生成视频',
      pluginType: 'service',
      capabilities: { ... }
    }]
  }
}

// 服务端处理
registerDistributedTools(serverId, tools) {
  for (tool of tools) {
    tool.isDistributed = true
    tool.serverId = serverId
    tool.displayName = `[云端] ${tool.name}`
    plugins.set(tool.name, tool)
  }
}

// Step 2: IP 上报
{
  type: 'report_ip',
  data: {
    localIPs: ['192.168.1.100'],
    publicIP: '203.0.113.50',
    serverName: 'GPU-Server-01'
  }
}

// Step 3: 占位符更新 (可选)
{
  type: 'update_static_placeholders',
  data: {
    placeholders: { '{{RemoteWeather}}': '晴天 25°C' }
  }
}
```

## 分布式工具执行

```
主服务器                                 分布式节点
    │                                       │
    │─ execute_tool ─────────────────────►│
    │  { requestId, toolName, toolArgs }   │
    │                                      │ (执行工具)
    │                                      │
    │◄──── tool_result ────────────────────│
    │  { requestId, status, result }       │
```

```javascript
// Promise-based 超时管理
executeDistributedTool(serverId, toolName, toolArgs) {
  return new Promise((resolve, reject) => {
    const requestId = generateId()
    const timeout = plugin.communication?.timeout || 60000

    // 设置超时
    const timeoutId = setTimeout(() => {
      pendingToolRequests.delete(requestId)
      reject(new Error('Timeout'))
    }, timeout)

    // 注册待处理
    pendingToolRequests.set(requestId, { resolve, reject, timeoutId })

    // 发送请求
    server.ws.send(JSON.stringify({
      type: 'execute_tool',
      data: { requestId, toolName, toolArgs }
    }))
  })
}
```

## 文件传输机制

```
插件请求 file:// URL
    ↓
本地不存在 (ENOENT)
    ↓
FileFetcherServer.fetchFile(url, requestIp)
    ↓
根据 requestIp 定位来源节点
(findServerByIp → distributedServerIPs)
    ↓
WebSocket 请求远程节点
(internal_request_file 内部工具)
    ↓
节点返回 Base64 编码数据
    ↓
缓存到 .file_cache/<hash>.<ext>
    ↓
返回 { buffer, mimeType }
```

### 缓存策略

| 缓存类型 | 位置 | 过期 | 用途 |
|---------|------|------|------|
| 文件缓存 | `.file_cache/` | 永久 | 已获取的文件 |
| 失败缓存 | `failedFetchCache` | 30秒 | 防止重复失败 |
| 请求缓存 | `recentRequests` | 5秒 | 防止循环请求 |

## ChromeBridge 集成

```javascript
// 混合服务：页面信息 + 浏览器控制
pluginType: "hybridservice"

// Observer 持续上报页面状态
{
  type: 'pageInfoUpdate',
  data: { markdown: '# Page Title\nURL: ...' }
}

// Control 发送命令
{
  type: 'command',
  data: {
    requestId: 'xxx',
    command: 'click',        // click, type, open_url
    target: '搜索框',
    wait_for_page_info: true
  }
}
```

## 设计启示

1. **中心化路由**: 所有通信经过主服务器，简化点对点复杂度
2. **动态注册**: 节点即插即用，断开自动注销
3. **透明文件传输**: 插件无需感知文件位置，自动回补
4. **Promise 管理**: 超时 + Map 实现高效的异步请求跟踪
5. **IP 溯源**: 支持跨节点文件定位，保持文件系统透明
