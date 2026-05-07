# 9 原子工具 + 动态扩展

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> 核心理念：最小工具集 + code_run 动态扩展

## 工具清单

| 工具 | 功能 | 关键参数 |
|-----|------|---------|
| `code_run` | 执行任意代码 | `code`, `lang`, `timeout` |
| `file_read` | 读取文件 | `path`, `keyword`, `count` |
| `file_write` | 写入文件 | `path`, `content`, `mode` |
| `file_patch` | 块级修改 | `path`, `old_content`, `new_content` |
| `web_scan` | 页面扫描 | `target_url`, `tab_index` |
| `web_execute_js` | JS执行 | `js_code`, `tab_index` |
| `ask_user` | 人机交互 | `question`, `candidates` |
| `update_working_checkpoint` | 工作记忆 | `key_info`, `related_sop` |
| `start_long_term_update` | 长期记忆 | - |

## 工具定义格式 (OpenAI Function Calling)

```json
{
  "type": "function",
  "function": {
    "name": "code_run",
    "description": "执行代码并返回stdout/stderr",
    "parameters": {
      "type": "object",
      "properties": {
        "code": {"type": "string", "description": "要执行的代码"},
        "lang": {"type": "string", "enum": ["python", "bash", "powershell"]},
        "timeout": {"type": "integer", "default": 60}
      },
      "required": ["code"]
    }
  }
}
```

## code_run 核心实现

```python
def run_code_subprocess(code, lang, timeout, cwd, stop_signal):
    '''独立进程执行代码，支持超时和中断'''
    cmd = _build_cmd(lang, code, cwd)

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        bufsize=0, cwd=cwd
    )

    # 独立线程读取流
    t = threading.Thread(target=stream_reader, args=(process, full_stdout), daemon=True)
    t.start()

    while t.is_alive():
        if time.time() - start_t > timeout or len(stop_signal) > 0:
            process.kill()
            full_stdout.append("\n[Timeout/Stopped]")
            break
        time.sleep(1)

    return ''.join(full_stdout)
```

## 动态扩展机制

### 1. code_run_header.py 自动注入

```python
# 每次 code_run 前自动 prepend
import sys, os
sys.path.insert(0, '/path/to/memory')
from helper import *  # 工具函数
```

### 2. _inline_eval 进程内执行

```python
# 自主任务模式：在 agent 进程内 eval
if args.get('_inline_eval'):
    exec(code, {'handler': self, 'parent': self.parent})
```

### 3. tool_before/after_callback 扩展点

```python
class CustomHandler(GenericAgentHandler):
    def tool_before_callback(self, tool_name, args, response):
        if tool_name == 'code_run':
            args['code'] = inject_safety_checks(args['code'])
        yield from super().tool_before_callback(...)
```

## file_patch 幂等性保证

```python
def file_patch(path, old_content, new_content):
    with open(path, 'r') as f:
        full_text = f.read()

    count = full_text.count(old_content)
    if count == 0:
        return {"status": "error", "msg": "未找到匹配"}
    if count > 1:
        return {"status": "error", "msg": f"找到 {count} 处匹配，无法确定唯一位置"}

    updated = full_text.replace(old_content, new_content, 1)
    with open(path, 'w') as f:
        f.write(updated)
    return {"status": "success"}
```

## ask_user 中断机制

```python
def do_ask_user(self, args, response):
    question = args.get("question", "请提供输入：")
    candidates = args.get("candidates", [])

    yield "Waiting for your answer ...\n"

    return StepOutcome(
        {"status": "INTERRUPT", "intent": "HUMAN_INTERVENTION",
         "data": {"question": question, "candidates": candidates}},
        next_prompt="",      # 空 prompt
        should_exit=True     # 强制退出循环
    )
```
