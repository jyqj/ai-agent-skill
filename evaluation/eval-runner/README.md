# Eval Runner

> **Evidence Status** — synthesized. `evaluation/eval-runner-spec.md` 与 `evaluation/fixtures/`；本目录提供一个最小可执行骨架，用于把 fixture、mock tool、trace comparator 连接起来。

> **定位**：本 Runner 是评估流程的参考骨架和格式规范，不是开箱即用的生产评估工具。它定义了 trace → fixture → scoring 的标准流程和数据契约，并提供基于合成 baseline trace 的参考实现。默认 `BaselineAdapter` 生成确定性合成 trace 用于验证评估管道本身的正确性；接入真实 Agent 需实现自定义 `AgentAdapter`。

## 1. 目标

这个 runner 不是替代真实 Agent，而是提供三件事：

```text
1. 读取 YAML fixture（优先 PyYAML；无依赖环境使用内置简易解析器）
2. 通过 AgentAdapter 生成 trace（默认使用 BaselineAdapter 合成基线 trace）
3. 根据 success_criteria 和 invariants 输出 pass/fail
```

## 2. 运行

```bash
# 以下命令可在本仓库根目录执行，运行的是合成 baseline trace 而非真实 Agent。
# 用于验证评估管道（fixture 解析 → trace 生成 → criteria/invariant 检查）本身是否正常工作。
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
| `runner.py` | CLI 入口和 fixture 执行（当前为参考实现，含 YAML 解析、baseline trace 合成、AgentAdapter 抽象） |
| `mock_tools.py` | Mock tool registry 和 world state（提供 CRM / browser 等场景的 mock 工具） |
| `trace_comparator.py` | Trace 断言和不变性检查（含结构不变量、合理性检查、字符串/结构化 criteria 匹配） |
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


## 5. Real Candidate Trace Adapter Contract

当前默认 `BaselineAdapter` 只证明评估管道可运行，不证明真实 Agent 能力。接入真实 Agent 时，adapter 至少要满足：

| 要求 | 说明 |
|---|---|
| trace events | 返回 observe / decide / tool_call / execution_result / effect_record / final 等关键事件 |
| stable IDs | 每个 task、tool_call、effect、artifact 有稳定 ID，便于断言 |
| world fixture binding | 工具读写必须落到 fixture 或可控 mock world，不能只返回自然语言 |
| policy trace | approval / deny / sandbox / retry 必须显式记录 |
| artifact refs | 大输出只传 ref，保留可回读路径 |
| honest status | `verified / failed / partially_verified / blocked / pending / unverifiable_by_agent` 不得压成 success/fail |

接入真实 Agent 后，结论应明确标注证据层级：

```text
L1 harness smoke test      # synthetic baseline，当前默认
L2 real trace replay       # 真实 Agent trace，受控工具/fixture
L3 world-effect eval       # 真实或强 mock world 的外部效果验证
```


## 5. 无依赖运行

`runner.py` 会优先使用 PyYAML；如果环境没有安装 PyYAML，会使用内置 YAML 解析器。内置解析器覆盖本仓库 fixture 所需的 mapping、list、string、number、bool 和 nested block，便于在最小 Python 环境中运行 eval。
