# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
from __future__ import annotations

from dataclasses import asdict, dataclass, field
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
    on_failure: str = "stop"  # stop | continue | ask_user | retry_once


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
    verification_status: str = "pending"  # pending | verified | failed | blocked
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FailureRecord:
    phase: str
    category: str
    severity: str
    message: str
    recovery_action: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    status: str = "open"  # open | recovered | stopped | escalated


@dataclass
class TraceEvent:
    event_type: str
    payload: Dict[str, Any]


@dataclass
class RunResult:
    goal: str
    success: bool
    effects: List[EffectRecord]
    trace: List[TraceEvent]
    summary: str
    failures: List[FailureRecord] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "success": self.success,
            "effects": [asdict(effect) for effect in self.effects],
            "failures": [asdict(failure) for failure in self.failures],
            "trace": [asdict(event) for event in self.trace],
            "summary": self.summary,
        }
