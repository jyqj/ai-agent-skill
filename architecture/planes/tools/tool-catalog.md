# Tool Catalog

> **Evidence Status** — synthesized. common coding/research/workflow agent tool surfaces; each product should prune aggressively。

## 1. Coding Agent

| 工具 | 风险 | 说明 |
|---|---|---|
| read_file/list_files | safe | 读取工作区 |
| search_code/search_text | safe | 代码和文本检索 |
| edit_file/apply_patch | check | 需要 diff 和回滚 |
| run_tests | safe/check | 资源限制和超时 |
| shell | check/approval | 命令策略决定风险 |
| git_diff/git_status | safe | 验证和交付证据 |
| git_commit/git_push | approval | 外部状态变化 |

## 2. Research Agent

| 工具 | 风险 | 说明 |
|---|---|---|
| web_search | safe | 需要来源记录 |
| open_url/read_pdf | safe | 需要引用和截断说明 |
| citation_manager | check | 结构化引用 |
| note_writer | check | 生成研究笔记 |
| report_export | check | 输出文档 |

## 3. Enterprise Workflow Agent

| 工具 | 风险 | 说明 |
|---|---|---|
| crm_lookup | safe/check | 权限和审计 |
| ticket_create/update | check | 可追踪副作用 |
| email_draft | check | 草稿优先 |
| email_send | approval | 外部沟通 |
| calendar_schedule | check/approval | 邀请外部人员时审批 |
| cloud_resource_update | approval | 成本和安全风险 |

## 4. Memory Agent

| 工具 | 风险 | 说明 |
|---|---|---|
| memory_search | safe | 检索长期记忆 |
| memory_write | check | 需要 provenance 和用户可撤销 |
| memory_update | check | 保留历史 |
| memory_forget | approval | 不可逆或影响大时确认 |
| memory_audit | safe | 展示记忆来源和用途 |

## 5. 最小工具面

```text
Read → Search → Draft → Edit/Act → Verify → Report
```

不要一开始就暴露“大而全”的工具。先给 Agent 小而稳的工具，再逐步增加高风险能力。
