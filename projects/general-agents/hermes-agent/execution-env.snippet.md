# 执行环境抽象

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> 来源：`tools/environments/`

## 基类接口

```python
class BaseEnvironment(ABC):
    def __init__(self, cwd: str, timeout: int, env: dict = None):
        self.cwd = cwd
        self.timeout = timeout
        self.env = env or {}

    @abstractmethod
    def execute(self, command: str, cwd: str = "", *,
                timeout: int | None = None,
                stdin_data: str | None = None) -> dict:
        """执行命令，返回 {"output": str, "returncode": int}。"""
        ...

    @abstractmethod
    def cleanup(self):
        """释放后端资源。"""
        ...

    def __del__(self):
        try:
            self.cleanup()
        except Exception:
            pass
```

**洞察**：统一接口屏蔽后端差异。`__del__()` 保证资源自动清理。7 个后端实现同一接口。

---

## 后端切换

```python
def _create_environment(task_id: str) -> BaseEnvironment:
    """根据 TERMINAL_ENV 动态选择后端。"""
    env_type = os.getenv("TERMINAL_ENV", "local")

    if env_type == "local":
        return LocalEnvironment(cwd=os.getcwd(), timeout=120)
    elif env_type == "docker":
        return DockerEnvironment(task_id=task_id, image="hermes-sandbox")
    elif env_type == "ssh":
        return SSHEnvironment(host=os.getenv("SSH_HOST"), user=os.getenv("SSH_USER"))
    elif env_type == "modal":
        return ModalEnvironment(app_name="hermes", timeout=3600)
    elif env_type == "daytona":
        return DaytonaEnvironment(workspace_id=os.getenv("DAYTONA_WORKSPACE"))
    elif env_type == "vercel_sandbox":
        return VercelSandboxEnvironment(timeout=timeout)
    elif env_type == "singularity":
        return SingularityEnvironment(image=os.getenv("SINGULARITY_IMAGE"), cwd=os.getcwd())
    else:
        raise ValueError(f"Unknown terminal environment: {env_type}")
```

**洞察**：运行时切换，无需重启。7 后端按场景分类：local(1) / container-based(Docker, Singularity) / cloud-managed(Modal, Daytona, Vercel) / remote(SSH)。

---

## 后端对比

| 后端 | 场景 | 文件同步 | 持久化 | 权限模型 |
|------|------|---------|--------|---------|
| local | 开发 | N/A | FS | User |
| docker | 测试/隔离 | bind mount | Image layer | root (capped) |
| ssh | 远程机 | SCP/rsync | Machine FS | User |
| modal | serverless | API | Ephemeral | Sandboxed |
| daytona | IDE 集成 | 双向 sync | Container | Sandboxed |
| vercel_sandbox | serverless 部署 | 受限 | Ephemeral | Sandboxed |
| singularity | HPC/cluster | bind mount | Container | User/Group |

---

## 环境变量隔离（Local）

```python
def _build_provider_env_blocklist() -> frozenset:
    """从 provider registry 动态构建阻止列表。"""
    blocked: set[str] = set()
    from hermes_cli.auth import PROVIDER_REGISTRY

    for pconfig in PROVIDER_REGISTRY.values():
        blocked.update(pconfig.api_key_env_vars)
        if pconfig.base_url_env_var:
            blocked.add(pconfig.base_url_env_var)

    return frozenset(blocked)

def _sanitize_subprocess_env(base_env: dict, extra_env: dict = None) -> dict:
    """过滤 Hermes 管理的密钥，支持 opt-in。"""
    sanitized = {}

    for key, value in (base_env or {}).items():
        # _HERMES_FORCE_* 前缀显式传递
        if key.startswith("_HERMES_FORCE_"):
            continue
        # 阻止列表或 passthrough 允许
        if key not in _BLOCKLIST or _is_passthrough(key):
            sanitized[key] = value

    # _HERMES_FORCE_FOO=bar → FOO=bar
    for key, value in (extra_env or {}).items():
        if key.startswith("_HERMES_FORCE_"):
            real_key = key[len("_HERMES_FORCE_"):]
            sanitized[real_key] = value

    return sanitized
```

**洞察**：三层防御：阻止列表（动态）+ `_HERMES_FORCE_*` opt-in + `env_passthrough` 显式允许。

---

## Docker 安全加固

```python
_SECURITY_ARGS = [
    "--cap-drop", "ALL",
    "--cap-add", "DAC_OVERRIDE",      # root 写 bind-mounted 目录
    "--cap-add", "CHOWN",             # pip/npm 需要
    "--cap-add", "FOWNER",
    "--security-opt", "no-new-privileges",
    "--pids-limit", "256",            # 进程数限制
    "--tmpfs", "/tmp:rw,nosuid,size=512m",
    "--tmpfs", "/var/tmp:rw,noexec,nosuid,size=256m",
]

# 持久化 vs 临时
if self._persistent:
    sandbox = get_sandbox_dir() / "docker" / task_id
    self._home_dir = str(sandbox / "home")
    writable_args.extend(["-v", f"{self._home_dir}:/root"])
else:
    writable_args.extend(["--tmpfs", "/workspace:rw,exec,size=10g"])
```

**洞察**：最小权限（drop ALL + add 必需）。tmpfs noexec/nosuid 防止恶意执行。支持持久化或临时模式。

---

## 持久 Shell IPC

```python
def _execute_persistent_locked(self, command: str, cwd: str, timeout: int) -> dict:
    cmd_id = uuid.uuid4().hex[:8]

    # 清空临时文件
    self._send_to_shell(f": > {self._stdout_file}\n: > {self._status_file}\n")

    # 发送包装命令
    ipc_script = f'''
cd {shlex.quote(cwd)}
eval '{escaped_cmd}' > {self._stdout_file} 2>&1
__EC=$?
pwd > {self._cwd_file}
echo {cmd_id}:$__EC > {self._status_file}
'''
    self._send_to_shell(ipc_script)

    # 自适应轮询
    poll_interval = 0.01  # 10ms
    while True:
        status = self._read_file(self._status_file).strip()
        if status.startswith(cmd_id + ":"):
            break
        time.sleep(poll_interval)
        poll_interval = min(poll_interval * 1.5, 0.25)  # max 250ms

    return self._parse_result()
```

**洞察**：文件 IPC 跨本地/SSH/Docker 通用。UUID 命令 ID 确保结果完整性。指数退避减少高频 I/O。

---

## Modal 文件同步

```python
def _push_file_to_sandbox(self, host_path: str, container_path: str) -> bool:
    """仅同步变化的文件（mtime+size 缓存）。"""
    stat = Path(host_path).stat()
    file_key = (stat.st_mtime, stat.st_size)

    if self._synced_files.get(container_path) == file_key:
        return False  # 已同步

    content = Path(host_path).read_bytes()
    b64 = base64.b64encode(content).decode("ascii")
    cmd = f"echo {shlex.quote(b64)} | base64 -d > {shlex.quote(container_path)}"

    async def _write():
        proc = await self._sandbox.exec.aio("bash", "-c", cmd)
        await proc.wait.aio()

    self._worker.run_coroutine(_write(), timeout=15)
    self._synced_files[container_path] = file_key
    return True
```

**洞察**：mtime+size 缓存避免重复上传。base64 + heredoc 绕过 Modal 的文件传输限制。

---

## 代码执行 RPC

```python
# 本地：Unix Domain Socket（高性能）
_UDS_TRANSPORT = '''
def _call(tool_name, args):
    conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    conn.connect(os.environ["HERMES_RPC_SOCKET"])
    request = json.dumps({"tool": tool_name, "args": args}) + "\\n"
    conn.sendall(request.encode())
    return json.loads(conn.recv(65536).decode().strip())
'''

# 远程：文件 RPC（通用）
_FILE_TRANSPORT = '''
def _call(tool_name, args):
    seq = f"{_seq:06d}"
    req_file = f"{_RPC_DIR}/req_{seq}"
    res_file = f"{_RPC_DIR}/res_{seq}"

    # 原子写
    with open(req_file + ".tmp", "w") as f:
        json.dump({"tool": tool_name, "args": args}, f)
    os.rename(req_file + ".tmp", req_file)

    # 轮询等待
    while not os.path.exists(res_file):
        time.sleep(poll_interval)

    return json.loads(open(res_file).read())
'''
```

**洞察**：生成 `hermes_tools.py` 存根，让用户脚本通过 RPC 调用工具。中间结果不进入 LLM 上下文。

---

## Checkpoints v2（新）

### 存储架构

```
# v1: per-directory shadow git repos → 磁盘膨胀（847MB / 47 repos）
# v2: 单一共享 store → 全局对象去重（<200MB）

~/.hermes/checkpoints/
  store/             # 共享 git object DB
  indexes/           # per-project 索引
  metadata/          # 快照元数据
  legacy-<ts>/       # v1 自动迁移的旧仓库
```

### 自动维护

```python
# 配置默认值变更：enabled=False, auto_prune=True
# 新增参数：max_total_size_mb=500, max_file_size_mb=10

def _prune(self):
    """重写 ref 到最后 max_snapshots，运行 git gc --prune=now"""

def _enforce_size_cap(self):
    """超过 max_total_size_mb 时删除最旧快照"""

def _drop_oversize_from_index(self):
    """过滤超过 max_file_size_mb 的单个文件"""
```

### CLI

```bash
hermes checkpoints status    # 当前存储状态
hermes checkpoints list      # 列出所有快照
hermes checkpoints prune     # 手动清理
hermes checkpoints clear     # 清空当前项目
hermes checkpoints clear-legacy  # 清理 v1 遗留
```

### 增强排除列表

```python
DEFAULT_EXCLUDES = [
    "target/", "*.so", "*.dylib", "*.dll",
    "*.mp4", "*.mov", "*.zip", "*.tar.gz",
    ".worktrees/", ".mypy_cache/", ...
]
```

**洞察**：v2 设计的核心是共享 object DB + per-project refs，同项目的多个 worktree 成本接近零。auto_prune 默认开启确保无人工维护。
