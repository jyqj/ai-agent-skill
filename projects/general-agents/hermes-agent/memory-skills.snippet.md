# 记忆与技能系统

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> 来源：`tools/memory_tool.py`, `tools/skills_tool.py`, `hermes_state.py`

## 冻快照模式

```python
class MemoryManager:
    def load_from_disk(self):
        self.memory_entries = self._read_file(MEMORY_MD)
        self.user_entries = self._read_file(USER_MD)

        # 冻结快照用于系统提示注入
        self._system_prompt_snapshot = {
            'memory': self._render_block('memory', self.memory_entries),
            'user': self._render_block('user', self.user_entries),
        }

    def format_for_system_prompt(self, target: str) -> Optional[str]:
        # 返回启动时的快照，不是实时状态
        return self._system_prompt_snapshot.get(target, '')

    def add(self, target: str, content: str) -> dict:
        # 实时写磁盘，但不改变系统提示
        self._write_file(target, self._entries[target] + [content])
        return {"success": True, "note": "Will be visible in next session"}
```

**洞察**：系统提示冻结保持前缀缓存热度。Mid-session 写入立即持久化，但下会话才注入系统提示。

---

## 原子文件持久化

```python
def _write_file(path: Path, entries: List[str]):
    content = "\n§\n".join(entries)  # § 作为分隔符

    # 写临时文件 → fsync → 原子重命名
    fd, tmp_path = tempfile.mkstemp(dir=str(path.parent), suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())  # 确保磁盘持久化
        os.replace(tmp_path, str(path))  # 同一文件系统上原子
    except BaseException:
        os.unlink(tmp_path)
        raise
```

**洞察**：避免 `open('w')` 的 truncate 竞态。并发读者总是看到完整旧或完整新文件。

---

## 威胁扫描

```python
_MEMORY_THREAT_PATTERNS = [
    (r'ignore\s+(previous|all|above)\s+instructions', 'prompt_injection'),
    (r'you\s+are\s+now\s+', 'role_hijack'),
    (r'do\s+not\s+tell\s+the\s+user', 'deception'),
    (r'curl\s+[^\n]*\$\{?\w*(KEY|TOKEN|SECRET)', 'exfil_curl'),
    (r'authorized_keys', 'ssh_backdoor'),
]

_INVISIBLE_CHARS = {'\u200b', '\u200c', '\u200d', '\u2060', '\ufeff'}

def _scan_memory_content(content: str) -> Optional[str]:
    # 检测零宽字符
    for char in _INVISIBLE_CHARS:
        if char in content:
            return f'Blocked: invisible unicode U+{ord(char):04X}'

    # 检测威胁模式
    for pattern, pid in _MEMORY_THREAT_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return f'Blocked: threat pattern "{pid}"'

    return None  # 安全
```

**洞察**：记忆写入前全扫描，防止通过 memory 工具植入恶意指令或隐藏字符。

---

## FTS5 会话搜索

```python
def search_messages(self, query: str, limit: int = 50) -> List[Dict]:
    query = self._sanitize_fts5_query(query)

    sql = '''
    SELECT m.id, m.session_id, m.role,
           snippet(messages_fts, 0, '>>>', '<<<', '...', 40) AS snippet,
           m.content, m.timestamp,
           s.source, s.model, s.started_at
    FROM messages_fts
    JOIN messages m ON m.id = messages_fts.rowid
    JOIN sessions s ON s.id = m.session_id
    WHERE messages_fts MATCH ?
    ORDER BY rank  -- BM25 排序
    LIMIT ? OFFSET ?
    '''

    # 加载前后 1 条消息提供上下文
    for match in matches:
        context = self._get_surrounding_messages(match['id'])
        match['context'] = context

    return matches
```

**洞察**：FTS5 虚拟表自动通过触发器同步。BM25 排序内置。snippet() 返回周围上下文摘要。

---

## 技能渐进式信息披露

```python
def skills_list() -> str:
    """Tier 1: 仅元数据（快速，低 token）。"""
    skills = []
    for skill_md in skills_dir.rglob('SKILL.md'):
        frontmatter, _ = _parse_frontmatter(skill_md.read_text())
        skills.append({
            'name': frontmatter.get('name'),
            'description': frontmatter.get('description'),
            'category': _get_category_from_path(skill_md),
        })
    return json.dumps(skills)

def skill_view(name: str, file_path: str = None) -> str:
    """Tier 2/3: 按需加载完整内容或支持文件。"""
    skill_dir = _find_skill_dir(name)

    if file_path:
        # Tier 3: 支持文件（references/templates/assets）
        return (skill_dir / file_path).read_text()
    else:
        # Tier 2: 完整 SKILL.md
        return (skill_dir / 'SKILL.md').read_text()
```

**洞察**：Agent 无需一次性加载所有技能。元数据列表 → 完整内容 → 支持文件，逐层展开。

---

## 技能 Frontmatter

```yaml
---
name: reverse-engineering  # ≤64 chars
description: Web service reverse engineering and automation  # ≤1024 chars
version: 1.0.0
platforms: [macos, linux]  # 平台限制
required_environment_variables:
  - name: CAPSOLVER_API_KEY
    prompt: "CAPSolver API key"
    required_for: captcha_solving
setup:
  help: "Configure API keys for reverse engineering tools"
  collect_secrets:
    - env_var: CAPSOLVER_API_KEY
      prompt: "Enter CAPSolver API key"
      secret: true
metadata:
  hermes:
    tags: [automation, security]
    related_skills: [browser-use]
---
```

**洞察**：Frontmatter 声明依赖，加载时自动检测缺失并交互收集。兼容 agentskills.io 开放标准。

---

## 学习循环（隐式）

```
Hermes 无显式 RL 循环。学习来自三个通道：

1. 用户纠正 → memory_tool(add, "user", "preference...")
   - "记住我喜欢简洁回复" → 写 USER.md

2. 发现的方法 → skill_view() + 存入 ~/.hermes/skills/
   - 复杂任务后建议创建 skill

3. 过去会话 → session_search(query)
   - 搜索 FTS5 → Gemini Flash 总结 → 返回相关历史
```

**洞察**：学习由 Agent 主动决策触发，而非外部反馈循环。记忆和技能是持久化的"经验结晶"。
