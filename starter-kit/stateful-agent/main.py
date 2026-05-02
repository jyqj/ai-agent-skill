# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
from __future__ import annotations

import json
import sys
from pathlib import Path

from agent_runtime import StatefulAgent, task_from_dict
from state_store import StateStore


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: python main.py <task.json> [workspace] [--no-resume]", file=sys.stderr)
        return 2
    task_path = Path(argv[1])
    workspace = Path(argv[2]) if len(argv) > 2 and not argv[2].startswith("--") else task_path.parent
    resume = "--no-resume" not in argv

    payload = json.loads(task_path.read_text(encoding="utf-8"))
    task = task_from_dict(payload)

    store = StateStore(workspace / ".checkpoints")
    agent = StatefulAgent(workspace, store)
    result = agent.run(task, resume=resume)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
