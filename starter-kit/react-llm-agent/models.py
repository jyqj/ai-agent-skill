# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
# models.py -- 核心数据对象，复用 verified-tool-agent 的设计并新增 LLM 决策类型
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TaskEnvelope:
    goal: str
    success_criteria: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EffectRecord:
    tool: str
    intended_effect: str
    verification_method: str = "none"  # readback | test | external_ack | human_confirm | none
    # pending | verified | partially_verified | failed | unverifiable_by_agent | blocked
    verification_status: str = "pending"
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TraceEvent:
    event_type: str
    payload: Dict[str, Any]


@dataclass
class Decision:
    """LLM 产出的单步决策。"""
    type: str  # "tool_call" | "finalize" | "ask_user"
    tool_name: Optional[str] = None
    args: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""
    intended_effect: str = ""  # 本次工具调用期望达成的世界状态变化
    postconditions: List[str] = field(default_factory=list)  # 执行后应为真的条件列表
    verification_method: str = "none"  # readback | test | external_ack | human_confirm | none


@dataclass
class RunResult:
    goal: str
    success: bool
    effects: List[EffectRecord]
    trace: List[TraceEvent]
    summary: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "success": self.success,
            "effects": [asdict(e) for e in self.effects],
            "trace": [asdict(e) for e in self.trace],
            "summary": self.summary,
        }
