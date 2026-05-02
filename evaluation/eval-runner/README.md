# Eval Runner

> **Evidence Status** — synthesized. `evaluation/eval-runner-spec.md` 与 `evaluation/fixtures/`；本目录提供一个最小可执行骨架，用于把 fixture、mock tool、trace comparator 连接起来。

## 1. 目标

这个 runner 不是替代真实 Agent，而是提供三件事：

```text
1. 读取 YAML fixture（优先 PyYAML；无依赖环境使用内置简易解析器）
2. 通过 AgentAdapter 生成 trace（默认使用 BaselineAdapter 合成基线 trace）
3. 根据 success_criteria 和 invariants 输出 pass/fail
```

## 2. 运行

```bash
python evaluation/eval-runner/runner.py evaluation/fixtures
python -m unittest discover -s evaluation/eval-runner/tests -p 'test_*.py'
```

## 3. 当前覆盖

- effect verification
- browser checkout / GUI grounding
- MCP prompt injection / confused deputy
- OCR confidence
- research citation / conflict / freshness
- memory poisoning

## 4. 扩展点

| 文件 | 作用 |
|---|---|
| `runner.py` | CLI 入口和 fixture 执行 |
| `mock_tools.py` | Mock tool registry 和 world state |
| `trace_comparator.py` | Trace 断言和不变性检查 |
| `world_fixture.py` | 读取和更新 world state fixture |
| `tests/` | runner 自身的最小回归测试 |

### AgentAdapter 接口

`runner.py` 通过 `AgentAdapter` 抽象类支持不同的 trace 来源：

```python
from abc import ABC, abstractmethod

class AgentAdapter(ABC):
    @abstractmethod
    def run(self, case: dict, world: WorldFixture) -> list[dict]:
        """Execute case against world and return trace events."""
```

默认使用 `BaselineAdapter`（调用 `generate_baseline_trace()` 生成合成基线 trace）。

接入真实 Agent 时，实现自定义 adapter 并传给 `run_case()`：

```python
from runner import AgentAdapter, run_case
from world_fixture import WorldFixture

class MyAgentAdapter(AgentAdapter):
    def run(self, case: dict, world: WorldFixture) -> list[dict]:
        # 调用真实 agent，收集 trace events
        agent = MyAgent(tools=..., world=world)
        return agent.execute(case["input_event"])

result = run_case(Path("fixture.yaml"), adapter=MyAgentAdapter())
```

不传 adapter 时，`run_case()` 自动使用 `BaselineAdapter`，保持向后兼容。


## 5. 无依赖运行

`runner.py` 会优先使用 PyYAML；如果环境没有安装 PyYAML，会使用内置 YAML 解析器。内置解析器覆盖本仓库 fixture 所需的 mapping、list、string、number、bool 和 nested block，便于在最小 Python 环境中运行 eval。
