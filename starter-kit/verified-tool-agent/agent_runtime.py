# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from effects import verify
from models import ActionSpec, EffectRecord, FailureRecord, RunResult, TaskEnvelope, TraceEvent
from tools import ToolRegistry, default_registry


class VerifiedToolAgent:
    def __init__(self, workspace: Path, registry: ToolRegistry | None = None) -> None:
        self.workspace = workspace
        self.registry = registry or default_registry()

    def _failure(
        self,
        *,
        phase: str,
        category: str,
        message: str,
        recovery_action: str,
        evidence: Dict[str, Any] | None = None,
        severity: str = "medium",
    ) -> FailureRecord:
        return FailureRecord(
            phase=phase,
            category=category,
            severity=severity,
            message=message,
            recovery_action=recovery_action,
            evidence=evidence or {},
        )

    def run(self, task: TaskEnvelope) -> RunResult:
        trace: List[TraceEvent] = []
        effects: List[EffectRecord] = []
        failures: List[FailureRecord] = []
        trace.append(TraceEvent("intake", {"goal": task.goal, "action_count": len(task.actions)}))
        trace.append(TraceEvent("represent", {"workspace": str(self.workspace), "success_criteria": task.success_criteria}))

        for index, action in enumerate(task.actions, start=1):
            trace.append(TraceEvent("decide", {"step": index, "tool": action.tool, "intended_effect": action.intended_effect}))

            try:
                result = self.registry.call(self.workspace, action.tool, action.args)
            except Exception as exc:  # starter-kit keeps failures explicit instead of hiding them.
                failure = self._failure(
                    phase="act",
                    category="tool_error",
                    message=str(exc),
                    recovery_action=action.on_failure,
                    evidence={"step": index, "tool": action.tool, "args": action.args},
                )
                failures.append(failure)
                trace.append(TraceEvent("failure_record", failure.__dict__))
                if action.on_failure == "continue":
                    continue
                failure.status = "stopped"
                trace.append(TraceEvent("stop_gate", {"reason": "tool_error", "step": index}))
                return RunResult(goal=task.goal, success=False, effects=effects, failures=failures, trace=trace, summary=f"Stopped after step {index} because tool execution failed.")

            trace.append(TraceEvent("tool_call", {"step": index, "tool": action.tool, "args": action.args, "result": result}))

            effect = EffectRecord(
                tool=action.tool,
                intended_effect=action.intended_effect,
                verification_kind=action.verification.kind,
            )
            try:
                ok, evidence = verify(self.workspace, action.verification, result)
            except Exception as exc:
                ok, evidence = False, {"error": str(exc)}

            effect.verification_status = "verified" if ok else "failed"
            effect.evidence = evidence
            effects.append(effect)
            trace.append(
                TraceEvent(
                    "effect_record",
                    {
                        "step": index,
                        "tool": action.tool,
                        "verification_status": effect.verification_status,
                        "evidence": evidence,
                    },
                )
            )
            if not ok:
                failure = self._failure(
                    phase="verify",
                    category="effect_failed",
                    message="verification failed",
                    recovery_action=action.on_failure,
                    evidence={"step": index, "tool": action.tool, "verification": action.verification.__dict__, "result": result},
                )
                failures.append(failure)
                trace.append(TraceEvent("failure_record", failure.__dict__))
                if action.on_failure == "continue":
                    continue
                failure.status = "stopped"
                trace.append(TraceEvent("stop_gate", {"reason": "verification_failed", "step": index}))
                summary = f"Stopped after step {index} because verification failed."
                return RunResult(goal=task.goal, success=False, effects=effects, failures=failures, trace=trace, summary=summary)

        success = all(effect.verification_status == "verified" for effect in effects) and not failures
        trace.append(TraceEvent("deliver", {"success": success, "verified_effects": sum(e.verification_status == 'verified' for e in effects), "failures": len(failures)}))
        summary = "All actions verified." if success else "Completed with verification gaps or recovered failures."
        return RunResult(goal=task.goal, success=success, effects=effects, failures=failures, trace=trace, summary=summary)


def action_from_dict(payload: dict) -> ActionSpec:
    from models import VerificationSpec

    verification = VerificationSpec(**payload["verification"])
    return ActionSpec(
        tool=payload["tool"],
        args=dict(payload.get("args", {})),
        intended_effect=payload["intended_effect"],
        verification=verification,
        on_failure=payload.get("on_failure", "stop"),
    )


def task_from_dict(payload: dict) -> TaskEnvelope:
    actions = [action_from_dict(item) for item in payload.get("actions", [])]
    return TaskEnvelope(
        goal=payload["goal"],
        actions=actions,
        success_criteria=list(payload.get("success_criteria", [])),
        metadata=dict(payload.get("metadata", {})),
    )
