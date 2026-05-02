# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict


ToolFn = Callable[[Path, Dict[str, Any]], Dict[str, Any]]


@dataclass
class ToolRegistry:
    tools: Dict[str, ToolFn] = field(default_factory=dict)

    def register(self, name: str, fn: ToolFn) -> None:
        self.tools[name] = fn

    def call(self, workspace: Path, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self.tools:
            raise KeyError(f"unknown tool: {name}")
        return self.tools[name](workspace, args)



def read_file(workspace: Path, args: Dict[str, Any]) -> Dict[str, Any]:
    path = workspace / str(args["path"])
    text = path.read_text(encoding="utf-8")
    return {"status": "success", "path": str(path), "text": text}



def edit_file(workspace: Path, args: Dict[str, Any]) -> Dict[str, Any]:
    path = workspace / str(args["path"])
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    old_text = str(args.get("old_text", ""))
    new_text = str(args.get("new_text", ""))
    mode = str(args.get("mode", "replace"))
    if mode == "replace":
        updated = text.replace(old_text, new_text)
    elif mode == "append":
        updated = text + new_text
    else:
        raise ValueError(f"unsupported edit mode: {mode}")
    path.write_text(updated, encoding="utf-8")
    return {"status": "success", "path": str(path), "changed": updated != text}



def run_test(workspace: Path, args: Dict[str, Any]) -> Dict[str, Any]:
    command = str(args["command"])
    completed = subprocess.run(
        command,
        cwd=workspace,
        shell=True,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "status": "success",
        "command": command,
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }



def default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register("read_file", read_file)
    registry.register("edit_file", edit_file)
    registry.register("run_test", run_test)
    return registry
