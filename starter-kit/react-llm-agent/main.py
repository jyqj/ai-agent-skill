# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
# main.py -- CLI 入口：接收任务描述，运行 ReAct agent，输出 trace 和结果
from __future__ import annotations

import json
import sys
from pathlib import Path

from agent_runtime import ReactAgent
from models import TaskEnvelope


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: python main.py <task_description> [workspace]", file=sys.stderr)
        print('example: python main.py "Read main.py and add a docstring" .', file=sys.stderr)
        return 2

    goal = argv[1]
    workspace = Path(argv[2]) if len(argv) > 2 else Path.cwd()

    task = TaskEnvelope(
        goal=goal,
        success_criteria=[f"The agent completes: {goal}"],
    )

    agent = ReactAgent(workspace)
    result = agent.run(task)

    # 打印 trace
    print("=== Trace ===")
    for event in result.trace:
        print(f"  [{event.event_type}] {json.dumps(event.payload, ensure_ascii=False)}")

    # 打印最终结果
    print(f"\n=== Result ===")
    print(f"  Goal:    {result.goal}")
    print(f"  Success: {result.success}")
    print(f"  Summary: {result.summary}")

    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
