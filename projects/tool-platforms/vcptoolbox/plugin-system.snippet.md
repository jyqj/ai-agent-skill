# VCPToolBox 插件系统架构

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

## 核心设计

**Manifest 驱动**: 所有插件行为由 `plugin-manifest.json` 声明式定义

```json
{
  "name": "PluginName",
  "pluginType": "synchronous",
  "entryPoint": { "type": "nodejs", "command": "node plugin.js" },
  "communication": { "protocol": "stdio", "timeout": 60000 },
  "configSchema": { "API_KEY": { "type": "string" } },
  "capabilities": {
    "invocationCommands": [{
      "commandIdentifier": "CommandName",
      "description": "工具描述（注入到 AI 系统提示词）"
    }]
  }
}
```

## 六种插件类型

### 1. static - 静态占位符
```
触发: Cron 定时执行
输出: 存储到 staticPlaceholderValues Map
用途: 周期性数据注入 (天气、日程等)
特性: 支持 vcp_dynamic_fold 语义折叠
```

### 2. synchronous - 同步工具
```
触发: AI 工具调用 (<<<[TOOL_REQUEST]>>>)
执行: spawn 子进程，stdin/stdout 通信
超时: 默认 60 秒
返回: { status, result, error, messageForAI }
```

### 3. asynchronous - 异步任务
```
触发: AI 工具调用
执行: 立即返回 requestId，后台处理
回调: POST /plugin-callback/:pluginName/:taskId
超时: 默认 30 分钟
```

### 4. service - 常驻服务
```
协议: direct (内存调用)
生命周期: initialize() → registerApiRoutes() → shutdown()
用途: HTTP 路由、WebSocket 服务
```

### 5. messagePreprocessor - 消息预处理
```
协议: direct
接口: processMessages(messages, config)
顺序: preprocessor_order.json
用途: 图像理解、格式转换
```

### 6. hybridservice - 混合服务
```
能力: 同时具备 service + 工具调用 + 占位符
示例: ChromeBridge (页面信息 + 浏览器控制)
```

## VCP 工具调用协议

```
<<<[TOOL_REQUEST]>>>
maid:「始」Agent署名「末」,
tool_name:「始」PluginName「末」,
command:「始」CommandId「末」,
param:「始」值「末」
<<<[END_TOOL_REQUEST]>>>
```

**串语法** (批量操作):
```
command1:「始」Action1「末」, param1:「始」Value1「末」,
command2:「始」Action2「末」, param2:「始」Value2「末」
```

## 配置级联机制

```
优先级: 插件 config.env > 全局 config.env > Schema 默认值

_getPluginConfig(manifest) {
  for (key in configSchema) {
    if (pluginSpecificEnv[key]) value = pluginSpecificEnv[key]
    else if (globalEnv[key]) value = globalEnv[key]
    else continue
    // 类型转换: integer, boolean, string
  }
}
```

## 关键实现模式

### 占位符生成
```javascript
// 占位符 key: {{VCP{PluginName}}}
buildVCPDescription() {
  for (plugin of plugins) {
    for (cmd of plugin.invocationCommands) {
      description = formatDescription(cmd)
      individualPluginDescriptions.set(`VCP${plugin.name}`, description)
    }
  }
}
```

### 动态折叠协议
```javascript
// 根据 Query 与插件描述的相似度展开内容
{
  vcp_dynamic_fold: true,
  plugin_description: "天气预报插件描述...",
  fold_blocks: [
    { threshold: 0.5, content: "【详尽版】..." },
    { threshold: 0.35, content: "【摘要版】..." },
    { threshold: 0.0, content: "【极简版】..." }
  ]
}
```

### 分布式文件透明化
```
插件读取 file:// → ENOENT →
抛出 FILE_NOT_FOUND_LOCALLY →
FileFetcherServer.fetchFile(url, requestIp) →
WebSocket 请求远程节点 →
返回 Base64 数据 → 重试执行
```

## 设计启示

1. **声明式优于命令式**: Manifest 描述能力，运行时自动编排
2. **协议无关**: stdio 统一所有语言，direct 优化常驻服务
3. **渐进式权限**: static < sync < async < service < hybrid
4. **自适应注入**: 动态折叠根据上下文决定信息密度
