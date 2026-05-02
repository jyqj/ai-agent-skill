# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Tuple

from models import VerificationSpec


def verify(workspace: Path, spec: VerificationSpec, last_result: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    kind = spec.kind
    if kind == "contains":
        if not spec.path or spec.value is None:
            raise ValueError("contains verification requires path and value")
        path = workspace / spec.path
        text = path.read_text(encoding="utf-8")
        ok = spec.value in text
        return ok, {"path": str(path), "contains": spec.value, "matched": ok}
    if kind == "file_exists":
        if not spec.path:
            raise ValueError("file_exists verification requires path")
        path = workspace / spec.path
        ok = path.exists()
        return ok, {"path": str(path), "exists": ok}
    if kind == "exit_code":
        expected = 0 if spec.exit_code is None else spec.exit_code
        actual = int(last_result.get("exit_code", -1))
        ok = actual == expected
        return ok, {"expected_exit_code": expected, "actual_exit_code": actual}
    if kind == "world_state_match":
        state = last_result.get("state", {})
        expected_key = spec.path or ""
        expected_value = spec.value
        actual_value = str(state.get(expected_key, ""))
        ok = actual_value == expected_value
        return ok, {"key": expected_key, "expected": expected_value, "actual": actual_value}
    raise ValueError(f"unsupported verification kind: {kind}")
