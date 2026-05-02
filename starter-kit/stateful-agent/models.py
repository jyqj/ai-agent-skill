# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


@dataclass
class VerificationSpec:
    kind: str
    path: Optional[str] = None
    value: Optional[str] = None
    exit_code: Optional[int] = None


@dataclass
class ActionSpec:
    tool: str
    args: Dict[str, Any]
    intended_effect: str
    verification: VerificationSpec
    on_failure: str = "stop"


@dataclass
class TaskEnvelope:
    goal: str
    actions: List[ActionSpec] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EffectRecord:
    tool: str
    intended_effect: str
    verification_kind: str
    verification_status: str = "pending"
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FailureRecord:
    phase: str
    category: str
    severity: str
    message: str
    recovery_action: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    status: str = "open"


@dataclass
class TraceEvent:
    event_type: str
    payload: Dict[str, Any]


@dataclass
class WorldStateSnapshot:
    """A point-in-time snapshot of an external object's state."""

    snapshot_id: str
    target: str
    state: Dict[str, Any]
    observed_at: datetime
    freshness_ttl: timedelta
    confidence: float = 1.0
    source: str = "tool"

    def is_fresh(self, now: Optional[datetime] = None) -> bool:
        now = now or datetime.utcnow()
        return (now - self.observed_at) < self.freshness_ttl


@dataclass
class TaskCheckpoint:
    """Persisted state for resuming a long-running task."""

    task_goal: str
    completed_step: int
    total_steps: int
    effects: List[EffectRecord]
    failures: List[FailureRecord]
    trace: List[TraceEvent]
    world_snapshots: List[WorldStateSnapshot]
    context_summary: str
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_goal": self.task_goal,
            "completed_step": self.completed_step,
            "total_steps": self.total_steps,
            "effects": [asdict(e) for e in self.effects],
            "failures": [asdict(f) for f in self.failures],
            "trace": [asdict(t) for t in self.trace],
            "world_snapshots": [
                {
                    "snapshot_id": ws.snapshot_id,
                    "target": ws.target,
                    "state": ws.state,
                    "observed_at": ws.observed_at.isoformat(),
                    "freshness_ttl": ws.freshness_ttl.total_seconds(),
                    "confidence": ws.confidence,
                    "source": ws.source,
                }
                for ws in self.world_snapshots
            ],
            "context_summary": self.context_summary,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TaskCheckpoint:
        effects = [EffectRecord(**e) for e in data.get("effects", [])]
        failures = [FailureRecord(**f) for f in data.get("failures", [])]
        trace = [TraceEvent(**t) for t in data.get("trace", [])]
        world_snapshots = [
            WorldStateSnapshot(
                snapshot_id=ws["snapshot_id"],
                target=ws["target"],
                state=ws["state"],
                observed_at=datetime.fromisoformat(ws["observed_at"]),
                freshness_ttl=timedelta(seconds=ws["freshness_ttl"]),
                confidence=ws.get("confidence", 1.0),
                source=ws.get("source", "tool"),
            )
            for ws in data.get("world_snapshots", [])
        ]
        return cls(
            task_goal=data["task_goal"],
            completed_step=data["completed_step"],
            total_steps=data["total_steps"],
            effects=effects,
            failures=failures,
            trace=trace,
            world_snapshots=world_snapshots,
            context_summary=data.get("context_summary", ""),
            created_at=datetime.fromisoformat(data["created_at"]),
        )


@dataclass
class RunResult:
    goal: str
    success: bool
    effects: List[EffectRecord]
    trace: List[TraceEvent]
    summary: str
    failures: List[FailureRecord] = field(default_factory=list)
    checkpoint: Optional[TaskCheckpoint] = None

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "goal": self.goal,
            "success": self.success,
            "effects": [asdict(e) for e in self.effects],
            "failures": [asdict(f) for f in self.failures],
            "trace": [asdict(t) for t in self.trace],
            "summary": self.summary,
        }
        if self.checkpoint:
            result["checkpoint"] = self.checkpoint.to_dict()
        return result
