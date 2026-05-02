# Execution Environment Abstraction


> **Evidence Status** — synthesized. 通用运行时模块来自多个参考项目的统一抽象。

## 问题

Agent 需要在多种环境中执行命令：
- 本地 shell
- Docker 容器
- SSH 远程机器
- Serverless 沙箱（Modal/Daytona）

如何统一接口、切换后端？

## 解法

**策略模式 + 抽象基类**：

```python
class BaseEnvironment(ABC):
    def __init__(self, cwd: str, timeout: int, env: dict = None):
        self.cwd = cwd
        self.timeout = timeout
        self.env = env or {}

    @abstractmethod
    def execute(self, command: str, cwd: str = "", *,
                timeout: int = None, stdin_data: str = None) -> dict:
        """返回 {"output": str, "returncode": int}"""
        ...

    @abstractmethod
    def cleanup(self):
        """释放后端资源"""
        ...

    def __del__(self):
        try:
            self.cleanup()
        except Exception:
            pass
```

## 后端切换

```python
def _create_environment(task_id: str) -> BaseEnvironment:
    env_type = os.getenv("TERMINAL_ENV", "local")

    if env_type == "local":
        return LocalEnvironment(cwd=os.getcwd())
    elif env_type == "docker":
        return DockerEnvironment(task_id=task_id, image="sandbox")
    elif env_type == "ssh":
        return SSHEnvironment(host=os.getenv("SSH_HOST"))
    elif env_type == "modal":
        return ModalEnvironment(app_name="agent")
    else:
        raise ValueError(f"Unknown: {env_type}")
```

## 关键实现技巧

### 1. 环境变量隔离（Local）

```python
_BLOCKLIST = frozenset(["OPENAI_API_KEY", "ANTHROPIC_API_KEY", ...])

def _sanitize_env(base_env: dict) -> dict:
    return {k: v for k, v in base_env.items()
            if k not in _BLOCKLIST or k in _PASSTHROUGH}
```

### 2. 安全加固（Docker）

```python
_SECURITY_ARGS = [
    "--cap-drop", "ALL",
    "--cap-add", "DAC_OVERRIDE",  # 最小权限
    "--security-opt", "no-new-privileges",
    "--pids-limit", "256",
    "--tmpfs", "/tmp:rw,nosuid,size=512m",
]
```

### 3. 持久 Shell（Local/SSH）

```python
def _execute_persistent(self, command: str) -> dict:
    cmd_id = uuid.uuid4().hex[:8]
    ipc_script = f'''
cd {cwd}
eval '{command}' > {stdout_file} 2>&1
echo {cmd_id}:$? > {status_file}
'''
    self._send_to_shell(ipc_script)

    # 自适应轮询
    poll_interval = 0.01
    while not self._result_ready(cmd_id):
        time.sleep(poll_interval)
        poll_interval = min(poll_interval * 1.5, 0.25)

    return self._parse_result()
```

### 4. 文件同步缓存（Modal）

```python
def _push_file(self, host_path: str, container_path: str):
    stat = Path(host_path).stat()
    file_key = (stat.st_mtime, stat.st_size)

    if self._synced_files.get(container_path) == file_key:
        return  # 已同步

    # Base64 编码传输
    b64 = base64.b64encode(Path(host_path).read_bytes()).decode()
    self._sandbox.exec(f"echo {b64} | base64 -d > {container_path}")
    self._synced_files[container_path] = file_key
```

## 权衡

| 优点 | 缺点 |
|-----|------|
| 运行时切换后端 | 每个后端有不同限制 |
| 统一接口 | 抽象泄漏（性能、功能差异） |
| 资源自动清理 | cleanup 可能失败 |

## 适用场景

- 多环境 Agent（开发/测试/生产）
- 沙箱执行（安全隔离）
- Serverless Agent（按需休眠/唤醒）

## 来源

Hermes Agent `tools/environments/`
