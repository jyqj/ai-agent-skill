# 自我进化机制

> **参考性**：以下代码片段只用于说明架构模式或源码观察点，不是完整实现；复制到项目中前需按真实接口、安全、测试和运维要求重写。


> **Evidence Status** — grounded. 本目录下的项目分析、源码片段或专题笔记。

> 核心理念：**能力不预设，靠进化获得**

## 进化流程图

```
[新任务]
    ↓
[自主摸索] (安装依赖、编写脚本、调试验证)
    ↓
[执行成功]
    ↓
[调用 start_long_term_update]
    ↓
[分类信息] → L2 (事实) / L3 (SOP) / L1 (索引)
    ↓
[file_patch 更新记忆层]
    ↓
[下次同类任务]
    ↓
[skill_search 召回] → 直接执行
```

## 进化前后对比

| 你说的话 | 第一次 Agent 做了什么 | 之后每次 |
|---------|---------------------|---------|
| "监控股票并提醒我" | 安装 mootdx → 构建选股流程 → 配置定时 → 保存 Skill | 一句话启动 |
| "用 Gmail 发文件" | 配置 OAuth → 编写发送脚本 → 保存 Skill | 直接可用 |
| "读取微信消息" | 安装依赖 → 逆向数据库 → 写读取脚本 → 保存 Skill | 一句话调用 |

## skill_search 集成

```python
# memory/skill_search/skill_search/engine.py
class SkillSearchEngine:
    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        '''语义匹配，返回相关 Skill'''
        # 远端 API (105K+ 技能库)
        response = requests.post(API_URL, json={"query": query, "top_k": top_k})
        return [SearchResult(**r) for r in response.json()]

@dataclass
class SearchResult:
    skill_name: str
    description: str
    file_path: str      # SOP 或脚本路径
    confidence: float
```

## 记忆固化触发

```python
def do_start_long_term_update(self, args, response):
    '''Agent 自主判断是否触发'''

    # 1. 注入现有记忆
    result = get_global_memory()

    # 2. 注入 L0 指导
    if os.path.exists('./memory/memory_management_sop.md'):
        result = file_read('./memory/memory_management_sop.md')

    # 3. 返回结算 prompt
    prompt = '''### [总结提炼经验]
    提取【事实验证成功且长期有效】的信息：
    - **环境事实** → file_patch 更新 L2 + 同步 L1
    - **复杂任务经验** → L3 精简 SOP（仅记核心坑点）

    禁止：临时变量、推理过程、未验证信息、通用常识
    '''
    return StepOutcome(result, next_prompt=prompt)
```

## L3 SOP 格式示例

```markdown
# tmwebdriver_sop.md

## 前置条件
- Chrome 已安装
- TMWebDriver CDP 桥接已配置

## 典型坑点
1. 文件上传需要用 input[type=file].sendKeys()，不能用 click()
2. iframe 内元素需要先 switchTo().frame()
3. 动态加载元素需要显式等待

## 常用代码
```python
# 文件上传
driver.find_element("css selector", "input[type=file]").send_keys(file_path)
```
```

## 权限边界

```python
# 自主行动框架 (autonomous_operation_sop)
PERMISSIONS = {
    'read_only': True,           # 只读操作无需审批
    'write_in_cwd': True,        # cwd 内写操作无需审批
    'modify_L1_L2_L3': 'pending', # 记忆层修改需待审
    'external_api': 'ask_user',   # 外部 API 需确认
}
```

## 多 Agent 协作（新）

### Agent BBS 服务器

```python
# assets/agent_bbs.py — FastAPI 轻量级实现
# 多板块支持（boards.json 热重载）
# API Key 中间件权限控制
# 文件上传支持 + 简易 HTML UI
# 启动：uvicorn agent_bbs:app --port 58800
```

### Team Worker 框架

```python
# reflect/agent_team_worker.py
# 周期性轮询 BBS 接任务
# 自主注册名字 + 长期记忆关键信息
# 120 秒冷却窗口（防止 on_done 后立即重复接单）
# BBS 上交互协调（异步任务协作）
```

**协作模式**：

```
Agent BBS (FastAPI)
  ├─ Board 1: 任务发布
  ├─ Board 2: 结果回传
  └─ Board N: 自由交流
      ↕
Team Worker A ←→ Team Worker B ←→ Team Worker C
  (轮询接单)      (轮询接单)      (轮询接单)
  (冷却 120s)     (冷却 120s)     (冷却 120s)
```

**战略意义**：从 V1.0 单实例 + 本地技能树，演进到 V1.1 Agent BBS + Team Worker + 分布式技能库。

## Langfuse 可观测性（新）

```python
# plugins/langfuse_tracing.py — Monkey-patch 无侵入集成
# 三层跟踪：
#   outer trace (agent_runner_loop 级)
#   generation span (llm.chat, input/output + usage)
#   tool span (tool_before/after callbacks)
# 支持 Cache Hit 统计 + Output Tokens 准确计数
# 启用：在 mykey.py 中添加 langfuse_config
```

## 进化指标

用几周后的典型结果：
- **Skill 数量**：从 0 → 50+
- **平均任务轮次**：从 10+ → 2-3
- **重复任务耗时**：从分钟级 → 秒级

---

## Plan Mode 五阶段（第二轮审计补充）

复杂任务触发 Plan Mode，将自由推理约束为五阶段流水线：

```
探索(Explore) → 规划(Plan) → 执行(Execute) → 验证(Verify) → 修复(Fix)
```

- **探索**：skill_search + 文件扫描 + 环境检测，禁止修改
- **规划**：输出编号步骤计划，每步对应具体工具调用
- **执行**：按计划逐步执行，偏离时回退到规划
- **验证**：运行测试/检查输出，与预期比对
- **修复**：验证失败时定向修复，最多 3 轮后升级为 ask_user

阶段转换由 system prompt 中的状态机指令驱动，Agent 在响应中声明当前阶段。

---

## Subagent 文件 IO 协议（第二轮审计补充）

主 Agent 可通过 `run_subagent` 工具启动独立子进程，进程间通过文件系统通信：

```python
# 协议目录结构
subagent_dir/
  input.txt      # 主 Agent 写入任务描述
  output.txt     # Subagent 写入执行结果
  reply.txt      # Subagent 需要主 Agent 介入时写入问题
  status.txt     # running / done / need_help / failed
```

Subagent 是完整的 agent_loop 实例（独立进程、独立上下文窗口），共享同一套记忆层但拥有独立工作记忆。
主 Agent 轮询 `status.txt`，发现 `need_help` 时读取 `reply.txt` 并写回 `input.txt`。
**设计价值**：突破单上下文窗口限制，支持并行长任务。

---

## Supervisor Mode 监察者模式（第二轮审计补充）

在 Subagent 协议之上，Supervisor Mode 提供更高层的编排：

- 主 Agent 切换为 Supervisor 角色，不直接执行工具，只分配任务给 Subagent
- 每轮审查所有活跃 Subagent 的 status/output，决定：继续等待 / 介入指导 / 终止并接管
- 超时或连续失败的 Subagent 被终止，任务回收到 Supervisor 队列
- Supervisor 自身也受 Plan Mode 约束，先规划任务分解再分发

---

## Reflect 事件驱动框架（第二轮审计补充）

`reflect/` 目录实现事件驱动的自省机制，核心是 `check() → prompt` 反射器模式：

```python
class BaseReflector:
    def check(self, context) -> Optional[str]:
        """检查条件，返回反射 prompt 或 None（无需反射）"""
        ...
```

三个内置反射器：
1. **LoopDetector**：检测连续 N 轮相同工具调用 + 相同失败，注入 "你正在重复失败，换一种方法"
2. **GoalDriftDetector**：比对当前行为与原始任务描述的语义距离，超阈值时注入 "回到原始目标"
3. **ResourceMonitor**：检测 token 消耗 / 轮次 / 时间，接近限制时注入 "资源紧张，精简行动"

反射器在 `turn_end_callback` 中依次执行，命中的 prompt 追加到下轮消息。
