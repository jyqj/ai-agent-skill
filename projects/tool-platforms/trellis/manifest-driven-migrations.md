# Manifest-Driven Migrations

> **Evidence Status** — grounded. Trellis migrations/ 源码分析。

## 设计

版本升级用 JSON manifest 文件声明需要执行的文件操作和配置变更，而不是写命令式迁移脚本。

## Manifest 格式

```json
{
  "version": "0.5.8",
  "migrations": [
    { "type": "rename", "from": "old-path", "to": "new-path" },
    { "type": "safe-file-delete", "path": "deprecated-file" }
  ],
  "configSectionsAdded": [
    { "file": ".trellis/config.yaml", "sentinel": "codex:", "sectionHeading": "Codex config" }
  ]
}
```

## 应用流程

1. 读取项目当前版本
2. 收集从当前版本到目标版本的所有 manifest
3. 按序执行 file renames / deletes
4. 对每个 configSectionsAdded：检查 sentinel 是否已存在，不存在则从模板提取并追加
5. 写入平台模板
6. 更新 .trellis/.version

## 优势

- 声明式：每个迁移操作可追溯
- 幂等性：sentinel 检查防止重复追加
- 可审计：manifest 文件本身就是变更日志
