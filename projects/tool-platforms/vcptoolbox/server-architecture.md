# VCPToolBox Server Architecture

> **Evidence Status** — grounded. 本项目 README 中对 server.js、WebSocketServer.js、KnowledgeBaseManager.js 的整理。

## 核心骨架

```text
server.js
  ├── Plugin.js                # 插件生命周期与 manifest 加载
  ├── WebSocketServer.js       # 分布式节点通信
  └── KnowledgeBaseManager.js  # RAG / 向量索引 / 检索
```

这个文件用于把 README 中已经总结的服务器骨架单独抽成可引用文档。
