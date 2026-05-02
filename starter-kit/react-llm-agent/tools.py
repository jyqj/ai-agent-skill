# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
# tools.py -- 示例工具集与注册表，提供 JSON Schema 供 LLM tool_use
from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List

ToolFn = Callable[[Path, Dict[str, Any]], Dict[str, Any]]


@dataclass
class ToolDef:
    name: str
    description: str
    parameters: Dict[str, Any]
    fn: ToolFn

@dataclass
class ToolRegistry:
    _tools: Dict[str, ToolDef] = field(default_factory=dict)

    def register(self, tool_def: ToolDef) -> None:
        self._tools[tool_def.name] = tool_def

    def call(self, workspace: Path, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self._tools:
            raise KeyError(f"unknown tool: {name}")
        return self._tools[name].fn(workspace, args)

    def schemas_for_llm(self) -> List[Dict[str, Any]]:
        """生成 Anthropic tool_use 格式的 schema 列表。"""
        return [
            {
                "name": td.name,
                "description": td.description,
                "input_schema": td.parameters,
            }
            for td in self._tools.values()
        ]


def read_file(workspace: Path, args: Dict[str, Any]) -> Dict[str, Any]:
    path = workspace / str(args["path"])
    if not path.exists():
        return {"status": "error", "error": f"file not found: {path}"}
    text = path.read_text(encoding="utf-8")
    return {"status": "success", "path": str(path), "text": text}


def edit_file(workspace: Path, args: Dict[str, Any]) -> Dict[str, Any]:
    path = workspace / str(args["path"])
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    old_text = str(args.get("old_text", ""))
    new_text = str(args.get("new_text", ""))
    if args.get("mode") == "append":
        updated = text + new_text
    else:
        updated = text.replace(old_text, new_text)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(updated, encoding="utf-8")
    return {"status": "success", "path": str(path), "changed": updated != text}


def run_command(workspace: Path, args: Dict[str, Any]) -> Dict[str, Any]:
    command = str(args["command"])
    completed = subprocess.run(
        command, cwd=workspace, shell=True,
        capture_output=True, text=True, check=False,
    )
    return {
        "status": "success" if completed.returncode == 0 else "error",
        "command": command,
        "exit_code": completed.returncode,
        "stdout": completed.stdout[:4000],
        "stderr": completed.stderr[:2000],
    }


def default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(ToolDef("read_file", "Read a file relative to workspace.",
        {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}, read_file))
    registry.register(ToolDef("edit_file", "Edit a file: replace old_text with new_text, or append.",
        {"type": "object", "properties": {
            "path": {"type": "string"}, "old_text": {"type": "string"},
            "new_text": {"type": "string"}, "mode": {"type": "string", "enum": ["replace", "append"]},
        }, "required": ["path", "new_text"]}, edit_file))
    registry.register(ToolDef("run_command", "Run a shell command in the workspace.",
        {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}, run_command))
    return registry
