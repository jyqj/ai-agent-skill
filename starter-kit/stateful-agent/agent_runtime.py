# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from effects import verify
from models import (
    ActionSpec,
    EffectRecord,
    FailureRecord,
    RunResult,
    TaskCheckpoint,
    TaskEnvelope,
    TraceEvent,
    VerificationSpec,
    WorldStateSnapshot,
)
from state_store import StateStore
from tools import ToolRegistry, default_registry


class StatefulAgent:
    """Agent with checkpoint persistence, world-state TTL, and resumption."""

    def __init__(
        self,
        workspace: Path,
        store: StateStore,
        registry: Optional[ToolRegistry] = None,
        world_state_ttl: timedelta = timedelta(seconds=60),
    ) -> None:
        self.workspace = workspace
        self.store = store
        self.registry = registry or default_registry()
        self.world_state_ttl = world_state_ttl

    @staticmethod
    def task_id(goal: str) -> str:
        return hashlib.sha256(goal.encode()).hexdigest()[:12]

    def _failure(
        self,
        *,
        phase: str,
        category: str,
        message: str,
        recovery_action: str,
        evidence: Optional[Dict[str, Any]] = None,
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

    def _refresh_world_state(
        self,
        snapshots: List[WorldStateSnapshot],
        target: str,
        now: datetime,
    ) -> WorldStateSnapshot:
        """Refresh a world-state snapshot if stale, or create a new one."""
        for snap in snapshots:
            if snap.target == target and snap.is_fresh(now):
                return snap

        result = self.registry.call(self.workspace, "check_world_state", {"target": target})
        new_snap = WorldStateSnapshot(
            snapshot_id=f"{target}_{now.isoformat()}",
            target=target,
            state=result.get("state", {}),
            observed_at=now,
            freshness_ttl=self.world_state_ttl,
            confidence=1.0 if result.get("status") == "success" else 0.5,
            source="tool",
        )
        snapshots.append(new_snap)
        return new_snap

    def _compact_context(self, trace: List[TraceEvent], effects: List[EffectRecord]) -> str:
        """Produce a compact summary of progress so far."""
        verified = sum(1 for e in effects if e.verification_status == "verified")
        failed = sum(1 for e in effects if e.verification_status == "failed")
        steps = sum(1 for t in trace if t.event_type == "decide")
        return f"Steps executed: {steps}. Effects: {verified} verified, {failed} failed."

    def _save_checkpoint(
        self,
        task: TaskEnvelope,
        step: int,
        effects: List[EffectRecord],
        failures: List[FailureRecord],
        trace: List[TraceEvent],
        world_snapshots: List[WorldStateSnapshot],
    ) -> TaskCheckpoint:
        checkpoint = TaskCheckpoint(
            task_goal=task.goal,
            completed_step=step,
            total_steps=len(task.actions),
            effects=effects,
            failures=failures,
            trace=trace,
            world_snapshots=world_snapshots,
            context_summary=self._compact_context(trace, effects),
        )
        self.store.save(self.task_id(task.goal), checkpoint)
        return checkpoint

    def run(self, task: TaskEnvelope, resume: bool = True) -> RunResult:
        tid = self.task_id(task.goal)
        checkpoint = self.store.load(tid) if resume else None

        if checkpoint:
            start_step = checkpoint.completed_step
            trace = list(checkpoint.trace)
            effects = list(checkpoint.effects)
            failures = list(checkpoint.failures)
            world_snapshots = list(checkpoint.world_snapshots)
            trace.append(TraceEvent("resume", {
                "from_step": start_step,
                "context_summary": checkpoint.context_summary,
            }))
        else:
            start_step = 0
            trace = []
            effects = []
            failures = []
            world_snapshots = []
            trace.append(TraceEvent("intake", {"goal": task.goal, "action_count": len(task.actions)}))

        now = datetime.utcnow()

        for index_0, action in enumerate(task.actions):
            step = index_0 + 1
            if step <= start_step:
                continue

            trace.append(TraceEvent("decide", {
                "step": step,
                "tool": action.tool,
                "intended_effect": action.intended_effect,
            }))

            # Refresh world state if the action has world_state metadata.
            ws_target = action.args.get("world_state_target")
            if ws_target:
                snap = self._refresh_world_state(world_snapshots, ws_target, now)
                trace.append(TraceEvent("world_state_refresh", {
                    "target": ws_target,
                    "fresh": snap.is_fresh(now),
                    "observed_at": snap.observed_at.isoformat(),
                }))

            try:
                result = self.registry.call(self.workspace, action.tool, action.args)
            except Exception as exc:
                failure = self._failure(
                    phase="act",
                    category="tool_error",
                    message=str(exc),
                    recovery_action=action.on_failure,
                    evidence={"step": step, "tool": action.tool},
                )
                failures.append(failure)
                trace.append(TraceEvent("failure_record", failure.__dict__))
                cp = self._save_checkpoint(task, step - 1, effects, failures, trace, world_snapshots)
                if action.on_failure == "continue":
                    continue
                failure.status = "stopped"
                trace.append(TraceEvent("stop_gate", {"reason": "tool_error", "step": step}))
                return RunResult(
                    goal=task.goal,
                    success=False,
                    effects=effects,
                    failures=failures,
                    trace=trace,
                    summary=f"Stopped at step {step} (tool error). Checkpoint saved.",
                    checkpoint=cp,
                )

            trace.append(TraceEvent("tool_call", {
                "step": step,
                "tool": action.tool,
                "result": result,
            }))

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
            trace.append(TraceEvent("effect_record", {
                "step": step,
                "tool": action.tool,
                "verification_status": effect.verification_status,
                "evidence": evidence,
            }))

            # Checkpoint after each step.
            self._save_checkpoint(task, step, effects, failures, trace, world_snapshots)

            if not ok:
                failure = self._failure(
                    phase="verify",
                    category="effect_failed",
                    message="verification failed",
                    recovery_action=action.on_failure,
                    evidence={"step": step, "tool": action.tool},
                )
                failures.append(failure)
                trace.append(TraceEvent("failure_record", failure.__dict__))
                if action.on_failure == "continue":
                    continue
                failure.status = "stopped"
                trace.append(TraceEvent("stop_gate", {"reason": "verification_failed", "step": step}))
                return RunResult(
                    goal=task.goal,
                    success=False,
                    effects=effects,
                    failures=failures,
                    trace=trace,
                    summary=f"Stopped at step {step} (verification failed). Checkpoint saved.",
                )

        success = all(e.verification_status == "verified" for e in effects) and not failures
        # Clean up checkpoint on success.
        self.store.delete(tid)
        trace.append(TraceEvent("deliver", {
            "success": success,
            "verified_effects": sum(e.verification_status == "verified" for e in effects),
            "failures": len(failures),
        }))
        summary = "All actions verified." if success else "Completed with verification gaps or recovered failures."
        return RunResult(goal=task.goal, success=success, effects=effects, failures=failures, trace=trace, summary=summary)


def action_from_dict(payload: dict) -> ActionSpec:
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
