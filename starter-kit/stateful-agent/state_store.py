# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from models import TaskCheckpoint


class StateStore:
    """Persist and restore TaskCheckpoint to/from disk."""

    def __init__(self, store_dir: Path) -> None:
        self.store_dir = store_dir
        self.store_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, task_id: str) -> Path:
        return self.store_dir / f"{task_id}.checkpoint.json"

    def save(self, task_id: str, checkpoint: TaskCheckpoint) -> Path:
        path = self._path(task_id)
        path.write_text(json.dumps(checkpoint.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def load(self, task_id: str) -> Optional[TaskCheckpoint]:
        path = self._path(task_id)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return TaskCheckpoint.from_dict(data)

    def delete(self, task_id: str) -> None:
        path = self._path(task_id)
        if path.exists():
            path.unlink()
